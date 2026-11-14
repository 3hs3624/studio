"""API definitions, encrypted credentials and audited execution queue."""
import hashlib,hmac,ipaddress,json,re,secrets,uuid
from datetime import timedelta
from urllib.parse import urlsplit,parse_qsl,urlencode,quote
from xml.sax.saxutils import escape
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.crypto import salted_hmac
from .. import services as s
from ..permissions import require,allowed
from ..access_graph import role_rows
from ..security_policy import require_recent
from ..models import (Organization,Person,IntegrationDefinition,IntegrationVersion,IntegrationCredential,IntegrationNetworkPolicy,IntegrationClient,IntegrationJob,IntegrationEvent,IntegrationDataLink,IntegrationDataRevision,EntityDefinition,ProcessDefinition)
from .transport import seal,unseal,address,request,authentication,TransportError
from .mapping import rules_validate,apply,path,MISSING,render,parse_xml,MappingError

PROTOCOLS={'REST':'REST / JSON','SOAP':'SOAP / XML','GRAPHQL':'GraphQL','WEBHOOK':'Webhook · 데이터 수신'}
AUTH={'NONE':'인증 없음','BEARER':'Bearer Token','BASIC':'Basic','API_KEY':'API Key','OAUTH2_CLIENT':'OAuth2 Client Credentials'}

def definition(actor,id):
    value=IntegrationDefinition.objects.filter(organization=actor.organization,id=s.identifier(id)).first()
    if not value:s.fail('NOT_FOUND','API 정의를 찾을 수 없습니다.',404)
    return value

def version(actor,id,active=True):
    value=IntegrationVersion.objects.filter(organization=actor.organization,id=s.identifier(id)).select_related('definition__run_as','credential').first()
    if not value or active and not value.definition.active:s.fail('NOT_FOUND','사용 가능한 API 버전을 찾을 수 없습니다.',404)
    return value

def typed_fields(raw):
    if not isinstance(raw,list) or len(raw)>100:s.fail('INVALID_CONTRACT','입력 항목은 최대 100개입니다.')
    result=[]
    for field in raw:
        s.check_fields(field,['key','type','required','description'],['key','type','required'])
        key=s.text(field,'key',80)
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,79}',key) or key in {f['key'] for f in result} or field['type'] not in ('text','number','boolean','json') or type(field['required']) is not bool:s.fail('INVALID_CONTRACT','입력 이름·유형·필수 여부를 확인하십시오.')
        result.append(dict(key=key,type=field['type'],required=field['required'],description=s.text(field,'description',500,False)))
    return result

def input_values(settings,raw):
    if settings.get('accept_any_json'):
        if not isinstance(raw,(dict,list)):s.fail('INVALID_INPUT','JSON 객체 또는 목록을 전달하십시오.')
        return raw
    if not isinstance(raw,dict) or set(raw)-{f['key'] for f in settings['input_fields']}:s.fail('INVALID_INPUT','등록된 입력 항목만 전달하십시오.')
    result={}
    for field in settings['input_fields']:
        key=field['key']
        if key not in raw:
            if field['required']:s.fail('REQUIRED_FIELD',key+' 항목이 필요합니다.')
            continue
        value=raw[key];type_=field['type']
        valid=isinstance(value,str) and len(value)<=20000 if type_=='text' else type(value) in (int,float) and abs(value)<=10**15 if type_=='number' else type(value) is bool if type_=='boolean' else isinstance(value,(dict,list))
        if not valid:s.fail('INVALID_INPUT',key+' 자료형을 확인하십시오.')
        result[key]=value
    return result

