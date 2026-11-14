"""Catalog publication, request intake and single designated-approver workflow."""
import re
import uuid
from datetime import date
from django.db.models import Q, OuterRef, Subquery
from django.utils import timezone
from . import services as s
from .models import (CatalogItem, CatalogVersion, CatalogAudience, ServiceRequest, RequestApproval,
    ApprovalDecision, Ticket, Person, Group, Membership, RoleGrant, Notification, Comment)

WORK_STATES = ['APPROVED','IN_PROGRESS','FULFILLED','CLOSED']
FIELD_TYPES = ['text','textarea','integer','choice','date','boolean']

def require_manager(p):
    if not s.manager(p):
        s.fail('FORBIDDEN','서비스 관리자 권한이 필요합니다.',403)

def membership_ids(p):
    return Membership.objects.filter(organization=p.organization,person=p,group__active=True).values_list('group_id',flat=True)

def latest_versions(p,eligible=True):
    latest=CatalogVersion.objects.filter(item_id=OuterRef('item_id')).order_by('-version').values('id')[:1]
    qs=CatalogVersion.objects.filter(organization=p.organization,id=Subquery(latest)).select_related('item','approver','fulfillment_group')
    if eligible:
        qs=qs.filter(available=True).filter(Q(public_to_org=True)|Q(audiences__group_id__in=membership_ids(p))).distinct()
    return qs

def offering(p,item_id):
    version=latest_versions(p).filter(item_id=item_id).first()
    if not version:
        s.fail('NOT_FOUND','신청 가능한 서비스를 찾을 수 없습니다.',404)
    return version

def catalog_data(v,management=False):
    data={'id':str(v.item_id),'catalog_version_id':str(v.id),'code':v.item.code,'name':v.name,
          'workflow_version_id':str(v.workflow_version_id) if v.workflow_version_id else None,'workflow_name':v.workflow_version.definition.name if v.workflow_version_id else None,'workflow_version':v.workflow_version.version if v.workflow_version_id else None,'description':v.description,'version':v.version,'fields':v.fields,'approval_required':v.approval_required}
    if management:
        data.update(fulfillment_group_id=str(v.fulfillment_group_id),approver_id=str(v.approver_id) if v.approver_id else None,
            public_to_org=v.public_to_org,available=v.available,
            audience_group_ids=[str(x) for x in v.audiences.values_list('group_id',flat=True)])
    return data

