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
                from .security import SESSION_KEY
                request.actor._session_binding=request.session.get(SESSION_KEY,'')
                request.actor._recent_auth=request.session.get('recent_auth_at',0)
                request.actor._request_context=request
                from django.conf import settings
                request.actor._proxy_unverified=bool(request.META.get('HTTP_X_FORWARDED_FOR') and not settings.SECURITY_TRUSTED_PROXY_CIDRS)
                from .permissions import require
                for prefix,read,write in [('/api/v1/admin/entities','entity.read','entity.write'),('/api/v1/admin/code-groups','code.read','code.write')]:
                    if request.path.startswith(prefix):require(request.actor,read if request.method=='GET' else write)
                if request.path.startswith('/api/v1/admin/plugins') or request.path.startswith('/api/v1/admin/plugin-runs'):
                    require(request.actor,'plugin.read' if request.method=='GET' else 'plugin.configure' if request.path.endswith('/configuration') else 'plugin.execute')
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
    if operation.startswith('admin_'):
        from .security_policy import require_recent
        require_recent(request.actor)
    data=body(request) if request.method!='DELETE' else {'expected_version':parse_version(request.GET.get('expected_version'))}
    if request.method=='DELETE':
        query(request,['expected_version'])
    result,status=s.execute(request.actor,operation,data,request.headers.get('Idempotency-Key'),
                            request.request_id,target,subtarget)
    response=HttpResponse(status=204) if status==204 else JsonResponse(result,status=status)
    if operation=='create':
        response['Location']='/api/v1/incidents/'+result['id']
    if operation=='req_create':
        response['Location']='/api/v1/requests/'+result['id']
    if operation=='asset_create':
        response['Location']='/api/v1/assets/'+result['id']
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
        return s.resource_data(obj,request.actor)
    params=query(request,['q','limit','cursor'])
    if params.get('q'):
        if len(params['q'])>200:
            s.fail('INVALID_QUERY','검색어는 최대 200자입니다.',400)
        qs=qs.filter(name__icontains=params['q'])
    return s.page(request.actor,qs,params,lambda obj:s.resource_data(obj,request.actor),model.__name__)

@endpoint(['GET','POST','PUT'])
def assets(request,id=None):
    if request.method=='POST' and id is None:
        return command(request,'asset_create')
    if request.method=='PUT' and id:
        return command(request,'asset_update',id)
    if request.method!='GET':
        response=error(request,'METHOD_NOT_ALLOWED','허용되지 않은 메서드입니다.',405)
        response['Allow']='GET, PUT' if id else 'GET, POST'
        return response
    if id is None:
        from .models import ASSET_STATUSES
        params=query(request,['q','status','limit','cursor'])
        if params.get('status') and params['status'] not in ASSET_STATUSES:
            s.fail('INVALID_STATUS','자산 상태를 확인하십시오.',400)
        qs=s.resources_query(request.actor,Asset)
        if params.get('status'):
            qs=qs.filter(status=params['status'])
        if params.get('q'):
            if len(params['q'])>200:
                s.fail('INVALID_QUERY','검색어는 최대 200자입니다.',400)
            qs=qs.filter(Q(name__icontains=params['q'])|Q(asset_no__icontains=params['q']))
        return s.page(request.actor,qs,params,lambda a:s.resource_data(a,request.actor),'Asset')
    return resource_read(request,Asset,id)

@endpoint(['POST'])
def asset_actions(request,id):
    return command(request,'asset_action',id)

@endpoint(['GET'])
def asset_history(request,id):
    from . import assets as service
    params=query(request,['limit','cursor'])
    qs=service.history_query(request.actor,id)
    if not service.full_reader(request.actor) and not qs.exists():
        s.fail('NOT_FOUND','자산 이력을 찾을 수 없습니다.',404)
    if service.full_reader(request.actor):
        service.get_asset(request.actor,id)
    return s.page(request.actor,qs,params,lambda h:service.history_data(h,request.actor),'asset_history:'+str(id))

@endpoint(['GET'])
def my_assets(request):
    params=query(request,['limit','cursor'])
    qs=Asset.objects.filter(organization=request.actor.organization,custodian=request.actor).select_related('custodian')
    return s.page(request.actor,qs,params,lambda a:s.resource_data(a,request.actor),'my_assets')

@endpoint(['GET'])
def my_asset_history(request):
    from . import assets as service
    params=query(request,['limit','cursor'])
    qs=service.history_query(request.actor,personal=True)
    return s.page(request.actor,qs,params,lambda h:service.history_data(h,request.actor,True),'my_asset_history')

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

