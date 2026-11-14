"""Operate isolated local AP/DB Compose projects without touching hosted services."""
import argparse
import datetime
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def private_file(path, values):
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(''.join(f'{key}={value}\n' for key, value in values.items()))


def read_values(which):
    path = ROOT / ('.env.' + which)
    if not path.is_file():
        raise SystemExit('Run configure first; existing volumes require their original configuration.')
    return dict(line.split('=', 1) for line in path.read_text(encoding='utf-8').splitlines()
                if line and not line.startswith('#') and '=' in line)


def configure(args):
    if any((ROOT / name).exists() for name in ('.env.ap', '.env.db')):
        raise SystemExit('Existing configuration retained; refusing to overwrite credentials.')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,24}', args.name):
        raise SystemExit('Use a short lowercase stack name.')
    if args.hostname not in ('localhost', '127.0.0.1'):
        raise SystemExit('This local-only profile supports localhost or 127.0.0.1.')
    if (args.http_port == args.https_port or
            not all(1024 <= port <= 65535 for port in (args.http_port, args.https_port))):
        raise SystemExit('Choose different ports in 1024..65535.')
    ca = Path(args.build_ca).expanduser().resolve() if args.build_ca else ROOT / 'build-ca.pem'
    if not ca.is_file() or '\n' in str(ca) or '\r' in str(ca):
        raise SystemExit('Build CA file is missing or has an invalid path.')
    uid = getattr(os, 'getuid', lambda: 1000)() or 1000
    gid = getattr(os, 'getgid', lambda: 1000)() or 1000
    access = ROOT / 'access'
    access.mkdir(mode=0o700, exist_ok=True)
    access.chmod(0o700)
    if hasattr(os, 'getuid') and os.getuid() == 0:
        os.chown(access, uid, gid)
    # These mounts contain no secrets and must be readable in non-root containers.
    for name in ('init-db.sql', 'Caddyfile'):
        (ROOT / name).chmod(0o644)
    common = {
        'STACK_NAME': args.name,
        'DB_PASSWORD': secrets.token_urlsafe(32),
        'MIGRATION_PASSWORD': secrets.token_urlsafe(32),
    }
    database = {**common, 'DB_OWNER_PASSWORD': secrets.token_urlsafe(40)}
    application = {
        **common, 'SECRET_KEY': secrets.token_urlsafe(64),
        'APP_HOST': args.hostname, 'HTTP_PORT': args.http_port, 'HTTPS_PORT': args.https_port,
        'APP_UID': uid, 'APP_GID': gid, 'APP_IMAGE': args.name + '-app:dev',
        'BUILD_CA_FILE': ca.as_posix(),
    }
    private_file(ROOT / '.env.db', database)
    try:
        private_file(ROOT / '.env.ap', application)
    except BaseException:
        (ROOT / '.env.db').unlink()
        raise
    print('Local AP/DB configuration created. Secret files use mode 0600.')
    print(f'URL: https://{args.hostname}:{args.https_port}/login/')


def compose(which, *arguments):
    return ['docker', 'compose', '--env-file', str(ROOT / ('.env.' + which)),
            '-f', str(ROOT / (which + '.compose.yaml')), *arguments]


def docker_env():
    # Compose normally gives the caller environment precedence over --env-file.
    # Prevent unrelated host/provider variables from overriding this local stack.
    blocked = set(read_values('db')) | set(read_values('ap'))
    return {key: value for key, value in os.environ.items() if key not in blocked}


def run(command, **kwargs):
    return subprocess.run(command, cwd=ROOT, env=docker_env(), check=True, **kwargs)


def start_ap(build=True):
    if build:
        # Build once: initialize and web share one image.
        run(compose('ap', 'build', 'web'))
    run(compose('ap', 'up', '-d', '--no-build', '--wait', '--wait-timeout', '180'))


def export_certificate():
    run(compose('ap', 'cp', 'proxy:/data/caddy/pki/authorities/local/root.crt',
                str(ROOT / 'local-root.crt')))
    print('Local CA exported. Trust local-root.crt in your local OS/browser to open HTTPS.')


def verify():
    run([sys.executable, str(ROOT / 'verify.py')])
    with (ROOT / 'probe.py').open('rb') as source:
        run(compose('ap', 'exec', '-T', 'web', 'python', '-'), stdin=source)


def backup():
    folder = ROOT / 'backups'
    folder.mkdir(mode=0o700, exist_ok=True)
    filename = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ.dump')
    target = folder / filename
    descriptor = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            run(compose('db', 'exec', '-T', 'database', 'pg_dump',
                        '-U', 'itsm_owner', '-d', 'itsm_local', '-Fc'), stdout=output)
        with target.open('rb') as source:
            run(compose('db', 'exec', '-T', 'database', 'pg_restore', '--list'),
                stdin=source, stdout=subprocess.DEVNULL)
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    print('Database backup saved: ' + str(target))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    conf = commands.add_parser('configure')
    conf.add_argument('--name', default='itsm-local')
    conf.add_argument('--hostname', default='localhost')
    conf.add_argument('--http-port', type=int, default=18080)
    conf.add_argument('--https-port', type=int, default=18443)
    conf.add_argument('--build-ca')
    for action in ('up', 'db-up', 'ap-up', 'status', 'stop', 'restart',
                   'certificate', 'check-config', 'verify', 'backup'):
        commands.add_parser(action)
    args = parser.parse_args()
    if args.action == 'configure':
        configure(args)
        return
    if args.action == 'check-config':
        run(compose('db', 'config', '--quiet'))
        run(compose('ap', 'config', '--quiet'))
    elif args.action in ('up', 'db-up', 'ap-up'):
        if args.action in ('up', 'db-up'):
            run(compose('db', 'up', '-d', '--wait', '--wait-timeout', '180'))
        if args.action in ('up', 'ap-up'):
            start_ap()
            export_certificate()
    elif args.action == 'status':
        run(compose('db', 'ps'))
        run(compose('ap', 'ps'))
    elif args.action == 'stop':
        run(compose('ap', 'down'))
        run(compose('db', 'down'))
        print('Containers stopped; named volumes and local secret files retained.')
    elif args.action == 'restart':
        run(compose('db', 'restart', 'database'))
        run(compose('db', 'up', '-d', '--wait', '--wait-timeout', '180'))
        run(compose('ap', 'restart', 'web', 'proxy'))
        start_ap(build=False)
        export_certificate()
    elif args.action == 'certificate':
        export_certificate()
    elif args.action == 'verify':
        verify()
    elif args.action == 'backup':
        backup()


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError:
        raise SystemExit('Local Docker command failed; inspect the named service logs. Secrets were not printed.')
