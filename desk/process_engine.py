"""Version-pinned graph execution. No eval, executable uploads or external side effects."""
import hashlib,json,re,uuid
from datetime import timedelta
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from . import services as s
from .models import (Person,Department,Group,ProcessDefinition,ProcessVersion,ProcessReview,ProcessRetirement,ProcessRun,ProcessTask,ProcessVote,ProcessEvent,ProcessArrival,ProcessBinding,ProcessAssignment)
from .permissions import require,allowed,BUILTIN
from .security_policy import require_recent
from .access_graph import role_rows,effective_groups,chain

KINDS={'START','TASK','APPROVAL','CONDITION','PARALLEL','JOIN','WAIT','SUBPROCESS','ACTION','END','TRANSFER','API'}
OPS={'eq','ne','gt','gte','lt','lte','in','empty'}


def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def definition(actor,id):
    value=ProcessDefinition.objects.filter(organization=actor.organization,id=s.identifier(id)).first()
    if not value:s.fail('NOT_FOUND','정의를 찾을 수 없습니다.',404)
    return value

def version(actor,id,kind=None,starting=False):
    value=ProcessVersion.objects.filter(organization=actor.organization,id=s.identifier(id)).select_related('definition').first()
    if not value or (kind and value.definition.kind!=kind):s.fail('NOT_FOUND','게시 버전을 찾을 수 없습니다.',404)
    if starting and (not value.definition.active or ProcessRetirement.objects.filter(version=value).exists()):s.fail('VERSION_RETIRED','신규 실행이 중지된 버전입니다.',409)
    return value


def run_for(actor,id):
    run=ProcessRun.objects.filter(organization=actor.organization,id=s.identifier(id)).select_related('version__definition','started_by').first()
    if not run:s.fail('NOT_FOUND','실행 건을 찾을 수 없습니다.',404)
    if run.started_by_id!=actor.id and not allowed(actor,'workflow.manage') and not any(str(actor.id) in task.person_ids for task in run.tasks.all()):s.fail('NOT_FOUND','실행 건을 찾을 수 없습니다.',404)
    from .data_access import restrict
    if not restrict(actor,'workflow-inbox',ProcessRun.objects.filter(pk=run.id),'started_by','tasks__assignments__person_id').exists():s.fail('NOT_FOUND','데이터 조회 범위에 포함되지 않습니다.',404)
    return run


