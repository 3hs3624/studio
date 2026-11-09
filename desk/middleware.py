import uuid

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        response = self.get_response(request)
        response['X-Request-ID'] = request.request_id
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store'
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response


class SessionBindingMiddleware:
    """Old, unbound or authorization-changed sessions require fresh authentication."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            from django.utils.crypto import constant_time_compare
            from django.shortcuts import redirect
            from .models import Person
            from .security import SESSION_KEY, binding, evidence
            person=Person.objects.filter(user=request.user).select_related('organization','user').first()
            expected=binding(person) if person else ''
            valid=person and person.active and person.user.is_active and person.organization.active
            if not valid or not constant_time_compare(request.session.get(SESSION_KEY,''),expected):
                evidence('SESSION_REVOKED',person,request)
                logout(request)
                if request.path.startswith('/api/'):
                    from .api import error
                    return error(request,'SESSION_REVOKED','계정 또는 권한이 변경되었습니다. 다시 로그인하십시오.',403)
                return redirect('/login/')
        return self.get_response(request)


class SecurityPolicyMiddleware:
    def __init__(self,get_response):self.get_response=get_response
    def __call__(self,request):
        from django.utils import timezone
        from django.shortcuts import redirect
        from django.contrib.auth import logout
        from .models import Person, LoginSession
        from .security_policy import policy, state, password_due, expired, allowed_ip, management_actor
        from .security import evidence
        if request.user.is_authenticated:
            person=Person.objects.select_related('organization','user').filter(user=request.user).first()
            if person:
                now=timezone.now();config=policy(person.organization,'session')
                key=request.session.session_key
                session,_=LoginSession.objects.get_or_create(session_key=key,defaults=dict(organization=person.organization,person=person))
                newest=list(LoginSession.objects.filter(person=person,revoked=False).order_by('-started_at','-id').values_list('id',flat=True)[:config['max_sessions']])
                invalid=session.id not in newest or session.revoked or (now-session.last_seen_at).total_seconds()>config['idle_minutes']*60 or (now-session.started_at).total_seconds()>config['max_hours']*3600 or expired(person)
                if invalid:
                    evidence('SESSION_EXPIRED',person,request);session.revoked=True;session.save(update_fields=['revoked']);logout(request)
                    if request.path.startswith('/api/'):
                        from .api import error
                        return error(request,'SESSION_EXPIRED','세션이 만료되었습니다.',403)
                    return redirect('/login/')
                session.last_seen_at=now;session.save(update_fields=['last_seen_at'])
                if not allowed_ip(person,request):
                    from django.http import HttpResponse
                    return HttpResponse('허용되지 않은 관리 접속 경로입니다.',status=403)
                allowed=request.path in ('/account/security','/logout/','/login/mfa/') or request.path.startswith('/static/')
                if not allowed:
                    credential=state(person)
                    required=(credential.mfa_secret or (management_actor(person) and policy(person.organization,'access')['admin_mfa_required'])) and request.session.get('mfa_verified_for')!=str(person.id)
                    code='MFA_REQUIRED' if required else 'PASSWORD_CHANGE_REQUIRED' if password_due(person) else None
                    if code:
                        if request.path.startswith('/api/'):
                            from .api import error
                            return error(request,code,'내 계정 보안에서 인증 설정을 완료하십시오.',403)
                        return redirect('/account/security')
        response=self.get_response(request)
        if request.path.startswith(('/account/','/console/users','/console/security','/login/','/activate/')):
            response['Cache-Control']='no-store, private'
        return response
