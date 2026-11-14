"""Receipt-based, versioned timeliness targets with explicit unscored and overdue cohorts."""
import csv,io,hashlib,json,uuid
from datetime import date,datetime,timedelta,time
from django.db.models import Max
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (Ticket,TimelinessPolicy,TimelinessTarget,TimelinessEvent,TimelinessReport,BusinessCalendar)
from . import services as s
from .business_time import add_business_microseconds
from .sla import calendar_data,require_manager

BASES={'RECEIPT':'접수 시각 + SLA 처리 시간','AGREED_START':'합의한 처리 시작 시각 + SLA 처리 시간','REQUESTED_DUE':'고객 요청 완료 기한','AGREED_DUE':'고객 합의 완료 기한'}
DEFAULT={'version':0,'name':'고객 정책 미설정 · 기본 24시간','basis':'RECEIPT','target_minutes':1440,'calendar':None,'reopen_rule':'FINAL_COMPLETION'}

def policy_snapshot(policy):return dict(version=policy.version,name=policy.name,basis=policy.basis,target_minutes=policy.target_minutes,calendar=calendar_data(policy.calendar) if policy.calendar_id else None,reopen_rule='FINAL_COMPLETION')

def deadline(target):
    spec=target.snapshot;basis=spec['basis']
    if basis in ('REQUESTED_DUE','AGREED_DUE'):return target.requested_due_at if basis=='REQUESTED_DUE' else target.agreed_due_at
    anchor=target.received_at if basis=='RECEIPT' else target.agreed_start_at
    if not anchor:return None
    return add_business_microseconds(anchor,spec['target_minutes']*60_000_000,spec['calendar']) if spec.get('calendar') else anchor+timedelta(minutes=spec['target_minutes'])

def ensure(ticket):
    existing=TimelinessTarget.objects.filter(ticket=ticket).first()
    if existing:return existing
    policy=TimelinessPolicy.objects.filter(organization=ticket.organization,ticket_type=ticket.type,created_at__lte=ticket.created_at).order_by('-version').first()
    target=TimelinessTarget(organization=ticket.organization,ticket=ticket,policy=policy,snapshot=policy_snapshot(policy) if policy else dict(DEFAULT),received_at=ticket.created_at,status_observed=ticket.status)
    target.due_at=deadline(target)
    # Historical completion must come from an actual transition, never last-modified time.
    if ticket.status in ('FULFILLED','CLOSED','RESOLVED'):
        history=ticket.statushistory_set.filter(to_status__in=['FULFILLED','RESOLVED']).order_by('-created_at').first()
        if history:target.completed_at=history.created_at;target.completion_source='STATUS_HISTORY'
    target.save();return target

@receiver(post_save,sender=Ticket,dispatch_uid='studio.timeliness.track')
def track(sender,instance,created,raw=False,**kwargs):
    if raw:return
    target=ensure(instance)
    if created:return
    old=target.status_observed;current=instance.status
    if old==current:return
    completed=current in ('FULFILLED','RESOLVED') or current=='CLOSED' and old not in ('FULFILLED','RESOLVED')
    reopened=current not in ('FULFILLED','RESOLVED','CLOSED','CANCELLED','REJECTED','TRANSFERRED') and old in ('FULFILLED','RESOLVED','CLOSED')
    if completed and not target.completed_at:target.completed_at=timezone.now();target.completion_source='STATUS_TRANSITION'
    if reopened:target.completed_at=None;target.completion_source=''
    target.status_observed=current;target.row_version+=1;target.save()
    TimelinessEvent.objects.create(organization=instance.organization,target=target,action='REOPENED' if reopened else 'COMPLETED' if completed else 'STATUS_CHANGED',details={'from':old,'to':current})

def handoff_complete(ticket):
    target=ensure(ticket)
    if not target.completed_at:
        target.completed_at=timezone.now();target.completion_source='HANDOFF_CHAIN_COMPLETED';target.row_version+=1;target.save()
        TimelinessEvent.objects.create(organization=ticket.organization,target=target,action='COMPLETED',details={'source':target.completion_source})

def visible_tickets(actor):
    from .catalog import request_query
    return Ticket.objects.filter(organization=actor.organization).filter(__import__('django.db.models',fromlist=['Q']).Q(id__in=s.ticket_query(actor,True).values('id'))|__import__('django.db.models',fromlist=['Q']).Q(id__in=request_query(actor).values('id')))

