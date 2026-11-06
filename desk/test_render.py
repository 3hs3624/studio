import io
import os
import secrets
from unittest.mock import patch
from django.test import TestCase, SimpleTestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.exceptions import ImproperlyConfigured
from .deployment import postgres_url, render_host
from .models import Person, Organization
from django.contrib.auth import get_user_model

class HostingConfigTests(SimpleTestCase):
    def test_postgres_url_decodes_credentials_and_requires_tls(self):
        result=postgres_url('postgresql://app:p%40ss@db.internal:5433/studio?sslmode=require')
        self.assertEqual(result['PASSWORD'],'p@ss');self.assertEqual(result['PORT'],5433)
        self.assertEqual(result['OPTIONS']['sslmode'],'require')
        for value in ['sqlite://db','postgres://u:p@db/test?sslmode=disable','postgres://u:p@db/test?unknown=x','postgres://u:p@db:bad/test']:
            with self.assertRaises(ImproperlyConfigured) as err:postgres_url(value)
            self.assertNotIn('p@ss',str(err.exception))

    def test_neon_url_preserves_tls_and_channel_binding(self):
        result=postgres_url('postgresql://app:p%40ss@ep-example-pooler.region.neon.tech/studio?sslmode=require&channel_binding=require')
        self.assertEqual(result['HOST'],'ep-example-pooler.region.neon.tech')
        self.assertEqual(result['OPTIONS'],{'sslmode':'require','channel_binding':'require'})
        for tail in ['channel_binding=disable','channel_binding=require&channel_binding=prefer','sslmode=disable&channel_binding=require']:
            with self.assertRaises(ImproperlyConfigured):postgres_url('postgresql://app:secret@db/studio?'+tail)

    def test_render_host_is_not_an_unvalidated_header(self):
        self.assertEqual(render_host('studio-abc.onrender.com'),'studio-abc.onrender.com')
        for value in ['*','https://evil.example','evil.example','a.onrender.com/evil']:
            with self.assertRaises(ImproperlyConfigured):render_host(value)

class HostedProvisionTests(TestCase):
    def values(self):
        return {'TEST_'+u+'_PASSWORD':secrets.token_urlsafe(24) for u in ['TEMP_ADMIN','TEMP_MANAGER','TEMP_EMPLOYEE','TEMP_ASSETS','TEMP_BUYER']}

    def test_ephemeral_filesystem_restart_does_not_reset_passwords(self):
        values=self.values();output=io.StringIO()
        with patch.dict(os.environ,values):
            call_command('bootstrap_local_access',password_prefix='TEST_',stdout=output)
        self.assertEqual(Person.objects.count(),5)
        password=get_user_model().objects.get(username='temp-admin').password
        with patch.dict(os.environ,self.values()):
            call_command('bootstrap_local_access',password_prefix='TEST_',stdout=output)
        self.assertEqual(get_user_model().objects.get(username='temp-admin').password,password)
        for v in values.values():self.assertNotIn(v,output.getvalue())

    def test_missing_or_reused_passwords_do_not_partially_provision(self):
        with patch.dict(os.environ,{'MISSING_TEMP_ADMIN_PASSWORD':secrets.token_urlsafe(24)}):
            with self.assertRaises(CommandError):call_command('bootstrap_local_access',password_prefix='MISSING_',stdout=io.StringIO())
        self.assertFalse(Organization.objects.exists())
        values={key:'unique-required-long-password' for key in self.values()}
        with patch.dict(os.environ,values):
            with self.assertRaises(CommandError):call_command('bootstrap_local_access',password_prefix='TEST_',stdout=io.StringIO())
        self.assertFalse(Person.objects.exists())


class RenderEntrypointTests(SimpleTestCase):
    def test_entrypoint_executes_ordered_steps_without_nested_shell_quoting(self):
        import subprocess
        import tempfile
        from pathlib import Path
        root=Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);log=folder/'steps'
            for executable in ['python','gunicorn']:
                stub=folder/executable
                stub.write_text('#!/bin/sh\nprintf "%s\\n" "'+executable+' $*" >> "$STEP_LOG"\n')
                stub.chmod(0o755)
            result=subprocess.run(['sh',str(root/'deploy/start-render')],env={**os.environ,'VERIFY_HOSTED_ACCESS':'0','NEON_MIGRATION_TARGET_URL':'','PATH':str(folder)+':'+os.environ['PATH'],'STEP_LOG':str(log),'PORT':'10000'},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            lines=log.read_text().splitlines()
            self.assertEqual(lines[0],'python manage.py migrate --noinput')
            self.assertIn('bootstrap_local_access',lines[1])
            self.assertIn('--bind 0.0.0.0:10000',lines[2])
            self.assertEqual(len(lines),3)

    def test_migration_failure_prevents_server_and_bootstrap(self):
        import subprocess
        import tempfile
        from pathlib import Path
        root=Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);log=folder/'steps'
            stub=folder/'python'
            stub.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$STEP_LOG"\nexit 1\n')
            stub.chmod(0o755)
            result=subprocess.run(['sh',str(root/'deploy/start-render')],env={**os.environ,'PATH':str(folder)+':'+os.environ['PATH'],'STEP_LOG':str(log),'NEON_MIGRATION_TARGET_URL':'not-logged'},capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(log.read_text().splitlines(),['deploy/migrate_postgres.py'])
