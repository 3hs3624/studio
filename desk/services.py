"""One transaction boundary for all supported business commands."""
import hashlib
import json
import uuid
from django.core import signing
from django.db import transaction
from django.db.models import Q
from .models import (Organization, Person, Group, Membership, RoleGrant, Asset, ConfigurationItem,
                     Ticket, Incident, TicketResource, Comment, StatusHistory, AuditEvent,
                     OutboxEvent, IdempotencyRecord, ROLES)

class BusinessError(Exception):
    def __init__(self, code, message, status=422):
        self.code, self.message, self.status = code, message, status

def fail(code='INVALID_INPUT', message='입력값을 확인하십시오.', status=422):
    raise BusinessError(code, message, status)

def actor_for(user):
    if not user.is_authenticated:
        fail('UNAUTHENTICATED', '로그인이 필요합니다.', 401)
    p = Person.objects.filter(user=user, active=True, organization__active=True, user__is_active=True).first()
    if not p:
        fail('FORBIDDEN', '활성 조직 계정이 필요합니다.', 403)
    return p

def roles(p):
    return set(RoleGrant.objects.filter(person=p, organization=p.organization).values_list('role', flat=True))

def manager(p):
    return 'SERVICE_MANAGER' in roles(p)

def can_console(p):
    return bool(roles(p) & {'ORG_ADMIN', 'DEVELOPER', 'SOLUTION_OPERATOR'})


def require_console(p):
    if not can_console(p):
        fail('FORBIDDEN', '개발자·솔루션 운영자·시스템 관리자 권한이 필요합니다.', 403)


def require_admin(p):
    if 'ORG_ADMIN' not in roles(p):
        fail('FORBIDDEN', '조직 관리자 권한이 필요합니다.', 403)

def group_ids(p):
    if 'AGENT' not in roles(p):
        return []
    return list(Membership.objects.filter(person=p, organization=p.organization, group__active=True)
                .values_list('group_id', flat=True))

def staff(p, t):
    return manager(p) or (t.status != 'NEW' and t.group_id in group_ids(p))

def ticket_query(p, queue=False):
    q = Ticket.objects.filter(organization=p.organization,type='INCIDENT').select_related('incident','requested_by','group','assignee','sla_instance')
    if manager(p):
        return q if queue else q.filter(requested_by=p)
    permitted = Q(group_id__in=group_ids(p)) & ~Q(status='NEW')
    if queue:
        return q.filter(permitted)
    return q.filter(requested_by=p)

def get_ticket(p, ident, lock=False):
    q = Ticket.objects.filter(organization=p.organization,type='INCIDENT')
    if lock:
        q = q.select_for_update()
    t = q.filter(id=ident).first()
    if not t or not (t.requested_by_id == p.id or staff(p, t)):
        fail('NOT_FOUND', '대상을 찾을 수 없습니다.', 404)
    return t

def check_fields(data, allowed, required=()):
    if not isinstance(data, dict) or set(data)-set(allowed) or set(required)-set(data):
        fail('INVALID_SCHEMA', '필수 항목과 허용된 필드를 확인하십시오.', 400)

def text(data, key, maximum=10000, required=True):
    value = data.get(key, '')
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        fail('INVALID_FIELD', f'{key} 입력값을 확인하십시오.')
    return value.strip()

def identifier(value):
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        fail('INVALID_ID', '식별자가 올바르지 않습니다.')

def version(obj, data):
    value = data.get('expected_version')
    if type(value) is not int or value < 1:
        fail('INVALID_VERSION', 'expected_version은 양의 정수여야 합니다.')
    if obj.row_version != value:
        fail('VERSION_CONFLICT', '최신 내용을 다시 확인하십시오.', 409)

def bump(obj):
    obj.row_version += 1
    obj.save()

def resources_query(p, model):
    if model is Asset:
        from .assets import query
        return query(p)
    q = model.objects.filter(organization=p.organization)
    return q if 'RESOURCE_READER' in roles(p) else q.filter(portal_visible=True)