def validate(actor,definition_,raw):
    if not isinstance(raw,dict):s.fail('INVALID_API','API 설정 객체가 필요합니다.')
    keys=['url','method','headers','input_fields','request_mapping','response_mapping','timeout','retries','target_idempotency','effect','credential_id','allowed_roles','allowed_workflows','body_template','graphql_document','soap_action','soap_version','xml_template','accept_any_json','entity_id','items_path','record_mapping','external_key_path','write_mode','documentation','schema_version_id']
    s.check_fields(raw,keys,['input_fields','response_mapping'])
    settings=dict(raw);settings['input_fields']=typed_fields(raw['input_fields'])
    try:
        settings['response_mapping']=rules_validate(raw['response_mapping'])
        settings['request_mapping']=rules_validate(raw.get('request_mapping',{}))
        settings['record_mapping']=rules_validate(raw.get('record_mapping',{}))
        path({},raw.get('items_path',''));path({},raw.get('external_key_path',''))
    except MappingError as exc:s.fail(str(exc),'항목 매핑 규칙을 확인하십시오.')
    for key,default,min_,max_ in [('timeout',15,1,30),('retries',0,0,3)]:
        settings[key]=raw.get(key,default)
        if type(settings[key]) is not int or not min_<=settings[key]<=max_:s.fail('INVALID_API','시간 제한·재시도 범위를 확인하십시오.')
    for key in ('target_idempotency','accept_any_json'):
        settings[key]=raw.get(key,False)
        if type(settings[key]) is not bool:s.fail('INVALID_API','실행 옵션을 확인하십시오.')
    settings['effect']=raw.get('effect','READ')
    if settings['effect'] not in ('READ','WRITE'):s.fail('INVALID_API','읽기·변경 API 구분을 확인하십시오.')
    settings['allowed_roles']=raw.get('allowed_roles',['ORG_ADMIN','DEVELOPER','SOLUTION_OPERATOR']);settings['allowed_workflows']=raw.get('allowed_workflows',[])
    from ..organization_management import role_object
    for key in ('allowed_roles','allowed_workflows'):
        if not isinstance(settings[key],list) or len(settings[key])>100 or any(not isinstance(v,str) for v in settings[key]):s.fail('INVALID_CALL_SCOPE','호출 허용 대상을 확인하십시오.')
    for role in settings['allowed_roles']:role_object(actor,role)
    if ProcessDefinition.objects.filter(organization=actor.organization,kind='WORKFLOW',id__in=[s.identifier(id) for id in settings['allowed_workflows']]).count()!=len(set(settings['allowed_workflows'])):s.fail('INVALID_CALL_SCOPE','현재 조직의 워크플로우만 지정하십시오.')
    credential=None
    if raw.get('credential_id'):
        credential=IntegrationCredential.objects.filter(organization=actor.organization,active=True,id=s.identifier(raw['credential_id'])).first()
        if not credential:s.fail('INVALID_CREDENTIAL','현재 조직의 활성 인증정보를 선택하십시오.')
    if definition_.protocol!='WEBHOOK':
        url=s.text(raw,'url',1000)
        try:address(actor.organization,url,False)
        except TransportError as error:s.fail(error.code,'보안 관리자가 허용한 HTTPS 호스트를 사용하십시오.')
        if settings.get('effect')=='READ' and raw.get('method','GET' if definition_.protocol=='REST' else 'POST').upper() in ('PUT','PATCH','DELETE'):s.fail('INVALID_EFFECT','변경 메서드는 변경 API로 분류하십시오.')
        if any(key.lower() in ('token','password','api_key','apikey','secret','authorization') for key,_ in parse_qsl(urlsplit(url).query)):s.fail('SECRET_IN_URL','인증 값은 별도 인증정보에 등록하십시오.')
        settings['method']=raw.get('method','GET' if definition_.protocol=='REST' else 'POST').upper()
        if settings['method'] not in ('GET','POST','PUT','PATCH','DELETE'):s.fail('INVALID_METHOD','HTTP 메서드를 확인하십시오.')
        if definition_.protocol in ('SOAP','GRAPHQL') and settings['method']!='POST':s.fail('INVALID_METHOD','SOAP·GraphQL은 POST를 사용하십시오.')
        headers=raw.get('headers',{})
        if not isinstance(headers,dict) or len(headers)>20:s.fail('INVALID_HEADERS','헤더를 확인하십시오.')
        for key,value in headers.items():
            if not re.fullmatch(r'[A-Za-z0-9-]{1,80}',key) or key.lower() in ('host','authorization','proxy-authorization','cookie','connection','content-length','transfer-encoding') or not isinstance(value,str) or len(value)>1000 or any(c in value for c in '\r\n'):s.fail('INVALID_HEADERS','인증·쿠키·연결 헤더는 직접 설정할 수 없습니다.')
        settings['headers']=headers
        if definition_.protocol=='SOAP':
            template=s.text(raw,'xml_template',20000);parse_xml(re.sub(r'\{\{[A-Za-z][A-Za-z0-9_]*\}\}','value',template).encode());settings['soap_version']=raw.get('soap_version','1.1')
            if settings['soap_version'] not in ('1.1','1.2') or any(c in raw.get('soap_action','') for c in '\r\n'):s.fail('INVALID_SOAP','SOAP 버전·Action을 확인하십시오.')
        if definition_.protocol=='GRAPHQL':
            document=s.text(raw,'graphql_document',20000)
            if not re.match(r'^\s*(query|mutation|\{)',document):s.fail('INVALID_GRAPHQL','고정된 GraphQL query·mutation 문서가 필요합니다.')
            if re.search(r'\bmutation\b',document) and settings['effect']!='WRITE':s.fail('GRAPHQL_EFFECT','mutation은 변경 API로 분류하십시오.')
    if raw.get('entity_id'):
        entity=EntityDefinition.objects.filter(organization=actor.organization,id=s.identifier(raw['entity_id'])).first()
        from ..entity_service import latest
        schema=latest(entity) if entity else None
        if not schema or not settings['record_mapping']:s.fail('INVALID_DATA_TARGET','게시된 대상 엔티티와 항목 매핑이 필요합니다.')
        if set(settings['record_mapping'])-{f['key'] for f in schema.fields}:s.fail('INVALID_DATA_TARGET','대상 엔티티에 없는 항목이 있습니다.')
        if not raw.get('external_key_path'):s.fail('EXTERNAL_KEY_REQUIRED','중복 판별용 원본 식별자 경로가 필요합니다.')
        settings['schema_version_id']=str(schema.id)
        settings['write_mode']=raw.get('write_mode','SKIP_DUPLICATE')
        if settings['write_mode'] not in ('SKIP_DUPLICATE','APPEND_REVISION'):s.fail('INVALID_DATA_TARGET','중복 건너뛰기 또는 개정 추가를 선택하십시오.')
    return settings,credential

