from types import SimpleNamespace
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from . import services as s
from .views import context
from .permissions import BUILTIN,require
from .models import (Person,Department,Group,Membership,GroupDepartment,RoleDefinition,RoleGrant,CustomRoleGrant,ScopedRoleGrant,RoleMenuPolicy,AuditEvent,PrivacyAccessEvent)
from .access_graph import departments_tree,role_rows,effective_groups
from .menu_access import MENUS,role_menus
from .organization_management import preview,department


def catalog(actor):
    from .templatetags.desk_tags import role_label
    return [dict(key=key,name='기본 사용자' if key=='EVERYONE' else role_label(key),system=True) for key in BUILTIN]+[dict(key=str(role.id),name=role.name,system=False) for role in RoleDefinition.objects.filter(organization=actor.organization,active=True).order_by('name')]


@login_required
def access(request):
    try:
        c=context(request);actor=c['actor'];require(actor,'iam.manage')
        tab=request.GET.get('tab','roles')
        labels=[('roles','역할'),('groups','그룹'),('menus','메뉴·운영콘솔 권한'),('departments','부서 관리'),('history','변경 이력')]
        if tab not in dict(labels):s.fail('NOT_FOUND','탭을 찾을 수 없습니다.',404)
        from .identity_views import tabs
        c.update(**tabs('/console/access',tab,labels),org_version=actor.organization.access_version,
            access_roles=catalog(actor),access_people=Person.objects.filter(organization=actor.organization,active=True,user__is_active=True).select_related('user','profile','department').order_by('profile__full_name'),
            access_groups=Group.objects.filter(organization=actor.organization,active=True).order_by('name'),departments=departments_tree(actor.organization))
        selected=request.GET.get('selected','')
        if tab in ('roles','menus'):
            key=selected or c['access_roles'][0]['key'];row=next((r for r in c['access_roles'] if r['key']==key),None)
            if not row:s.fail('NOT_FOUND','역할을 찾을 수 없습니다.',404)
            c['selected_role']=row
            direct=set(str(x) for x in (RoleGrant.objects.filter(organization=actor.organization,role=key).values_list('person_id',flat=True) if key in BUILTIN else CustomRoleGrant.objects.filter(organization=actor.organization,role_id=key,active=True).values_list('person_id',flat=True)))
            scoped=ScopedRoleGrant.objects.filter(organization=actor.organization,role_key=key)
            c.update(selected_people=direct,selected_departments=set(str(x) for x in scoped.exclude(department=None).values_list('department_id',flat=True)),selected_groups=set(str(x) for x in scoped.exclude(group=None).values_list('group_id',flat=True)),include_children=scoped.filter(include_children=True).exists())
            keys,button=role_menus(actor.organization,key)
            from .data_access import SUPPORTED,SCOPES
            from .models import RoleDataPolicy
            rules={r.menu_key:r for r in RoleDataPolicy.objects.filter(organization=actor.organization,role_key=key)}
            c.update(menu_options=[dict(key=k,label=v[0],checked=k in keys,scoped=k in SUPPORTED,read_scope=rules[k].read_scope if k in rules else 'LEGACY',write_scope=rules[k].write_scope if k in rules else 'LEGACY') for k,v in MENUS.items()],scope_options=SCOPES.items(),console_button=button)
        elif tab=='groups':
            group=c['access_groups'].filter(id=s.identifier(selected)).first() if selected else c['access_groups'].first()
            if selected and not group:s.fail('NOT_FOUND','그룹을 찾을 수 없습니다.',404)
            c.update(selected_group=group)
            if group:
                links=GroupDepartment.objects.filter(group=group,organization=actor.organization)
                c.update(selected_people=set(str(x) for x in Membership.objects.filter(group=group).values_list('person_id',flat=True)),selected_departments=set(str(x) for x in links.values_list('department_id',flat=True)),include_children=links.filter(include_children=True).exists())
        elif tab=='departments':
            dep=department(actor,selected) if selected and selected!='new' else None
            c.update(selected_department=dep,new_department=selected=='new')
            if dep:
                proxy=SimpleNamespace(id=None,department_id=dep.id,organization=actor.organization,organization_id=actor.organization_id)
                c.update(department_roles=[r for r in role_rows(proxy) if r['key']!='EVERYONE'],department_groups=list(effective_groups(proxy).values()),department_people=Person.objects.filter(organization=actor.organization,department=dep).select_related('profile','user'))
        else:c['organization_history']=AuditEvent.objects.filter(organization=actor.organization).filter(action__startswith='ORGANIZATION_').select_related('actor').order_by('-created_at')[:100]
        return render(request,'desk/organization-access.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)


@login_required
def copy_preview(request):
    from .api import error
    try:
        if request.method!='GET':s.fail('METHOD_NOT_ALLOWED','조회 요청만 허용됩니다.',405)
        actor=s.actor_for(request.user);actor._recent_auth=request.session.get('recent_auth_at',0)
        data=preview(actor,request.GET.get('kind'),request.GET.get('id'))
        response=JsonResponse(data);response['Cache-Control']='no-store, private';return response
    except s.BusinessError as exc:return error(request,exc.code,exc.message,exc.status)


@login_required
def my_profile(request):
    from .privacy import mask
    actor=s.actor_for(request.user)
    PrivacyAccessEvent.objects.create(organization=actor.organization,actor=actor,subject=actor,action='SELF_VIEW',request_id=request.request_id)
    response=JsonResponse(dict(name=actor.display_name,username=actor.user.username,department=actor.department.name if actor.department_id else '미지정',email=mask(actor.profile.email),phone=mask(actor.profile.phone),roles=role_rows(actor),groups=[dict(name=g['group'].name,paths=g['paths']) for g in effective_groups(actor).values()]))
    response['Cache-Control']='no-store, private';return response
