import uuid
from datetime import timedelta
from django.test import TestCase,override_settings
from django.utils import timezone
from django.db import IntegrityError,transaction
from .tests import Fixtures
from .models import DeliveryRecord,DeliveryImport,RoleDefinition,CustomRoleGrant
from .services import BusinessError
from .delivery import ingest

@override_settings(SECURE_SSL_REDIRECT=False)
class DeliveryTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):cls.build_fixtures()
    def source(self,**values):
        return dict(external_id='alpha/app#12',title='로그인 개선',repository='alpha/app',branch='feature/login',revision='abc123',
          status='OPEN',build_status='FAILED',external_actor='dev-account',external_url='https://github.com/alpha/app/pull/12',occurred_at=timezone.now().isoformat(),**values)
    def deployment(self):return dict(external_id='app-deploy/21',title='운영 배포',service='앱 서비스',version='v1.2',environment='운영',status='AWAITING_APPROVAL',external_url='https://ci.example.test/job/app-deploy/21/',occurred_at=timezone.now().isoformat())
    def put(self,provider,rows,actor=None):return ingest(actor or self.admin,provider,rows,uuid.uuid4())
    def test_dashboard_lists_metrics_and_provider_state(self):
        self.put('github',[self.source()]);self.put('jenkins',[self.deployment()])
        self.client.force_login(self.admin.user)
        for path in ['/','/systems/resource']:
            response=self.client.get(path);self.assertEqual(response.status_code,200)
            self.assertContains(response,'로그인 개선');self.assertContains(response,'앱 서비스')
            self.assertEqual([x['value'] for x in response.context['delivery_metrics']],[1,1,1,0])
            self.assertContains(response,'수동 수신');self.assertNotContains(response,'최근 등록 구성항목')
    def test_unconfigured_and_unauthorized_are_distinct(self):
        self.client.force_login(self.admin.user);self.assertContains(self.client.get('/systems/resource'),'연계 미설정')
        self.put('github',[self.source()]);self.client.force_login(self.employee.user)
        self.assertNotContains(self.client.get('/'),'로그인 개선')
        self.assertContains(self.client.get('/systems/resource'),'조회 권한이 필요')
        self.assertEqual(self.client.get('/resources/changes').status_code,403)
        with self.assertRaises(BusinessError):self.put('github',[self.source()],self.employee)
    def test_tenant_detail_and_filters(self):
        self.put('github',[self.source()]);self.put('github',[self.source()],self.foreign)
        record=DeliveryRecord.objects.filter(organization=self.other_org).get()
        self.client.force_login(self.admin.user)
        self.assertEqual(self.client.get('/resources/changes/'+str(record.id)).status_code,404)
        response=self.client.get('/resources/changes?build_status=FAILED&status=OPEN&q=login')
        self.assertEqual(response.context['delivery_page'].paginator.count,0)
        response=self.client.get('/resources/changes?build_status=FAILED&status=OPEN&q=alpha')
        self.assertEqual(response.context['delivery_page'].paginator.count,1)
        record=DeliveryRecord.objects.get(organization=self.org)
        self.assertContains(self.client.get('/resources/changes/'+str(record.id)),'원문에서 확인')
        self.assertEqual(self.client.get('/resources/deployments/'+str(record.id)).status_code,404)
        self.assertEqual(self.client.get('/resources/changes?status=INVALID').status_code,422)
    def test_replay_update_and_stale_observation(self):
        row=self.source();self.put('github',[row]);self.put('github',[row]);self.assertEqual(DeliveryRecord.objects.count(),1)
        row['status']='MERGED';row['occurred_at']=(timezone.now()+timedelta(seconds=1)).isoformat();self.put('github',[row])
        row['status']='OPEN';row['occurred_at']=(timezone.now()-timedelta(days=1)).isoformat();self.assertEqual(self.put('github',[row]),0)
        self.assertEqual(DeliveryRecord.objects.get().status,'MERGED')
    def test_rejects_insecure_or_invalid_batch_without_partial_write(self):
        for key,value in [('external_url','javascript:alert(1)'),('external_url','https://github.com.evil.test/alpha/app/pull/12'),('external_url','https://github.com/alpha/app/pull/12?token=secret'),('occurred_at','2026-01-01'),('status','SUCCESS')]:
            row=self.source();row['external_id']='alpha/app#bad';row[key]=value
            with self.assertRaises(BusinessError):self.put('github',[self.source(),row])
            self.assertEqual(DeliveryRecord.objects.count(),0)
        with self.assertRaises(BusinessError):self.put('github',[self.source(),self.source()])
    def test_database_boundary_and_history(self):
        self.put('github',[self.source()]);record=DeliveryRecord.objects.get()
        with self.assertRaises(IntegrityError),transaction.atomic():DeliveryRecord.objects.filter(pk=record.id).update(organization=self.other_org)
        with self.assertRaises(IntegrityError),transaction.atomic():DeliveryImport.objects.filter(organization=self.org).update(imported_by=self.foreign)
        with self.assertRaises(IntegrityError),transaction.atomic():DeliveryImport.objects.all().delete()
    def test_custom_read_permission_and_navigation(self):
        role=RoleDefinition.objects.create(organization=self.org,code='DELIVERY_VIEW',name='배포 조회',permissions=['delivery.read'])
        CustomRoleGrant.objects.create(organization=self.org,person=self.employee,role=role)
        self.client.force_login(self.employee.user)
        response=self.client.get('/resources/changes');self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['active_area'],'resource')
        links=[link['url'] for group in response.context['nav_groups'] for link in group['links']]
        self.assertIn('/resources/deployments',links);self.assertNotIn('/cis',links)
        response=self.client.get('/cis');self.assertEqual(response.context['active_area'],'service')

    def test_import_command_requires_actor_and_valid_export(self):
        import json,tempfile
        from pathlib import Path
        from django.core.management import call_command
        from django.core.management.base import CommandError
        from io import StringIO
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'export.json';file.write_text(json.dumps([self.source()]),encoding='utf-8')
            output=StringIO()
            call_command('import_delivery_snapshot',organization=self.org.id,actor=self.admin.user.username,provider='github',file=str(file),stdout=output)
            self.assertIn('Imported 1',output.getvalue())
            with self.assertRaises(CommandError):
                call_command('import_delivery_snapshot',organization=self.org.id,actor=self.employee.user.username,provider='github',file=str(file))
            self.assertEqual(DeliveryRecord.objects.count(),1)