def authorize(actor,operation,target):
    if operation=='int_network':require(actor,'security.manage')
    elif operation=='int_invoke':require(actor,'integration.invoke')
    else:require(actor,'integration.manage')
    require_recent(actor)

def mutate(actor,operation,data,request_id,target):
    reason=s.text(data,'reason',500,False)
    if operation=='int_network':
        s.check_fields(data,['allowed_hosts','allowed_private_cidrs','expected_version','reason'],['allowed_hosts','allowed_private_cidrs','expected_version','reason'])
        if not isinstance(data['allowed_hosts'],list) or len(data['allowed_hosts'])>100 or not isinstance(data['allowed_private_cidrs'],list) or len(data['allowed_private_cidrs'])>50:s.fail('INVALID_NETWORK_POLICY','허용 호스트·대역을 확인하십시오.')
        hosts=[]
        for host in data['allowed_hosts']:
            if not isinstance(host,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.\-]{0,252}',host) or host.lower()=='localhost':s.fail('INVALID_NETWORK_POLICY','정확한 호스트명을 입력하십시오. 와일드카드는 허용하지 않습니다.')
            hosts.append(host.lower())
        try:cidrs=[str(ipaddress.ip_network(value,strict=False)) for value in data['allowed_private_cidrs']]
        except (ValueError,TypeError):s.fail('INVALID_NETWORK_POLICY','CIDR 표기를 확인하십시오.')
        value=IntegrationNetworkPolicy.objects.filter(organization=actor.organization).first()
        if data['expected_version']!=(value.row_version if value else 0):s.fail('VERSION_CONFLICT','허용 정책이 변경되었습니다.',409)
        if not value:value=IntegrationNetworkPolicy(organization=actor.organization,updated_by=actor,row_version=0)
        value.allowed_hosts=list(dict.fromkeys(hosts));value.allowed_private_cidrs=cidrs;value.updated_by=actor;value.row_version+=1;value.save();s.record(actor,value,'INTEGRATION_NETWORK_CHANGED',request_id,after={'hosts':hosts,'cidrs':cidrs,'reason':reason});return {'id':str(value.id),'version':value.row_version},200
    if operation=='int_credential':
        s.check_fields(data,['name','auth_type','secret','active','expected_version','reason'],['name','auth_type','active','expected_version','reason'])
        if data['auth_type'] not in AUTH or type(data['active']) is not bool:s.fail('INVALID_CREDENTIAL','인증 유형과 사용 여부를 확인하십시오.')
        value=IntegrationCredential.objects.filter(organization=actor.organization,id=s.identifier(target)).first() if target else None
        if target and not value:s.fail('NOT_FOUND','인증정보를 찾을 수 없습니다.',404)
        if data['expected_version']!=(value.row_version if value else 0):s.fail('VERSION_CONFLICT','인증정보가 변경되었습니다.',409)
        if not value:value=IntegrationCredential(organization=actor.organization,updated_by=actor,row_version=0)
        secret=data.get('secret')
        if secret is None:
            if not value.encrypted_secret or data['auth_type']!=value.auth_type:s.fail('SECRET_REQUIRED','새 인증정보를 입력하십시오.')
        else:
            names={'NONE':set(),'BEARER':{'token'},'BASIC':{'username','password'},'API_KEY':{'name','value','location'},'OAUTH2_CLIENT':{'token_url','client_id','client_secret','scope'}}[data['auth_type']]
            if not isinstance(secret,dict) or set(secret)-names or any(not isinstance(v,str) or len(v)>16384 or any(c in v for c in '\r\n') for v in secret.values()):s.fail('INVALID_CREDENTIAL','인증 항목을 확인하십시오.')
            required=names-{'scope'}
            if any(not secret.get(k) for k in required):s.fail('SECRET_REQUIRED','필수 인증 항목을 입력하십시오.')
            if data['auth_type']=='API_KEY' and (secret['location'] not in ('HEADER','QUERY') or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}',secret['name']) or secret['name'].lower() in ('host','cookie','connection','content-length','authorization','proxy-authorization')):s.fail('INVALID_CREDENTIAL','API Key 위치·이름을 확인하십시오.')
            if data['auth_type']=='OAUTH2_CLIENT':
                try:address(actor.organization,secret['token_url'],False)
                except TransportError:s.fail('INVALID_CREDENTIAL','허용된 HTTPS 토큰 주소를 사용하십시오.')
            value.encrypted_secret=seal(secret)
        value.name=s.text(data,'name',200);value.auth_type=data['auth_type'];value.active=data['active'];value.updated_by=actor;value.row_version+=1;value.save();s.record(actor,value,'INTEGRATION_CREDENTIAL_CHANGED',request_id,after={'auth_type':value.auth_type,'active':value.active,'reason':reason});return {'id':str(value.id),'version':value.row_version},200
    if operation=='int_save':
        s.check_fields(data,['code','name','protocol','run_as','active','settings','expected_version','reason'],['code','name','protocol','run_as','active','settings','expected_version','reason'])
        from ..identity_management import code
        key=code(data);value=definition(actor,target) if target else None
        if data['protocol'] not in PROTOCOLS or type(data['active']) is not bool:s.fail('INVALID_API','프로토콜·사용 여부를 확인하십시오.')
        if data['expected_version']!=(value.row_version if value else 0):s.fail('VERSION_CONFLICT','API 정의가 변경되었습니다.',409)
        if value and (key!=value.code or data['protocol']!=value.protocol):s.fail('IMMUTABLE_CODE','API 코드·프로토콜은 변경할 수 없습니다.')
        run_as=Person.objects.filter(organization=actor.organization,active=True,user__is_active=True,id=s.identifier(data['run_as'])).first()
        if not run_as or not allowed(run_as,'integration.invoke'):s.fail('INVALID_EXECUTOR','연계 호출 권한이 있는 활성 실행 계정을 선택하십시오.')
        if not value:value=IntegrationDefinition(organization=actor.organization,code=key,protocol=data['protocol'],updated_by=actor,run_as=run_as,row_version=0)
        raw=data['settings']
        if not isinstance(raw,dict):s.fail('INVALID_API','설정 객체가 필요합니다.')
        # Never retain a plaintext credential even in an invalid draft.
        sensitive={'authorization','proxy-authorization','cookie','x-api-key','api-key','x-auth-token'}
        if any(str(k).lower() in sensitive or re.search(r'(password|secret|token)',str(k),re.I) for k in raw.get('headers',{})):s.fail('SECRET_IN_HEADERS','인증 값은 별도 인증정보에 등록하십시오.')
        if any(k in raw for k in ('secret','password','token','client_secret','api_key')):s.fail('SECRET_IN_SETTINGS','비밀 값은 별도 인증정보에 등록하십시오.')
        try:settings,_=validate(actor,value,data['settings']);errors=[]
        except (s.BusinessError,MappingError) as error:settings=data['settings'];errors=[error.message if isinstance(error,s.BusinessError) else str(error)]
        if not isinstance(settings,dict):s.fail('INVALID_API','설정 객체가 필요합니다.')
        value.name=s.text(data,'name',200);value.run_as=run_as;value.active=data['active'];value.draft=settings;value.validation_errors=errors;value.updated_by=actor;value.row_version+=1;value.save();s.record(actor,value,'INTEGRATION_DRAFT_SAVED',request_id,after={'revision':value.row_version,'reason':reason});return {'id':str(value.id),'version':value.row_version,'validation_errors':errors},200
    if operation=='int_publish':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason']);value=definition(actor,target);s.version(value,data);settings,credential=validate(actor,value,value.draft)
        number=(value.versions.aggregate(value=Max('version'))['value'] or 0)+1
        api=IntegrationVersion.objects.create(organization=actor.organization,definition=value,version=number,settings=settings,credential=credential,published_by=actor,reason=s.text(data,'reason',500),digest=hashlib.sha256(json.dumps(settings,sort_keys=True).encode()).hexdigest());value.published=api;value.row_version+=1;value.save();s.record(actor,value,'INTEGRATION_PUBLISHED',request_id,after={'version_id':str(api.id),'number':number,'reason':reason});return {'id':str(value.id),'version':value.row_version},200
    if operation=='int_invoke':
        s.check_fields(data,['inputs','confirm_write','reason'],['inputs']);api=version(actor,target)
        if not set(api.settings['allowed_roles'])&{r['key'] for r in role_rows(actor)}:s.fail('CALL_NOT_ALLOWED','이 API의 호출 허용 역할이 아닙니다.',403)
        if api.settings['effect']=='WRITE' and data.get('confirm_write') is not True:s.fail('WRITE_CONFIRMATION','외부 시스템 변경 호출임을 확인하십시오.')
        job=enqueue(actor,api,data['inputs'],str(request_id));return {'id':str(job.id),'status':job.status},202
    if operation=='int_client':
        s.check_fields(data,['name','rate_limit','auth_mode','reason'],['name','rate_limit','auth_mode','reason']);api=version(actor,target)
        if type(data['rate_limit']) is not int or not 1<=data['rate_limit']<=1000 or data['auth_mode'] not in ('API_KEY','HMAC_SHA256'):s.fail('INVALID_CLIENT','호출 한도·인증 방식을 확인하십시오.')
        value=IntegrationClient.objects.create(organization=actor.organization,version=api,name=s.text(data,'name',200),rate_limit=data['rate_limit'],auth_mode=data['auth_mode'],created_by=actor);s.record(actor,value,'INTEGRATION_CLIENT_CREATED',request_id,after={'version_id':str(api.id),'rate_limit':value.rate_limit,'auth_mode':value.auth_mode,'reason':reason});return {'id':str(value.id)},201
    if operation=='int_client-stop':
        s.check_fields(data,['reason'],['reason']);value=IntegrationClient.objects.filter(organization=actor.organization,id=s.identifier(target)).first()
        if not value:s.fail('NOT_FOUND','호출 계정을 찾을 수 없습니다.',404)
        value.active=False;value.save(update_fields=['active']);s.record(actor,value,'INTEGRATION_CLIENT_STOPPED',request_id,after={'reason':s.text(data,'reason',500)});return {'id':str(value.version.definition_id)},200
    if operation in ('int_retry','int_remap'):
        s.check_fields(data,['reason','mapping_version_id'],['reason']);job=IntegrationJob.objects.filter(organization=actor.organization,id=s.identifier(target)).select_related('version__definition').first()
        if not job:s.fail('NOT_FOUND','호출 이력을 찾을 수 없습니다.',404)
        if operation=='int_retry':
            if job.status!='FAILED' or job.version.settings['effect']=='WRITE' and not job.version.settings['target_idempotency']:s.fail('UNSAFE_RETRY','안전하게 재시도 가능한 실패 건만 선택하십시오.',409)
            job.status='QUEUED';job.next_attempt_at=timezone.now();job.error_code='';job.save(update_fields=['status','next_attempt_at','error_code'])
        else:
            if not job.response_cipher or job.status not in ('MAPPING_FAILED','SUCCESS'):s.fail('NO_RESPONSE','보관된 응답이 있어야 매핑만 재처리할 수 있습니다.',409)
            replacement=version(actor,data.get('mapping_version_id'))
            if replacement.definition_id!=job.version.definition_id:s.fail('INVALID_MAPPING_VERSION','같은 API 정의의 게시 버전을 선택하십시오.')
            job.mapping_version=replacement;job.save(update_fields=['mapping_version']);finish_mapping(job,unseal(job.response_cipher),actor)
        IntegrationEvent.objects.create(organization=actor.organization,job=job,actor=actor,action='RETRY_REQUESTED' if operation=='int_retry' else 'RESPONSE_REMAPPED',details={'mapping_version_id':str(job.mapping_version_id) if job.mapping_version_id else None,'reason':s.text(data,'reason',500)})
        return {'id':str(job.id),'status':job.status},200
    s.fail('INVALID_OPERATION','지원하지 않는 API 관리 작업입니다.')

