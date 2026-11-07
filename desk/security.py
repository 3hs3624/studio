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
    data = {'person':str(person.id),'org':str(person.organization_id),
            'epoch':str(person.session_epoch),'active':person.active,
            'organization_active':person.organization.active,'user_active':person.user.is_active,
            'roles':sorted(roles(person)),
            'groups':sorted(str(x) for x in person.membership_set.filter(group__active=True).values_list('group_id',flat=True))}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()

def evidence(action,person=None,request=None):
    SecurityEvent.objects.create(organization=person.organization if person else None,person=person,
        action=action,request_id=getattr(request,'request_id',uuid.uuid4()))

@receiver(user_logged_in, dispatch_uid='desk.bind_session')
def login_event(sender,request,user,**kwargs):
    person=Person.objects.filter(user=user).select_related('organization','user').first()
    if person:
        request.session[SESSION_KEY]=binding(person)
    evidence('LOGIN_SUCCESS',person,request)

@receiver(user_logged_out, dispatch_uid='desk.logout_event')
def logout_event(sender,request,user,**kwargs):
    person=Person.objects.filter(user=user).first() if user and user.pk else None
    evidence('LOGOUT',person,request)

@receiver(user_login_failed, dispatch_uid='desk.login_failure')
def failure_event(sender,credentials,request=None,**kwargs):
    # Never persist submitted usernames/passwords, tokens, cookies or request bodies.
    evidence('LOGIN_FAILED',request=request)
