"""Policy values and enforcement shared by browser login, API and management."""
import ipaddress
import re
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from . import services as s
from .models import SecurityPolicy, CredentialState, PasswordHistory

# key: default, lower bound, upper bound, operator label. No unsafe/off switch for platform protections.
FIELDS = {
 'password': {
  'enforce_existing':(False,None,None,'이 정책 버전으로 기존 계정 변경 강제'),'min_length':(8,8,128,'최소 길이'),'max_length':(128,16,256,'최대 길이'),
  'require_upper':(False,None,None,'영문 대문자 필수'),'require_lower':(False,None,None,'영문 소문자 필수'),
  'require_digit':(False,None,None,'숫자 필수'),'require_symbol':(False,None,None,'특수문자 필수'),
  'history_count':(5,1,24,'이전 비밀번호 재사용 제한 개수'),'max_age_days':(0,0,365,'변경 주기(일, 0=정기 변경 없음)'),
  'warning_days':(7,1,30,'만료 사전 안내(일)'), 'blocked_sha256':('',None,None,'추가 취약 비밀번호 SHA256 목록(쉼표 구분)')},
 'login': {'max_failures':(5,3,20,'계정별 실패 제한 횟수'),'window_minutes':(15,1,60,'실패 집계 시간(분)'),
  'lock_minutes':(15,1,1440,'잠금 시간(분)'),'ip_limit':(100,10,1000,'접속 경로별 요청 제한'),'ip_window_minutes':(5,1,60,'접속 경로 집계 시간(분)')},
 'session': {'idle_minutes':(30,5,240,'유휴 만료(분)'),'max_hours':(8,1,24,'최대 유지시간(시간)'),
  'max_sessions':(3,1,10,'동시 세션 수'),'reauth_minutes':(10,1,30,'민감 작업 재인증 유효시간(분)')},
 'account': {'inactive_days':(0,0,365,'미접속 계정 제한(일, 0=미사용)'),'default_expiry_days':(0,0,365,'신규 계정 기본 사용기간(일, 0=별도 종료일)')},
 'access': {'admin_mfa_required':(False,None,None,'관리 기능 MFA 필수'),'admin_allowed_cidrs':('',None,None,'관리자 허용 IP/CIDR(쉼표 구분, 비움=제한 없음)')},
 'audit': {'minimum_retention_days':(365,90,3650,'감사 이력 최소 보존기간(일)'), 'mask_contacts':(True,None,None,'개인정보 기본 마스킹')},
}
LABELS = {'password':'비밀번호 생성·수명','login':'로그인 실패·잠금','session':'세션·재인증','account':'계정 수명','access':'관리자 접근·MFA','audit':'감사·개인정보'}


def policy(org,category):
    value={key:meta[0] for key,meta in FIELDS[category].items()}
    saved=SecurityPolicy.objects.filter(organization=org,category=category).first()
    if saved:
        value.update(saved.configuration)
    return value


def state(person):
    return CredentialState.objects.get_or_create(person=person,defaults={'organization_id':person.organization_id})[0]


def validate(category,value):
    if category not in FIELDS or not isinstance(value,dict) or set(value)!=set(FIELDS[category]):
        s.fail('INVALID_POLICY','정책 항목을 확인하십시오.')
    for key,meta in FIELDS[category].items():
        default,minimum,maximum,_=meta;item=value[key]
        if isinstance(default,bool):
            valid=type(item) is bool
        elif isinstance(default,int):
            valid=type(item) is int and minimum<=item<=maximum
        else:
            valid=isinstance(item,str) and len(item)<=2000
        if not valid:
            s.fail('INVALID_POLICY','정책 허용 범위와 자료형을 확인하십시오.')
    if category=='password' and value['min_length']>value['max_length']:
        s.fail('INVALID_POLICY','최소 길이는 최대 길이보다 클 수 없습니다.')
    if category=='password' and any(not re.fullmatch(r'[a-fA-F0-9]{64}',item.strip()) for item in value['blocked_sha256'].split(',') if item.strip()):
        s.fail('INVALID_POLICY','취약 비밀번호 목록은 SHA256 해시로 입력하십시오.')
    if category=='audit' and not value['mask_contacts']:
        s.fail('SECURITY_FLOOR','개인정보 기본 마스킹은 해제할 수 없습니다.')
    if category=='access':
        try:
            for item in value['admin_allowed_cidrs'].split(','):
                if item.strip(): ipaddress.ip_network(item.strip(),strict=False)
        except ValueError:
            s.fail('INVALID_POLICY','올바른 IP 또는 CIDR을 입력하십시오.')
    return dict(value)


