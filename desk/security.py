"""Session binding and credential-free authentication evidence."""
import hashlib
import json
import uuid
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import Person, SecurityEvent

SESSION_KEY = 'desk_security_binding'

def binding(person):
    from .services import roles
    from .permissions import effective,custom_grants
    data = {'person':str(person.id),'org':str(person.organization_id),
            'data_scopes':list(__import__('desk.models',fromlist=['RoleDataPolicy']).RoleDataPolicy.objects.filter(organization=person.organization,role_key__in=[r['key'] for r in __import__('desk.access_graph',fromlist=['role_rows']).role_rows(person)]).order_by('role_key','menu_key').values_list('role_key','menu_key','read_scope','write_scope')),'menus':sorted(__import__('desk.menu_access',fromlist=['menu_keys']).menu_keys(person)),'department':str(person.department_id),'epoch':str(person.session_epoch),'active':person.active,
            'organization_active':person.organization.active,'user_active':person.user.is_active,
            'roles':sorted(roles(person)),
            'permissions':sorted(effective(person)),
            'custom_roles':sorted(str(g.role_id)+':'+str(g.role.row_version) for g in custom_grants(person).select_related('role')),
            'groups':sorted(str(x) for x in __import__('desk.access_graph',fromlist=['group_ids']).group_ids(person))}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()

def evidence(action,person=None,request=None):
    SecurityEvent.objects.create(organization=person.organization if person else None,person=person,
        action=action,request_id=getattr(request,'request_id',uuid.uuid4()))

@receiver(user_logged_in, dispatch_uid='desk.bind_session')
def login_event(sender,request,user,**kwargs):
    person=Person.objects.filter(user=user).select_related('organization','user').first()
    if person:
        request.session[SESSION_KEY]=binding(person)
        from django.utils import timezone
        from django.db import transaction
        from .models import Organization, LoginSession
        from .security_policy import policy
        request.session['recent_auth_at']=timezone.now().timestamp()
        if not request.session.session_key:request.session.save()
        with transaction.atomic():
            Organization.objects.select_for_update().get(pk=person.organization_id)
            LoginSession.objects.get_or_create(session_key=request.session.session_key,defaults=dict(organization=person.organization,person=person))
            sessions=LoginSession.objects.filter(person=person,revoked=False).exclude(session_key=request.session.session_key).order_by('-started_at','-id')
            ids=list(sessions.values_list('id',flat=True))[max(0,policy(person.organization,'session')['max_sessions']-1):]
            LoginSession.objects.filter(id__in=ids).update(revoked=True)
    evidence('LOGIN_SUCCESS',person,request)

@receiver(user_logged_out, dispatch_uid='desk.logout_event')
def logout_event(sender,request,user,**kwargs):
    person=Person.objects.filter(user=user).first() if user and user.pk else None
    if request and request.session.session_key:
        from .models import LoginSession
        LoginSession.objects.filter(session_key=request.session.session_key).update(revoked=True)
    evidence('LOGOUT',person,request)

@receiver(user_login_failed, dispatch_uid='desk.login_failure')
def failure_event(sender,credentials,request=None,**kwargs):
    # Never persist submitted usernames/passwords, tokens, cookies or request bodies.
    if request and getattr(request,'_rate_limited',False):
        if getattr(request,'_rate_limited_first',False):evidence('LOGIN_THROTTLED',getattr(request,'_auth_target_person',None),request)
        return
    evidence('LOGIN_FAILED',getattr(request,'_auth_target_person',None) if request else None,request)