def resource_data(obj,p=None):
    if isinstance(obj,Asset):
        from .assets import data
        return data(obj,p)
    fields = ['id','asset_no','name','model','location'] if isinstance(obj, Asset) else ['id','ci_no','name','type','status']
    return {f: str(getattr(obj, f)) for f in fields}

def person_data(p):
    return {'id': str(p.id), 'display_name': p.display_name}

TRANSITIONS = {
    'START': ('ASSIGNED','IN_PROGRESS'), 'WAIT': ('IN_PROGRESS','PENDING'),
    'RESUME': ('PENDING','IN_PROGRESS'), 'RESOLVE': ('IN_PROGRESS','RESOLVED'),
    'CLOSE': ('RESOLVED','CLOSED'), 'REOPEN': ('RESOLVED','IN_PROGRESS')}

def can_transition(p, t, action):
    expected = TRANSITIONS.get(action)
    if not expected or t.status != expected[0]:
        return False
    if action in ('CLOSE','REOPEN'):
        return t.requested_by_id == p.id or manager(p)
    return staff(p,t) and (t.assignee_id == p.id or manager(p))

def ticket_data(p, t, detail=True):
    from .sla import summary
    inc = t.incident
    d = {'id':str(t.id), 'number':t.number, 'title':t.title, 'status':t.status,
         'priority':f'P{inc.priority}', 'group':{'id':str(t.group_id),'name':t.group.name},
         'assignee':person_data(t.assignee) if t.assignee else None,
         'created_at':t.created_at.isoformat(), 'updated_at':t.updated_at.isoformat(), 'version':t.row_version,
         'sla':summary(t)}
    if not detail:
        return d
    links = []
    for link in t.resources.select_related('asset','ci'):
        obj, model = (link.asset,Asset) if link.asset_id else (link.ci,ConfigurationItem)
        if resources_query(p,model).filter(id=obj.id).exists():
            links.append({'link_id':str(link.id), 'resource_type':'ASSET' if link.asset_id else 'CI',
                          'resource_id':str(obj.id), 'name':obj.name})
    actions = [a for a in TRANSITIONS if can_transition(p,t,a)]
    if t.status != 'CLOSED' and (manager(p) or staff(p,t)):
        actions.append('ASSIGN')
    d.update(description=t.description, impact=inc.impact, urgency=inc.urgency,
             requested_by=person_data(t.requested_by), resolution=inc.resolution or None,
             resources=links, allowed_actions=actions)
    if staff(p,t):
        d['pending_reason'] = inc.pending_reason
    return d

def comment_data(c):
    return {'id':str(c.id),'body':c.body,'visibility':c.visibility,
            'author':person_data(c.author),'created_at':c.created_at.isoformat()}

def record(p, obj, action, request_id, before=None, after=None):
    event = AuditEvent.objects.create(organization=p.organization,actor=p,action=action,
                             entity_type=obj.__class__.__name__,entity_id=obj.id,
                             before_data=before or {},after_data=after or {},request_id=request_id)
    OutboxEvent.objects.create(organization=p.organization,event_type=action,entity_id=obj.id,
                               payload={'request_id':str(request_id)})
    return event

def history(p, t, old, reason=''):
    StatusHistory.objects.create(organization=p.organization,ticket=t,actor=p,
                                 from_status=old,to_status=t.status,reason=reason)

def attach(p, t, data):
    check_fields(data,['resource_type','resource_id'],['resource_type','resource_id'])
    kind = data['resource_type']
    if kind not in ('ASSET','CI'):
        fail('INVALID_RESOURCE', '자산 또는 CI를 선택하십시오.')
    model = Asset if kind == 'ASSET' else ConfigurationItem
    obj = resources_query(p,model).filter(id=identifier(data['resource_id'])).first()
    if not obj:
        fail('NOT_FOUND','대상을 찾을 수 없습니다.',404)
    kwargs = {'asset':obj} if kind=='ASSET' else {'ci':obj}
    if TicketResource.objects.filter(ticket=t,**kwargs).exists():
        fail('DUPLICATE_RESOURCE','이미 연결된 대상입니다.',409)
    return TicketResource.objects.create(organization=p.organization,ticket=t,**kwargs)