@endpoint(['GET'])
def catalog_items(request,id=None):
    from . import catalog
    if id:
        return catalog.catalog_data(catalog.offering(request.actor,id))
    params=query(request,['limit','cursor','q'])
    qs=catalog.latest_versions(request.actor)
    if params.get('q'):
        if len(params['q'])>200:
            s.fail('INVALID_QUERY','검색어는 최대 200자입니다.',400)
        qs=qs.filter(name__icontains=params['q'])
    return s.page(request.actor,qs,params,catalog.catalog_data,'catalog_items')

@endpoint(['GET','POST'])
def catalog_versions(request):
    from . import catalog
    from .models import CatalogVersion
    catalog.require_manager(request.actor)
    if request.method=='POST':
        return command(request,'catalog_publish')
    params=query(request,['limit','cursor'])
    qs=CatalogVersion.objects.filter(organization=request.actor.organization).select_related('item')
    return s.page(request.actor,qs,params,lambda v:catalog.catalog_data(v,True),'catalog_versions')

@endpoint(['GET','POST'])
def service_requests(request):
    from . import catalog
    from .models import REQUEST_STATUSES
    if request.method=='POST':
        return command(request,'req_create')
    params=query(request,['scope','status','limit','cursor'])
    scope=params.get('scope','mine')
    if scope not in ('mine','queue'):
        s.fail('INVALID_SCOPE','scope는 mine 또는 queue입니다.',400)
    qs=catalog.request_query(request.actor,scope)
    if params.get('status'):
        if params['status'] not in REQUEST_STATUSES:
            s.fail('INVALID_STATUS','요청 상태를 확인하십시오.',400)
        qs=qs.filter(status=params['status'])
    return s.page(request.actor,qs,params,lambda t:catalog.request_data(request.actor,t,False),'service_requests')

@endpoint(['GET'])
def service_request(request,id):
    from . import catalog
    return catalog.request_data(request.actor,catalog.get_request(request.actor,id))

@endpoint(['POST'])
def request_assignment(request,id):
    return command(request,'req_assign',id)

@endpoint(['POST'])
def request_action(request,id):
    return command(request,'req_action',id)

@endpoint(['POST'])
def request_decision(request,id):
    return command(request,'req_decision',id)

@endpoint(['GET','POST'])
def request_comments(request,id):
    from . import catalog
    if request.method=='POST':
        return command(request,'req_comment',id)
    t=catalog.get_request(request.actor,id)
    params=query(request,['limit','cursor'])
    qs=Comment.objects.filter(ticket=t).select_related('author')
    if not catalog.request_staff(request.actor,t):
        qs=qs.filter(visibility='PUBLIC')
    return s.page(request.actor,qs,params,s.comment_data,'request_comments:'+str(id))

@endpoint(['GET'])
def approvals(request):
    from . import catalog
    params=query(request,['limit','cursor'])
    qs=catalog.request_query(request.actor).filter(request_approval__approver=request.actor,
                      request_approval__status='PENDING',status='PENDING_APPROVAL')
    return s.page(request.actor,qs,params,lambda t:catalog.request_data(request.actor,t,False),'approvals')


@endpoint(['POST'])
def account_state(request,id):
    return command(request,'admin_account',id)

@endpoint(['POST'])
def revoke_sessions(request,id):
    return command(request,'admin_revoke_sessions',id)

@endpoint(['GET'])
def security_events(request):
    from .models import SecurityEvent
    s.require_admin(request.actor)
    params=query(request,['limit','cursor'])
    return s.page(request.actor,SecurityEvent.objects.filter(organization=request.actor.organization).select_related('person'),
        params,lambda e:{'id':str(e.id),'action':e.action,'person':s.person_data(e.person) if e.person else None,
                        'created_at':e.created_at.isoformat(),'request_id':str(e.request_id)},'security_events')


@endpoint(['GET'])
def plugins(request):
    from .plugin_service import catalog
    query(request, [])
    return {'items':catalog(request.actor)}


@endpoint(['POST'])
def plugin_configuration(request, plugin_id):
    return command(request, 'plugin_configure', plugin_id)


@endpoint(['POST'])
def plugin_preview(request, plugin_id):
    return plugin_command(request, 'plugin_preview', plugin_id)


@endpoint(['GET'])
def plugin_runs(request):
    from .models import PluginRun
    s.require_console(request.actor)
    query(request, [])
    runs = PluginRun.objects.filter(organization=request.actor.organization).order_by('-created_at', '-id')[:50]
    return {'items':[dict(id=str(run.id), plugin_id=run.plugin_id, plugin_version=run.plugin_version,
                         manifest_digest=run.manifest_digest, binding_version=run.binding_version,
                         input_length=run.input_length, output_length=run.output_length,
                         actor_id=str(run.actor_id), created_at=run.created_at.isoformat()) for run in runs]}