def validate_fields(fields):
    if not isinstance(fields,list) or len(fields)>20:
        s.fail('INVALID_FORM','신청 항목은 최대 20개입니다.')
    seen=set()
    result=[]
    for field in fields:
        s.check_fields(field,['key','label','type','required','options'],['key','label','type','required'])
        key=field['key']
        if not isinstance(key,str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',key) or key in seen:
            s.fail('INVALID_FORM','항목 식별자는 중복 없는 영문 소문자·숫자·밑줄이어야 합니다.')
        if field['type'] not in FIELD_TYPES or type(field['required']) is not bool:
            s.fail('INVALID_FORM','항목 종류와 필수 여부를 확인하십시오.')
        clean={'key':key,'label':s.text(field,'label',100),'type':field['type'],'required':field['required']}
        if field['type']=='choice':
            options=field.get('options')
            if not isinstance(options,list) or not 1<=len(options)<=30 or any(not isinstance(x,str) or not x.strip() or len(x)>100 for x in options):
                s.fail('INVALID_FORM','선택지는 1~30개, 각 100자 이내여야 합니다.')
            options=[x.strip() for x in options]
            if len(set(options))!=len(options):
                s.fail('INVALID_FORM','선택지는 중복될 수 없습니다.')
            clean['options']=options
        elif field.get('options'):
            s.fail('INVALID_FORM','선택 항목에만 선택지를 지정하십시오.')
        seen.add(key)
        result.append(clean)
    return result

def validate_values(fields,values):
    if not isinstance(values,dict) or set(values)-{f['key'] for f in fields}:
        s.fail('INVALID_ANSWERS','허용된 신청 항목만 입력하십시오.')
    result={}
    for field in fields:
        key=field['key']
        if key not in values:
            if field['required']:
                s.fail('REQUIRED_ANSWER',field['label']+' 항목을 입력하십시오.')
            continue
        value=values[key]
        kind=field['type']
        valid=True
        if kind in ('text','textarea'):
            valid=isinstance(value,str) and len(value)<=(4000 if kind=='textarea' else 2000)
            if valid:
                value=value.strip()
                valid=bool(value) or not field['required']
        elif kind=='integer':
            valid=type(value) is int and -1_000_000_000<=value<=1_000_000_000
        elif kind=='boolean':
            valid=type(value) is bool
        elif kind=='choice':
            valid=isinstance(value,str) and value in field['options']
        elif kind=='date':
            try:
                valid=isinstance(value,str) and date.fromisoformat(value).isoformat()==value
            except ValueError:
                valid=False
        if not valid:
            s.fail('INVALID_ANSWER',field['label']+' 입력 형식을 확인하십시오.')
        result[key]=value
    return result

def publish(p,data,request_id):
    require_manager(p)
    names=['code','name','description','fulfillment_group_id','approval_required','approver_id',
           'public_to_org','audience_group_ids','available','fields','expected_version']
    s.check_fields(data,names+['workflow_version_id'],names)
    code=s.text(data,'code',40).upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9_-]{0,39}',code):
        s.fail('INVALID_CODE','서비스 코드는 영문자로 시작하는 영문·숫자·밑줄·하이픈이어야 합니다.')
    for key in ['approval_required','public_to_org','available']:
        if type(data[key]) is not bool:
            s.fail('INVALID_CATALOG','공개·승인·신청 허용 여부를 확인하십시오.')
    expected=data['expected_version']
    if type(expected) is not int or expected<0:
        s.fail('INVALID_VERSION','게시 기준 버전은 0 이상의 정수여야 합니다.')
    item=CatalogItem.objects.filter(organization=p.organization,code=code).first()
    latest=item.versions.order_by('-version').first() if item else None
    if expected!=(latest.version if latest else 0):
        s.fail('VERSION_CONFLICT','카탈로그가 변경되었습니다. 최신 버전을 다시 확인하십시오.',409)
    group=Group.objects.filter(id=s.identifier(data['fulfillment_group_id']),organization=p.organization,active=True).first()
    if not group:
        s.fail('INVALID_GROUP','활성 처리 그룹을 선택하십시오.')
    workflow=None
    from .models import ProcessBinding
    binding=ProcessBinding.objects.filter(organization=p.organization,menu_key='service-request').first()
    workflow_id=data.get('workflow_version_id') or (str(binding.version_id) if binding else None)
    if workflow_id:
        from .process_engine import version as process_version
        workflow=process_version(p,workflow_id,'WORKFLOW',True)
        data={**data,'approval_required':False,'approver_id':None}
    approver=None
    if data['approval_required']:
        approver=Person.objects.filter(id=s.identifier(data['approver_id']),organization=p.organization,active=True,user__is_active=True).first()
        if not approver:
            s.fail('INVALID_APPROVER','활성 승인자를 선택하십시오.')
    elif data['approver_id'] is not None:
        s.fail('INVALID_APPROVER','승인이 없으면 승인자는 비워야 합니다.')
    ids=data['audience_group_ids']
    if not isinstance(ids,list) or len(ids)>30:
        s.fail('INVALID_AUDIENCE','공개 그룹은 최대 30개입니다.')
    ids=[s.identifier(x) for x in ids]
    if len(set(ids))!=len(ids) or (data['public_to_org'] and ids) or (not data['public_to_org'] and not ids):
        s.fail('INVALID_AUDIENCE','조직 전체 또는 중복 없는 특정 그룹 공개를 선택하십시오.')
    groups=list(Group.objects.filter(id__in=ids,organization=p.organization,active=True))
    if len(groups)!=len(ids):
        s.fail('INVALID_AUDIENCE','같은 조직의 활성 그룹만 선택하십시오.')
    fields=validate_fields(data['fields'])
    if workflow:
        types={'text':'text','textarea':'text','choice':'text','date':'text','integer':'number','boolean':'boolean'}
        for field in workflow.graph.get('fields',[]):
            source=next((f for f in fields if f['key']==field['key']),None)
            if not source and not field['required']:continue
            if not source or types[source['type']]!=field['type'] or (field['required'] and not source['required']):s.fail('WORKFLOW_FORM_MISMATCH','워크플로우 입력 항목을 신청 양식에 같은 유형·필수 조건으로 구성하십시오.')
    if not item:
        item=CatalogItem.objects.create(organization=p.organization,code=code)
    version=CatalogVersion.objects.create(workflow_version=workflow,organization=p.organization,item=item,version=expected+1,
        name=s.text(data,'name',200),description=s.text(data,'description',10000),fulfillment_group=group,
        approver=approver,approval_required=data['approval_required'],public_to_org=data['public_to_org'],available=data['available'],fields=fields)
    for audience in groups:
        CatalogAudience.objects.create(organization=p.organization,catalog_version=version,group=audience)
    s.record(p,version,'CATALOG_PUBLISHED',request_id,after={'item_id':str(item.id),'code':code,'version':version.version,'available':version.available})
    return catalog_data(version,True),201