def authorize_command(p, operation, target):
    if operation.startswith('code_'):
        from .common_codes import authorize
        authorize(p, operation, target)
        return
    if operation.startswith('entity_'):
        from .entity_service import authorize
        authorize(p, operation, target)
        return
    if operation.startswith('plugin_'):
        from .plugin_service import authorize
        authorize(p, operation, target)
        return
    if operation.startswith(('buy_','stock_')):
        from .procurement import authorize
        authorize(p,operation,target)
    elif operation.startswith('asset_'):
        from .assets import authorize
        authorize(p,operation,target)
    elif operation=='catalog_publish' or operation.startswith('req_'):
        from .catalog import authorize
        authorize(p,operation,target)
    elif operation in ('sla_calendar','sla_policy'):
        from .sla import require_manager
        require_manager(p)
    elif operation=='notification_read':
        from .sla import visible_notifications
        if not visible_notifications(p).filter(id=target).exists():
            fail('NOT_FOUND','알림을 찾을 수 없습니다.',404)
    elif operation.startswith('admin_'):
        require_admin(p)
        model = Group if operation=='admin_members' else Person
        if not model.objects.filter(id=target,organization=p.organization).exists():
            fail('NOT_FOUND','대상을 찾을 수 없습니다.',404)
    elif operation != 'create':
        t = get_ticket(p,target,lock=True)
        if operation in ('assign','attach','detach') and not (staff(p,t) or manager(p)):
            fail('FORBIDDEN','처리 권한이 없습니다.',403)
    # Replay checks visibility and command class permissions, then regenerates redacted responses.

def execute(p, operation, data, key, request_id, target=None, subtarget=None):
    if not isinstance(key,str) or not 1 <= len(key) <= 128:
        fail('IDEMPOTENCY_REQUIRED','Idempotency-Key가 필요합니다.',400)
    op_key = f'{operation}:{target or ""}:{subtarget or ""}'
    digest = hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    session_binding=getattr(p,'_session_binding',None)
    with transaction.atomic():
        # Coarse per-organization lock prioritizes correctness in the first release.
        Organization.objects.select_for_update().get(id=p.organization_id)
        p = Person.objects.select_for_update().get(id=p.id)
        if not p.active or not p.user.is_active or not p.organization.active:
            fail('FORBIDDEN','활성 계정이 필요합니다.',403)
        if session_binding is not None:
            from .security import binding
            from django.utils.crypto import constant_time_compare
            if not constant_time_compare(session_binding,binding(p)):
                fail('SESSION_REVOKED','다시 로그인하십시오.',403)
        authorize_command(p,operation,target)
        previous = IdempotencyRecord.objects.filter(organization=p.organization,actor=p,operation=op_key,key=key).first()
        if previous:
            if previous.request_hash != digest:
                fail('IDEMPOTENCY_CONFLICT','같은 키에 다른 요청을 사용할 수 없습니다.',409)
            if operation=='transition':
                current=get_ticket(p,target)
                action=data.get('action')
                permitted=(current.requested_by_id==p.id or manager(p)) if action in ('CLOSE','REOPEN') else (staff(p,current) and (current.assignee_id==p.id or manager(p)))
                if not permitted:
                    fail('FORBIDDEN','현재 상태 변경 권한이 없습니다.',403)
            result = dict(previous.response_body)
            if operation.startswith(('buy_','stock_')):
                from .procurement import replay
                result=replay(p,operation,data,result)
            if operation.startswith('asset_'):
                from .assets import replay
                result=replay(p,operation,data,result)
            if operation=='catalog_publish' or operation.startswith('req_'):
                from .catalog import replay
                result=replay(p,operation,data,result,target)
            if operation in ('create','assign','transition','attach'):
                current = get_ticket(p,identifier(result['id']))
                if not staff(p,current):
                    result.pop('pending_reason',None)
                result['allowed_actions'] = [a for a in TRANSITIONS if can_transition(p,current,a)]
                if current.status!='CLOSED' and staff(p,current):
                    result['allowed_actions'].append('ASSIGN')
                visible = {r['resource_id'] for r in ticket_data(p,current)['resources']}
                result['resources'] = [r for r in result['resources'] if r['resource_id'] in visible]
            elif operation == 'comment':
                c = Comment.objects.get(id=identifier(result['id']))
                if c.visibility == 'INTERNAL' and not staff(p,c.ticket):
                    fail('FORBIDDEN','현재 댓글 접근 권한이 없습니다.',403)
            return result, previous.response_code
        result, status = mutate(p,operation,data,request_id,target,subtarget)
        IdempotencyRecord.objects.create(organization=p.organization,actor=p,operation=op_key,key=key,
                                         request_hash=digest,response_code=status,response_body=result)
        return result,status

