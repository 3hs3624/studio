"""Verify provisioned accounts over HTTPS without printing credentials."""
import argparse
import http.cookiejar
import json
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--url',default='https://localhost:8443')
p.add_argument('--ca',required=True)
p.add_argument('--credentials',default=str(Path(__file__).parent/'access/temporary-accounts.json'))
a=p.parse_args()
context=ssl.create_default_context(cafile=a.ca)
accounts=json.loads(Path(a.credentials).read_text())['accounts']
for account in accounts:
    opener=urllib.request.build_opener(urllib.request.HTTPSHandler(context=context),urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    login=a.url.rstrip('/')+'/login/'
    with opener.open(login,timeout=10) as r:html=r.read().decode()
    csrf=re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',html).group(1)
    data=urllib.parse.urlencode({'username':account['username'],'password':account['password'],'csrfmiddlewaretoken':csrf}).encode()
    with opener.open(urllib.request.Request(login,data=data,headers={'Referer':login}),timeout=10) as r:
        if '/portal/incidents' not in r.url:raise SystemExit('Login verification failed.')
    with opener.open(a.url.rstrip('/')+'/api/v1/me',timeout=10) as r:
        if r.status!=200:raise SystemExit('Authenticated request failed.')
    with opener.open(a.url.rstrip('/')+'/static/desk/app.css',timeout=10) as r:
        if r.status!=200:raise SystemExit('Static asset verification failed.')
print(f'HTTPS certificate, CSRF login, authenticated API and static assets verified for {len(accounts)} accounts. No credentials printed.')