def request_staff(p,t):
    return s.manager(p) or (t.status in WORK_STATES and t.group_id in s.group_ids(p))

def request_query(p,scope='visible'):
    qs=Ticket.objects.filter(organization=p.organization,type='SERVICE_REQUEST').select_related('service_request','group','assignee','requested_by','request_approval')
    # System administrators audit all requests within their own organization.
    if 'ORG_ADMIN' in s.roles(p):
        return qs.filter(requested_by=p) if scope=='mine' else qs
    from .data_access import restrict
    qs=restrict(p,'requests',qs,'requested_by','assignee_id')
    if scope=='mine':
        return qs.filter(requested_by=p)
    if scope=='queue':
        return qs if s.manager(p) else qs.filter(group_id__in=s.group_ids(p),status__in=WORK_STATES)
    if s.manager(p):
        return qs
    return qs.filter(Q(requested_by=p)|Q(request_approval__approver=p)|Q(group_id__in=s.group_ids(p),status__in=WORK_STATES)|Q(process_run__tasks__assignments__person=p)|Q(process_run__descendant_runs__tasks__assignments__person=p)).distinct()

def get_request(p,ident,lock=False):
    # No nullable joins in SELECT FOR UPDATE; the organization is already locked for commands.
    qs=Ticket.objects.filter(organization=p.organization,type='SERVICE_REQUEST')
    if lock:
        qs=qs.select_for_update()
    t=qs.filter(id=ident).first()
    if not t or not request_query(p).filter(id=ident).exists():
        s.fail('NOT_FOUND','서비스 요청을 찾을 수 없습니다.',404)
    return t

def approval_for(t):
    try:
        return t.request_approval
    except RequestApproval.DoesNotExist:
        return None

def allowed_actions(p,t):
    if t.service_request.catalog_version.workflow_version_id:return []
    actions=[]
    owner=t.requested_by_id==p.id
    if owner and t.status in ('PENDING_APPROVAL','APPROVED'):
        actions.append('CANCEL')
    if t.status=='APPROVED' and t.assignee_id and request_staff(p,t) and (t.assignee_id==p.id or s.manager(p)):
        actions.append('START')
    if t.status=='IN_PROGRESS' and request_staff(p,t) and (t.assignee_id==p.id or s.manager(p)):
        actions.append('FULFILL')
    if t.status=='FULFILLED' and (owner or s.manager(p)):
        actions.append('CLOSE')
    return actions