def selector(actor,value):
    if not isinstance(value,dict):s.fail('INVALID_SELECTOR','할당 대상을 선택하십시오.')
    s.check_fields(value,['kind','ids','include_children'],['kind','ids'])
    kind=value['kind'];ids=value['ids']
    if kind=='STARTER':
        if not isinstance(ids,list) or ids:s.fail('INVALID_SELECTOR','신청자 자동 할당은 고정 대상을 지정하지 않습니다.')
        return dict(kind=kind,ids=[])
    if kind=='FIELD_USER':
        if not isinstance(ids,list) or len(ids)!=1 or not isinstance(ids[0],str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',ids[0]):s.fail('INVALID_SELECTOR','담당자 필드 하나를 선택하십시오.')
        return dict(kind=kind,ids=ids)
    if kind not in ('USER','ROLE','GROUP','DEPARTMENT') or not isinstance(ids,list) or not 1<=len(ids)<=200 or any(not isinstance(v,str) for v in ids) or len(set(ids))!=len(ids):s.fail('INVALID_SELECTOR','할당 유형과 대상 목록을 확인하십시오.')
    if type(value.get('include_children',False)) is not bool:s.fail('INVALID_SELECTOR','하위 부서 포함 여부를 확인하십시오.')
    if kind=='ROLE':
        from .organization_management import role_object
        for key in ids:role_object(actor,key)
    else:
        model={'USER':Person,'GROUP':Group,'DEPARTMENT':Department}[kind]
        if model.objects.filter(organization=actor.organization,active=True,id__in=[s.identifier(v) for v in ids]).count()!=len(ids):s.fail('INVALID_SELECTOR','현재 조직의 활성 대상만 선택하십시오.')
    return dict(kind=kind,ids=ids,include_children=value.get('include_children',False))


def recipients(actor,spec,run=None):
    people=Person.objects.filter(organization=actor.organization,active=True,user__is_active=True)
    values=set(spec['ids']);kind=spec['kind']
    if kind=='STARTER':return list(people.filter(id=run.started_by_id).values_list('id',flat=True)) if run else []
    if kind=='FIELD_USER':
        if not run:return []
        key=spec['ids'][0];value=run.data.get(key);field=next((f for f in run.graph.get('fields',[]) if f['key']==key and f['type']=='person'),None)
        if not value or not field:return []
        try:person=people.filter(id=uuid.UUID(value)).first()
        except (ValueError,TypeError,AttributeError):return []
        return [person.id] if person and (not field.get('group_id') or field['group_id'] in effective_groups(person)) else []
    if kind=='USER':return list(people.filter(id__in=values).values_list('id',flat=True))
    result=[]
    for person in people:
        if kind=='ROLE':hit=bool(values&{row['key'] for row in role_rows(person)})
        elif kind=='GROUP':hit=bool(values&set(effective_groups(person)))
        else:
            departments=chain(person)
            hit=any(str(department.id) in values for department in (departments if spec.get('include_children') else departments[:1]))
        if hit:result.append(person.id)
    return result


def fields_validate(fields,actor=None):
    if not isinstance(fields,list) or len(fields)>30:s.fail('INVALID_FIELDS','입력 항목은 최대 30개입니다.')
    result=[];keys=set()
    for field in fields:
        if not isinstance(field,dict):s.fail('INVALID_FIELDS','입력 항목을 확인하십시오.')
        s.check_fields(field,['key','label','type','required','group_id'],['key','label','type','required'])
        key=s.text(field,'key',40)
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',key) or key in keys or field['type'] not in ('text','number','boolean','person') or type(field['required']) is not bool:s.fail('INVALID_FIELDS','항목 식별자·종류·필수 여부를 확인하십시오.')
        item=dict(key=key,label=s.text(field,'label',100),type=field['type'],required=field['required'])
        if field.get('group_id'):
            if field['type']!='person' or not actor or not Group.objects.filter(organization=actor.organization,id=s.identifier(field['group_id']),active=True).exists():s.fail('INVALID_PERSON_GROUP','담당자 선택 범위는 현재 조직의 활성 그룹이어야 합니다.')
            item['group_id']=str(field['group_id'])
        keys.add(key);result.append(item)
    return result


def values_validate(fields,values,required=True,actor=None):
    if not isinstance(values,dict) or set(values)-{f['key'] for f in fields}:s.fail('INVALID_VALUES','허용된 입력 항목만 전달하십시오.')
    result={}
    for field in fields:
        key=field['key']
        if key not in values:
            if required and field['required']:s.fail('REQUIRED_FIELD',field['label']+' 항목을 입력하십시오.')
            continue
        value=values[key]
        if field['type']=='person':
            try:person=Person.objects.filter(organization=actor.organization,id=uuid.UUID(value),active=True,user__is_active=True).first() if actor else None
            except (ValueError,TypeError,AttributeError):person=None
            if not person or field.get('group_id') and field['group_id'] not in effective_groups(person):s.fail('INVALID_ASSIGNEE','선택 범위의 활성 담당자를 지정하십시오.')
            result[key]=str(person.id);continue
        valid=(isinstance(value,str) and len(value)<=2000) if field['type']=='text' else (type(value) in (int,float) and abs(value)<=10**15) if field['type']=='number' else type(value) is bool
        if not valid or (required and field['required'] and isinstance(value,str) and not value.strip()):s.fail('INVALID_VALUES',field['label']+' 값을 확인하십시오.')
        result[key]=value
    return result


def validate(actor,kind,raw):
    if not isinstance(raw,dict):s.fail('INVALID_GRAPH','설정 객체가 필요합니다.')
    if kind=='SCREEN':
        s.check_fields(raw,['fields','read_only','columns'],['fields','read_only','columns'])
        fields=fields_validate(raw['fields'],actor);read_only=raw['read_only']
        if not isinstance(read_only,list) or any(not isinstance(k,str) for k in read_only) or not set(read_only)<={f['key'] for f in fields} or type(raw['columns']) is not int or raw['columns'] not in (1,2,3):s.fail('INVALID_SCREEN','읽기 전용 항목과 화면 열 수를 확인하십시오.')
        return dict(fields=fields,read_only=read_only,columns=raw['columns'])
    if kind=='APPROVAL':
        s.check_fields(raw,['stages'],['stages'])
        stages=raw['stages']
        if not isinstance(stages,list) or not 1<=len(stages)<=20:s.fail('INVALID_GRAPH','결재 단계는 1~20개입니다.')
        result=[]
        for stage in stages:
            if not isinstance(stage,dict):s.fail('INVALID_GRAPH','결재 단계를 확인하십시오.')
            s.check_fields(stage,['key','label','selector','mode'],['key','label','selector','mode'])
            key=s.text(stage,'key',40)
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}',key) or key in {x['key'] for x in result} or stage['mode'] not in ('ALL','ANY'):s.fail('INVALID_GRAPH','결재 단계 식별자와 합의 방식을 확인하십시오.')
            result.append(dict(key=key,label=s.text(stage,'label',150),selector=selector(actor,stage['selector']),mode=stage['mode']))
        return {'stages':result}
    s.check_fields(raw,['nodes','start','fields','positions','screen_version_id','screen','close_on_complete','ticket_assignee_field','catalog_only'],['nodes','start'])
    common_screen=version(actor,raw['screen_version_id'],'SCREEN',True) if raw.get('screen_version_id') else None
    fields=fields_validate(raw.get('fields',common_screen.graph['fields'] if common_screen else []),actor);nodes=raw['nodes'];start=raw['start']
    if common_screen:
        for field in common_screen.graph['fields']:
            if not any(f['key']==field['key'] and f['type']==field['type'] for f in fields):s.fail('SCREEN_FIELD_MISMATCH','공통 화면의 항목을 프로세스 데이터에 선언하십시오.')
    if not isinstance(nodes,list) or not 2<=len(nodes)<=100 or not isinstance(start,str):s.fail('INVALID_GRAPH','워크플로우는 2~100개 노드와 시작 노드가 필요합니다.')
    result={}
    for value in nodes:
        if not isinstance(value,dict):s.fail('INVALID_NODE','노드 설정을 확인하십시오.')
        s.check_fields(value,['key','label','type','next','reject','true','false','branches','join','selector','mode','condition','wait_seconds','version_id','action','field','value','field_keys','approval_version_id','approval_timing','screen_version_id','screen','field_modes','field_roles','required_fields','count','count_field','input_mapping','output_mapping','api_version_id'],['key','label','type'])
        key=s.text(value,'key',40);type_=value['type']
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}',key) or '__' in key or key in result or type_ not in KINDS:s.fail('INVALID_NODE','노드 식별자와 종류를 확인하십시오.')
        node=dict(key=key,label=s.text(value,'label',150),type=type_)
        edge_names=['true','false'] if type_=='CONDITION' else ['next'] if type_ not in ('END','PARALLEL','TRANSFER') else []
        for edge in edge_names:node[edge]=s.text(value,edge,40)
        if value.get('reject'):
            if type_ not in ('APPROVAL','TASK'):s.fail('INVALID_NODE','결재 노드만 반려 경로를 지정할 수 있습니다.')
            node['reject']=s.text(value,'reject',40)
        if type_=='PARALLEL':
            branches=value.get('branches')
            if not isinstance(branches,list) or not 2<=len(branches)<=10 or any(not isinstance(b,str) for b in branches) or len(set(branches))!=len(branches):s.fail('INVALID_FORK','병렬 분기는 중복 없이 2~10개입니다.')
            node.update(branches=branches,join=s.text(value,'join',40))
        if type_=='API':
            from .integrations.service import version as api_version
            api=api_version(actor,value.get('api_version_id'))
            node['api_version_id']=str(api.id)
            for mapping_key in ('input_mapping','output_mapping'):
                mapping=value.get(mapping_key,{})
                if not isinstance(mapping,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in mapping.items()):s.fail('INVALID_MAPPING','API 항목 매핑을 확인하십시오.')
                declared={f['key'] for f in fields}
                if mapping_key=='input_mapping' and (set(mapping.values())-declared or set(mapping)-{f['key'] for f in api.settings['input_fields']}):s.fail('INVALID_MAPPING','API 입력 항목과 프로세스 항목을 확인하십시오.')
                if mapping_key=='output_mapping' and (set(mapping)-declared or set(mapping.values())-set(api.settings['response_mapping'])):s.fail('INVALID_MAPPING','API 결과 항목과 프로세스 항목을 확인하십시오.')
                node[mapping_key]=mapping
        if type_=='TASK':
            node['selector']=selector(actor,value.get('selector'))
            if node['selector']['kind']=='FIELD_USER' and not any(f['key']==node['selector']['ids'][0] and f['type']=='person' for f in fields):s.fail('INVALID_SELECTOR','선언된 담당자 유형 필드를 연결하십시오.')
            node['mode']=value.get('mode','ANY')
            if node['mode'] not in ('ALL','ANY'):s.fail('INVALID_NODE','처리 방식을 확인하십시오.')
            keys=value.get('field_keys',[])
            if not isinstance(keys,list) or any(not isinstance(k,str) for k in keys) or not set(keys)<={f['key'] for f in fields}:s.fail('INVALID_FIELDS','선언된 입력 항목만 업무에 연결하십시오.')
            node['field_keys']=keys
            if value.get('screen_version_id'):
                screen=version(actor,value['screen_version_id'],'SCREEN',True)
                for field in screen.graph['fields']:
                    if not any(f['key']==field['key'] and f['type']==field['type'] for f in fields):s.fail('SCREEN_FIELD_MISMATCH','화면 항목을 워크플로우 데이터에 같은 유형으로 선언하십시오.')
                node['screen_version_id']=str(screen.id);node['screen']=screen.graph;node['field_keys']=[f['key'] for f in screen.graph['fields'] if f['key'] not in screen.graph['read_only']]
            if value.get('approval_version_id'):
                approval=version(actor,value['approval_version_id'],'APPROVAL',True)
                if value.get('approval_timing','AFTER') not in ('BEFORE','AFTER'):s.fail('INVALID_APPROVAL_TIMING','결재 시점을 확인하십시오.')
                node.update(approval_version_id=str(approval.id),approval_timing=value.get('approval_timing','AFTER'))
            elif value.get('reject'):s.fail('INVALID_APPROVAL','반려 경로에는 결재선 설정이 필요합니다.')
        if type_ in ('TASK','APPROVAL','WAIT','SUBPROCESS','TRANSFER'):
            screen=node.get('screen') or (common_screen.graph if common_screen else None)
            if screen:node['screen']=screen
            available={f['key'] for f in (screen['fields'] if screen else fields)}
            modes=value.get('field_modes',{})
            if not isinstance(modes,dict) or set(modes)-available or any(mode not in ('HIDDEN','READ','EDIT') for mode in modes.values()):s.fail('INVALID_FIELD_ACCESS','필드 표시·입력 권한을 확인하십시오.')
            if screen:
                for field in screen['fields']:modes.setdefault(field['key'],'READ' if field['key'] in screen['read_only'] or type_=='APPROVAL' else 'EDIT')
            roles=value.get('field_roles',{})
            if not isinstance(roles,dict) or set(roles)-available:s.fail('INVALID_FIELD_ACCESS','필드별 역할을 확인하십시오.')
            from .organization_management import role_object
            for rule in roles.values():
                if not isinstance(rule,dict) or set(rule)-{'read','write'}:s.fail('INVALID_FIELD_ACCESS','조회·입력 역할 목록을 확인하십시오.')
                for selected in rule.values():
                    if not isinstance(selected,list) or len(selected)>50 or any(not isinstance(key,str) for key in selected):s.fail('INVALID_FIELD_ACCESS','역할 목록을 확인하십시오.')
                    for role_key in selected:role_object(actor,role_key)
            required=value.get('required_fields',[])
            if not isinstance(required,list) or any(not isinstance(k,str) for k in required) or not set(required)<=available:s.fail('INVALID_FIELD_ACCESS','필수 항목을 확인하십시오.')
            if any(modes.get(k)=='HIDDEN' for k in required):s.fail('INVALID_FIELD_ACCESS','숨김 항목은 이 태스크의 필수 입력으로 지정할 수 없습니다.')
            node.update(field_modes=modes,field_roles=roles,required_fields=required)
            if type_=='TASK' and screen:node['field_keys']=[k for k,mode in modes.items() if mode=='EDIT']
        if type_ in ('APPROVAL','SUBPROCESS','TRANSFER'):
            ref=version(actor,value.get('version_id'),'APPROVAL' if type_=='APPROVAL' else 'WORKFLOW',True);node['version_id']=str(ref.id)
            if type_ in ('SUBPROCESS','TRANSFER'):
                count=value.get('count',1)
                if type(count) is not int or not 1<=count<=20:s.fail('INVALID_CHILD_COUNT','하위 실행 수는 1~20개입니다.')
                count_field=value.get('count_field','')
                if count_field and not any(f['key']==count_field and f['type']=='number' for f in fields):s.fail('INVALID_CHILD_COUNT','선언된 숫자 항목으로 실행 수를 지정하십시오.')
                if type_=='TRANSFER' and (count!=1 or count_field):s.fail('INVALID_TRANSFER','이관 대상은 한 건입니다.')
                node.update(count=count,count_field=count_field)
                for mapping_key in ('input_mapping','output_mapping'):
                    mapping=value.get(mapping_key,{})
                    if not isinstance(mapping,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in mapping.items()):s.fail('INVALID_MAPPING','상하위 항목 매핑을 확인하십시오.')
                    parent_keys={f['key'] for f in fields};child_keys={f['key'] for f in ref.graph.get('fields',[])}
                    if mapping_key=='input_mapping' and (not set(mapping)<=child_keys or not set(mapping.values())<=parent_keys):s.fail('INVALID_MAPPING','입력 매핑의 항목이 없습니다.')
                    if mapping_key=='output_mapping' and (not set(mapping)<=parent_keys or not set(mapping.values())<=child_keys or (type_=='TRANSFER' and mapping)):s.fail('INVALID_MAPPING','출력 매핑을 확인하십시오.')
                    node[mapping_key]=mapping
        if type_=='WAIT':
            seconds=value.get('wait_seconds')
            if type(seconds) is not int or not 1<=seconds<=604800:s.fail('INVALID_WAIT','대기 시간은 1초~7일입니다.')
            node['wait_seconds']=seconds
        if type_=='CONDITION':
            condition=value.get('condition')
            if not isinstance(condition,dict) or set(condition)-{'field','op','value'} or condition.get('field') not in {f['key'] for f in fields} or condition.get('op') not in OPS:s.fail('INVALID_CONDITION','선언된 항목과 허용 연산자로 조건을 구성하십시오.')
            if condition['op']!='empty':
                if condition['op']=='in':
                    values=condition.get('value')
                    if not isinstance(values,list) or len(values)>100:s.fail('INVALID_CONDITION','목록 조건을 확인하십시오.')
                    for candidate in values:values_validate([f for f in fields if f['key']==condition['field']],{condition['field']:candidate},actor=actor)
                else:values_validate([f for f in fields if f['key']==condition['field']],{condition['field']:condition.get('value')},actor=actor)
            node['condition']=condition
        if type_=='ACTION':
            if value.get('action') not in ('NOOP','SET_FIELD'):s.fail('INVALID_ACTION','등록된 안전한 동작만 선택하십시오.')
            node['action']=value['action']
            if value['action']=='SET_FIELD':
                field=value.get('field');values_validate(fields,{field:value.get('value')},False,actor=actor);node.update(field=field,value=value.get('value'))
        result[key]=node
    if start not in result or result[start]['type']!='START' or sum(n['type']=='START' for n in result.values())!=1 or not any(n['type'] in ('END','TRANSFER') for n in result.values()):s.fail('INVALID_GRAPH','시작 노드 하나와 종료 노드가 필요합니다.')
    def edges(node):return [node[e] for e in ('next','true','false','reject') if e in node]+node.get('branches',[])
    for node in result.values():
        if any(target not in result or result[target]['type']=='START' for target in edges(node)):s.fail('INVALID_EDGE','연결 대상이 없거나 시작 노드로 돌아갈 수 없습니다.')
        if node['type']=='PARALLEL' and (node['join'] not in result or result[node['join']]['type']!='JOIN'):s.fail('INVALID_JOIN','병렬 분기에 합류 노드를 지정하십시오.')
    reachable=set();pending=[start]
    while pending:
        current=pending.pop()
        if current in reachable:continue
        reachable.add(current);pending+=edges(result[current])
    if reachable!=set(result):s.fail('UNREACHABLE_NODE','도달할 수 없는 노드가 있습니다.')
    ending={key for key,node in result.items() if node['type'] in ('END','TRANSFER')}
    while True:
        extra={key for key,node in result.items() if any(edge in ending for edge in edges(node))}
        if extra<=ending:break
        ending|=extra
    if ending!=set(result):s.fail('NO_END_PATH','종료 경로가 없는 노드가 있습니다.')
    # Human and wait nodes break automatic cycles; static automatic loops never run.
    colors={}
    def automatic(key):
        node=result[key]
        if node['type'] in ('TASK','APPROVAL','WAIT','END','SUBPROCESS','TRANSFER','API'):return
        if colors.get(key)==1:s.fail('AUTOMATIC_CYCLE','자동 노드만 반복되는 순환은 허용되지 않습니다.')
        if colors.get(key)==2:return
        colors[key]=1
        for target in edges(node):automatic(target)
        colors[key]=2
    for key in result:automatic(key)
    claimed=set()
    for key,node in result.items():
        if node['type']!='PARALLEL':continue
        if node['join'] in claimed:s.fail('SHARED_JOIN','병렬 분기별로 별도 합류 노드를 사용하십시오.')
        claimed.add(node['join'])
        for branch in node['branches']:
            seen=set();pending=[branch];joined=False
            while pending:
                current=pending.pop()
                if current==node['join']:joined=True;continue
                if current in seen:continue
                seen.add(current)
                if result[current]['type'] in ('END','TRANSFER'):s.fail('JOIN_BYPASS','병렬 경로는 합류 전에 종료·이관할 수 없습니다.')
                pending+=edges(result[current])
            if not joined:s.fail('JOIN_BYPASS','합류에 도달할 수 없는 병렬 경로입니다.')
    if any(n['type']=='JOIN' and key not in claimed for key,n in result.items()):s.fail('ORPHAN_JOIN','연결된 병렬 분기가 없는 합류 노드입니다.')
    positions=raw.get('positions',{})
    if not isinstance(positions,dict) or set(positions)-set(result):s.fail('INVALID_POSITION','캔버스 위치를 확인하십시오.')
    for point in positions.values():
        if not isinstance(point,dict) or set(point)!= {'x','y'} or any(type(v) is not int or not 0<=v<=4000 for v in point.values()):s.fail('INVALID_POSITION','캔버스 좌표를 확인하십시오.')
    close=raw.get('close_on_complete',False);assignment=raw.get('ticket_assignee_field','');catalog_only=raw.get('catalog_only',False)
    if type(catalog_only) is not bool or type(close) is not bool or assignment and not any(f['key']==assignment and f['type']=='person' for f in fields):s.fail('INVALID_TICKET_BINDING','종료 정책과 담당자 필드를 확인하십시오.')
    return dict(start=start,nodes=list(result.values()),fields=fields,positions=positions,catalog_only=catalog_only,close_on_complete=close,ticket_assignee_field=assignment,**({'screen_version_id':str(common_screen.id),'screen':common_screen.graph} if common_screen else {}))