def authorize(actor,operation,target):
    require_manager(actor)
    from .security_policy import require_recent
    if operation in ('kpi_policy','kpi_adjust'):require_recent(actor)
    if operation=='kpi_adjust':
        ticket=visible_tickets(actor).filter(id=s.identifier(target)).first()
        if not ticket:s.fail('NOT_FOUND','요청을 찾을 수 없습니다.',404)
        from .data_access import can_write
        if not can_write(actor,'requests' if ticket.type=='SERVICE_REQUEST' else 'incidents',ticket,'requested_by','assignee_id'):s.fail('FORBIDDEN','합의 내용을 변경할 범위가 아닙니다.',403)

def mutate(actor,operation,data,request_id,target):
    if operation=='kpi_policy':
        s.check_fields(data,['name','ticket_type','basis','target_minutes','calendar_id','expected_version','reason'],['name','ticket_type','basis','target_minutes','expected_version','reason'])
        if data['ticket_type'] not in ('INCIDENT','SERVICE_REQUEST') or data['basis'] not in BASES or type(data['target_minutes']) is not int or not 1<=data['target_minutes']<=525600:s.fail('INVALID_KPI_POLICY','대상 업무·기준·목표 시간을 확인하십시오.')
        latest=TimelinessPolicy.objects.filter(organization=actor.organization,ticket_type=data['ticket_type']).aggregate(value=Max('version'))['value'] or 0
        if data['expected_version']!=latest:s.fail('VERSION_CONFLICT','정책 버전이 변경되었습니다.',409)
        calendar=None
        if data.get('calendar_id'):
            calendar=BusinessCalendar.objects.filter(organization=actor.organization,id=s.identifier(data['calendar_id'])).first()
            if not calendar:s.fail('INVALID_CALENDAR','현재 조직의 업무 달력을 선택하십시오.')
        value=TimelinessPolicy.objects.create(organization=actor.organization,ticket_type=data['ticket_type'],version=latest+1,name=s.text(data,'name',200),basis=data['basis'],target_minutes=data['target_minutes'],calendar=calendar,published_by=actor,reason=s.text(data,'reason',500))
        s.record(actor,value,'TIMELINESS_POLICY_PUBLISHED',request_id,after={**policy_snapshot(value),'reason':value.reason})
        return {'id':str(value.id),'version':value.version},201
    if operation=='kpi_adjust':
        s.check_fields(data,['expected_version','agreed_start_at','requested_due_at','agreed_due_at','reason'],['expected_version','reason'])
        ticket=visible_tickets(actor).get(id=s.identifier(target));value=ensure(ticket);s.version(value,data)
        if value.completed_at or ticket.status in ('REJECTED','CANCELLED'):s.fail('KPI_FINISHED','완료·종료된 건의 기한은 변경할 수 없습니다.',409)
        before={field:getattr(value,field).isoformat() if getattr(value,field) else None for field in ('agreed_start_at','requested_due_at','agreed_due_at','due_at')}
        for field in ('agreed_start_at','requested_due_at','agreed_due_at'):
            if field not in data:continue
            moment=parse_datetime(data[field]) if isinstance(data[field],str) and data[field] else None
            if data[field] and (not moment or timezone.is_naive(moment)):s.fail('INVALID_DATE','시간대가 포함된 합의 시각·기한을 입력하십시오.')
            if moment and moment<value.received_at:s.fail('INVALID_DATE','접수 시각보다 이전인 합의 시각·기한은 허용되지 않습니다.')
            setattr(value,field,moment)
        value.due_at=deadline(value);value.row_version+=1;value.save();reason=s.text(data,'reason',500)
        after={field:getattr(value,field).isoformat() if getattr(value,field) else None for field in before}
        TimelinessEvent.objects.create(organization=actor.organization,target=value,actor=actor,action='AGREEMENT_CHANGED',details={'before':before,'after':after},reason=reason);s.record(actor,value,'TIMELINESS_AGREEMENT_CHANGED',request_id,before=before,after={**after,'reason':reason})
        return {'id':str(ticket.id),'version':value.row_version},200
    if operation=='kpi_report':
        s.check_fields(data,['starts_on','ends_on','cohort'],['starts_on','ends_on','cohort'])
        starts,ends=period(data['starts_on'],data['ends_on']);totals,rows,asof=calculate(actor,starts,ends,data['cohort'])
        value=TimelinessReport.objects.create(organization=actor.organization,generated_by=actor,starts_on=starts,ends_on=ends,cohort=data['cohort'],as_of=asof,totals=totals,rows=rows,digest=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
        s.record(actor,value,'TIMELINESS_REPORT_GENERATED',request_id,after={'totals':totals,'starts_on':str(starts),'ends_on':str(ends),'cohort':data['cohort'],'digest':value.digest})
        return {'id':str(value.id),'totals':totals},201
    s.fail('INVALID_OPERATION','지원하지 않는 KPI 작업입니다.')

def period(starts,ends):
    try:
        first=date.fromisoformat(starts);last=date.fromisoformat(ends)
        if last<first or (last-first).days>3660 or last.year>=9999:raise ValueError()
        return first,last
    except (ValueError,TypeError):s.fail('INVALID_PERIOD','조회 기간은 시작일부터 종료일까지 최대 10년입니다.')

def calculate(actor,starts,ends,cohort='COMPLETION'):
    require_manager(actor)
    if cohort not in ('COMPLETION','DUE'):s.fail('INVALID_COHORT','집계 기준을 확인하십시오.')
    asof=timezone.now();zone=timezone.get_default_timezone();begin=timezone.make_aware(datetime.combine(starts,time.min),zone);finish=timezone.make_aware(datetime.combine(ends+timedelta(days=1),time.min),zone)
    # Backfill only visible records; original completion timestamps are reconstructed conservatively.
    tickets=visible_tickets(actor)
    for ticket in tickets.filter(timelinesstarget__isnull=True).iterator():ensure(ticket)
    targets=TimelinessTarget.objects.filter(organization=actor.organization,ticket_id__in=tickets.values('id')).select_related('ticket')
    targets=targets.filter(completed_at__gte=begin,completed_at__lt=finish) if cohort=='COMPLETION' else targets.filter(due_at__gte=begin,due_at__lt=finish)
    rows=[];totals={'eligible':0,'on_time':0,'late_completed':0,'overdue_open':0,'not_due_open':0,'unscored':0,'excluded':0}
    for target in targets:
        completed=target.completed_at if target.completed_at and target.completed_at<=asof else None
        if target.ticket.status in ('CANCELLED','REJECTED'):result='EXCLUDED';totals['excluded']+=1
        elif not target.due_at:result='UNSCORED';totals['unscored']+=1
        elif completed:
            totals['eligible']+=1;result='ON_TIME' if completed<=target.due_at else 'LATE';totals['on_time' if result=='ON_TIME' else 'late_completed']+=1
        elif target.due_at<asof:totals['eligible']+=1;totals['overdue_open']+=1;result='OVERDUE_OPEN'
        else:totals['not_due_open']+=1;result='NOT_DUE'
        rows.append(dict(ticket_id=str(target.ticket_id),number=target.ticket.number,ticket_type=target.ticket.type,policy_name=target.snapshot['name'],policy_version=target.snapshot['version'],basis=target.snapshot['basis'],received_at=target.received_at.isoformat(),due_at=target.due_at.isoformat() if target.due_at else None,completed_at=completed.isoformat() if completed else None,result=result,source=target.completion_source))
    totals['percentage']=round(totals['on_time']*100/totals['eligible'],2) if totals['eligible'] else None
    totals['missing_deadline_total']=TimelinessTarget.objects.filter(ticket_id__in=tickets.values('id'),due_at__isnull=True).count()
    totals['missing_completion_total']=TimelinessTarget.objects.filter(ticket_id__in=tickets.filter(status__in=['FULFILLED','RESOLVED','CLOSED']).values('id'),completed_at__isnull=True).count()
    return totals,rows,asof

def export(actor,id):
    require_manager(actor);report=TimelinessReport.objects.filter(organization=actor.organization,id=s.identifier(id)).first()
    if not report:s.fail('NOT_FOUND','보고서를 찾을 수 없습니다.',404)
    visible={str(id) for id in visible_tickets(actor).filter(id__in=[r['ticket_id'] for r in report.rows]).values_list('id',flat=True)}
    if any(row['ticket_id'] not in visible for row in report.rows):s.fail('SCOPE_CHANGED','보고서 생성 후 조회 범위가 변경되었습니다. 다시 산출하십시오.',403)
    stream=io.StringIO(newline='');writer=csv.writer(stream);columns=['number','ticket_type','policy_name','policy_version','basis','received_at','due_at','completed_at','result','source'];writer.writerow(columns)
    for row in report.rows:
        values=[]
        for key in columns:
            value='' if row[key] is None else str(row[key]);values.append("'"+value if value.lstrip().startswith(('=','+','-','@')) else value)
        writer.writerow(values)
    response=HttpResponse('\ufeff'+stream.getvalue(),content_type='text/csv; charset=utf-8');response['Content-Disposition']='attachment; filename="timeliness-'+str(report.id)+'.csv"';response['Cache-Control']='no-store';return response