def request_data(p,t,detail=True):
    sr=t.service_request
    approval=approval_for(t)
    result={'id':str(t.id),'number':t.number,'title':t.title,'status':t.status,'version':t.row_version,
        'created_at':t.created_at.isoformat(),'updated_at':t.updated_at.isoformat(),
        'catalog_name':sr.snapshot['name'],'catalog_version':sr.snapshot['version'],
        'group':{'id':str(t.group_id),'name':t.group.name},'assignee':s.person_data(t.assignee) if t.assignee else None}
    if not detail:
        return result
    decision=ApprovalDecision.objects.filter(approval=approval).first() if approval else None
    result.update(requested_by=s.person_data(t.requested_by),catalog_item_id=sr.snapshot['id'],
        fields=sr.snapshot['fields'],values=sr.values,resubmission_of=str(sr.resubmission_of_id) if sr.resubmission_of_id else None,
        allowed_actions=allowed_actions(p,t),can_assign=request_staff(p,t) and t.status in ('APPROVED','IN_PROGRESS'),
        can_comment_internal=request_staff(p,t),can_decide=bool(approval and approval.approver_id==p.id and approval.status=='PENDING' and t.status=='PENDING_APPROVAL' and not t.requested_by_id==p.id),
        approval={'approver':s.person_data(approval.approver),'status':approval.status,
                  'decision':decision.decision if decision else None,'reason':decision.reason if decision else None} if approval else None)
    from .assets import request_asset_events
    result['asset_events']=request_asset_events(p,t)
    if sr.catalog_version.workflow_version_id:
        from .models import ProcessRun
        run=ProcessRun.objects.filter(ticket=t).first()
        result.update(can_assign=False,can_decide=False,allowed_actions=[],process_run_id=str(run.id) if run else None,process_status=run.status if run else None)
        if run and (run.graph.get('screen') or any(node.get('screen') for node in run.graph['nodes'])):
            from .process_engine import task_fields
            tasks=list(run.tasks.filter(status='OPEN')) or list(run.tasks.order_by('-created_at')[:1]);visible=set()
            for task in tasks:
                node=next(n for n in run.graph['nodes'] if n['key']==task.node_key)
                visible.update(field['key'] for field in task_fields(p,run,node,task))
            result['fields']=[field for field in result['fields'] if field['key'] in visible];result['values']={key:value for key,value in result['values'].items() if key in visible}
    return result

def notify(p,t,event,kind,recipients):
    for person in Person.objects.filter(id__in=set(recipients),organization=p.organization,active=True,user__is_active=True):
        if request_query(person).filter(id=t.id).exists():
            Notification.objects.get_or_create(organization=p.organization,recipient=person,ticket=t,event=event,defaults={'kind':kind})

def ready_recipients(t):
    from .permissions import people_with
    managers=people_with(t.organization,'service.manage').values_list('id',flat=True)
    agents=people_with(t.organization,'service.work').filter(membership__group=t.group,membership__group__active=True).values_list('id',flat=True)
    return set(managers)|set(agents)

def authorize(p,op,target):
    if op=='catalog_publish':
        require_manager(p)
        return
    if op=='req_create':
        return
    t=get_request(p,target,True)
    from .data_access import can_write
    if not can_write(p,'requests',t,'requested_by','assignee_id'):s.fail('FORBIDDEN','이 요청의 변경 범위를 벗어났습니다.',403)
    if op in ('req_assign','req_decision','req_action') and t.service_request.catalog_version.workflow_version_id:s.fail('WORKFLOW_MANAGED','연결된 워크플로우 업무·결재 화면에서 처리하십시오.',409)
    if op=='req_assign' and not request_staff(p,t):
        s.fail('FORBIDDEN','요청 처리 권한이 없습니다.',403)
    if op=='req_decision':
        approval=approval_for(t)
        if not approval or approval.approver_id!=p.id or t.requested_by_id==p.id:
            s.fail('FORBIDDEN','지정 승인자만 결정할 수 있습니다.',403)

def replay(p,op,data,result,target):
    if op in ('req_create','req_assign','req_action','req_decision'):
        t=get_request(p,s.identifier(result['id']))
        if op=='req_action':
            action=data.get('action')
            allowed=(t.requested_by_id==p.id) if action=='CANCEL' else (t.requested_by_id==p.id or s.manager(p)) if action=='CLOSE' else (request_staff(p,t) and (t.assignee_id==p.id or s.manager(p)))
            if not allowed:
                s.fail('FORBIDDEN','현재 처리 권한이 없습니다.',403)
        current=request_data(p,t)
        for key in ('allowed_actions','can_assign','can_comment_internal','can_decide'):
            result[key]=current[key]
    if op=='req_comment':
        t=get_request(p,target)
        comment=Comment.objects.get(id=s.identifier(result['id']))
        if comment.visibility=='INTERNAL' and not request_staff(p,t):
            s.fail('FORBIDDEN','내부 댓글 접근 권한이 없습니다.',403)
    return result

