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
