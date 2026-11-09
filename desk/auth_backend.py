"""Shared DB lockout; authenticates passwords only. MFA is completed by the view."""
from datetime import timedelta
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac
from .models import Person, Organization, CredentialState, LoginThrottle
from .security_policy import policy, state, expired, allowed_ip, client_ip
from .security import evidence


def register_failure(person,request):
    configuration=policy(person.organization,'login');credential=state(person);now=timezone.now()
    if credential.first_failed_at is None or credential.first_failed_at+timedelta(minutes=configuration['window_minutes'])<now:
        credential.failed_count=0;credential.first_failed_at=now
    credential.failed_count+=1
    if credential.failed_count>=configuration['max_failures']:
        credential.locked_until=now+timedelta(minutes=configuration['lock_minutes'])
        evidence('ACCOUNT_LOCKED',person,request)
    credential.save()


class PolicyBackend(ModelBackend):
    def authenticate(self,request,username=None,password=None,**kwargs):
        if username is None or password is None:return None
        person=Person.objects.filter(user__username=username).select_related('user','organization').first()
        if request:request._auth_target_person=person
        configuration=policy(person.organization,'login') if person else dict(ip_limit=100,ip_window_minutes=5)
        key=salted_hmac('login-ip',(client_ip(request) if request else 'internal')+':'+(str(person.organization_id) if person else 'unknown'),algorithm='sha256').hexdigest()
        now=timezone.now()
        with transaction.atomic():
            bucket,_=LoginThrottle.objects.get_or_create(key=key)
            bucket=LoginThrottle.objects.select_for_update().get(pk=bucket.pk)
            if bucket.since+timedelta(minutes=configuration['ip_window_minutes'])<now:
                bucket.count=0;bucket.since=now
            bucket.count+=1;bucket.save()
            if bucket.count>configuration['ip_limit']:
                if request:
                    request._rate_limited=True
                    request._rate_limited_first=bucket.count==configuration['ip_limit']+1
                return None
        if person is None:
            get_user_model()().set_password(password)
            return None
        with transaction.atomic():
            Organization.objects.select_for_update().get(pk=person.organization_id)
            person=Person.objects.select_for_update().select_related('user','organization').get(pk=person.pk)
            credential=state(person)
            if credential.locked_until and credential.locked_until>now:
                person.user.check_password(password)
                return None
            if not person.user.check_password(password):
                register_failure(person,request)
                return None
            if not person.active or not person.organization.active or not self.user_can_authenticate(person.user) or expired(person) or (request and not allowed_ip(person,request)):
                return None
            if not credential.mfa_secret:
                credential.failed_count=0;credential.first_failed_at=None
            credential.locked_until=None;credential.save()
            return person.user
