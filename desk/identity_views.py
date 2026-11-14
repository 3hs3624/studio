from types import SimpleNamespace
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from . import services as s
from .views import context
from .permissions import require,PERMISSIONS,BUILTIN
from .identity_management import person,role,group
from .privacy import mask
from .security_policy import FIELDS,LABELS,policy,state,require_recent
from .models import (Person,Group,RoleGrant,RoleDefinition,CustomRoleGrant,Membership,PrivacyAccessEvent,AuditEvent,LoginSession,SecurityPolicy,SecurityEvent,UserProfile,Department)


def tabs(base,selected,values):
    return dict(active_tab=selected,tabs=[dict(key=key,label=label,url=base+'?tab='+key) for key,label in values])


@login_required
def users(request,id=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'users.manage')
        selected=person(actor,id) if id and id!='new' else None
        query=Person.objects.filter(organization=actor.organization).select_related('user','profile').order_by('profile__full_name')
        text=request.GET.get('q','')[:150]
        if text:query=query.filter(Q(user__username__icontains=text)|Q(profile__full_name__icontains=text))
        status=request.GET.get('status','')
        if status in ('active','inactive'):query=query.filter(active=status=='active')
        if request.GET.get('department'):query=query.filter(department_id=s.identifier(request.GET['department']))
        if request.GET.get('group'):
            from .access_graph import effective_groups
            group_id=str(s.identifier(request.GET['group']))
            query=query.filter(id__in=[p.id for p in query if group_id in effective_groups(p)])
        if request.GET.get('role'):
            value=request.GET['role']
            from .access_graph import role_rows
            if value not in BUILTIN:s.identifier(value)
            query=query.filter(id__in=[p.id for p in query if value in {row['key'] for row in role_rows(p)}])
        roles=[dict(code=code,name=code) for code in BUILTIN]+[dict(code=str(r.id),name=r.name) for r in RoleDefinition.objects.filter(organization=actor.organization,active=True)]
        from .access_graph import departments_tree,role_rows,effective_groups
        c.update(departments=departments_tree(actor.organization),copy_people=Person.objects.filter(organization=actor.organization,active=True).select_related('profile','user'),effective_roles=role_rows(selected) if selected else [],effective_groups=list(effective_groups(selected).values()) if selected else [])
        c.update(selected_user=selected,new_user=id=='new',people=query.distinct()[:100],groups=Group.objects.filter(organization=actor.organization),role_options=roles,q=text,status=status)
        if selected:
            tab=request.GET.get('tab','profile')
            if tab not in ('profile','roles','security','sessions','history'):s.fail('NOT_FOUND','탭을 찾을 수 없습니다.',404)
            reveal=request.GET.get('reveal')=='1'
            if reveal:require_recent(actor)
            PrivacyAccessEvent.objects.create(organization=actor.organization,actor=actor,subject=selected,
                action='VIEW_REVEALED' if reveal else 'VIEW_MASKED',request_id=request.request_id)
            profile=selected.profile
            c.update(**tabs('/console/users/'+str(selected.id),tab,[('profile','기본정보'),('roles','조직·역할'),('security','인증·보안'),('sessions','세션'),('history','변경 이력')]),
                reveal=reveal,profile=profile,masked_email=mask(profile.email),masked_phone=mask(profile.phone),masked_employee=mask(profile.employee_id),
                credential=state(selected),user_sessions=LoginSession.objects.filter(person=selected).order_by('-started_at')[:30],
                assigned_roles=RoleGrant.objects.filter(person=selected),custom_roles=CustomRoleGrant.objects.filter(person=selected,active=True).select_related('role'),
                user_groups=Membership.objects.filter(person=selected).select_related('group'),
                user_changes=AuditEvent.objects.filter(organization=actor.organization,entity_id=selected.id).select_related('actor').order_by('-created_at')[:50],
                privacy_events=PrivacyAccessEvent.objects.filter(subject=selected,organization=actor.organization).select_related('actor').order_by('-created_at')[:30])
        else:
            PrivacyAccessEvent.objects.create(organization=actor.organization,actor=actor,subject=actor,action='LIST_MASKED',request_id=request.request_id)
        return render(request,'desk/users.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)


@login_required
def roles(request,id=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'iam.manage')
        selected=None;system=False
        if id and id!='new':
            system=id in BUILTIN
            selected=SimpleNamespace(id=id,code=id,name=id,permissions=sorted(BUILTIN[id]),system=True,active=True,row_version=1) if system else role(actor,id)
        catalog=[dict(id=code,code=code,name=code,system=True,active=True) for code in BUILTIN]
        catalog+=list(RoleDefinition.objects.filter(organization=actor.organization).order_by('code'))
        permissions=[dict(key=key,label=value[0],scope=value[1],checked=bool(selected and key in selected.permissions)) for key,value in PERMISSIONS.items()]
        c.update(role_list=catalog,selected_role=selected,new_role=id=='new',permissions=permissions,system_role=system,
            people=Person.objects.filter(organization=actor.organization,active=True).select_related('profile').order_by('profile__full_name'))
        if selected:
            c['assignments']=RoleGrant.objects.filter(organization=actor.organization,role=id).select_related('person') if system else CustomRoleGrant.objects.filter(role=selected).select_related('person')
            c['role_changes']=AuditEvent.objects.filter(organization=actor.organization,entity_id=selected.id).select_related('actor').order_by('-created_at')[:30] if not system else []
        return render(request,'desk/roles.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)


@login_required
def groups(request,id=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'iam.manage')
        selected=group(actor,id) if id and id!='new' else None
        c.update(group_list=Group.objects.filter(organization=actor.organization).order_by('name'),selected_group=selected,new_group=id=='new')
        if selected:
            c['members']=[dict(person=p,checked=Membership.objects.filter(group=selected,person=p).exists()) for p in Person.objects.filter(organization=actor.organization).select_related('profile').order_by('profile__full_name')]
            c['group_changes']=AuditEvent.objects.filter(organization=actor.organization,entity_id=selected.id).select_related('actor').order_by('-created_at')[:30]
            open_=selected.ticket_set.exclude(status__in=['CLOSED','REJECTED','CANCELLED'])
            c['open_count']=open_.count()
            c['open_tickets']=(open_ if s.manager(actor) else open_.filter(group_id__in=s.group_ids(actor))).order_by('-created_at')[:30]
        return render(request,'desk/groups.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)


@login_required
def security_policies(request,category=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'security.manage')
        if category and category not in FIELDS:s.fail('NOT_FOUND','정책을 찾을 수 없습니다.',404)
        rows=[]
        for key,label in LABELS.items():
            saved=SecurityPolicy.objects.filter(organization=actor.organization,category=key).select_related('applied_by').first()
            rows.append(dict(key=key,label=label,saved=saved))
        c.update(policy_list=rows,category=category,policy_label=LABELS.get(category))
        if category:
            saved=SecurityPolicy.objects.filter(organization=actor.organization,category=category).first()
            current=policy(actor.organization,category)
            tab=request.GET.get('tab','settings')
            if tab not in ('settings','targets','history','checks'):s.fail('NOT_FOUND','탭을 찾을 수 없습니다.',404)
            c.update(**tabs('/console/security/'+category,tab,[('settings','설정'),('targets','적용 대상'),('history','변경 이력'),('checks','점검 결과')]))
            c.update(policy_version=saved.row_version if saved else 0,
                policy_fields=[dict(key=key,label=meta[3],value=current[key],kind='boolean' if isinstance(meta[0],bool) else 'integer' if isinstance(meta[0],int) else 'string',minimum=meta[1],maximum=meta[2]) for key,meta in FIELDS[category].items()],
                policy_changes=AuditEvent.objects.filter(organization=actor.organization,action='SECURITY_POLICY_APPLIED',entity_id=saved.id).select_related('actor').order_by('-created_at')[:30] if saved else [],
                policy_targets=Person.objects.filter(organization=actor.organization).count(),
                minimum_retention=policy(actor.organization,'audit')['minimum_retention_days'],
                security_events=SecurityEvent.objects.filter(organization=actor.organization).select_related('person').order_by('-created_at')[:50])
        return render(request,'desk/security-policies.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)
