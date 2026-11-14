"""Generate owner-only local access configuration; never print secrets."""
import argparse
import os
import re
import secrets
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--hostname',default='localhost')
a=p.parse_args()
if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]{0,251}[a-zA-Z0-9])?',a.hostname):
    p.error('Use a hostname without a scheme, port or path.')
root=Path(__file__).resolve().parent
for name in ['init-database.sql','Caddyfile']:
    (root/name).chmod(0o644)
path=root/'.env'
if path.exists():p.error('Existing configuration retained; refusing to overwrite secrets.')
local=a.hostname=='localhost'
access=root/'access';access.mkdir(mode=0o700,exist_ok=True);access.chmod(0o700)
values={
 'SECRET_KEY':secrets.token_urlsafe(64),'DB_PASSWORD':secrets.token_urlsafe(32),
 'DB_OWNER_PASSWORD':secrets.token_urlsafe(32),
 'APP_HOST':a.hostname,'ALLOWED_HOSTS':a.hostname,
 'CSRF_TRUSTED_ORIGINS':f'https://{a.hostname}:8443' if local else f'https://{a.hostname}',
 'BIND_ADDRESS':'127.0.0.1' if local else '0.0.0.0',
 'HTTP_PORT':'8080' if local else '80','HTTPS_PORT':'8443' if local else '443',
 'APP_UID':str(os.getuid()),'APP_GID':str(os.getgid()),
}
fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:f.write(''.join(f'{k}={v}\n' for k,v in values.items()))
print('Configuration created; secrets remain in deploy/.env (0600).')
print(f'Planned URL: https://{a.hostname}'+(':8443' if local else '')+'/login/')