def compile_graph(actor,version_,depth=0):
    if depth>5:s.fail('SUBPROCESS_DEPTH','하위 프로세스 깊이는 최대 5단계입니다.')
    graph=json.loads(json.dumps(version_.graph));output=[];total=0
    for node in graph['nodes']:
        type_=node['type']
        if type_=='TASK' and node.get('approval_version_id'):
            ref=version(actor,node['approval_version_id'],'APPROVAL',True);stages=ref.graph['stages'];prefix=node['key']+'__approval_';work={**node,'key':node['key']+'__work'}
            before=node['approval_timing']=='BEFORE'
            work['next']=node['next'] if before else prefix+stages[0]['key']
            output.extend([dict(key=node['key'],label=node['label'],type='ACTION',action='NOOP',next=prefix+stages[0]['key'] if before else work['key']),work])
            for index,stage in enumerate(stages):output.append(dict(key=prefix+stage['key'],label=node['label']+' / '+stage['label'],type='APPROVAL',selector=stage['selector'],mode=stage['mode'],**{k:node[k] for k in ('screen','field_modes','field_roles','required_fields') if k in node},next=prefix+stages[index+1]['key'] if index+1<len(stages) else work['key'] if before else node['next'],**({'reject':node['reject']} if node.get('reject') else {})))
        elif type_=='APPROVAL':
            ref=version(actor,node['version_id'],'APPROVAL',True);stages=ref.graph['stages'];prefix=node['key']+'__'
            output.append(dict(key=node['key'],label=node['label'],type='ACTION',action='NOOP',next=prefix+stages[0]['key']))
            for index,stage in enumerate(stages):
                output.append(dict(key=prefix+stage['key'],label=node['label']+' / '+stage['label'],type='APPROVAL',selector=stage['selector'],mode=stage['mode'],**{k:node[k] for k in ('screen','field_modes','field_roles','required_fields') if k in node},next=prefix+stages[index+1]['key'] if index+1<len(stages) else node['next'],**({'reject':node['reject']} if node.get('reject') else {})))
        else:
            if type_ in ('SUBPROCESS','TRANSFER'):
                ref=version(actor,node['version_id'],'WORKFLOW',True);node['child_graph']=compile_graph(actor,ref,depth+1);total+=len(node['child_graph']['nodes'])
            output.append(node)
    if len({n['key'] for n in output})!=len(output):s.fail('DUPLICATE_COMPILED_NODE','확장된 노드 식별자가 중복되었습니다.')
    if len(output)+total>300:s.fail('EXPANSION_LIMIT','확장된 프로세스 크기가 제한을 초과합니다.')
    return dict(start=graph['start'],nodes=output,fields=graph.get('fields',[]),catalog_only=graph.get('catalog_only',False),close_on_complete=graph.get('close_on_complete',False),ticket_assignee_field=graph.get('ticket_assignee_field',''),**({'screen':graph['screen'],'screen_version_id':graph['screen_version_id']} if graph.get('screen') else {}))


