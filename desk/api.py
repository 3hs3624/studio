import json
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError, OperationalError
from django.db.models import Q
from django.core.exceptions import RequestDataTooBig
from . import services as s
from .models import Person, Group, Membership, Ticket, Asset, ConfigurationItem, Comment, StatusHistory
from .business_time import CalendarError

def error(request, code, message, status):
    return JsonResponse({'error':{'code':code,'message':message,'fields':{},
                                 'request_id':getattr(request,'request_id','')}},status=status)

def csrf_failure(request, reason=''):
    if request.path.startswith('/api/'):
        return error(request,'CSRF_FAILED','보안 토큰을 새로 받아 다시 시도하십시오.',403)
    return HttpResponse('보안 검증에 실패했습니다. 페이지를 새로고침하십시오.',status=403)

def not_found(request, exception=None):
    if request.path.startswith('/api/'):
        return error(request,'NOT_FOUND','대상을 찾을 수 없습니다.',404)
    return HttpResponse('페이지를 찾을 수 없습니다.',status=404)

def server_error(request):
    if request.path.startswith('/api/'):
        return error(request,'INTERNAL_ERROR','처리 중 오류가 발생했습니다.',500)
    return HttpResponse('처리 중 오류가 발생했습니다.',status=500)

def endpoint(methods):
    def decorate(fn):
        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            if request.method not in methods:
                response=error(request,'METHOD_NOT_ALLOWED','허용되지 않은 메서드입니다.',405)
                response['Allow']=', '.join(methods)
                return response
            try:
                request.actor=s.actor_for(request.user)
                result=fn(request,*args,**kwargs)
                return result if isinstance(result,HttpResponse) else JsonResponse(result)
            except s.BusinessError as exc:
                return error(request,exc.code,exc.message,exc.status)
            except CalendarError as exc:
                return error(request,'INVALID_CALENDAR',str(exc),422)
            except (json.JSONDecodeError,UnicodeDecodeError):
                return error(request,'INVALID_JSON','올바른 JSON이 필요합니다.',400)
            except RequestDataTooBig:
                return error(request,'PAYLOAD_TOO_LARGE','요청 크기를 줄이십시오.',413)
            except (IntegrityError,OperationalError):
                return error(request,'WRITE_CONFLICT','다른 변경과 충돌했습니다. 같은 키로 재시도하십시오.',409)
        return wrapped
    return decorate

def body(request):
    if request.content_type!='application/json':
        s.fail('INVALID_CONTENT_TYPE','application/json 형식이 필요합니다.',400)
    value=json.loads(request.body)
    if not isinstance(value,dict):
        s.fail('INVALID_SCHEMA','JSON 객체가 필요합니다.',400)
    return value

def query(request,allowed):
    if set(request.GET)-set(allowed) or any(len(request.GET.getlist(k))!=1 for k in request.GET):
        s.fail('INVALID_QUERY','조회 조건을 확인하십시오.',400)
    return request.GET.dict()

def command(request,operation,target=None,subtarget=None):
    data=body(request) if request.method!='DELETE' else {'expected_version':parse_version(request.GET.get('expected_version'))}
    if request.method=='DELETE':
        query(request,['expected_version'])
    result,status=s.execute(request.actor,operation,data,request.headers.get('Idempotency-Key'),
                            request.request_id,target,subtarget)
    response=HttpResponse(status=204) if status==204 else JsonResponse(result,status=status)
    if operation=='create':
        response['Location']='/api/v1/incidents/'+result['id']
    return response

def parse_version(raw):
    try:
        return int(raw)
    except (ValueError,TypeError):
        s.fail('INVALID_VERSION','expected_version이 필요합니다.')

@endpoint(['GET'])
def me(request):
    p=request.actor
    return {**s.person_data(p),'organization':{'id':str(p.organization_id),'name':p.organization.name},
            'roles':sorted(s.roles(p))}

@endpoint(['GET','POST'])
def incidents(request):
    if request.method=='POST':
        return command(request,'create')
    params=query(request,['scope','status','priority','group_id','assignee','limit','cursor'])
    scope=params.get('scope','mine')
    if scope not in ('mine','queue'):
        s.fail('INVALID_SCOPE','scope는 mine 또는 queue입니다.',400)
    qs=s.ticket_query(request.actor,scope=='queue')
    if 'status' in params:
        from .models import STATUSES
        if params['status'] not in STATUSES:
            s.fail('INVALID_STATUS','상태를 확인하십시오.',400)
        qs=qs.filter(status=params['status'])
    if 'priority' in params:
        if params['priority'] not in ['P1','P2','P3','P4','P5']:
            s.fail('INVALID_PRIORITY','우선순위를 확인하십시오.',400)
        qs=qs.filter(incident__priority=int(params['priority'][1]))
    if 'group_id' in params:
        qs=qs.filter(group_id=s.identifier(params['group_id']))
    if 'assignee' in params:
        if params['assignee']!='me':
            s.fail('INVALID_ASSIGNEE','assignee는 me만 지원합니다.',400)
        qs=qs.filter(assignee=request.actor)
    return s.page(request.actor,qs,params,lambda t:s.ticket_data(request.actor,t,False),'incidents')