def mutate(p, op, data, request_id, target, subtarget):
    if op.startswith('code_'):
        from .common_codes import mutate as code_mutate
        return code_mutate(p, op, data, request_id, target)
    if op.startswith('entity_'):
        from .entity_service import mutate as entity_mutate
        return entity_mutate(p, op, data, request_id, target)
    if op.startswith('plugin_'):
        from .plugin_service import mutate as plugin_mutate
        return plugin_mutate(p, op, data, request_id, target)
    if op.startswith(('buy_','stock_')):
        from .procurement import mutate as mutate_procurement
        return mutate_procurement(p,op,data,request_id,target)
    if op.startswith('asset_'):
        from .assets import mutate as mutate_asset
        return mutate_asset(p,op,data,request_id,target)
    if op=='catalog_publish' or op.startswith('req_'):
        from .catalog import mutate as mutate_request
        return mutate_request(p,op,data,request_id,target)
    if op in ('sla_calendar','sla_policy'):
        from .sla import publish
        return publish(p,op,data,request_id)
    if op=='notification_read':
        from .sla import visible_notifications
        from django.utils import timezone
        check_fields(data,[])
        n=visible_notifications(p).select_for_update().get(id=target)
        if n.read_at is None:
            n.read_at=timezone.now()
            n.save(update_fields=['read_at'])
        return {'id':str(n.id),'read_at':n.read_at.isoformat()},200
    if op == 'create':
        check_fields(data,['title','description','impact','urgency','resources'],['title','description','impact','urgency'])
        title, description = text(data,'title',200), text(data,'description')
        impact, urgency = data['impact'],data['urgency']
        if type(impact) is not int or type(urgency) is not int or impact not in (1,2,3) or urgency not in (1,2,3):
            fail('INVALID_PRIORITY','영향도와 긴급도는 1~3입니다.')
        links = data.get('resources',[])
        if not isinstance(links,list) or len(links)>20:
            fail('INVALID_RESOURCE','연결 대상은 최대 20개입니다.')
        group = Group.objects.filter(organization=p.organization,active=True,triage=True).first()
        if not group:
            fail('TRIAGE_UNCONFIGURED','기본 접수 그룹이 설정되지 않았습니다.')
        t = Ticket.objects.create(organization=p.organization,number='INC-'+uuid.uuid4().hex.upper(),
                                  title=title,description=description,requested_by=p,group=group)
        Incident.objects.create(ticket=t,impact=impact,urgency=urgency,priority=impact+urgency-1)
        for item in links:
            attach(p,t,item)
        history(p,t,'')
        record(p,t,'INCIDENT_CREATED',request_id,after={'status':t.status,'version':1})
        from .sla import apply_to_new_ticket
        apply_to_new_ticket(t,p)
        return ticket_data(p,t),201

    if op.startswith('admin_'):
        return admin_mutate(p,op,data,request_id,target,subtarget)

    t = get_ticket(p,target,lock=True)
    if op == 'assign':
        check_fields(data,['group_id','assignee_id','expected_version'],['group_id','assignee_id','expected_version'])
        version(t,data)
        if t.status == 'CLOSED':
            fail('INVALID_STATE','종료된 장애는 배정할 수 없습니다.',409)
        group = Group.objects.filter(id=identifier(data['group_id']),organization=p.organization,active=True).first()
        assignee = Person.objects.filter(id=identifier(data['assignee_id']),organization=p.organization,
                                         active=True,user__is_active=True).first()
        if not group or not assignee or not Membership.objects.filter(group=group,person=assignee).exists() or 'AGENT' not in roles(assignee):
            fail('INVALID_ASSIGNEE','활성 그룹에 소속된 담당자를 선택하십시오.')
        if not manager(p) and group.id != t.group_id:
            fail('FORBIDDEN','다른 그룹 배정은 관리자만 할 수 있습니다.',403)
        old = t.status
        before = {'group_id':str(t.group_id),'assignee_id':str(t.assignee_id) if t.assignee_id else None}
        t.group,t.assignee = group,assignee
        if t.status=='NEW':
            t.status='ASSIGNED'
            history(p,t,old)
        bump(t)
        record(p,t,'INCIDENT_ASSIGNED',request_id,before,{'group_id':str(group.id),'assignee_id':str(assignee.id)})
        return ticket_data(p,t),200

    if op == 'transition':
        check_fields(data,['action','reason','resolution','expected_version'],['action','expected_version'])
        version(t,data)
        action = data['action']
        if not isinstance(action,str) or action not in TRANSITIONS:
            fail('INVALID_ACTION','지원하지 않는 동작입니다.')
        if t.status != TRANSITIONS[action][0]:
            fail('INVALID_STATE','현재 상태에서 실행할 수 없습니다.',409)
        if not can_transition(p,t,action):
            fail('FORBIDDEN','상태 변경 권한이 없습니다.',403)
        reason = text(data,'reason',required=action in ('WAIT','REOPEN'))
        resolution = text(data,'resolution',required=action=='RESOLVE')
        old = t.status
        t.status=TRANSITIONS[action][1]
        inc = t.incident
        if action=='WAIT':
            inc.pending_reason=reason
        if action in ('RESUME','REOPEN'):
            inc.pending_reason=''
        if action=='RESOLVE':
            inc.resolution=resolution
        if action=='REOPEN':
            inc.resolution=''
        inc.save()
        bump(t)
        history(p,t,old,reason or resolution)
        record(p,t,'INCIDENT_'+action,request_id,{'status':old},{'status':t.status,'version':t.row_version})
        from .sla import transition
        transition(t,action,p)
        return ticket_data(p,t),200

    if op == 'comment':
        check_fields(data,['body','visibility','expected_version'],['body','visibility','expected_version'])
        version(t,data)
        visibility=data['visibility']
        if visibility not in ('PUBLIC','INTERNAL'):
            fail('INVALID_VISIBILITY','댓글 공개 범위를 확인하십시오.')
        if visibility=='INTERNAL' and not staff(p,t):
            fail('FORBIDDEN','내부 댓글 작성 권한이 없습니다.',403)
        c=Comment.objects.create(organization=p.organization,ticket=t,author=p,visibility=visibility,body=text(data,'body'))
        bump(t)
        record(p,t,'COMMENT_ADDED',request_id,after={'comment_id':str(c.id),'visibility':visibility})
        return {**comment_data(c),'ticket_version':t.row_version},201

    if op in ('attach','detach'):
        check_fields(data,['resource_type','resource_id','expected_version'] if op=='attach' else ['expected_version'],
                     ['resource_type','resource_id','expected_version'] if op=='attach' else ['expected_version'])
        version(t,data)
        if t.status=='CLOSED':
            fail('INVALID_STATE','종료된 장애는 변경할 수 없습니다.',409)
        if op=='attach':
            link=attach(p,t,{k:v for k,v in data.items() if k!='expected_version'})
        else:
            link=TicketResource.objects.filter(id=subtarget,ticket=t).first()
            if not link:
                fail('NOT_FOUND','연결을 찾을 수 없습니다.',404)
            model,ident=(Asset,link.asset_id) if link.asset_id else (ConfigurationItem,link.ci_id)
            if not resources_query(p,model).filter(id=ident).exists():
                fail('NOT_FOUND','대상을 찾을 수 없습니다.',404)
        link_id=str(link.id)
        if op=='detach':
            link.delete()
        bump(t)
        record(p,t,'RESOURCE_'+op.upper(),request_id,after={'link_id':link_id})
        return (ticket_data(p,t),200) if op=='attach' else ({},204)
    fail('INVALID_OPERATION','지원하지 않는 동작입니다.',400)