def enqueue(actor,api,inputs,key,process_task=None):
    definition_=api.definition;executor=definition_.run_as
    if not definition_.active or not executor.active or not executor.user.is_active or not allowed(executor,'integration.invoke'):s.fail('EXECUTOR_DISABLED','연계 정의·실행 계정이 중지되었습니다.',403)
    values=input_values(api.settings,inputs);value_hash=hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
    existing=IntegrationJob.objects.filter(organization=actor.organization,version=api,initiated_by=actor,external_key=key).first()
    if existing:
        if hashlib.sha256(json.dumps(unseal(existing.input_cipher),sort_keys=True).encode()).hexdigest()!=value_hash:s.fail('IDEMPOTENCY_CONFLICT','같은 호출 키에 다른 입력을 사용할 수 없습니다.',409)
        return existing
    job=IntegrationJob.objects.create(organization=actor.organization,version=api,initiated_by=actor,external_key=key,input_cipher=seal(values),process_task=process_task)
    IntegrationEvent.objects.create(organization=actor.organization,job=job,actor=actor,action='QUEUED',details={'input_digest':value_hash});return job

def issue_secret(actor,id):
    with transaction.atomic():
        client=IntegrationClient.objects.select_for_update().filter(organization=actor.organization,id=s.identifier(id)).first()
        if not client or client.issued:return None
        token=secrets.token_urlsafe(40);client.token_hash=hashlib.sha256(token.encode()).hexdigest();client.secret_cipher=seal({'secret':token}) if client.auth_mode=='HMAC_SHA256' else '';client.issued=True;client.save(update_fields=['token_hash','secret_cipher','issued']);return token

