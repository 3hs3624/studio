from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from . import services as s
from .models import Person, Group, Membership, Asset, ConfigurationItem, Comment, StatusHistory, ROLES

class StudioLoginView(LoginView):
    """Local process throttle; shared edge throttling is required for multi-worker deployments."""
    def post(self,request,*args,**kwargs):
        key='login:'+request.META.get('REMOTE_ADDR','unknown')
        attempts=cache.get(key,0)
        if attempts>=10:
            return HttpResponse('로그인 시도가 많습니다. 잠시 후 다시 시도하십시오.',status=429)
        cache.set(key,attempts+1,300)
        result=super().post(request,*args,**kwargs)
        if result.status_code==302:
            cache.delete(key)
        return result

def context(request):
    from .sla import visible_notifications
    from .models import RequestApproval
    p=s.actor_for(request.user)
    return {'actor':p,'roles':s.roles(p),'org':p.organization,'can_work':bool(s.group_ids(p)) or s.manager(p),
            'is_admin':'ORG_ADMIN' in s.roles(p),'is_service_manager':s.manager(p),
            'is_asset_manager':'ASSET_MANAGER' in s.roles(p),
            'is_buyer':'PROCUREMENT_MANAGER' in s.roles(p),'is_stock_manager':'STOCK_MANAGER' in s.roles(p),
            'can_purchase_request':bool(s.roles(p)&{'PROCUREMENT_MANAGER','SERVICE_MANAGER'}),
            'can_stock_read':bool(s.roles(p)&{'PROCUREMENT_MANAGER','STOCK_MANAGER'}),
            'can_contract_read':bool(s.roles(p)&{'PROCUREMENT_MANAGER','ASSET_MANAGER'}),
            'pending_approvals':RequestApproval.objects.filter(organization=p.organization,approver=p,status='PENDING',ticket__status='PENDING_APPROVAL').count(),
            'unread_notifications':visible_notifications(p).filter(read_at__isnull=True).count()}

@login_required
def home(request):
    return redirect('/portal/incidents')

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
        for p in Person.objects.filter(organization=c['org']).order_by('display_name'):
            people.append({'person':p,'roles':[{'name':r,'checked':r in s.roles(p)} for r in ROLES]})
        c.update(people=people,groups=Group.objects.filter(organization=c['org']))
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
        qs=catalog.request_query(c['actor'],'queue' if work else 'mine')
        if approvals:
            qs=catalog.request_query(c['actor']).filter(request_approval__approver=c['actor'],request_approval__status='PENDING',status='PENDING_APPROVAL')
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
        return render(request,'desk/catalog-manage.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)
