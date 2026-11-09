"""Versioned SLA policies, business clocks and transactional in-app escalation."""
from copy import copy
from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .business_time import validate_calendar, add_business_microseconds, business_microseconds, CalendarError
from .models import (Organization, BusinessCalendar, SLAPolicy, SLAInstance, SLAClockEvent,
                     SLAAlert, Notification, Person, RoleGrant, OutboxEvent)

MINUTE_US = 60_000_000
GOALS = ('RESPONSE','RESOLUTION')

def require_manager(p):
    from . import services as s
    if not s.manager(p):
        s.fail('FORBIDDEN','서비스 관리자 권한이 필요합니다.',403)

def calendar_data(c):
    return {'id':str(c.id),'name':c.name,'timezone':c.timezone,'weekdays':c.weekdays,
            'starts_at':c.starts_at,'ends_at':c.ends_at,'holidays':c.holidays}

def policy_data(p):
    return {'id':str(p.id),'name':p.name,'priority':p.priority,'version':p.version,
            'calendar_id':str(p.calendar_id),'response_minutes':p.response_minutes,
            'resolution_minutes':p.resolution_minutes,'warning_percent':p.warning_percent,
            'pause_on_pending':p.pause_on_pending}

def publish(p,operation,data,request_id):
    from . import services as s
    require_manager(p)
    if operation=='sla_calendar':
        s.check_fields(data,['name','timezone','weekdays','starts_at','ends_at','holidays'],
                       ['name','timezone','weekdays','starts_at','ends_at','holidays'])
        validate_calendar(data)
        c=BusinessCalendar.objects.create(organization=p.organization,name=s.text(data,'name',200),
             timezone=data['timezone'],weekdays=sorted(data['weekdays']),starts_at=data['starts_at'],
             ends_at=data['ends_at'],holidays=sorted(data['holidays']))
        s.record(p,c,'SLA_CALENDAR_PUBLISHED',request_id,after=calendar_data(c))
        return calendar_data(c),201
    s.check_fields(data,['name','calendar_id','priority','response_minutes','resolution_minutes','warning_percent','pause_on_pending'],
                   ['name','calendar_id','priority','response_minutes','resolution_minutes','warning_percent','pause_on_pending'])
    for field,maximum in [('priority',5),('response_minutes',10080),('resolution_minutes',10080),('warning_percent',99)]:
        if type(data[field]) is not int or not 1<=data[field]<=maximum:
            s.fail('INVALID_SLA_POLICY',f'{field} 범위를 확인하십시오.')
    if data['response_minutes']>data['resolution_minutes'] or type(data['pause_on_pending']) is not bool:
        s.fail('INVALID_SLA_POLICY','응답 목표는 해결 목표 이하이고 대기 정지는 boolean이어야 합니다.')
    c=BusinessCalendar.objects.filter(id=s.identifier(data['calendar_id']),organization=p.organization).first()
    if not c:
        s.fail('NOT_FOUND','업무 달력을 찾을 수 없습니다.',404)
    # Reject calendars/policies that cannot produce a deadline within our supported horizon.
    add_business_microseconds(timezone.now(),data['resolution_minutes']*MINUTE_US,calendar_data(c))
    latest=SLAPolicy.objects.filter(organization=p.organization,priority=data['priority']).order_by('-version').first()
    policy=SLAPolicy.objects.create(organization=p.organization,calendar=c,name=s.text(data,'name',200),
            priority=data['priority'],version=(latest.version+1 if latest else 1),
            response_minutes=data['response_minutes'],resolution_minutes=data['resolution_minutes'],
            warning_percent=data['warning_percent'],pause_on_pending=data['pause_on_pending'])
    s.record(p,policy,'SLA_POLICY_PUBLISHED',request_id,after=policy_data(policy))
    return policy_data(policy),201

def budget(instance,goal):
    key='response_minutes' if goal=='RESPONSE' else 'resolution_minutes'
    return instance.snapshot[key]*MINUTE_US

def elapsed(instance,goal):
    return instance.response_elapsed_us if goal=='RESPONSE' else instance.resolution_elapsed_us

def completed(instance,goal):
    return instance.response_completed_at if goal=='RESPONSE' else instance.resolved_at

def due(instance,goal):
    return instance.response_due_at if goal=='RESPONSE' else instance.resolution_due_at

def paused(instance,goal):
    return goal=='RESOLUTION' and instance.paused_at is not None and instance.resolved_at is None

