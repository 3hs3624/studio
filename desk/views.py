from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from . import services as s
from .models import Person, Group, Membership, Asset, ConfigurationItem, Comment, StatusHistory, ROLES

class LocalAccountAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self,user):
        super().confirm_login_allowed(user)
        if not Person.objects.filter(user=user,active=True,organization__active=True).exists():
            raise ValidationError('로그인할 수 없습니다. 계정 상태를 확인하십시오.',code='inactive')

class StudioLoginView(LoginView):
    authentication_form = LocalAccountAuthenticationForm
    def form_valid(self,form):
        from .security_policy import state
        person=Person.objects.get(user=form.get_user())
        if state(person).mfa_secret:
            from .security import evidence
            evidence('MFA_CHALLENGE',person,self.request)
            from django.utils import timezone
            self.request.session['pending_mfa_user']=person.user_id
            self.request.session['pending_mfa_time']=timezone.now().timestamp()
            self.request.session['pending_mfa_next']=self.get_success_url()
            return redirect('/login/mfa/')
        return super().form_valid(form)

def context(request):
    from .sla import visible_notifications
    from .models import RequestApproval
    p=s.actor_for(request.user)
    p._recent_auth=request.session.get('recent_auth_at',0)
    c = {'actor':p,'roles':s.roles(p),'org':p.organization,'can_work':bool(s.group_ids(p)) or s.manager(p),
            'is_admin':'ORG_ADMIN' in s.roles(p),'is_service_manager':s.manager(p),
            'is_asset_manager':'ASSET_MANAGER' in s.roles(p),
            'is_buyer':'PROCUREMENT_MANAGER' in s.roles(p),'is_stock_manager':'STOCK_MANAGER' in s.roles(p),
            'can_purchase_request':bool(s.roles(p)&{'PROCUREMENT_MANAGER','SERVICE_MANAGER'}),
            'can_stock_read':bool(s.roles(p)&{'PROCUREMENT_MANAGER','STOCK_MANAGER'}),
            'can_contract_read':bool(s.roles(p)&{'PROCUREMENT_MANAGER','ASSET_MANAGER'}),
            'pending_approvals':__import__('desk.catalog',fromlist=['pending_approval_requests']).pending_approval_requests(p).count(),
            'unread_notifications':visible_notifications(p).filter(read_at__isnull=True).count()}
    from .navigation import navigation, console_navigation, LEGACY_CONSOLE_PATHS
    from django.conf import settings
    c['delivery_can_read']=s.has_permission(p,'delivery.read')
    c.update(navigation(request.path,c))
    from .security_policy import policy,state
    from django.utils import timezone
    from datetime import timedelta
    security_password=policy(p.organization,'password')
    c['password_notice']=''
    if security_password['max_age_days']:
        days=(state(p).password_changed_at+timedelta(days=security_password['max_age_days'])-timezone.now()).days
        if 0<=days<=security_password['warning_days']:c['password_notice']=str(days)+'일 이내 비밀번호가 만료됩니다. 내 계정 보안에서 변경하십시오.'
    c['can_console'] = s.can_console(p)
    c['can_entity_write'] = s.has_permission(p,'entity.write')
    c['can_plugin_configure'] = s.has_permission(p,'plugin.configure')
    c['can_plugin_execute'] = s.has_permission(p,'plugin.execute')
    c['can_code_write'] = s.has_permission(p,'code.write')
    c['can_users'] = s.has_permission(p,'users.manage')
    c['can_iam'] = s.has_permission(p,'iam.manage')
    c['can_security'] = s.has_permission(p,'security.manage')
    c['console_mode'] = (request.path == '/console' or request.path.startswith('/console/')
                         or request.path.startswith(LEGACY_CONSOLE_PATHS))
    c['base_template'] = 'desk/console-base.html' if c['console_mode'] else 'desk/base.html'
    c['console_groups'] = console_navigation(request.path,c) if c['can_console'] else []
    c['console_environment_key'] = settings.STUDIO_ENVIRONMENT
    c['console_environment_label'] = {'development':'개발 환경','staging':'검증 환경',
        'production':'운영 환경','unspecified':'환경 미지정'}[settings.STUDIO_ENVIRONMENT]
    c['entity_base'] = '/console/entities'
    if c['console_mode']:
        s.require_console(p)
        from .permissions import require
        canonical=request.path.replace('/admin/entities','/console/entities').replace('/admin/plugins','/console/plugins').replace('/admin/access','/console/access')
        for prefix,permission in [('/console/users','users.manage'),('/console/security','security.manage'),('/console/roles','iam.manage'),('/console/groups','iam.manage'),('/console/access','iam.manage'),('/console/entities','entity.read'),('/console/plugins','plugin.read'),('/console/codes','code.read')]:
            if canonical.startswith(prefix):require(p,permission)
        c.update(active_area='console', area_name='운영 콘솔')
    return c

