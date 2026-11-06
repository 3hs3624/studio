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