def advance(instance,at):
    if at<instance.accounted_at:
        raise CalendarError('이전 처리보다 과거인 시각으로 평가할 수 없습니다.')
    if not instance.response_completed_at or (not instance.resolved_at and not instance.paused_at):
        amount=business_microseconds(instance.accounted_at,at,instance.snapshot['calendar'])
        if not instance.response_completed_at:
            instance.response_elapsed_us+=amount
        if not instance.resolved_at and not instance.paused_at:
            instance.resolution_elapsed_us+=amount
    instance.accounted_at=at

def breached(instance,goal,at):
    end=completed(instance,goal)
    if elapsed(instance,goal)>budget(instance,goal):
        return True
    if end:
        return end>due(instance,goal)
    return not paused(instance,goal) and at>due(instance,goal)

def notify(instance,goal,level):
    alert,created=SLAAlert.objects.get_or_create(organization=instance.organization,instance=instance,goal=goal,level=level)
    if not created:
        return
    t=instance.ticket
    from .permissions import people_with
    recipients=set(people_with(instance.organization,'service.manage').values_list('id',flat=True))
    if t.assignee_id:
        recipients.add(t.assignee_id)
    from .services import staff
    for p in Person.objects.filter(id__in=recipients,organization=instance.organization,active=True,user__is_active=True):
        if staff(p,t):
            Notification.objects.get_or_create(organization=instance.organization,recipient=p,ticket=t,alert=alert)
    OutboxEvent.objects.create(organization=instance.organization,event_type='SLA_'+level,
        entity_id=alert.id,payload={'ticket_id':str(t.id),'goal':goal,'level':level})

def evaluate_instance(instance,at):
    for goal in GOALS:
        if breached(instance,goal,at):
            notify(instance,goal,'BREACH')
        elif not completed(instance,goal) and not paused(instance,goal) and elapsed(instance,goal)*100>=budget(instance,goal)*instance.snapshot['warning_percent']:
            notify(instance,goal,'WARNING')

def schedule(instance,at):
    fired=set(instance.slaalert_set.values_list('goal','level'))
    candidates=[]
    for goal in GOALS:
        if completed(instance,goal) or paused(instance,goal) or (goal,'BREACH') in fired:
            continue
        remaining_warning=budget(instance,goal)*instance.snapshot['warning_percent']//100-elapsed(instance,goal)
        if (goal,'WARNING') not in fired and remaining_warning>0:
            candidates.append(add_business_microseconds(at,remaining_warning,instance.snapshot['calendar']))
        else:
            candidates.append(max(at,due(instance,goal))+timedelta(microseconds=1))
    instance.next_evaluation_at=min(candidates) if candidates else None

def clock_event(instance,kind,at,actor=None):
    SLAClockEvent.objects.create(organization=instance.organization,instance=instance,actor=actor,
        kind=kind,occurred_at=at,detail={'response_elapsed_us':instance.response_elapsed_us,
        'resolution_elapsed_us':instance.resolution_elapsed_us,'paused':instance.paused_at is not None,
        'response_due_at':instance.response_due_at.isoformat(),
        'resolution_due_at':instance.resolution_due_at.isoformat()})

def apply_to_new_ticket(t,actor):
    policy=SLAPolicy.objects.filter(organization=t.organization,priority=t.incident.priority).select_related('calendar').order_by('-version').first()
    if not policy:
        return
    snapshot={**policy_data(policy),'calendar':calendar_data(policy.calendar)}
    instance=SLAInstance.objects.create(organization=t.organization,ticket=t,policy=policy,snapshot=snapshot,
        accounted_at=t.created_at,response_due_at=add_business_microseconds(t.created_at,policy.response_minutes*MINUTE_US,snapshot['calendar']),
        resolution_due_at=add_business_microseconds(t.created_at,policy.resolution_minutes*MINUTE_US,snapshot['calendar']))
    schedule(instance,t.created_at)
    instance.save()
    clock_event(instance,'APPLIED',t.created_at,actor)

