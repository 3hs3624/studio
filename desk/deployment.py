"""Explicit hosting adapters; no provider credentials or network calls."""
import re
from urllib.parse import urlsplit, unquote, parse_qs
from django.core.exceptions import ImproperlyConfigured

def postgres_url(value):
    try:
        u=urlsplit(value)
        if u.scheme not in ('postgres','postgresql') or not u.hostname or not u.username or not u.password or not u.path.strip('/') or u.fragment:
            raise ValueError()
        query=parse_qs(u.query)
        if set(query)-{'sslmode'} or query.get('sslmode',['require']) not in (['require'],['verify-ca'],['verify-full']):raise ValueError()
        return {'ENGINE':'django.db.backends.postgresql','NAME':unquote(u.path[1:]),'USER':unquote(u.username),'PASSWORD':unquote(u.password),
                'HOST':u.hostname,'PORT':u.port or 5432,'OPTIONS':{'sslmode':query.get('sslmode',['require'])[0]}}
    except (ValueError,TypeError):
        raise ImproperlyConfigured('DATABASE_URL must be a valid PostgreSQL URL with TLS; its value is not logged.') from None

def render_host(value):
    if not re.fullmatch(r'[a-zA-Z0-9-]+\.onrender\.com',value):
        raise ImproperlyConfigured('Invalid Render service hostname.')
    return value.lower()