def password_check(person,value):
    configuration=policy(person.organization,'password')
    if not isinstance(value,str) or not configuration['min_length']<=len(value)<=configuration['max_length']:
        raise ValidationError('비밀번호 길이가 조직 정책에 맞지 않습니다.')
    for key,pattern in [('require_upper',r'[A-Z]'),('require_lower',r'[a-z]'),('require_digit',r'[0-9]'),('require_symbol',r'[^A-Za-z0-9\s]')]:
        if configuration[key] and not re.search(pattern,value):
            raise ValidationError('비밀번호 문자 조합이 조직 정책에 맞지 않습니다.')
    if person.user.username.lower() in value.lower():
        raise ValidationError('로그인 ID를 비밀번호에 포함할 수 없습니다.')
    import hashlib
    if hashlib.sha256(value.encode()).hexdigest() in {item.strip().lower() for item in configuration['blocked_sha256'].split(',')}:raise ValidationError('사용이 제한된 취약 비밀번호입니다.')
    validate_password(value,person.user)
    if person.user.check_password(value):
        raise ValidationError('현재 비밀번호를 다시 사용할 수 없습니다.')
    for old in PasswordHistory.objects.filter(person=person).order_by('-created_at')[:configuration['history_count']]:
        if check_password(value,old.password_hash):
            raise ValidationError('이전에 사용한 비밀번호를 다시 사용할 수 없습니다.')


def change_password(person,value,force=False):
    password_check(person,value)
    PasswordHistory.objects.create(organization=person.organization,person=person,password_hash=person.user.password)
    person.user.set_password(value);person.user.save(update_fields=['password'])
    credential=state(person);credential.password_changed_at=timezone.now();credential.force_change=force
    current=SecurityPolicy.objects.filter(organization=person.organization,category='password').first()
    credential.password_policy_version=current.row_version if current else 0
    credential.failed_count=0;credential.first_failed_at=None;credential.locked_until=None;credential.save()
    import uuid
    person.session_epoch=uuid.uuid4();s.bump(person)


def password_due(person):
    credential=state(person);days=policy(person.organization,'password')['max_age_days']
    current=SecurityPolicy.objects.filter(organization=person.organization,category='password').first()
    return credential.force_change or bool(current and current.configuration.get('enforce_existing') and credential.password_policy_version<current.row_version) or bool(days and credential.password_changed_at+timedelta(days=days)<=timezone.now())


def expired(person):
    now=timezone.now()
    if person.expires_on and person.expires_on<timezone.localdate(): return True
    days=policy(person.organization,'account')['inactive_days']
    if not days:return False
    from .models import LoginSession
    last=person.user.last_login or person.created_at
    seen=LoginSession.objects.filter(person=person).order_by('-last_seen_at').first()
    if seen and seen.last_seen_at>last:last=seen.last_seen_at
    credential=state(person)
    if credential.reactivated_at and credential.reactivated_at>last:last=credential.reactivated_at
    return bool(days and last+timedelta(days=days)<now)


def client_ip(request):
    address=request.META.get('REMOTE_ADDR','127.0.0.1')
    try:
        current=ipaddress.ip_address(address)
        trusted=[ipaddress.ip_network(item.strip(),strict=False) for item in getattr(settings,'SECURITY_TRUSTED_PROXY_CIDRS',[]) if item.strip()]
        if any(current in network for network in trusted):
            chain=[part.strip() for part in request.META.get('HTTP_X_FORWARDED_FOR','').split(',') if part.strip()]
            for candidate in reversed(chain):
                candidate=ipaddress.ip_address(candidate)
                if not any(candidate in network for network in trusted): return str(candidate)
        return str(current)
    except ValueError:
        return ''


def management_actor(person):
    from .permissions import effective
    return bool(effective(person)&{'console.access','users.manage','iam.manage','security.manage'})


def allowed_ip(person,request,configuration=None):
    configuration=configuration or policy(person.organization,'access')
    if not configuration['admin_allowed_cidrs'] or not management_actor(person): return True
    try:
        address=ipaddress.ip_address(client_ip(request))
        return any(address in ipaddress.ip_network(item.strip(),strict=False) for item in configuration['admin_allowed_cidrs'].split(',') if item.strip())
    except ValueError:
        return False


def require_recent(person):
    age=policy(person.organization,'session')['reauth_minutes']*60
    if timezone.now().timestamp()-getattr(person,'_recent_auth',0)>age:
        s.fail('REAUTH_REQUIRED','민감 작업 전 내 계정 보안에서 비밀번호를 다시 확인하십시오.',403)