def event(actor,run,action,key='',details=None):ProcessEvent.objects.create(organization=actor.organization,run=run,actor=actor,action=action,node_key=key,details=details or {})

def condition_match(data,spec):
    value=data.get(spec['field']);target=spec.get('value');op=spec['op']
    if op=='empty':return value is None or value==''
    if op=='eq':return type(value) is type(target) and value==target
    if op=='ne':return type(value) is not type(target) or value!=target
    if op=='in':return value in target
    if type(value) not in (int,float) or type(target) not in (int,float):return False
    return {'gt':lambda:value>target,'gte':lambda:value>=target,'lt':lambda:value<target,'lte':lambda:value<=target}[op]()


def advance(actor,run,tokens,notify=True):
    nodes={n['key']:n for n in run.graph['nodes']};count=0
    while tokens:
        count+=1
        if count>600:s.fail('EXECUTION_LIMIT','자동 전이 제한을 초과했습니다.',409)
        key,frames=tokens.pop(0);node=nodes[key];kind=node['type'];event(actor,run,'NODE_ENTERED',key)
        if kind=='API':
            from .integrations.service import version as api_version,enqueue
            api=api_version(actor,node['api_version_id'])
            if str(run.version.definition_id) not in api.settings['allowed_workflows']:s.fail('WORKFLOW_CALL_DENIED','이 워크플로우는 해당 API의 호출 허용 대상이 아닙니다.',403)
            created=ProcessTask.objects.create(organization=actor.organization,run=run,node_key=key,kind='API',label=node['label'],frames=frames)
            enqueue(actor,api,{target:run.data[source] for target,source in node['input_mapping'].items() if source in run.data},str(created.id),created)
        elif kind in ('SUBPROCESS','TRANSFER'):

            if kind=='TRANSFER' and frames:s.fail('TRANSFER_IN_FORK','병렬 작업은 합류한 후 이관하십시오.')
            task=ProcessTask.objects.create(organization=actor.organization,run=run,node_key=key,kind=kind,label=node['label'],frames=frames,status='OPEN' if kind=='SUBPROCESS' else 'COMPLETED')
            spawn_children(actor,run,task,node)
            if kind=='TRANSFER':
                run.status='TRANSFERRED';run.save(update_fields=['status','data','row_version']);event(actor,run,'TRANSFERRED',key,{'child_run_ids':task.child_ids});sync_ticket(actor,run)
                if notify:settle_parent(actor,run)
                return
            if children_complete(actor,run,task,node):tokens.append((node['next'],frames))
        elif kind in ('TASK','APPROVAL','WAIT'):
            people=[] if kind=='WAIT' else [str(id) for id in recipients(actor,node['selector'],run) if kind!='APPROVAL' or id!=run.started_by_id]
            created=ProcessTask.objects.create(organization=actor.organization,run=run,node_key=key,kind=kind,label=node['label'],selector=node.get('selector',{}),person_ids=people,frames=frames,mode=node.get('mode','ALL'),due_at=timezone.now()+timedelta(seconds=node['wait_seconds']) if kind=='WAIT' else None)
            for person_id in people:ProcessAssignment.objects.create(organization=actor.organization,task=created,person_id=person_id)
        elif kind=='END':
            if frames:s.fail('OPEN_FORK','병렬 경로가 합류 전에 종료되었습니다.',409)
        elif kind=='CONDITION':tokens.append((node['true'] if condition_match(run.data,node['condition']) else node['false'],frames))
        elif kind=='PARALLEL':
            fork=str(uuid.uuid4())
            for index,target in enumerate(node['branches']):tokens.append((target,frames+[dict(id=fork,branch=index,count=len(node['branches']),join=node['join'])]))
        elif kind=='JOIN':
            if not frames or frames[-1]['join']!=key:s.fail('INVALID_JOIN_CONTEXT','합류 실행 문맥이 일치하지 않습니다.',409)
            frame=frames[-1];_,created=ProcessArrival.objects.get_or_create(organization=actor.organization,run=run,fork_id=frame['id'],branch=frame['branch'])
            if created and ProcessArrival.objects.filter(run=run,fork_id=frame['id']).count()==frame['count']:tokens.append((node['next'],frames[:-1]))
        else:
            if kind=='ACTION' and node['action']=='SET_FIELD':run.data[node['field']]=node['value'];event(actor,run,'FIELD_UPDATED',key,{'field':node['field']})
            tokens.append((node['next'],frames))
    tasks=run.tasks.filter(status='OPEN')
    run.status='COMPLETED' if not tasks.exists() else 'BLOCKED' if run.block_reason or any(task.kind in ('TASK','APPROVAL') and not task.person_ids or task.kind=='SUBPROCESS' and any(effective_child(c).status in ('BLOCKED','REJECTED','CANCELLED') for c in ProcessRun.objects.filter(id__in=task.child_ids)) for task in tasks) else 'ACTIVE'
    if run.status=='COMPLETED':event(actor,run,'COMPLETED')
    run.save(update_fields=['data','status','row_version'])
    sync_ticket(actor,run)
    if notify:settle_parent(actor,run)