def build_request(job,inputs):
    api=job.version;settings=api.settings;protocol=api.definition.protocol;params=apply(inputs,settings.get('request_mapping',{})) if settings.get('request_mapping') else inputs
    if not isinstance(params,dict):raise MappingError('OUTBOUND_OBJECT_REQUIRED')
    headers={'Accept':'application/json',**settings.get('headers',{})};auth_headers,auth_query=authentication(job.organization,api.credential,settings['timeout']);headers.update(auth_headers)
    url=settings['url']
    for key,value in params.items():
        if '{'+key+'}' in url:
            if not isinstance(value,(str,int,float,bool)) or str(value) in ('.','..'):raise MappingError('INVALID_PATH_PARAMETER')
            url=url.replace('{'+key+'}',quote(str(value),safe=''))
    method=settings['method'];body=None;query=dict(parse_qsl(urlsplit(url).query));query.update(auth_query)
    if method=='GET':query.update({key:str(value) for key,value in params.items() if '{'+key+'}' not in settings['url']})
    elif protocol=='SOAP':
        template=settings['xml_template']
        for key,value in params.items():template=template.replace('{{'+key+'}}',escape(str(value),{'"':'&quot;',"'":'&apos;'}))
        if re.search(r'\{\{[^}]+\}\}',template):raise MappingError('MISSING_SOAP_INPUT')
        parse_xml(template.encode());body=template.encode();headers['Content-Type']='application/soap+xml; charset=utf-8' if settings['soap_version']=='1.2' else 'text/xml; charset=utf-8'
        if settings.get('soap_action'):headers['SOAPAction']=settings['soap_action']
    else:
        content={'query':settings['graphql_document'],'variables':params} if protocol=='GRAPHQL' else render(settings.get('body_template',params),params)
        body=json.dumps(content,ensure_ascii=False,allow_nan=False).encode();headers['Content-Type']='application/json'
    if query:url=url.split('?',1)[0]+'?'+urlencode(query)
    headers['Idempotency-Key']=str(job.id)
    return method,url,headers,body