@endpoint(['GET','POST'])
def entities(request):
    from .models import EntityDefinition
    from .entity_service import entity_data
    if request.method == 'POST':
        return command(request, 'entity_save')
    s.require_console(request.actor)
    query(request, [])
    return {'items':[entity_data(e) for e in EntityDefinition.objects.filter(
        organization=request.actor.organization).order_by('code')[:100]]}


@endpoint(['GET'])
def entity_definition(request, id):
    from .entity_service import get_entity, entity_data, schema_data
    s.require_console(request.actor)
    query(request, [])
    entity = get_entity(request.actor, id)
    return {**entity_data(entity), 'history':[schema_data(v) for v in entity.schema_versions.order_by('-version')[:50]]}


@endpoint(['POST'])
def entity_publish(request, id):
    return command(request, 'entity_publish', id)


@endpoint(['GET','POST'])
def entity_records(request, id):
    from .models import EntityRecord
    from .entity_service import get_entity, record_data
    if request.method == 'POST':
        return command(request, 'entity_record', id)
    s.require_console(request.actor)
    query(request, [])
    entity = get_entity(request.actor, id)
    return {'items':[record_data(r) for r in EntityRecord.objects.filter(
        organization=request.actor.organization, entity=entity).select_related('schema_version').order_by('-created_at','-id')[:50]]}


@endpoint(['GET'])
def entity_record_relations(request, id, record_id):
    from .entity_service import get_entity, related_data
    s.require_console(request.actor)
    query(request, [])
    return related_data(request.actor, get_entity(request.actor, id), record_id)


def plugin_command(request, operation, plugin_id):
    from hashlib import sha256
    from .models import PluginBinding, PluginFailure
    from .plugin_service import definition
    s.require_console(request.actor)
    definition(plugin_id)
    try:
        return command(request, operation, plugin_id)
    except s.BusinessError as exc:
        key = request.headers.get('Idempotency-Key', '')
        binding = PluginBinding.objects.filter(organization=request.actor.organization, plugin_id=plugin_id).first()
        if binding and key and len(key) <= 128 and exc.code not in ('FORBIDDEN', 'SESSION_REVOKED'):
            PluginFailure.objects.get_or_create(organization=request.actor.organization, actor=request.actor,
                binding=binding, operation=operation, key_digest=sha256(key.encode()).hexdigest(),
                defaults=dict(error_code=exc.code, binding_version=binding.row_version, request_id=request.request_id))
        raise


@endpoint(['POST'])
def plugin_issue(request, plugin_id):
    return plugin_command(request, 'plugin_issue', plugin_id)


@endpoint(['GET','POST'])
def common_code_groups(request):
    from .models import CommonCodeGroup
    from .common_codes import data
    if request.method == 'POST':
        return command(request, 'code_group')
    s.require_console(request.actor)
    query(request, [])
    return {'items':[data(value) for value in CommonCodeGroup.objects.filter(organization=request.actor.organization).order_by('code')[:100]]}


@endpoint(['GET','POST'])
def common_code_group(request, id):
    from .common_codes import group, data, uses
    if request.method == 'POST':
        return command(request, 'code_group', id)
    s.require_console(request.actor)
    query(request, [])
    value = group(request.actor, id)
    return {**data(value), 'usage':uses(request.actor, value)}


@endpoint(['POST'])
def common_code_items(request, id):
    return command(request, 'code_items', id)


@endpoint(['POST'])
def identity_command(request,kind,id=None):
    commands={'users':'user_create' if id is None else 'user_save','roles':'role_save','groups':'group_save',
              'role-delete':'role_delete','role-grant':'role_grant','group-delete':'group_delete',
              'user-reset':'user_reset','user-unlock':'user_unlock','user-invite':'user_invite',
              'user-mfa-reset':'user_mfa_reset','user-session':'user_session','user-erase':'user_erase', 'policies':'policy_save','policy-preview':'policy_preview'}
    if kind not in commands:s.fail('NOT_FOUND','관리 작업을 찾을 수 없습니다.',404)
    response=command(request,'manage_'+commands[kind],id)
    if kind=='user-invite' and response.status_code==200:
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from .identity_management import person
        member=person(request.actor,id)
        value=json.loads(response.content)
        value['invitation_url']=request.build_absolute_uri('/activate/'+urlsafe_base64_encode(force_bytes(member.user_id))+'/#'+default_token_generator.make_token(member.user))
        return value
    return response