def transition(t,action,actor,at=None):
    instance=SLAInstance.objects.filter(ticket=t).first()
    if not instance:
        return
    at=at or timezone.now()
    advance(instance,at)
    # A late WAIT cannot hide an already missed deadline.
    if action=='WAIT':
        evaluate_instance(instance,at)
    if action=='START' and not instance.response_completed_at:
        instance.response_completed_at=at
    if action=='WAIT' and instance.snapshot['pause_on_pending']:
        instance.paused_at=at
    if action in ('RESUME','REOPEN'):
        if action=='REOPEN':
            instance.resolved_at=None
        was_paused=instance.paused_at is not None
        instance.paused_at=None
        if was_paused or action=='REOPEN':
            remaining=budget(instance,'RESOLUTION')-instance.resolution_elapsed_us
            if remaining>0:
                instance.resolution_due_at=add_business_microseconds(at,remaining,instance.snapshot['calendar'])
    if action=='RESOLVE':
        instance.resolved_at=at
    evaluate_instance(instance,at)
    schedule(instance,at)
    instance.save()
    clock_event(instance,action,at,actor)

def summary(t,at=None):
    try:
        original=t.sla_instance
    except SLAInstance.DoesNotExist:
        return None
    instance=copy(original)
    at=at or timezone.now()
    advance(instance,max(at,instance.accounted_at))
    result={'policy_id':str(instance.policy_id),'policy_name':instance.snapshot['name'],
            'policy_version':instance.snapshot['version'],'timezone':instance.snapshot['calendar']['timezone']}
    for goal in GOALS:
        done=completed(instance,goal)
        over=breached(instance,goal,at)
        percent=min(100,elapsed(instance,goal)*100//budget(instance,goal))
        state='OVERDUE' if over else 'MET' if done else 'PAUSED' if paused(instance,goal) else 'AT_RISK' if percent>=instance.snapshot['warning_percent'] else 'RUNNING'
        result[goal.lower()]={'state':state,'target_minutes':budget(instance,goal)//MINUTE_US,
            'paused':paused(instance,goal),
            'elapsed_seconds':elapsed(instance,goal)//1_000_000,
            'remaining_seconds':max(0,budget(instance,goal)-elapsed(instance,goal))//1_000_000,
            'percent':percent,'due_at':None if paused(instance,goal) else due(instance,goal).isoformat(),
            'completed_at':done.isoformat() if done else None}
    return result

def evaluate_due(at=None,limit=500):
    at=at or timezone.now()
    candidates=list(SLAInstance.objects.filter(next_evaluation_at__lte=at,organization__active=True)
          .order_by('next_evaluation_at').values_list('id','organization_id')[:limit])
    count=0
    for ident,org_id in candidates:
        with transaction.atomic():
            org=Organization.objects.select_for_update().get(id=org_id)
            if not org.active:
                continue
            instance=SLAInstance.objects.select_for_update().select_related('ticket').get(id=ident)
            if not instance.next_evaluation_at or instance.next_evaluation_at>at:
                continue
            # A transition may have committed after the scheduler captured its timestamp.
            moment=max(at,instance.accounted_at)
            advance(instance,moment)
            evaluate_instance(instance,moment)
            schedule(instance,moment)
            instance.save()
            count+=1
    return count

def visible_notifications(p):
    from . import services as s
    from .catalog import request_query
    tickets=Q(ticket__requested_by=p) | (Q(ticket__group_id__in=s.group_ids(p)) & ~Q(ticket__status='NEW'))
    qs=Notification.objects.filter(organization=p.organization,recipient=p)
    return qs if s.manager(p) else qs.filter((Q(ticket__type='INCIDENT') & tickets)|Q(ticket_id__in=request_query(p).values('id')))

def notification_data(n):
    labels={'APPROVAL_REQUESTED':'승인 요청','APPROVAL_DECIDED':'승인 결과','REQUEST_READY':'처리 대기',
            'REQUEST_FULFILLED':'서비스 처리 완료','REQUEST_CANCELLED':'요청 취소'}
    sla=n.kind=='SLA'
    label=(('응답' if n.alert.goal=='RESPONSE' else '해결')+' · '+('기한 초과' if n.alert.level=='BREACH' else '기한 임박')) if sla else labels[n.kind]
    return {'id':str(n.id),'ticket_id':str(n.ticket_id),'ticket_title':n.ticket.title,
            'kind':n.kind,'label':label,'ticket_url':('/work/incidents/' if sla else '/portal/requests/')+str(n.ticket_id),
            'goal':n.alert.goal if sla else 'REQUEST','level':n.alert.level if sla else 'INFO','created_at':n.created_at.isoformat(),
            'read_at':n.read_at.isoformat() if n.read_at else None}
