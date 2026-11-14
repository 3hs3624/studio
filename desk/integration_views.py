import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .views import context
from . import services as s
from .api import endpoint,error,body
from .permissions import require,people_with
from .models import IntegrationDefinition,IntegrationCredential,IntegrationJob,IntegrationNetworkPolicy,IntegrationClient
from .integrations import service, specs
from .integrations.transport import unseal

@login_required
def manage(request,id=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'integration.manage')
        selected=service.definition(actor,id) if id else None
        c.update(integrations=IntegrationDefinition.objects.filter(organization=actor.organization).order_by('code'),integration=selected,integration_protocols=service.PROTOCOLS.items(),integration_auth=service.AUTH.items(),integration_credentials=IntegrationCredential.objects.filter(organization=actor.organization),integration_executors=people_with(actor.organization,'integration.invoke'),integration_network=IntegrationNetworkPolicy.objects.filter(organization=actor.organization).first(),integration_versions=selected.versions.order_by('-version') if selected else [],integration_jobs=IntegrationJob.objects.filter(organization=actor.organization,version__definition=selected).order_by('-created_at')[:50] if selected else [],integration_clients=IntegrationClient.objects.filter(organization=actor.organization,version__definition=selected) if selected else [])
        return render(request,'desk/integrations.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)

@endpoint(['POST'])
def command(request,action,id=None):
    if action not in ('network','credential','save','publish','invoke','client','client-stop','retry','remap'):s.fail('INVALID_OPERATION','지원하지 않는 작업입니다.')
    data=body(request);result,status=s.execute(request.actor,'int_'+action,data,request.headers.get('Idempotency-Key'),getattr(request,'request_id',''),id)
    # Secrets are issued after idempotency persistence, never stored in replay responses.
    if action=='client':result={**result,'secret':service.issue_secret(request.actor,result['id'])}
    return JsonResponse(result,status=status)

@endpoint(['POST'])
def import_spec(request):
    require(request.actor,'integration.manage');data=body(request)
    return {'operations':specs.operations(data.get('document'))} if not data.get('method') else {'settings':specs.draft(data['document'],data['method'],data['path'])}

@endpoint(['GET'])
def job(request,id):
    require(request.actor,'integration.manage');value=IntegrationJob.objects.filter(organization=request.actor.organization,id=id).first()
    if not value:s.fail('NOT_FOUND','실행 이력을 찾을 수 없습니다.',404)
    # Result data can contain business information: require recent authentication.
    from .security_policy import require_recent
    require_recent(request.actor)
    return {'id':str(value.id),'status':value.status,'http_status':value.http_status,'error_code':value.error_code,'attempts':value.attempts,'mapped':unseal(value.mapped_cipher) if value.mapped_cipher else None,'events':[{'action':e.action,'at':e.created_at.isoformat(),'details':e.details} for e in value.integrationevent_set.order_by('created_at')]}

# Machine endpoint: exclusively client-key/HMAC authentication, never cookie auth.
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare
import hashlib,hmac,time,re

@csrf_exempt
def receive(request,client_id,job_id=None):
    try:
        if request.method!=('GET' if job_id else 'POST'):s.fail('METHOD_NOT_ALLOWED','허용되지 않은 메서드입니다.',405)
        client=IntegrationClient.objects.select_related('version__definition__run_as','organization').filter(id=client_id,active=True,issued=True).first()
        if not client or not client.organization.active:s.fail('CLIENT_AUTH_FAILED','호출 인증에 실패했습니다.',401)
        key=request.headers.get('Idempotency-Key','')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',key):s.fail('IDEMPOTENCY_REQUIRED','1~80자 호출 키가 필요합니다.')
        if client.auth_mode=='API_KEY':
            value=request.headers.get('Authorization','');token=value[7:] if value.startswith('Bearer ') else ''
            valid=bool(token) and constant_time_compare(hashlib.sha256(token.encode()).hexdigest(),client.token_hash)
        else:
            timestamp=request.headers.get('X-Integration-Timestamp','')
            try:recent=abs(time.time()-int(timestamp))<=300
            except ValueError:recent=False
            message='\n'.join([request.method,request.path,timestamp,key]).encode()+b'\n'+request.body
            signature=hmac.new(unseal(client.secret_cipher)['secret'].encode(),message,hashlib.sha256).hexdigest()
            valid=recent and constant_time_compare(signature,request.headers.get('X-Integration-Signature',''))
        if not valid:s.fail('CLIENT_AUTH_FAILED','호출 인증에 실패했습니다.',401)
        with transaction.atomic():
            from .models import Organization
            Organization.objects.select_for_update().get(pk=client.organization_id)
            client=IntegrationClient.objects.select_for_update().get(pk=client.id)
            if not client.active:s.fail('CLIENT_AUTH_FAILED','호출 인증에 실패했습니다.',401)
            now=timezone.now()
            if (now-client.window_started).total_seconds()>=60:client.calls=0;client.window_started=now
            if client.calls>=client.rate_limit:s.fail('RATE_LIMITED','분당 호출 한도를 초과했습니다.',429)
            client.calls+=1;client.save(update_fields=['calls','window_started'])
            external_key=str(client.id)+':'+key;actor=client.version.definition.run_as
            from .permissions import allowed
            if not actor.active or not actor.user.is_active or not allowed(actor,'integration.invoke') or not client.version.definition.active:s.fail('CLIENT_AUTH_FAILED','호출 계정이 중지되었습니다.',401)
            if job_id:
                value=IntegrationJob.objects.filter(id=job_id,organization=client.organization,version=client.version,initiated_by=actor,external_key=external_key).first()
                if not value:s.fail('NOT_FOUND','호출 결과를 찾을 수 없습니다.',404)
                result={'id':str(value.id),'status':value.status,'error_code':value.error_code,'result':unseal(value.mapped_cipher) if value.status=='SUCCESS' else None};status=200
            else:
                data=body(request);value=service.enqueue(actor,client.version,data,external_key);result={'id':str(value.id),'status':value.status};status=202
        return JsonResponse(result,status=status)
    except s.BusinessError as exc:return error(request,exc.code,exc.message,exc.status)
    except (ValueError,TypeError,KeyError):return error(request,'INVALID_PAYLOAD','인증·JSON 입력을 확인하십시오.',400)
