"""Initialize a fresh local database; never calls Render/Neon migration scripts."""
import os
import sys
import time
import urllib.request


def initialize():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    from django.db import connections, OperationalError
    from django.core.management import call_command
    for attempt in range(60):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute('SELECT 1')
            break
        except OperationalError:
            connections.close_all()
            if attempt == 59:
                raise RuntimeError('Local database did not become ready.') from None
            time.sleep(1)
    call_command('migrate', interactive=False)
    call_command('bootstrap_local_access', credential_file='/run/local-access/accounts.json')


def health():
    request = urllib.request.Request('http://127.0.0.1:8000/login/', headers={
        'Host': os.environ['APP_HOST'], 'X-Forwarded-Proto': 'https'})
    with urllib.request.urlopen(request, timeout=3) as response:
        if response.status != 200:
            raise RuntimeError('Local AP health check failed.')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) == 2 else ''
    if mode == 'initialize':
        initialize()
    elif mode == 'health':
        health()
    elif mode == 'web':
        os.execvp('gunicorn', [
            'gunicorn', 'config.wsgi:application', '--bind', '0.0.0.0:8000',
            '--workers', '2', '--timeout', '60', '--access-logfile', '-', '--error-logfile', '-'])
    else:
        raise SystemExit('Use initialize, web, or health.')
