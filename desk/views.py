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
    p=s.actor_for(request.user)
    return {'actor':p,'roles':s.roles(p),'org':p.organization,'can_work':bool(s.group_ids(p)) or s.manager(p),
            'is_admin':'ORG_ADMIN' in s.roles(p)}

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
        c.update(item=s.resource_data(item),ci=ci)
        return render(request,'desk/resource-detail.html',c)
    q=request.GET.get('q','')[:200]
    if q:
        qs=qs.filter(name__icontains=q)
    c.update(s.page(c['actor'],qs,request.GET.dict(),s.resource_data,model.__name__))
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
