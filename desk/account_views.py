"""Self-service password/second factor; no password or recovery code in persistent UI state."""
import uuid
from urllib.parse import urlencode
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Person, Organization, LoginSession
from .security import SESSION_KEY, binding, evidence
from .security_policy import state, policy, change_password, password_due, management_actor
from . import mfa


def refresh(request,person):
    person.refresh_from_db()
    request.session[SESSION_KEY]=binding(person)
    request.session['recent_auth_at']=timezone.now().timestamp()
    LoginSession.objects.filter(person=person).exclude(session_key=request.session.session_key).update(revoked=True)
    LoginSession.objects.get_or_create(session_key=request.session.session_key,defaults=dict(organization=person.organization,person=person))


@login_required
def account_security(request):
    person=Person.objects.select_related('user','organization').get(user=request.user)
    credential=state(person);error='';notice='';codes=[]
    if request.method=='POST':
        try:
            with transaction.atomic():
                Organization.objects.select_for_update().get(pk=person.organization_id)
                credential=state(person)
                if not person.user.check_password(request.POST.get('current_password','')):
                    from .auth_backend import register_failure
                    register_failure(person,request)
                    error='현재 비밀번호를 확인하십시오.'
                else:
                    action=request.POST.get('action')
                    if credential.locked_until and credential.locked_until>timezone.now():raise ValidationError('계정이 잠겨 있습니다. 잠금 해제 후 다시 시도하십시오.')
                    if credential.mfa_secret and action in ('password','reauth','mfa_disable'):
                        if not mfa.verify_state(credential,request.POST.get('otp','')):raise ValidationError('MFA 인증번호 또는 복구 코드를 확인하십시오.')
                        credential.failed_count=0;credential.first_failed_at=None;credential.locked_until=None;credential.save()
                    if action=='password':
                        value=request.POST.get('new_password','')
                        if value!=request.POST.get('confirm_password',''):raise ValidationError('새 비밀번호가 일치하지 않습니다.')
                        change_password(person,value)
                        update_session_auth_hash(request,person.user)
                        refresh(request,person);notice='비밀번호를 변경하고 다른 세션을 회수했습니다.'
                        evidence('PASSWORD_CHANGED',person,request)
                    elif action=='reauth':
                        previous=LoginSession.objects.filter(session_key=request.session.session_key).first()
                        if previous:previous.revoked=True;previous.save(update_fields=['revoked'])
                        request.session.cycle_key()
                        LoginSession.objects.create(organization=person.organization,person=person,session_key=request.session.session_key,started_at=previous.started_at if previous else timezone.now())
                        request.session['recent_auth_at']=timezone.now().timestamp();notice='재인증을 완료했습니다.'
                    elif action=='mfa_enroll':
                        pending=request.session.get('pending_mfa_seed')
                        if not pending or credential.mfa_secret:raise ValidationError('MFA 등록 상태를 확인하십시오.')
                        secret=mfa.decrypt(pending);counter=mfa.verify(secret,request.POST.get('otp',''))
                        if counter is None:raise ValidationError('인증번호를 확인하십시오.')
                        credential.mfa_secret=pending;credential.mfa_last_counter=counter
                        codes,credential.recovery_hashes=mfa.recovery_codes();credential.save()
                        person.session_epoch=uuid.uuid4();person.save(update_fields=['session_epoch'])
                        request.session.cycle_key()
                        request.session['mfa_verified_for']=str(person.id)
                        request.session.pop('pending_mfa_seed',None);refresh(request,person)
                        notice='MFA를 등록했습니다. 복구 코드는 지금만 표시됩니다.';evidence('MFA_ENROLLED',person,request)
                    elif action=='mfa_disable':
                        if management_actor(person) and policy(person.organization,'access')['admin_mfa_required']:raise ValidationError('관리 기능 MFA 필수 정책에 따라 해제할 수 없습니다.')
                        if not credential.mfa_secret:raise ValidationError('MFA 등록 상태를 확인하십시오.')
                        credential.mfa_secret='';credential.recovery_hashes=[];credential.save()
                        person.session_epoch=uuid.uuid4();person.save(update_fields=['session_epoch']);request.session.cycle_key();refresh(request,person)
                        request.session.pop('mfa_verified_for',None);notice='MFA를 해제했습니다.';evidence('MFA_DISABLED',person,request)
                    else:raise ValidationError('허용되지 않은 작업입니다.')
        except ValidationError as exc:
            error=' '.join(exc.messages)
            if 'MFA 인증번호' in error:
                from .auth_backend import register_failure
                with transaction.atomic():
                    Organization.objects.select_for_update().get(pk=person.organization_id)
                    register_failure(person,request)
    credential=state(person)
    secret=''
    if not credential.mfa_secret:
        if not request.session.get('pending_mfa_seed'):request.session['pending_mfa_seed']=mfa.encrypt(mfa.new_secret())
        secret=mfa.decrypt(request.session['pending_mfa_seed'])
    response=render(request,'desk/account-security.html',dict(actor=person,org=person.organization,
        error=error,notice=notice,recovery_codes=codes,mfa_enabled=bool(credential.mfa_secret),mfa_secret=secret,
        provisioning_uri='otpauth://totp/IT-Operations:'+person.user.username+'?'+urlencode(dict(secret=secret,issuer='IT-Operations')) if secret else '',
        password_due=password_due(person),password_policy=policy(person.organization,'password')))
    response['Cache-Control']='no-store, private'
    return response