def authorize(actor,operation,target):
    if operation not in {'flow_save','flow_review','flow_publish','flow_retire','flow_clone','flow_start','flow_act','flow_reassign','flow_tick','flow_cancel','flow_retry_children','flow_resolve_outputs','flow_bind'}:s.fail('INVALID_OPERATION','지원하지 않는 워크플로우 작업입니다.')
    if operation in ('flow_start','flow_act','flow_cancel'):
        require(actor,'workflow.use')
        if operation!='flow_start':run_for(actor,target)
    else:
        require(actor,'workflow.review' if operation=='flow_review' else 'workflow.manage');require_recent(actor)
        if operation in ('flow_tick','flow_reassign','flow_retry_children','flow_resolve_outputs'):run_for(actor,target)


def mutate(actor,operation,data,request_id,target):
    reason=s.text(data,'reason',2000,False)
    if operation=='flow_save':
        s.check_fields(data,['kind','code','name','graph','active','expected_version','reason'],['kind','code','name','graph','active','expected_version','reason'])
        if data['kind'] not in ('WORKFLOW','APPROVAL','SCREEN') or type(data['active']) is not bool:s.fail('INVALID_DEFINITION','정의 유형과 사용 여부를 확인하십시오.')
        value=definition(actor,target) if target else None
        from .identity_management import code
        key=code(data)
        if value:
            s.version(value,data)
            if value.kind!=data['kind'] or value.code!=key:s.fail('IMMUTABLE_CODE','정의 코드·유형은 변경할 수 없습니다.')
        else:
            if data['expected_version']!=0:s.fail('VERSION_CONFLICT','새 정의 버전은 0입니다.',409)
            value=ProcessDefinition(organization=actor.organization,kind=data['kind'],code=key,row_version=0,draft_author=actor)
        if not isinstance(data['graph'],dict):s.fail('INVALID_GRAPH','설정 객체가 필요합니다.')
        try:graph=validate(actor,value.kind,data['graph']);errors=[]
        except s.BusinessError as error:graph=data['graph'];errors=[error.message]
        value.validation_errors=errors
        value.name=s.text(data,'name',200);value.active=data['active'];value.draft=graph;value.draft_author=actor;value.row_version+=1;value.save()
        s.record(actor,value,'PROCESS_DRAFT_SAVED',request_id,after={'revision':value.row_version,'digest':digest(graph),'reason':reason})
        return {'id':str(value.id),'version':value.row_version,'validation_errors':value.validation_errors},200
    if operation in ('flow_review','flow_publish','flow_clone'):
        s.check_fields(data,['expected_version','reason','version_id'],['expected_version','reason'])
        value=definition(actor,target);s.version(value,data)
        if operation=='flow_clone':
            original=version(actor,data.get('version_id'))
            if original.definition_id!=value.id:s.fail('INVALID_VERSION','같은 정의의 버전만 복제하십시오.')
            value.draft=original.graph;value.draft_author=actor;value.row_version+=1;value.save()
            s.record(actor,value,'PROCESS_VERSION_CLONED',request_id,after={'from_version':str(original.id),'revision':value.row_version,'reason':reason})
        else:
            graph=validate(actor,value.kind,value.draft);hash_=digest(graph)
            if operation=='flow_review':
                if value.draft_author_id==actor.id:s.fail('INDEPENDENT_REVIEW','초안 작성자와 다른 검토자가 필요합니다.',409)
                ProcessReview.objects.create(organization=actor.organization,definition=value,revision=value.row_version,digest=hash_,reviewer=actor,reason=s.text(data,'reason',500))
                s.record(actor,value,'PROCESS_REVIEWED',request_id,after={'revision':value.row_version,'digest':hash_,'reason':reason})
            else:
                review=ProcessReview.objects.filter(definition=value,revision=value.row_version,digest=hash_).exclude(reviewer=value.draft_author).order_by('-created_at').first()
                if not review:s.fail('REVIEW_REQUIRED','현재 초안을 독립 검토한 후 게시하십시오.',409)
                if not allowed(review.reviewer,'workflow.review') or not review.reviewer.active or not review.reviewer.user.is_active:s.fail('REVIEW_PERMISSION_CHANGED','검토자의 권한·계정을 다시 확인하십시오.',409)
                number=(value.versions.aggregate(value=Max('version'))['value'] or 0)+1
                published=ProcessVersion.objects.create(organization=actor.organization,definition=value,version=number,graph=graph,digest=hash_,published_by=actor,reviewed_by=review.reviewer,reason=s.text(data,'reason',500))
                if value.kind=='WORKFLOW':compile_graph(actor,published)
                value.published=published;value.row_version+=1;value.save()
                s.record(actor,value,'PROCESS_PUBLISHED',request_id,after={'published_version':str(published.id),'version':number,'reason':reason})
        return {'id':str(value.id),'version':value.row_version},200
    if operation=='flow_retire':
        s.check_fields(data,['reason'],['reason']);value=version(actor,target)
        retirement,_=ProcessRetirement.objects.get_or_create(organization=actor.organization,version=value,defaults={'actor':actor,'reason':s.text(data,'reason',500)})
        s.record(actor,value,'PROCESS_RETIRED',request_id,after={'reason':reason})
        return {'id':str(value.definition_id),'version':value.version},200
    if operation=='flow_bind':
        s.check_fields(data,['version_id','expected_version','reason'],['version_id','expected_version','reason'])
        if target!='service-request':s.fail('ADAPTER_REQUIRED','현재 자동 업무 어댑터는 서비스요청입니다. 다른 프로세스는 공통 실행·이관 기능으로 연결하십시오.')
        value=version(actor,data['version_id'],'WORKFLOW',True)
        binding=ProcessBinding.objects.filter(organization=actor.organization,menu_key=target).first()
        if data['expected_version']!=(binding.row_version if binding else 0):s.fail('VERSION_CONFLICT','업무 연결 설정이 변경되었습니다.',409)
        if not binding:binding=ProcessBinding(organization=actor.organization,menu_key=target,row_version=0,updated_by=actor,version=value)
        binding.version=value;binding.updated_by=actor;binding.reason=s.text(data,'reason',500);binding.row_version+=1;binding.save();s.record(actor,binding,'PROCESS_BOUND',request_id,after={'menu_key':target,'version_id':str(value.id),'reason':reason})
        return {'id':str(value.definition_id),'version':binding.row_version},200
    if operation=='flow_start':
        s.check_fields(data,['version_id','title','values','reason'],['version_id','title','values'])
        value=version(actor,data['version_id'],'WORKFLOW',True)
        if value.definition.published_id!=value.id:s.fail('VERSION_CONFLICT','게시 버전이 변경되었습니다. 다시 확인하십시오.',409)
        run=start_run(actor,value,s.text(data,'title',300),data['values'])
        return {'id':str(run.id),'version':run.row_version},201
    run=run_for(actor,target);s.version(run,data)
    if run.status not in ('ACTIVE','BLOCKED'):s.fail('RUN_FINISHED','이미 종료된 실행 건입니다.',409)
    if operation=='flow_resolve_outputs':
        s.check_fields(data,['expected_version','reason','task_id','values'],['expected_version','reason','task_id','values'])
        task=run.tasks.filter(id=s.identifier(data['task_id']),kind='SUBPROCESS',status='OPEN').first()
        if not task:s.fail('INVALID_CHILD_TASK','하위 결과 대기 작업을 선택하십시오.')
        node=next(n for n in run.graph['nodes'] if n['key']==task.node_key)
        if not task.child_ids or any(effective_child(c).status!='COMPLETED' for c in ProcessRun.objects.filter(id__in=task.child_ids)):s.fail('CHILDREN_PENDING','모든 하위 작업이 완료되어야 결과를 확정할 수 있습니다.',409)
        if not isinstance(data['values'],dict) or set(data['values'])!=set(node.get('output_mapping',{})):s.fail('INVALID_VALUES','정의된 결과 매핑 항목을 모두 확정하십시오.')
        updates=values_validate(run.graph.get('fields',[]),data['values'],False,actor=actor);run.data.update(updates);run.block_reason='';task.status='COMPLETED';task.save(update_fields=['status']);run.row_version+=1;event(actor,run,'OUTPUTS_RECONCILED',task.node_key,{'fields':list(updates),'digest':digest(updates),'reason':s.text(data,'reason',2000)});advance(actor,run,[(node['next'],task.frames)]);return {'id':str(run.id),'version':run.row_version},200
    if operation=='flow_retry_children':
        s.check_fields(data,['expected_version','reason','task_id'],['expected_version','reason','task_id'])
        task=run.tasks.filter(id=s.identifier(data['task_id']),kind='SUBPROCESS',status='OPEN').first()
        if not task:s.fail('INVALID_CHILD_TASK','대기 중인 하위 프로세스 작업을 선택하십시오.')
        node=next(n for n in run.graph['nodes'] if n['key']==task.node_key);retry_children(actor,run,task,node,reason);run.row_version+=1;advance(actor,run,[]);return {'id':str(run.id),'version':run.row_version},200
    if operation=='flow_cancel':
        from .data_access import can_write
        if not can_write(actor,'workflow-inbox',run,'started_by','tasks__assignments__person_id'):s.fail('FORBIDDEN','이 실행 건의 변경 범위를 벗어났습니다.',403)
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        if run.started_by_id!=actor.id and not allowed(actor,'workflow.manage'):s.fail('FORBIDDEN','시작자 또는 관리자만 취소할 수 있습니다.',403)
        run.status='CANCELLED';run.row_version+=1;run.save();cancel_descendants(actor,run);run.tasks.filter(status='OPEN').update(status='CANCELLED');event(actor,run,'CANCELLED',details={'reason':s.text(data,'reason',2000)});sync_ticket(actor,run);settle_parent(actor,run);return {'id':str(run.id),'version':run.row_version},200
    if operation=='flow_tick':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason']);tokens=[]
        for task in run.tasks.filter(status='OPEN',kind='WAIT',due_at__lte=timezone.now()):
            task.status='COMPLETED';task.save(update_fields=['status']);node=next(n for n in run.graph['nodes'] if n['key']==task.node_key);tokens.append((node['next'],task.frames));event(actor,run,'WAIT_ELAPSED',task.node_key)
        if not tokens:s.fail('NO_DUE_WAIT','만료된 대기 노드가 없습니다.',409)
        run.row_version+=1;advance(actor,run,tokens);return {'id':str(run.id),'version':run.row_version},200
    s.check_fields(data,['expected_version','reason','task_id','decision','values','person_ids'],['expected_version','reason','task_id'])
    from .data_access import can_write
    if not can_write(actor,'workflow-inbox',run,'started_by','tasks__assignments__person_id'):s.fail('FORBIDDEN','이 실행 건의 입력 범위를 벗어났습니다.',403)
    task=run.tasks.filter(id=s.identifier(data['task_id']),status='OPEN').first()
    if not task:s.fail('TASK_CLOSED','현재 열린 업무를 선택하십시오.',409)
    if operation=='flow_reassign':
        ids=data.get('person_ids');spec=selector(actor,{'kind':'USER','ids':ids})
        if task.kind not in ('TASK','APPROVAL'):s.fail('INVALID_TASK','대기 노드는 재할당할 수 없습니다.')
        if task.kind=='APPROVAL' and str(run.started_by_id) in ids:s.fail('SELF_APPROVAL','시작자를 결재자로 지정할 수 없습니다.')
        if ProcessVote.objects.filter(task=task).exists():s.fail('VOTED_TASK','결정 이력이 있는 업무는 재할당할 수 없습니다.',409)
        previous=task.person_ids;task.selector=spec;task.person_ids=ids;task.row_version+=1;task.save();ProcessAssignment.objects.filter(task=task).exclude(person_id__in=ids).delete()
        for person_id in ids:ProcessAssignment.objects.get_or_create(organization=actor.organization,task=task,person_id=person_id)
        run.row_version+=1;run.status='ACTIVE' if not any(t.kind in ('TASK','APPROVAL') and not t.person_ids for t in run.tasks.filter(status='OPEN')) else 'BLOCKED';run.save();event(actor,run,'REASSIGNED',task.node_key,{'before':previous,'after':ids,'reason':s.text(data,'reason',2000)});settle_parent(actor,run)
    else:
        if task.kind not in ('TASK','APPROVAL') or str(actor.id) not in task.person_ids or actor.id not in recipients(actor,task.selector,run):s.fail('NOT_ASSIGNED','현재 유효한 담당자만 처리할 수 있습니다.',403)
        if task.kind=='APPROVAL' and actor.id==run.started_by_id:s.fail('SELF_APPROVAL','본인 결재는 허용되지 않습니다.',403)
        decision=data.get('decision')
        if decision not in (('APPROVE','REJECT') if task.kind=='APPROVAL' else ('COMPLETE',)):s.fail('INVALID_DECISION','허용된 처리 동작을 선택하십시오.')
        if ProcessVote.objects.filter(task=task,actor=actor).exists():s.fail('ALREADY_DECIDED','이미 결정했습니다.',409)
        if decision=='REJECT':reason=s.text(data,'reason',2000)
        ProcessVote.objects.create(organization=actor.organization,task=task,actor=actor,decision=decision,reason=reason)
        node=next(n for n in run.graph['nodes'] if n['key']==task.node_key)
        if task.kind=='TASK':
            fields=[{**field,'required':False} for field in task_fields(actor,run,node,task,True) if not field['read_only']];updates=values_validate(fields,data.get('values',{}),False,actor=actor);run.data.update(updates)
        elif data.get('values'):s.fail('READ_ONLY_TASK','결재 단계에서는 업무 데이터를 수정할 수 없습니다.')
        event(actor,run,decision,task.node_key,{'reason':reason,'task_id':str(task.id)})
        run.row_version+=1
        if decision=='REJECT':
            task.status='REJECTED';task.save(update_fields=['status'])
            if node.get('reject'):advance(actor,run,[(node['reject'],task.frames)])
            else:run.status='REJECTED';run.save();run.tasks.filter(status='OPEN').update(status='CANCELLED');event(actor,run,'REJECTED');cancel_descendants(actor,run);sync_ticket(actor,run);settle_parent(actor,run)
        elif task.mode=='ANY' or ProcessVote.objects.filter(task=task).count()==len(task.person_ids):
            if task.kind=='TASK':
                all_fields=node.get('screen',run.graph.get('screen',{})).get('fields',run.graph.get('fields',[]))
                required=set(node.get('required_fields',[]))|{f['key'] for f in all_fields if f['required'] and f['key'] in node.get('field_keys',[])}
                for field in all_fields:
                    if field['key'] in required:values_validate([{**field,'required':True}],{field['key']:run.data[field['key']]} if field['key'] in run.data else {},actor=actor)
            task.status='COMPLETED';task.save(update_fields=['status']);advance(actor,run,[(node['next'],task.frames)])
        else:run.save(update_fields=['data','row_version'])
    return {'id':str(run.id),'version':run.row_version},200