@endpoint(['GET'])
def incident(request,id):
    return s.ticket_data(request.actor,s.get_ticket(request.actor,id))

@endpoint(['POST'])
def assign(request,id):
    return command(request,'assign',id)

@endpoint(['POST'])
def transitions(request,id):
    return command(request,'transition',id)

@endpoint(['GET','POST'])
def comments(request,id):
    if request.method=='POST':
        return command(request,'comment',id)
    t=s.get_ticket(request.actor,id)
    params=query(request,['limit','cursor'])
    qs=Comment.objects.filter(ticket=t).select_related('author')
    if not s.staff(request.actor,t):
        qs=qs.filter(visibility='PUBLIC')
    return s.page(request.actor,qs,params,s.comment_data,'comments:'+str(id))

@endpoint(['GET'])
def activity(request,id):
    t=s.get_ticket(request.actor,id)
    params=query(request,['limit','cursor'])
    def serialize(h):
        d={'id':str(h.id),'from_status':h.from_status,'to_status':h.to_status,
           'actor':s.person_data(h.actor),'created_at':h.created_at.isoformat()}
        if s.staff(request.actor,t):
            d['reason']=h.reason
        return d
    return s.page(request.actor,StatusHistory.objects.filter(ticket=t).select_related('actor'),params,serialize,'activity:'+str(id))

@endpoint(['POST'])
def resources(request,id):
    return command(request,'attach',id)

@endpoint(['DELETE'])
def resource_delete(request,id,link_id):
    return command(request,'detach',id,link_id)

def resource_read(request,model,id=None):
    qs=s.resources_query(request.actor,model)
    if id:
        obj=qs.filter(id=id).first()
        if not obj:
            s.fail('NOT_FOUND','대상을 찾을 수 없습니다.',404)
        return s.resource_data(obj)
    params=query(request,['q','limit','cursor'])
    if params.get('q'):
        if len(params['q'])>200:
            s.fail('INVALID_QUERY','검색어는 최대 200자입니다.',400)
        qs=qs.filter(name__icontains=params['q'])
    return s.page(request.actor,qs,params,s.resource_data,model.__name__)

@endpoint(['GET'])
def assets(request,id=None):
    return resource_read(request,Asset,id)

@endpoint(['GET'])
def cis(request,id=None):
    return resource_read(request,ConfigurationItem,id)

@endpoint(['GET'])
def access(request):
    p=request.actor
    s.require_admin(p)
    params=query(request,['limit','cursor'])
    def serialize(member):
        return {**s.person_data(member),'active':member.active,'version':member.row_version,'roles':sorted(s.roles(member))}
    return s.page(p,Person.objects.filter(organization=p.organization),params,serialize,'access')

@endpoint(['GET'])
def groups(request):
    p=request.actor
    s.require_admin(p)
    params=query(request,['limit','cursor'])
    def serialize(group):
        return {'id':str(group.id),'name':group.name,'active':group.active,'version':group.row_version,
                'members':[str(x) for x in Membership.objects.filter(group=group).values_list('person_id',flat=True)]}
    return s.page(p,Group.objects.filter(organization=p.organization),params,serialize,'groups')

@endpoint(['PUT'])
def members(request,id,person_id):
    return command(request,'admin_members',id,person_id)

@endpoint(['PUT'])
def grants(request,id):
    return command(request,'admin_roles',id)

@endpoint(['GET','POST'])
def sla_calendars(request):
    from .sla import require_manager,calendar_data
    from .models import BusinessCalendar
    require_manager(request.actor)
    if request.method=='POST':
        return command(request,'sla_calendar')
    params=query(request,['limit','cursor'])
    return s.page(request.actor,BusinessCalendar.objects.filter(organization=request.actor.organization),params,calendar_data,'sla_calendars')

@endpoint(['GET','POST'])
def sla_policies(request):
    from .sla import require_manager,policy_data
    from .models import SLAPolicy
    require_manager(request.actor)
    if request.method=='POST':
        return command(request,'sla_policy')
    params=query(request,['limit','cursor'])
    return s.page(request.actor,SLAPolicy.objects.filter(organization=request.actor.organization),params,policy_data,'sla_policies')

@endpoint(['GET'])
def notifications(request):
    from .sla import visible_notifications,notification_data
    params=query(request,['limit','cursor'])
    qs=visible_notifications(request.actor).select_related('ticket','alert')
    return s.page(request.actor,qs,params,notification_data,'notifications')

@endpoint(['POST'])
def notification_read(request,id):
    return command(request,'notification_read',id)
