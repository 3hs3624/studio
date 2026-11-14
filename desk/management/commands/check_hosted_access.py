"""Verify the hosted Django request path without exposing provisioned passwords."""
import os
import re
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from desk.deployment import render_host


class Command(BaseCommand):
    help = 'Verify HTTPS, CSRF, password login, authenticated API and static assets.'

    def handle(self, *args, **options):
        host = render_host(os.environ['RENDER_EXTERNAL_HOSTNAME'])
        for username in ['temp-admin','temp-manager','temp-employee','temp-assets','temp-buyer']:
            client = Client(enforce_csrf_checks=True, HTTP_HOST=host)
            response = client.get('/login/', secure=True)
            if response.status_code != 200:
                raise CommandError('Hosted login page verification failed.')
            token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"',response.content.decode())
            password = os.environ.get('STUDIO_LOCAL_'+username.upper().replace('-','_')+'_PASSWORD')
            if not token or not password:
                raise CommandError('Hosted access verification configuration is incomplete.')
            response = client.post('/login/', {'username':username,'password':password,'csrfmiddlewaretoken':token.group(1)},secure=True,HTTP_REFERER='https://'+host+'/login/')
            if response.status_code != 302 or response.get('Location','') != '/':
                raise CommandError('Hosted password login verification failed; no password was changed.')
            if client.get('/api/v1/me',secure=True).status_code != 200:
                raise CommandError('Hosted authenticated API verification failed.')
            for path in ['/', '/systems/service', '/systems/asset', '/systems/resource']:
                if client.get(path,secure=True).status_code != 200:
                    raise CommandError('Integrated workspace verification failed.')
            static = client.get('/static/desk/app.css',secure=True)
            if static.status_code != 200:
                raise CommandError('Hosted static asset verification failed.')
            static.close()
            client.logout()
        self.stdout.write('HOSTED_ACCESS verified: HTTPS, CSRF password login, authenticated API and static assets for five roles; no credentials printed.')