def sync_ticket(actor,run):
    if not run.ticket_id:return
    ticket=run.ticket;old=ticket.status;old_assignee=ticket.assignee_id
    mapping={'COMPLETED':'CLOSED' if run.graph.get('close_on_complete') else 'FULFILLED','REJECTED':'REJECTED','CANCELLED':'CANCELLED','TRANSFERRED':'TRANSFERRED'}
    ticket.status=mapping.get(run.status,'PENDING_APPROVAL' if run.tasks.filter(status='OPEN',kind='APPROVAL').exists() else 'IN_PROGRESS')
    field=run.graph.get('ticket_assignee_field')
    if field and run.data.get(field):ticket.assignee_id=uuid.UUID(run.data[field])
    if ticket.status!=old or ticket.assignee_id!=old_assignee:
        ticket.row_version+=1;ticket.save(update_fields=['status','assignee','row_version'])
        if ticket.status!=old:s.history(actor,ticket,old,'워크플로우 상태 반영')
        s.record(actor,ticket,'WORKFLOW_STATE_CHANGED',uuid.uuid4(),before={'status':old,'assignee_id':str(old_assignee) if old_assignee else None},after={'status':ticket.status,'assignee_id':str(ticket.assignee_id) if ticket.assignee_id else None,'run_id':str(run.id)})