def mutate(p,op,data,request_id,target):
    if op=='catalog_publish':
        return publish(p,data,request_id)
    if op=='req_create':
        return submit(p,data,request_id)
    t=get_request(p,target,True)
    if op=='req_comment':
        s.check_fields(data,['body','visibility','expected_version'],['body','visibility','expected_version'])
        s.version(t,data)
        visibility=data['visibility']
        if visibility not in ('PUBLIC','INTERNAL'):
            s.fail('INVALID_VISIBILITY','공개 범위를 확인하십시오.')
        if visibility=='INTERNAL' and not request_staff(p,t):
            s.fail('FORBIDDEN','내부 댓글 작성 권한이 없습니다.',403)
        c=Comment.objects.create(organization=p.organization,ticket=t,author=p,body=s.text(data,'body'),visibility=visibility)
        s.bump(t)
        s.record(p,t,'REQUEST_COMMENT_ADDED',request_id,after={'comment_id':str(c.id),'visibility':visibility})
        return {**s.comment_data(c),'ticket_version':t.row_version},201
    if op=='req_assign':
        s.check_fields(data,['assignee_id','expected_version'],['assignee_id','expected_version'])
        s.version(t,data)
        if t.status not in ('APPROVED','IN_PROGRESS'):
            s.fail('INVALID_STATE','승인된 처리 단계에서만 배정할 수 있습니다.',409)
        person=Person.objects.filter(id=s.identifier(data['assignee_id']),organization=p.organization,active=True,user__is_active=True).first()
        if not person or 'AGENT' not in s.roles(person) or not Membership.objects.filter(group=t.group,person=person,group__active=True).exists():
            s.fail('INVALID_ASSIGNEE','처리 그룹의 활성 담당자를 선택하십시오.')
        old=str(t.assignee_id) if t.assignee_id else None
        t.assignee=person
        s.bump(t)
        s.record(p,t,'REQUEST_ASSIGNED',request_id,{'assignee_id':old},{'assignee_id':str(person.id)})
        return request_data(p,t),200
    s.check_fields(data,['decision','reason','expected_version'] if op=='req_decision' else ['action','reason','expected_version'],
                   ['decision','expected_version'] if op=='req_decision' else ['action','expected_version'])
    s.version(t,data)
    old=t.status
    if op=='req_decision':
        approval=approval_for(t)
        if t.status!='PENDING_APPROVAL' or approval.status!='PENDING':
            s.fail('INVALID_STATE','이미 결정되었거나 취소된 승인입니다.',409)
        decision=data['decision']
        if decision not in ('APPROVE','REJECT'):
            s.fail('INVALID_DECISION','승인 또는 반려를 선택하십시오.')
        reason=s.text(data,'reason',required=decision=='REJECT')
        approval.status=t.status='APPROVED' if decision=='APPROVE' else 'REJECTED'
        approval.closed_at=timezone.now()
        approval.save()
        ApprovalDecision.objects.create(organization=p.organization,approval=approval,actor=p,decision=decision,reason=reason)
        action='APPROVAL_DECIDED'
    else:
        action=data['action']
        if not isinstance(action,str) or action not in ('START','FULFILL','CLOSE','CANCEL'):
            s.fail('INVALID_ACTION','지원하지 않는 요청 동작입니다.')
        if action not in allowed_actions(p,t):
            s.fail('ACTION_NOT_ALLOWED','현재 상태 또는 권한으로 처리할 수 없습니다.',409)
        reason=s.text(data,'reason',required=action in ('FULFILL','CANCEL'))
        t.status={'START':'IN_PROGRESS','FULFILL':'FULFILLED','CLOSE':'CLOSED','CANCEL':'CANCELLED'}[action]
        if action=='CANCEL':
            approval=approval_for(t)
            if approval and approval.status=='PENDING':
                approval.status='CANCELLED';approval.closed_at=timezone.now();approval.save()
        action='REQUEST_'+action
    s.bump(t)
    s.history(p,t,old,reason)
    event=s.record(p,t,action,request_id,{'status':old},{'status':t.status,'version':t.row_version})
    if action=='APPROVAL_DECIDED':
        notify(p,t,event,'APPROVAL_DECIDED',[t.requested_by_id])
        if t.status=='APPROVED':
            notify(p,t,event,'REQUEST_READY',ready_recipients(t))
    elif action=='REQUEST_FULFILL':
        notify(p,t,event,'REQUEST_FULFILLED',[t.requested_by_id])
    elif action=='REQUEST_CANCEL':
        approval=approval_for(t)
        notify(p,t,event,'REQUEST_CANCELLED',[approval.approver_id] if approval else ready_recipients(t))
    return request_data(p,t),200