def admin_mutate(p,op,data,request_id,target,subtarget):
    require_admin(p)
    if op in ('admin_account','admin_revoke_sessions'):
        fields=['expected_version','reason'] + (['active'] if op=='admin_account' else [])
        check_fields(data,fields,fields)
        member=Person.objects.select_for_update().get(id=target,organization=p.organization)
        version(member,data)
        reason=text(data,'reason')
        before={'active':member.active}
        if op=='admin_account':
            if type(data['active']) is not bool:
                fail('INVALID_ACCOUNT','active는 boolean이어야 합니다.')
            if not data['active']:
                if member.id==p.id:
                    fail('ADMIN_PROTECTED','본인 계정을 중지할 수 없습니다.',409)
                if 'ORG_ADMIN' in roles(member) and not RoleGrant.objects.filter(organization=p.organization,role='ORG_ADMIN',person__active=True,person__user__is_active=True).exclude(person=member).exists():
                    fail('ADMIN_PROTECTED','마지막 활성 관리자를 중지할 수 없습니다.',409)
                if Ticket.objects.filter(assignee=member).exclude(status__in=['CLOSED','REJECTED','CANCELLED']).exists():
                    fail('OPEN_ASSIGNMENTS','열린 배정 건을 먼저 재배정하십시오.',409)
                from .models import RequestApproval, PurchaseRequisition
                if RequestApproval.objects.filter(approver=member,status='PENDING').exists() or PurchaseRequisition.objects.filter(approver=member,status='PENDING').exists():
                    fail('PENDING_APPROVALS','대기 중인 승인을 먼저 정리하십시오.',409)
            member.active=data['active']
        member.session_epoch=uuid.uuid4()
        bump(member)
        # bump persists all fields; no session or token value enters the audit payload.
        record(p,member,'ACCOUNT_CHANGED' if op=='admin_account' else 'SESSIONS_REVOKED',request_id,
            before,{'active':member.active,'reason':reason})
        return {'person_version':member.row_version,'active':member.active},200
    if op=='admin_members':
        check_fields(data,['active','expected_version','reason'],['active','expected_version'])
        reason=text(data,'reason',500,required=False)
        group=Group.objects.get(id=target,organization=p.organization)
        version(group,data)
        member=Person.objects.filter(id=subtarget,organization=p.organization,active=True,user__is_active=True).first()
        if not member or not group.active:
            fail('INVALID_MEMBER','활성 그룹과 사용자가 필요합니다.')
        if type(data['active']) is not bool:
            fail('INVALID_MEMBER','active는 boolean이어야 합니다.')
        if data['active']:
            Membership.objects.get_or_create(organization=p.organization,group=group,person=member)
        else:
            if Ticket.objects.filter(group=group,assignee=member).exclude(status__in=['CLOSED','REJECTED','CANCELLED']).exists():
                fail('OPEN_ASSIGNMENTS','열린 배정 건을 먼저 재배정하십시오.',409)
            Membership.objects.filter(group=group,person=member).delete()
        member.session_epoch=uuid.uuid4()
        bump(member)
        bump(group)
        record(p,group,'MEMBERSHIP_CHANGED',request_id,after={'person_id':str(member.id),'active':data['active'],'reason':reason})
        return {'group_version':group.row_version},200
    check_fields(data,['roles','expected_version','reason'],['roles','expected_version'])
    reason=text(data,'reason',500,required=False)
    member=Person.objects.get(id=target,organization=p.organization)
    version(member,data)
    desired=data['roles']
    if not isinstance(desired,list) or not all(isinstance(x,str) for x in desired) or set(desired)-set(ROLES) or len(set(desired))!=len(desired):
        fail('INVALID_ROLES','허용된 역할을 중복 없이 지정하십시오.')
    old=roles(member)
    if 'ORG_ADMIN' in old and 'ORG_ADMIN' not in desired:
        others=RoleGrant.objects.filter(organization=p.organization,role='ORG_ADMIN',person__active=True,
                                         person__user__is_active=True).exclude(person=member)
        if member.id==p.id or not others.exists():
            fail('ADMIN_PROTECTED','자기 관리자 권한 또는 마지막 관리자는 제거할 수 없습니다.',409)
    if 'AGENT' in old and 'AGENT' not in desired and Ticket.objects.filter(assignee=member).exclude(status__in=['CLOSED','REJECTED','CANCELLED']).exists():
        fail('OPEN_ASSIGNMENTS','열린 배정 건을 먼저 재배정하십시오.',409)
    RoleGrant.objects.filter(person=member).delete()
    for role in desired:
        RoleGrant.objects.create(organization=p.organization,person=member,role=role)
    if old != set(desired):
        member.session_epoch=uuid.uuid4()
    bump(member)
    record(p,member,'ROLES_CHANGED',request_id,{'roles':sorted(old)},{'roles':sorted(desired),'reason':reason})
    return {'person_version':member.row_version},200