def spawn_children(actor,run,task,node,count=None):
    count=count if count is not None else run.data.get(node.get('count_field')) if node.get('count_field') else node.get('count',1)
    if type(count) is not int or not 1<=count<=20:s.fail('INVALID_CHILD_COUNT','실행 시 하위 작업 수는 1~20의 정수여야 합니다.')
    root=run.root_run or run
    if ProcessRun.objects.filter(root_run=root).count()+count>200:s.fail('CHILD_RUN_LIMIT','한 실행의 하위 실행은 최대 200건입니다.')
    ref=version(actor,node['version_id'],'WORKFLOW')
    mapping=node.get('input_mapping',{});child_values={field['key']:run.data[mapping.get(field['key'],field['key'])] for field in node['child_graph'].get('fields',[]) if mapping.get(field['key'],field['key']) in run.data}
    values=values_validate(node['child_graph'].get('fields',[]),child_values,actor=actor)
    children=[ProcessRun.objects.create(organization=actor.organization,version=ref,started_by=run.started_by,title=(run.title+' / '+node['label']+' '+str(index+1))[:300],data=dict(values),graph=node['child_graph'],parent_task=task,root_run=root) for index in range(count)]
    task.child_ids=[str(child.id) for child in children];task.save(update_fields=['child_ids'])
    event(actor,run,'CHILDREN_STARTED',task.node_key,{'child_run_ids':task.child_ids,'version':str(ref.id)})
    for child in children:event(actor,child,'STARTED',details={'parent_run_id':str(run.id),'version':str(ref.id)});advance(actor,child,[(child.graph['start'],[])],notify=False)


def children_complete(actor,run,task,node):
    children=list(ProcessRun.objects.filter(organization=actor.organization,id__in=task.child_ids))
    if len(children)!=len(task.child_ids):s.fail('MISSING_CHILD','연결된 하위 실행을 확인하십시오.',409)
    if not children or any(effective_child(child).status!='COMPLETED' for child in children):return False
    # Parallel outputs must agree; conflicting results block rather than silently overwrite.
    updates={}
    for key,child_key in node.get('output_mapping',{}).items():
        values=[effective_child(child).data.get(child_key) for child in children]
        if any(value!=values[0] for value in values):
            run.block_reason='CHILD_OUTPUT_CONFLICT';run.status='BLOCKED';run.save(update_fields=['block_reason','status']);event(actor,run,'CHILD_OUTPUT_CONFLICT',task.node_key,{'field':key});return False
        updates[key]=values[0]
    run.data.update(values_validate(run.graph.get('fields',[]),updates,False,actor=actor));task.status='COMPLETED';task.save(update_fields=['status']);event(actor,run,'CHILDREN_COMPLETED',task.node_key,{'child_run_ids':task.child_ids});return True