def submit(p,data,request_id):
    s.check_fields(data,['catalog_version_id','values','resubmission_of'],['catalog_version_id','values'])
    v=CatalogVersion.objects.filter(id=s.identifier(data['catalog_version_id']),organization=p.organization).select_related('item','approver','fulfillment_group').first()
    if not v:
        s.fail('NOT_FOUND','서비스를 찾을 수 없습니다.',404)
    current=offering(p,v.item_id)
    if current.id!=v.id:
        s.fail('VERSION_CONFLICT','신청 양식이 변경되었습니다. 최신 양식을 확인하십시오.',409)
    if not v.fulfillment_group.active:
        s.fail('INVALID_GROUP','처리 그룹이 비활성 상태입니다.')
    if v.approval_required and (not v.approver.active or not v.approver.user.is_active or v.approver_id==p.id):
        s.fail('INVALID_APPROVER','활성 승인자가 필요하며 자기 승인은 허용되지 않습니다.')
    previous=None
    if data.get('resubmission_of') is not None:
        previous=Ticket.objects.filter(id=s.identifier(data['resubmission_of']),organization=p.organization,
                    type='SERVICE_REQUEST',requested_by=p,status__in=['REJECTED','CANCELLED'],
                    service_request__catalog_version__item_id=v.item_id).first()
        if not previous:
            s.fail('INVALID_RESUBMISSION','본인의 반려·취소 요청에서 같은 서비스를 재신청하십시오.')
    values=validate_values(v.fields,data['values'])
    t=Ticket.objects.create(organization=p.organization,type='SERVICE_REQUEST',number='SR-'+uuid.uuid4().hex.upper(),
            title=v.name,description=v.description,requested_by=p,group=v.fulfillment_group,
            status='PENDING_APPROVAL' if v.approval_required else 'APPROVED')
    snapshot=catalog_data(v,True)
    ServiceRequest.objects.create(organization=p.organization,ticket=t,catalog_version=v,values=values,snapshot=snapshot,resubmission_of=previous)
    if v.workflow_version_id:
        from .process_engine import version as process_version,start_run
        workflow=process_version(p,str(v.workflow_version_id),'WORKFLOW',True)
        keys={field['key'] for field in workflow.graph.get('fields',[])}
        start_run(p,workflow,v.name,{key:val for key,val in values.items() if key in keys},ticket=t);t.refresh_from_db()
    if v.approval_required:
        RequestApproval.objects.create(organization=p.organization,ticket=t,approver=v.approver)
    s.history(p,t,'')
    event=s.record(p,t,'SERVICE_REQUEST_CREATED',request_id,after={'status':t.status,'catalog_version_id':str(v.id),
            'resubmission_of':str(previous.id) if previous else None})
    if v.workflow_version_id:
        pass
    elif v.approval_required:
        notify(p,t,event,'APPROVAL_REQUESTED',[v.approver_id])
    else:
        notify(p,t,event,'REQUEST_READY',ready_recipients(t))
    return request_data(p,t),201


def pending_approval_requests(actor):
    from django.db.models import Q
    return request_query(actor).filter(Q(request_approval__approver=actor,request_approval__status='PENDING',status='PENDING_APPROVAL')|Q(process_run__tasks__kind='APPROVAL',process_run__tasks__status='OPEN',process_run__tasks__assignments__person=actor,process_run__status__in=['ACTIVE','BLOCKED'])).distinct()