def page(p, qs, params, serialize, scope=''):
    try:
        limit=int(params.get('limit',25))
        if limit<1 or limit>100:
            raise ValueError()
    except (ValueError,TypeError):
        fail('INVALID_LIMIT','limit은 1~100입니다.',400)
    fingerprint=hashlib.sha256(json.dumps({'person':str(p.id),'org':str(p.organization_id),
        'roles':sorted(roles(p)),'groups':sorted(str(x) for x in group_ids(p)),
        'memberships':sorted(str(x) for x in Membership.objects.filter(person=p,organization=p.organization,group__active=True).values_list('group_id',flat=True)),
        'endpoint':scope, 'query':{k:v for k,v in params.items() if k not in ('cursor','limit') and v},
        'limit':limit},sort_keys=True).encode()).hexdigest()
    cursor=params.get('cursor')
    if cursor:
        try:
            value=signing.loads(cursor,salt='desk.cursor',max_age=3600)
            if value['scope']!=fingerprint:
                raise ValueError()
            from django.utils.dateparse import parse_datetime
            stamp=parse_datetime(value['created_at'])
            if stamp is None:
                raise ValueError()
            ident=uuid.UUID(value['id'])
            qs=qs.filter(Q(created_at__lt=stamp)|Q(created_at=stamp,id__lt=ident))
        except (signing.BadSignature,ValueError,KeyError,TypeError):
            fail('INVALID_CURSOR','현재 조회 범위에 맞는 커서가 아닙니다.',400)
    rows=list(qs.order_by('-created_at','-id')[:limit+1])
    next_cursor=None
    if len(rows)>limit:
        last=rows[limit-1]
        next_cursor=signing.dumps({'scope':fingerprint,'created_at':last.created_at.isoformat(),'id':str(last.id)},salt='desk.cursor')
    return {'items':[serialize(x) for x in rows[:limit]],'next_cursor':next_cursor}