def sink(job,data,settings,actor):
    if not settings.get('entity_id'):return {'inserted':0,'revised':0,'skipped':0}
    from ..entity_service import create_record
    rows=path(data,settings.get('items_path',''))
    if rows is MISSING:raise MappingError('MISSING_ITEMS')
    if not isinstance(rows,list):rows=[rows]
    if len(rows)>500:raise MappingError('ITEM_LIMIT')
    result={'inserted':0,'revised':0,'skipped':0}
    for index,item in enumerate(rows):
        key=path(item,settings['external_key_path'])
        if key is MISSING or not isinstance(key,(str,int)):raise MappingError('EXTERNAL_KEY_REQUIRED')
        values=apply(item,settings['record_mapping']);row_digest=hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest();external_hash=salted_hmac('integration-key',str(key),algorithm='sha256').hexdigest()
        link=IntegrationDataLink.objects.filter(organization=job.organization,definition=job.version.definition,entity_id=settings['entity_id'],external_hash=external_hash).first()
        if link and (link.row_digest==row_digest or settings['write_mode']=='SKIP_DUPLICATE'):result['skipped']+=1;continue
        from ..permissions import require
        require(actor,'entity.write')
        record,_=create_record(actor,{'schema_version_id':settings['schema_version_id'],'values':values},uuid.uuid4(),settings['entity_id'])
        if link:link.record_id=record['id'];link.row_digest=row_digest;link.save();result['revised']+=1
        else:link=IntegrationDataLink.objects.create(organization=job.organization,definition=job.version.definition,entity_id=settings['entity_id'],external_hash=external_hash,record_id=record['id'],row_digest=row_digest);result['inserted']+=1
        IntegrationDataRevision.objects.create(organization=job.organization,link=link,record_id=record['id'],job=job)
    return result