def settle_parent(actor,child):
    if not child.parent_task_id:return
    task=ProcessTask.objects.select_related('run').get(pk=child.parent_task_id)
    if str(child.id) not in task.child_ids:return
    if task.kind=='TRANSFER':
        if task.run.ticket_id and effective_child(task.run).status=='COMPLETED':
            from .timeliness import handoff_complete
            handoff_complete(task.run.ticket)
        settle_parent(actor,task.run);return
    if task.status!='OPEN':return
    parent=task.run
    if parent.status not in ('ACTIVE','BLOCKED'):return
    node=next(n for n in parent.graph['nodes'] if n['key']==task.node_key)
    parent.row_version+=1
    if children_complete(actor,parent,task,node):advance(actor,parent,[(node['next'],task.frames)])
    else:
        state='BLOCKED' if parent.block_reason or any(effective_child(c).status in ('BLOCKED','REJECTED','CANCELLED','TRANSFERRED') for c in ProcessRun.objects.filter(id__in=task.child_ids)) else 'ACTIVE'
        parent.status=state;parent.save(update_fields=['status','row_version']);event(actor,parent,'CHILD_STATE_CHANGED',task.node_key,{'child_id':str(child.id),'status':child.status});sync_ticket(actor,parent);settle_parent(actor,parent)


def retry_children(actor,run,task,node,reason):
    reason=reason.strip()
    if not reason:s.fail('REASON_REQUIRED','재실행 사유를 입력하십시오.')
    children=list(ProcessRun.objects.filter(organization=actor.organization,id__in=task.child_ids));failed=[c for c in children if effective_child(c).status in ('REJECTED','CANCELLED')]
    if not failed:s.fail('NO_FAILED_CHILD','재실행할 반려·취소 건이 없습니다.',409)
    remaining=[str(c.id) for c in children if c not in failed];old_ids=list(task.child_ids)
    spawn_children(actor,run,task,node,len(failed));task.child_ids=remaining+task.child_ids;task.save(update_fields=['child_ids'])
    event(actor,run,'CHILDREN_RETRIED',task.node_key,{'before':old_ids,'after':task.child_ids,'reason':reason})
    if children_complete(actor,run,task,node):advance(actor,run,[(node['next'],task.frames)])


def cancel_descendants(actor,run):
    pending=[run.id];seen=set()
    while pending:
        ids=pending;pending=[]
        for child in ProcessRun.objects.filter(parent_task__run_id__in=ids,organization=actor.organization,status__in=['ACTIVE','BLOCKED']):
            if child.id in seen:continue
            seen.add(child.id);pending.append(child.id);child.status='CANCELLED';child.row_version+=1;child.save(update_fields=['status','row_version']);child.tasks.filter(status='OPEN').update(status='CANCELLED');event(actor,child,'PARENT_CANCELLED');sync_ticket(actor,child)


def effective_child(run,seen=None):
    seen=seen or set()
    if run.id in seen or run.status!='TRANSFERRED':return run
    seen.add(run.id)
    task=run.tasks.filter(kind='TRANSFER').order_by('-created_at').first()
    if not task or len(task.child_ids)!=1:return run
    child=ProcessRun.objects.filter(organization=run.organization,id=task.child_ids[0]).first()
    return effective_child(child,seen) if child else run


def start_run(actor,value,title,values,ticket=None):
    if value.graph.get('catalog_only') and not ticket:s.fail('CATALOG_REQUIRED','이 프로세스는 서비스 카탈로그에서 신청하십시오.')
    graph=compile_graph(actor,value)
    run=ProcessRun.objects.create(organization=actor.organization,version=value,started_by=actor,title=title,data=values_validate(graph.get('fields',[]),values,actor=actor),graph=graph,ticket=ticket)
    event(actor,run,'STARTED',details={'version':str(value.id),'digest':value.digest});advance(actor,run,[(graph['start'],[])])
    return run


def task_fields(actor,run,node,task,editing=False):
    screen=node.get('screen') or run.graph.get('screen')
    fields=screen['fields'] if screen else [f for f in run.graph.get('fields',[]) if f['key'] in node.get('field_keys',[])]
    roles={r['key'] for r in role_rows(actor)};result=[]
    for field in fields:
        key=field['key'];mode=node.get('field_modes',{}).get(key,'READ' if task.kind=='APPROVAL' else 'EDIT')
        rules=node.get('field_roles',{}).get(key,{})
        if mode=='HIDDEN' or (rules.get('read') and not roles&set(rules['read'])):continue
        readonly=mode!='EDIT' or task.kind!='TASK' or not editing or key in (screen or {}).get('read_only',[]) or bool(rules.get('write') and not roles&set(rules['write']))
        item={**field,'read_only':readonly,'required':key in node.get('required_fields',[]) or field['required'],'value':run.data.get(key,'')}
        if field['type']=='person':
            people=Person.objects.filter(organization=actor.organization,active=True,user__is_active=True).select_related('profile')
            item['options']=[dict(id=str(p.id),name=p.display_name+' · '+p.user.username) for p in people if not field.get('group_id') or field['group_id'] in effective_groups(p)]
            item['display_value']=next((p['name'] for p in item['options'] if p['id']==item['value']),'—')
        result.append(item)
    return result


def api_failed(actor,job,code):
    task=ProcessTask.objects.select_for_update().get(id=job.process_task_id)
    run=ProcessRun.objects.select_for_update().get(id=task.run_id)
    if task.status!='OPEN' or run.status in ('CANCELLED','COMPLETED','REJECTED'):return
    run.status='BLOCKED';run.block_reason='API:'+str(task.id);run.row_version+=1;run.save(update_fields=['status','block_reason','row_version']);event(actor,run,'API_FAILED',task.node_key,{'job_id':str(job.id),'code':code});sync_ticket(actor,run);settle_parent(actor,run)

def resume_api(actor,job,mapped):
    task=ProcessTask.objects.select_for_update().get(id=job.process_task_id)
    run=ProcessRun.objects.select_for_update().get(id=task.run_id)
    if task.status!='OPEN' or run.status in ('CANCELLED','COMPLETED','REJECTED','TRANSFERRED'):return
    node=next(n for n in run.graph['nodes'] if n['key']==task.node_key)
    updates={key:mapped[source] for key,source in node['output_mapping'].items() if source in mapped}
    if len(updates)!=len(node['output_mapping']):s.fail('MISSING_API_OUTPUT','프로세스에 필요한 API 결과가 없습니다.')
    run.data.update(values_validate(run.graph.get('fields',[]),updates,False,actor=actor))
    task.status='COMPLETED';task.save(update_fields=['status'])
    if run.block_reason=='API:'+str(task.id):run.block_reason='';run.save(update_fields=['block_reason'])
    run.row_version+=1;event(actor,run,'API_COMPLETED',task.node_key,{'job_id':str(job.id),'fields':list(updates)});advance(actor,run,[(node['next'],task.frames)])