def mfa_login(request):
    now=timezone.now().timestamp();user_id=request.session.get('pending_mfa_user')
    if not user_id or now-request.session.get('pending_mfa_time',0)>300:return redirect('/login/')
    person=Person.objects.filter(user_id=user_id,active=True,user__is_active=True,organization__active=True).select_related('user','organization').first()
    if not person:return redirect('/login/')
    error=''
    if request.method=='POST':
        with transaction.atomic():
            Organization.objects.select_for_update().get(pk=person.organization_id)
            credential=state(person)
            if credential.locked_until and credential.locked_until>timezone.now():error='인증할 수 없습니다. 잠시 후 다시 시도하십시오.'
            elif mfa.verify_state(credential,request.POST.get('otp','')):
                credential.failed_count=0;credential.first_failed_at=None;credential.locked_until=None;credential.save()
                destination=request.session.pop('pending_mfa_next','/')
                request.session.pop('pending_mfa_user',None);request.session.pop('pending_mfa_time',None)
                login(request,person.user,backend='desk.auth_backend.PolicyBackend')
                request.session['mfa_verified_for']=str(person.id);return redirect(destination)
            else:
                from .auth_backend import register_failure
                register_failure(person,request);error='인증번호 또는 복구 코드를 확인하십시오.'
                evidence('MFA_FAILED',person,request)
    response=render(request,'desk/mfa-login.html',dict(error=error));response['Cache-Control']='no-store';return response


def activate_account(request,uid,token=None):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import get_user_model
    if request.method!='POST':return render(request,'desk/activate-account.html',dict(error=''))
    token=token or request.POST.get('token','')
    try:user=get_user_model().objects.get(pk=urlsafe_base64_decode(uid).decode())
    except Exception:return HttpResponse('유효하지 않은 초대입니다.',status=400)
    person=Person.objects.filter(user=user,active=True,organization__active=True).first()
    if not person or user.has_usable_password() or not default_token_generator.check_token(user,token):return HttpResponse('초대가 만료되었거나 이미 사용되었습니다.',status=400)
    error=''
    if request.method=='POST':
        try:
            with transaction.atomic():
                Organization.objects.select_for_update().get(pk=person.organization_id)
                user.refresh_from_db()
                if user.has_usable_password() or not default_token_generator.check_token(user,token):raise ValidationError('초대가 만료되었습니다.')
                password=request.POST.get('new_password','')
                if password!=request.POST.get('confirm_password',''):raise ValidationError('비밀번호가 일치하지 않습니다.')
                change_password(person,password);evidence('INVITATION_ACCEPTED',person,request)
                return redirect('/login/')
        except ValidationError as exc:error=' '.join(exc.messages)
    return render(request,'desk/activate-account.html',dict(error=error))