def finish_mapping(job,data,actor=None):
    api=job.mapping_version or job.version;executor=job.version.definition.run_as
    mapped=apply(data,api.settings['response_mapping']);counts=sink(job,data,api.settings,executor)
    job.mapped_cipher=seal(mapped);job.status='SUCCESS';job.completed_at=timezone.now();job.error_code='';job.save(update_fields=['mapped_cipher','status','completed_at','error_code'])
    IntegrationEvent.objects.create(organization=job.organization,job=job,actor=actor,action='MAPPED',details={'fields':list(mapped),'counts':counts,'mapping_version':str(api.id)})
    if job.process_task_id:
        from ..process_engine import resume_api
        resume_api(executor,job,mapped)

def process_one(id=None):
    from django.db.models import Q
    candidate=IntegrationJob.objects.filter(id=id).first() if id else IntegrationJob.objects.filter(Q(status='QUEUED',next_attempt_at__lte=timezone.now())|Q(status='RUNNING',lease_until__lt=timezone.now())).order_by('next_attempt_at','created_at').first()
    if not candidate:return None
    with transaction.atomic():
        Organization.objects.select_for_update().get(pk=candidate.organization_id)
        job=IntegrationJob.objects.select_for_update().select_related('version__definition__run_as','version__credential','organization').get(pk=candidate.id)
        now=timezone.now()
        if job.status=='RUNNING' and job.lease_until and job.lease_until<now:
            job.status='QUEUED' if job.version.settings['effect']=='READ' else 'UNKNOWN';job.error_code='WORKER_LEASE_EXPIRED';job.save(update_fields=['status','error_code'])
        if job.status!='QUEUED' or job.next_attempt_at>now:return job
        if job.process_task_id and job.process_task.status!='OPEN':
            job.status='FAILED';job.error_code='WORKFLOW_CANCELLED';job.completed_at=now;job.save(update_fields=['status','error_code','completed_at']);IntegrationEvent.objects.create(organization=job.organization,job=job,action='CANCELLED_BEFORE_CALL',details={});return job
        job.status='RUNNING';job.attempts+=1;job.lease_until=now+timedelta(seconds=job.version.settings['timeout']+30);job.save(update_fields=['status','attempts','lease_until']);IntegrationEvent.objects.create(organization=job.organization,job=job,action='STARTED',details={'attempt':job.attempts})
    response=None;status=None;failure=None
    try:
        executor=job.version.definition.run_as
        if not job.version.definition.active or not executor.active or not executor.user.is_active or not allowed(executor,'integration.invoke'):raise TransportError('EXECUTOR_DISABLED')
        if job.version.definition.protocol=='WEBHOOK':response=unseal(job.input_cipher)
        else:
            method,url,headers,body=build_request(job,unseal(job.input_cipher));status,payload,content_type=request(job.organization,method,url,headers,body,job.version.settings['timeout'])
            response=parse_xml(payload) if job.version.definition.protocol=='SOAP' or 'xml' in content_type.lower() else json.loads(payload or b'{}')
        if job.version.definition.protocol=='GRAPHQL' and isinstance(response,dict) and response.get('errors'):raise TransportError('GRAPHQL_ERRORS')
    except TransportError as error:failure=error
    except (MappingError,ValueError,KeyError,TypeError):failure=TransportError('INVALID_REQUEST_OR_RESPONSE')
    except Exception:failure=TransportError('CREDENTIAL_OR_EXECUTION_ERROR')
    with transaction.atomic():
        Organization.objects.select_for_update().get(pk=job.organization_id);job=IntegrationJob.objects.select_for_update().select_related('version__definition__run_as').get(pk=job.id)
        if job.status!='RUNNING':return job
        job.http_status=status or (failure.status if failure else None)
        if failure:
            safe=job.version.settings['effect']=='READ' or job.version.settings['target_idempotency'];retry=failure.retryable and safe and job.attempts<=job.version.settings['retries']
            job.status='QUEUED' if retry else 'UNKNOWN' if failure.retryable and not safe else 'FAILED';job.error_code=failure.code;job.next_attempt_at=timezone.now()+timedelta(seconds=min(300,2**job.attempts));job.completed_at=None if retry else timezone.now();job.save();IntegrationEvent.objects.create(organization=job.organization,job=job,action='RETRY_SCHEDULED' if retry else job.status,details={'code':failure.code,'http_status':job.http_status})
            if job.process_task_id and not retry:
                from ..process_engine import api_failed
                api_failed(job.version.definition.run_as,job,failure.code)
        else:
            job.response_cipher=seal(response);job.save(update_fields=['response_cipher','http_status'])
            try:
                with transaction.atomic():finish_mapping(job,response)
            except (MappingError,s.BusinessError,ValueError,TypeError) as error:
                job.refresh_from_db();job.status='MAPPING_FAILED';job.error_code=error.code if isinstance(error,s.BusinessError) else str(error)[:80] if isinstance(error,MappingError) else 'OUTPUT_TYPE_ERROR';job.completed_at=timezone.now();job.save(update_fields=['status','error_code','completed_at']);IntegrationEvent.objects.create(organization=job.organization,job=job,action='MAPPING_FAILED',details={'code':job.error_code})
                if job.process_task_id:
                    from ..process_engine import api_failed
                    api_failed(job.version.definition.run_as,job,job.error_code)
        return job
