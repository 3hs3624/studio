"""Verify local TLS, CSRF login, integrated pages, role gate and static assets."""
import http.cookiejar
import json
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent


def verify():
    settings = dict(line.split('=', 1) for line in (ROOT / '.env.ap').read_text().splitlines()
                    if '=' in line)
    base = f"https://{settings['APP_HOST']}:{settings['HTTPS_PORT']}"
    context = ssl.create_default_context(cafile=str(ROOT / 'local-root.crt'))
    accounts = json.loads((ROOT / 'access/accounts.json').read_text())['accounts']
    if len(accounts) != 5:
        raise RuntimeError('Expected five provisioned local accounts.')
    for account in accounts:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPSHandler(context=context),
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        login = base + '/login/'
        with opener.open(login, timeout=20) as response:
            page = response.read().decode()
        csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page).group(1)
        data = urllib.parse.urlencode({
            'username': account['username'], 'password': account['password'],
            'csrfmiddlewaretoken': csrf}).encode()
        with opener.open(urllib.request.Request(
                login, data=data, headers={'Referer': login}), timeout=20) as response:
            if urllib.parse.urlsplit(response.url).path != '/':
                raise RuntimeError('Local authentication verification failed.')
            page = response.read().decode()
        permitted = account['username'] == 'temp-admin'
        if ('class="mode-switch"' in page) != permitted:
            raise RuntimeError('Console button permission mismatch.')
        if permitted and not re.search(
                r'class="mode-switch"[^>]+target="_blank"[^>]+rel="noopener noreferrer"', page):
            raise RuntimeError('Console must open in a protected new tab.')
        try:
            with opener.open(base + '/console', timeout=20) as response:
                if not permitted or response.status != 200:
                    raise RuntimeError('Console authorization mismatch.')
        except urllib.error.HTTPError as error:
            if permitted or error.code != 403:
                raise RuntimeError('Console authorization mismatch.') from None
        for path in ('/systems/service', '/systems/asset', '/systems/resource',
                     '/api/v1/me', '/static/desk/carbon-ui.css'):
            with opener.open(base + path, timeout=20) as response:
                if response.status != 200:
                    raise RuntimeError('Local integrated page/API/static check failed.')
    print('Verified TLS certificate, CSRF login, three workspaces, API, static assets and console gate for five accounts.')


if __name__ == '__main__':
    verify()
