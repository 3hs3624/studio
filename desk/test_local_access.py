import io
import json
import tempfile
from pathlib import Path
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from .models import Organization, Person, RoleGrant, SecurityEvent

@override_settings(SECURE_SSL_REDIRECT=False)
class LocalAccessTests(TestCase):
    def provision(self,path):
        out=io.StringIO()
        call_command('bootstrap_local_access',credential_file=str(path),stdout=out)
        return out.getvalue()

    def test_generated_accounts_are_unique_scoped_and_can_login(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'accounts.json';output=self.provision(path)
            data=json.loads(path.read_text());accounts=data['accounts']
            self.assertEqual(len(accounts),5)
            self.assertEqual(len({a['password'] for a in accounts}),5)
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            for account in accounts:
                self.assertNotIn(account['password'],output)
                response=self.client.post('/login/',{'username':account['username'],'password':account['password']})
                self.assertEqual(response.status_code,302)
                self.assertEqual(self.client.get('/api/v1/me').status_code,200)
                self.client.logout()
            admin=Person.objects.get(user__username='temp-admin')
            self.assertEqual(set(RoleGrant.objects.filter(person=admin).values_list('role',flat=True)),{'ORG_ADMIN'})
            employee=Person.objects.get(user__username='temp-employee')
            self.assertFalse(RoleGrant.objects.filter(person=employee).exists())

    def test_restart_keeps_existing_passwords(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'accounts.json';self.provision(path)
            content=path.read_bytes();password=get_user_model().objects.get(username='temp-admin').password
            self.provision(path)
            self.assertEqual(content,path.read_bytes())
            self.assertEqual(password,get_user_model().objects.get(username='temp-admin').password)

    def test_existing_installation_is_not_modified(self):
        Organization.objects.create(name='Existing')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(CommandError):self.provision(Path(d)/'accounts.json')
        self.assertEqual(Organization.objects.count(),1)
        self.assertFalse(Person.objects.exists())

    def test_missing_credential_file_never_resets_accounts(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'accounts.json';self.provision(path);path.unlink()
            with self.assertRaises(CommandError):self.provision(path)
            self.assertFalse(path.exists())
            self.assertEqual(Person.objects.count(),5)

    def test_suspended_account_is_rejected_at_login(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'accounts.json';self.provision(path)
            account=json.loads(path.read_text())['accounts'][2]
            Person.objects.filter(user__username=account['username']).update(active=False)
            response=self.client.post('/login/',account)
            self.assertEqual(response.status_code,200)
            self.assertNotIn('_auth_user_id',self.client.session)
            self.assertFalse(SecurityEvent.objects.filter(action='LOGIN_SUCCESS').exists())

    def test_no_default_password_or_proxy_header_login(self):
        self.assertEqual(self.client.get('/api/v1/me',HTTP_REMOTE_USER='temp-admin').status_code,401)
        self.assertEqual(self.client.post('/login/',{'username':'temp-admin','password':'admin'}).status_code,200)
        self.assertNotIn('_auth_user_id',self.client.session)