@login_required
def home(request):
    c=context(request)
    from .delivery import overview
    c.update(overview(c['actor']))
    return render(request,'desk/portal.html',c)

@login_required
def listing(request,work=False):
    try:
        c=context(request)
        p=c['actor']
        if work and not c['can_work']:
            return HttpResponse('처리 권한이 없습니다.',status=403)
        qs=s.ticket_query(p,work)
        state=request.GET.get('status','')
        if state:
            qs=qs.filter(status=state)
        c.update(s.page(p,qs,{'scope':'queue' if work else 'mine',**request.GET.dict()},lambda t:s.ticket_data(p,t,False),'incidents'))
        c.update(work=work,selected_status=state,total=qs.count())
        return render(request,'desk/list.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def new_incident(request):
    c=context(request)
    p=c['actor']
    c.update(assets=s.resources_query(p,Asset),cis=s.resources_query(p,ConfigurationItem))
    return render(request,'desk/new.html',c)

@login_required
def detail(request,id,work=False):
    try:
        c=context(request)
        p=c['actor']
        t=s.get_ticket(p,id)
        comments=Comment.objects.filter(ticket=t).select_related('author').order_by('created_at')
        internal=s.staff(p,t)
        if not internal:
            comments=comments.filter(visibility='PUBLIC')
        groups=Group.objects.filter(organization=p.organization,active=True)
        if not s.manager(p):
            groups=groups.filter(id=t.group_id)
        assignments=[]
        for group in groups:
            for membership in Membership.objects.filter(group=group,person__active=True,person__user__is_active=True).select_related('person'):
                if 'AGENT' in s.roles(membership.person):
                    assignments.append({'group_id':str(group.id),'person_id':str(membership.person_id),
                                        'label':group.name+' / '+membership.person.display_name})
        c.update(ticket=s.ticket_data(p,t),comments=comments,internal=internal,assignments=assignments,
                 activity=StatusHistory.objects.filter(ticket=t).select_related('actor').order_by('created_at'),
                 assets=s.resources_query(p,Asset),cis=s.resources_query(p,ConfigurationItem),work=work)
        c['has_transitions']=any(a!='ASSIGN' for a in c['ticket']['allowed_actions'])
        return render(request,'desk/detail.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def inventory(request,ci=False,id=None):
    c=context(request)
    model=ConfigurationItem if ci else Asset
    qs=s.resources_query(c['actor'],model)
    if id:
        item=qs.filter(id=id).first()
        if not item:
            return HttpResponse('대상을 찾을 수 없습니다.',status=404)
        c.update(item=s.resource_data(item,c['actor']),ci=ci)
        return render(request,'desk/resource-detail.html',c)
    q=request.GET.get('q','')[:200]
    if q:
        qs=qs.filter(name__icontains=q)
    c.update(s.page(c['actor'],qs,request.GET.dict(),lambda obj:s.resource_data(obj,c['actor']),model.__name__))
    c.update(ci=ci,q=q)
    return render(request,'desk/resources.html',c)

@login_required
def admin_access(request):
    try:
        c=context(request)
        s.require_admin(c['actor'])
        people=[]
        for p in Person.objects.filter(organization=c['org']).order_by('profile__full_name'):
            people.append({'person':p,'roles':[{'name':r,'checked':r in s.roles(p)} for r in ROLES]})
        from .models import SecurityEvent
        tab = request.GET.get('tab','roles' if request.path.startswith('/console') else 'users')
        labels = [('users','사용자'),('roles','역할·권한'),('groups','담당 그룹'),('accounts','계정·세션'),('history','변경 이력')]
        if request.path.startswith('/console'):labels=[('roles','기본 역할 배정'),('groups','그룹 소속'),('history','변경 이력')]
        if tab not in dict(labels):
            s.fail('NOT_FOUND','탭을 찾을 수 없습니다.',404)
        from .models import AuditEvent
        c.update(active_tab=tab, tabs=[dict(key=key,label=label,url='/console/access?tab='+key) for key,label in labels],
                 access_changes=AuditEvent.objects.filter(organization=c['org'],action__in=['ROLES_CHANGED','MEMBERSHIP_CHANGED','ACCOUNT_CHANGED','SESSIONS_REVOKED','ROLE_DEFINED','ROLE_DELETED','GROUP_DEFINED','GROUP_DELETED','CUSTOM_ROLE_ASSIGNED']).select_related('actor').order_by('-created_at')[:50])
        c.update(people=people,groups=Group.objects.filter(organization=c['org']),
                 security_events=SecurityEvent.objects.filter(organization=c['org']).select_related('person').order_by('-created_at')[:50])
        c['memberships']=[{'group':g,'people':[{'person':item['person'],
                 'checked':Membership.objects.filter(group=g,person=item['person']).exists()} for item in people]} for g in c['groups']]
        return render(request,'desk/access.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def sla_settings(request):
    from .sla import require_manager
    from .models import BusinessCalendar,SLAPolicy
    try:
        c=context(request)
        require_manager(c['actor'])
        c.update(calendars=BusinessCalendar.objects.filter(organization=c['org']).order_by('-created_at'),
                 policies=SLAPolicy.objects.filter(organization=c['org']).select_related('calendar').order_by('priority','-version'))
        return render(request,'desk/sla-settings.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def notifications(request):
    from .sla import visible_notifications,notification_data
    try:
        c=context(request)
        qs=visible_notifications(c['actor']).select_related('ticket','alert')
        c.update(s.page(c['actor'],qs,request.GET.dict(),notification_data,'notifications'))
        return render(request,'desk/notifications.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def catalog_listing(request):
    from . import catalog
    try:
        c=context(request)
        qs=catalog.latest_versions(c['actor'])
        q=request.GET.get('q','')[:200]
        if q:
            qs=qs.filter(name__icontains=q)
        c.update(s.page(c['actor'],qs,request.GET.dict(),catalog.catalog_data,'catalog_items'))
        c['q']=q
        return render(request,'desk/catalog.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def catalog_detail(request,id):
    from . import catalog
    from .models import Ticket
    try:
        c=context(request)
        v=catalog.offering(c['actor'],id)
        previous=None
        if request.GET.get('resubmission_of'):
            previous=Ticket.objects.filter(id=s.identifier(request.GET['resubmission_of']),organization=c['org'],
                type='SERVICE_REQUEST',requested_by=c['actor'],status__in=['REJECTED','CANCELLED'],service_request__catalog_version__item_id=id).first()
            if not previous:
                s.fail('NOT_FOUND','재신청할 요청을 찾을 수 없습니다.',404)
        values=previous.service_request.values if previous else {}
        fields=[{**f,'value':values.get(f['key'],'')} for f in v.fields]
        c.update(offering=catalog.catalog_data(v),form_fields=fields,resubmission_of=str(previous.id) if previous else '')
        return render(request,'desk/catalog-detail.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def request_listing(request,work=False,approvals=False):
    from . import catalog
    from .models import REQUEST_STATUSES
    try:
        c=context(request)
        if work and not c['can_work']:
            s.fail('FORBIDDEN','처리 권한이 없습니다.',403)
        qs=catalog.request_query(c['actor'],'visible' if c['is_admin'] and not work else 'queue' if work else 'mine')
        if approvals:
            qs=catalog.pending_approval_requests(c['actor'])
        state=request.GET.get('status','')
        if state:
            if state not in REQUEST_STATUSES:
                s.fail('INVALID_STATUS','요청 상태를 확인하십시오.',400)
            qs=qs.filter(status=state)
        c.update(s.page(c['actor'],qs,request.GET.dict(),lambda t:catalog.request_data(c['actor'],t,False),'approvals' if approvals else 'request_queue' if work else 'requests'))
        c.update(work=work,approvals=approvals,selected_status=state,states=REQUEST_STATUSES)
        return render(request,'desk/request-list.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def request_detail(request,id):
    from . import catalog
    try:
        c=context(request)
        p=c['actor'];t=catalog.get_request(p,id)
        data=catalog.request_data(p,t)
        answers=[]
        for field in data['fields']:
            value=data['values'].get(field['key'],'—')
            if type(value) is bool:
                value='예' if value else '아니오'
            answers.append({'label':field['label'],'value':value})
        comments=Comment.objects.filter(ticket=t).select_related('author').order_by('created_at')
        if not catalog.request_staff(p,t):
            comments=comments.filter(visibility='PUBLIC')
        assignments=[]
        if data['can_assign']:
            for member in Membership.objects.filter(group=t.group,group__active=True,person__active=True,person__user__is_active=True).select_related('person'):
                if 'AGENT' in s.roles(member.person):
                    assignments.append(member.person)
        c.update(ticket=data,answers=answers,comments=comments,assignments=assignments,
                 activity=StatusHistory.objects.filter(ticket=t).select_related('actor').order_by('created_at'))
        from .assets import manager as asset_manager, query as asset_query
        c['can_issue_asset']=asset_manager(p) and catalog.request_staff(p,t) and t.status=='IN_PROGRESS'
        if c['can_issue_asset']:
            c['stock_assets']=asset_query(p).filter(status='STOCK')
            if 'STOCK_MANAGER' not in s.roles(p): c['stock_assets']=c['stock_assets'].filter(stock_record__isnull=True)
        return render(request,'desk/request-detail.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def catalog_manage(request):
    from . import catalog
    from .models import CatalogVersion
    try:
        c=context(request)
        catalog.require_manager(c['actor'])
        c.update(groups=Group.objects.filter(organization=c['org'],active=True),
                 people=Person.objects.filter(organization=c['org'],active=True,user__is_active=True),
                 versions=CatalogVersion.objects.filter(organization=c['org']).select_related('item').order_by('item__code','-version'),
                 version_map={v.item.code:v.version for v in catalog.latest_versions(c['actor'],False)})
        from .process_views import versions as process_versions
        from .models import ProcessBinding
        c.update(workflow_versions=process_versions(c['actor'],'WORKFLOW'),workflow_binding=ProcessBinding.objects.filter(organization=c['org'],menu_key='service-request').select_related('version__definition').first())
        return render(request,'desk/catalog-manage.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)


@login_required
def system_home(request,system):
    from .navigation import SYSTEMS
    from .catalog import request_query
    from . import assets
    c=context(request);p=c['actor']
    c['system']=next(x for x in SYSTEMS if x['key']==system)
    if system=='service':
        incidents=s.ticket_query(p,c['can_work'])
        requests=request_query(p,'queue' if c['can_work'] else 'mine')
        c.update(metrics=[{'label':'진행 중 장애','value':incidents.exclude(status__in=['RESOLVED','CLOSED']).count(),'url':'/work/incidents' if c['can_work'] else '/portal/incidents'},
            {'label':'진행 중 서비스 요청','value':requests.exclude(status__in=['FULFILLED','CLOSED','REJECTED','CANCELLED']).count(),'url':'/work/requests' if c['can_work'] else '/portal/requests'},
            {'label':'내 승인 대기','value':c['pending_approvals'],'url':'/approvals'}],
            recent_items=[{'title':t.title,'number':t.number,'status':t.status,'url':('/work/incidents/' if c['can_work'] else '/portal/incidents/')+str(t.id)} for t in incidents.order_by('-created_at')[:6]],recent_title='최근 장애 요청',
            primary_url='/catalog',primary_label='서비스 요청하기')
    elif system=='asset':
        qs=assets.query(p)
        c.update(metrics=[{'label':'조회 가능한 자산','value':qs.count(),'url':'/assets'},
            {'label':'사용 중 자산','value':qs.filter(status='IN_USE').count(),'url':'/assets?status=IN_USE'},
            {'label':'내 지급 자산','value':qs.filter(custodian=p).count(),'url':'/my-assets'}],
            recent_items=[{'title':a.name,'number':a.asset_no,'status':a.status,'url':'/assets/'+str(a.id)} for a in qs.order_by('-created_at')[:6]],recent_title='최근 등록 자산',
            primary_url='/assets/new' if c['is_asset_manager'] else '/my-assets',primary_label='자산 등록' if c['is_asset_manager'] else '내 지급 자산')
    else:
        from .delivery import overview
        c.update(overview(p))
        return render(request,'desk/delivery-home.html',c)
    from .menu_access import path_allowed
    c['metrics']=[metric for metric in c['metrics'] if path_allowed(p,metric['url'])]
    c['recent_items']=[item for item in c['recent_items'] if path_allowed(p,item['url'])]
    if not path_allowed(p,c['primary_url']):c.update(primary_url='/',primary_label='통합 홈')
    labels={'NEW':'신규','ASSIGNED':'배정','IN_PROGRESS':'처리 중','PENDING':'대기','RESOLVED':'해결','CLOSED':'종료','UNVERIFIED':'미검증','STOCK':'보관','IN_USE':'사용 중','RETIRED':'폐기','ACTIVE':'운영 중','INACTIVE':'비활성'}
    for item in c['recent_items']: item['status_label']=labels.get(item['status'],item['status'])
    return render(request,'desk/system-home.html',c)


@login_required
def plugin_management(request, plugin_id=None):
    from .plugin_service import catalog, definition
    from .models import PluginRun, NumberIssue, PluginFailure, AuditEvent
    try:
        c = context(request)
        items = catalog(c['actor'])
        for item in items:
            item['last_run'] = PluginRun.objects.filter(organization=c['org'],plugin_id=item['manifest']['plugin_id']).order_by('-created_at').first()
        tab = request.GET.get('tab', 'overview')
        tabs = [('overview','개요'),('settings','설정'),('test','실행 테스트'),('runs','실행 이력'),('changes','변경 이력')]
        if tab not in dict(tabs):
            s.fail('NOT_FOUND','탭을 찾을 수 없습니다.',404)
        selected = None
        if plugin_id:
            definition(plugin_id)
            selected = next(item for item in items if item['manifest']['plugin_id']==plugin_id)
            binding = selected['binding']
            configuration = binding['configuration'] if binding else {}
            selected['version'] = binding['version'] if binding else 0
            labels = {'reset':{'never':'초기화 없음','year':'연별','month':'월별','day':'일별'}, 'date_format':{'NONE':'날짜 없음'}, 'separator':{'':'없음'}}
            selected['settings'] = [{**field,'value':configuration.get(field['key'],field.get('default','')),
                'choices':[dict(value=option,label=labels.get(field['key'],{}).get(option,option)) for option in field.get('options',[])]}
                for field in selected['manifest']['settings_fields']]
        runs = PluginRun.objects.filter(organization=c['org']).select_related('actor')
        if plugin_id:
            runs = runs.filter(plugin_id=plugin_id)
        events = []
        for run in runs.order_by('-created_at','-id')[:50]:
            issue = NumberIssue.objects.filter(run=run).first()
            events.append(dict(created_at=run.created_at, actor=run.actor.display_name,
                operation='실제 발급' if issue else '미리보기', status='성공', detail=issue.value if issue else f'{run.input_length} / {run.output_length} 글자', version=run.binding_version))
        failures = PluginFailure.objects.filter(organization=c['org']).select_related('actor','binding')
        if plugin_id:
            failures = failures.filter(binding__plugin_id=plugin_id)
        events += [dict(created_at=f.created_at,actor=f.actor.display_name, operation='실제 발급' if f.operation=='plugin_issue' else '미리보기',status='실패',detail=f.error_code,version=f.binding_version) for f in failures.order_by('-created_at')[:50]]
        changes = AuditEvent.objects.filter(organization=c['org'],action='PLUGIN_CONFIGURED')
        if selected and selected['binding']:
            changes = changes.filter(entity_id=selected['binding']['id'])
        elif plugin_id:
            changes = changes.none()
        c.update(plugins=items, plugin=selected, active_tab=tab,
                 tabs=[dict(key=key,label=label,url=f'/console/plugins/{plugin_id}?tab={key}') for key,label in tabs],
                 plugin_events=sorted(events,key=lambda e:e['created_at'],reverse=True)[:50],
                 plugin_changes=changes.select_related('actor').order_by('-created_at')[:50])
        return render(request, 'desk/plugins.html', c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message, status=exc.status)


@login_required
def entity_management(request, id=None):
    from .models import EntityDefinition, EntityRecord
    from .entity_service import get_entity, entity_data, latest
    from .entities.system_fields import system_fields, RELATIONSHIPS, multiple
    from .entities.fields import FIELD_TYPES
    try:
        c = context(request)
        actor = c['actor']
        s.require_console(actor)
        entity = get_entity(actor, id) if id else None
        schema = latest(entity) if entity else None
        targets = EntityDefinition.objects.filter(organization=actor.organization, schema_versions__isnull=False).distinct().order_by('code')[:100]
        schema_fields = []
        if schema:
            for field in schema.fields:
                item = dict(field)
                if field['type']=='choice':
                    if field.get('code_group_id'):
                        from .models import CommonCodeItem
                        item['choice_options'] = [dict(value=code.code,label=code.label) for code in CommonCodeItem.objects.filter(organization=actor.organization,group_id=field['code_group_id'],group__active=True,active=True)]
                    else:
                        item['choice_options'] = [dict(value=value,label=value) for value in field['options']]
                if field['type'] == 'reference':
                    item['multiple'] = multiple(field)
                    choices = __import__('desk.entity_service',fromlist=['records_query']).records_query(actor).filter(
                        organization=actor.organization, entity_id=field['target_entity_id']).select_related('schema_version').order_by('-created_at')[:100]
                    item['reference_choices'] = [
                        {'id':record.id, 'label':next((str(value)[:100] for value in record.values.values()
                                                      if isinstance(value, str) and value.strip()), str(record.id))}
                        for record in choices]
                schema_fields.append(item)
        records = []
        if entity:
            for record in __import__('desk.entity_service',fromlist=['records_query']).records_query(actor).filter(organization=actor.organization, entity=entity).select_related('schema_version').order_by('-created_at','-id')[:20]:
                lines = []
                for field in record.schema_version.fields:
                    value = record.values.get(field['key'])
                    if field['type'] == 'reference' and isinstance(value, list):
                        related = __import__('desk.entity_service',fromlist=['records_query']).records_query(actor).filter(id__in=value, organization=actor.organization,
                                                              entity_id=field['target_entity_id'])
                        labels = {str(item.id): next((str(v) for v in item.values.values() if isinstance(v, str) and v.strip()), str(item.id)) for item in related}
                        value = ', '.join(labels.get(item, item) for item in value)
                    elif field['type'] == 'reference' and value:
                        related = __import__('desk.entity_service',fromlist=['records_query']).records_query(actor).filter(id=value, organization=actor.organization,
                            entity_id=field['target_entity_id']).first()
                        if related:
                            value = next((str(v) for v in related.values.values()
                                          if isinstance(v, str) and v.strip()), str(related.id))
                    elif field['type']=='choice' and field.get('code_group_id') and value:
                        from .models import CommonCodeItem
                        label = CommonCodeItem.objects.filter(organization=actor.organization,group_id=field['code_group_id'],code=value).first()
                        value = label.label if label else value
                    elif type(value) is bool:
                        value = '예' if value else '아니오'
                    lines.append(field['label'] + ': ' + (str(value) if value is not None else '—'))
                records.append({'id':record.id, 'version':record.schema_version.version,
                                'values':'\n'.join(lines), 'created_at':record.created_at,
                                'created_by':record.created_by.display_name, 'updated_at':record.updated_at,
                                'updated_by':record.updated_by.display_name, 'row_version':record.row_version,
                                'links': [dict(direction='→', field=link.field_key, label=next((str(v)[:100] for v in link.target.values.values() if isinstance(v, str) and v.strip()), str(link.target_id))) for link in record.outgoing_links.select_related('target')]
                                + [dict(direction='←', field=link.field_key, label=next((str(v)[:100] for v in link.source.values.values() if isinstance(v, str) and v.strip()), str(link.source_id))) for link in record.incoming_links.select_related('source')]})
        from .models import CommonCodeGroup
        c.update(code_groups=CommonCodeGroup.objects.filter(organization=actor.organization).order_by('code'),
                 show_editor=bool(entity or request.GET.get('new') == '1'), system_fields=system_fields(),
                 relationships=[{'key':key, 'label':label} for key,label in RELATIONSHIPS.items()],
                 entity=entity, entity_info=entity_data(entity) if entity else None,
                 draft_fields=entity.draft_fields if entity else [], schema=schema,
                 schema_fields=schema_fields, records=records, targets=targets,
                 field_types=[{'key':key,'label':value[0]} for key,value in FIELD_TYPES.items()],
                 entity_list=EntityDefinition.objects.filter(organization=actor.organization).order_by('code')[:100],
                 history=entity.schema_versions.order_by('-version')[:20] if entity else [])
        return render(request, 'desk/entities.html', c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message, status=exc.status)


@login_required
def console_home(request):
    try:
        c = context(request)
        if not c['can_console']:
            s.fail('FORBIDDEN', '운영 콘솔 접근 권한이 없습니다.', 403)
        return render(request, 'desk/console-home.html', c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message, status=exc.status)


@login_required
def common_code_management(request, id=None):
    from .common_codes import group, data, uses
    from .models import CommonCodeGroup, AuditEvent
    try:
        c = context(request)
        s.require_console(c['actor'])
        value = group(c['actor'], id) if id else None
        c.update(code_groups=CommonCodeGroup.objects.filter(organization=c['org']).order_by('code'),
                 code_group=value, code_data=data(value) if value else None,
                 code_usage=uses(c['actor'], value) if value else [],
                 code_changes=AuditEvent.objects.filter(organization=c['org'],action='COMMON_CODE_CHANGED',entity_id=id).select_related('actor').order_by('-created_at')[:30] if id else [])
        return render(request, 'desk/codes.html', c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)
