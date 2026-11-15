"""Dashboard task scopes narrow existing read access; they never grant access."""
from django.db.models import Q,Exists,OuterRef,F
from . import services as s
from .permissions import allowed
from .menu_access import path_allowed
from .models import ProcessRun,ProcessTask,ProcessAssignment,ProcessVote

SCOPES=(('all','전체'),('department','부서'),('mine','나'))


def visible_runs(actor):
    query=ProcessRun.objects.filter(organization=actor.organization)
    if not allowed(actor,'workflow.manage'):
        query=query.filter(Q(started_by=actor)|Q(tasks__assignments__person=actor)).distinct()
    from .data_access import restrict
    return restrict(actor,'workflow-inbox',query,'started_by','tasks__assignments__person_id')


def scoped_people(query,actor,scope,path):
    if scope=='mine':return query.filter(**{path+'_id':actor.id})
    if scope=='department':
        if not actor.department_id:return query.none()
        return query.filter(**{path+'__department_id':actor.department_id})
    return query


def workflow_tasks(actor,scope):
    if not allowed(actor,'workflow.use') or not path_allowed(actor,'/processes'):return ProcessTask.objects.none()
    pending=ProcessAssignment.objects.filter(organization=actor.organization,person__organization=actor.organization,person__active=True,person__user__is_active=True)
    votes=ProcessVote.objects.filter(task_id=OuterRef('task_id'),actor_id=OuterRef('person_id'),organization=actor.organization)
    pending=pending.annotate(_voted=Exists(votes)).filter(_voted=False).exclude(task__kind='APPROVAL',task__run__started_by_id=F('person_id'))
    pending=scoped_people(pending,actor,scope,'person')
    query=ProcessTask.objects.filter(organization=actor.organization,status='OPEN',kind__in=['TASK','APPROVAL'],run_id__in=visible_runs(actor).filter(status__in=['ACTIVE','BLOCKED']).values('id'))
    query=query.annotate(_pending=Exists(pending.filter(task_id=OuterRef('pk'))))
    if scope=='all':return query.filter(Q(_pending=True)|Q(assignments__isnull=True)).distinct()
    return query.filter(_pending=True)


def dashboard(actor,request):
    scope=request.GET.get('todo_scope','mine')
    if scope not in dict(SCOPES):scope='mine'
    query=request.GET.copy();query.pop('todo_scope',None);query.pop('todo_page',None)
    tabs=[]
    for key,label in SCOPES:
        params=query.copy();params['todo_scope']=key
        tabs.append(dict(key=key,label=label,url='?'+params.urlencode()+'#dashboard-tasks'))
    counts={key:0 for key in ('workflow','requests','incidents')};rows=[]
    tasks=workflow_tasks(actor,scope)
    counts['workflow']=tasks.count()
    for task in tasks.select_related('run__version__definition').order_by('-created_at','-id')[:10]:
        rows.append(dict(title=task.run.title,step=task.label,type='결재' if task.kind=='APPROVAL' else '워크플로우',created_at=task.created_at,url='/processes/'+str(task.run_id)))
    from .catalog import request_query
    if path_allowed(actor,'/portal/requests'):
        # Workflow-backed requests are represented by their human task, once.
        legacy=request_query(actor).filter(process_run__isnull=True)
        approvals=legacy.filter(status='PENDING_APPROVAL',request_approval__status='PENDING',request_approval__approver__active=True,request_approval__approver__user__is_active=True).exclude(requested_by_id=F('request_approval__approver_id'))
        approvals=scoped_people(approvals,actor,scope,'request_approval__approver')
        assigned=scoped_people(legacy.filter(status__in=['APPROVED','IN_PROGRESS'],assignee__active=True,assignee__user__is_active=True),actor,scope,'assignee')
        requests=(approvals|assigned).distinct();counts['requests']=requests.count()
        for ticket in requests.order_by('-created_at','-id')[:10]:
            rows.append(dict(title=ticket.title,step='승인 대기' if ticket.status=='PENDING_APPROVAL' else '처리 대기',type='서비스 요청',created_at=ticket.created_at,url='/portal/requests/'+str(ticket.id)))
    if path_allowed(actor,'/portal/incidents'):
        incidents=s.ticket_query(actor,True)|s.ticket_query(actor,False)
        incidents=scoped_people(incidents.filter(status__in=['ASSIGNED','IN_PROGRESS','PENDING'],assignee__active=True,assignee__user__is_active=True),actor,scope,'assignee').distinct()
        counts['incidents']=incidents.count()
        for ticket in incidents.order_by('-created_at','-id')[:10]:
            rows.append(dict(title=ticket.title,step={'ASSIGNED':'배정','IN_PROGRESS':'처리 중','PENDING':'대기'}[ticket.status],type='장애',created_at=ticket.created_at,url='/portal/incidents/'+str(ticket.id)))
    rows.sort(key=lambda row:(row['created_at'],row['url'],row['step']),reverse=True)
    return dict(todo_scope=scope,todo_tabs=tabs,todo_total=sum(counts.values()),todo_counts=counts,todo_rows=rows[:10],todo_department_missing=scope=='department' and not actor.department_id)
