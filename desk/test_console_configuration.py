import json
import uuid
from datetime import date
from unittest.mock import patch
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from .tests import Fixtures
from . import test_entities as entity_helpers
from .models import CommonCodeGroup, CommonCodeItem, EntityRecord, NumberIssue, NumberSequence, PluginRun, PluginFailure, RoleGrant
from .plugins.bundled import REGISTRY
from .plugins.number_generator import DEFAULTS


@override_settings(SECURE_SSL_REDIRECT=False)
class ConfigurationTests(Fixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()

    def setUp(self):
        self.client.force_login(self.admin.user)

    def post(self, path, data, key=None):
        return self.client.post('/api/v1/admin/'+path, json.dumps(data),content_type='application/json',HTTP_IDEMPOTENCY_KEY=key or str(uuid.uuid4()))

    def code_group(self, code='PRIORITY'):
        result=self.post('code-groups',dict(code=code,name='우선순위',description='공통 선택값',active=True,expected_version=0,reason='생성'))
        self.assertEqual(result.status_code,201,result.content)
        return result.json()

    def items(self, group, version=1, active=True, key=None):
        return self.post('code-groups/'+group['id']+'/items',dict(expected_version=version,reason='코드 설정',items=[
            dict(code='HIGH',label='높음',description='',sort_order=1,active=active),
            dict(code='NORMAL',label='보통',description='',sort_order=2,active=True)]),key)

    def configure_number(self, values=None, version=0, enabled=True):
        return self.post('plugins/number.generate/configuration',dict(expected_version=version,enabled=enabled,
            configuration=values or DEFAULTS,reason='번호 설정',manifest_digest=REGISTRY['number.generate'].manifest()['digest']))

    def number(self, issue=False, key=None, version=1, data=None):
        return self.post('plugins/number.generate/'+('issue' if issue else 'preview'),
            dict(expected_version=version,manifest_digest=REGISTRY['number.generate'].manifest()['digest'],input={} if data is None else data),key)

    def test_code_group_items_version_and_idempotency(self):
        group=self.code_group()
        response=self.items(group,key='save-items')
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(self.items(group,key='save-items').json(),response.json())
        self.assertEqual(self.items(group).status_code,409)
        self.assertEqual(CommonCodeItem.objects.count(),2)
        self.assertEqual(self.post('code-groups',dict(code='PRIORITY',name='중복',description='',active=True,expected_version=0,reason='중복')).status_code,409)
        with self.assertRaises(IntegrityError),transaction.atomic():
            CommonCodeItem.objects.filter(code='HIGH').update(code='OTHER')

    def test_cross_org_and_locked_codes(self):
        group=self.code_group()
        self.items(group)
        self.client.force_login(self.foreign.user)
        self.assertEqual(self.client.get('/api/v1/admin/code-groups').json()['items'],[])
        self.assertEqual(self.items(group,version=2).status_code,404)
        self.assertEqual(self.client.get('/console/codes/'+group['id']).status_code,404)
        self.client.force_login(self.admin.user)
        locked=CommonCodeGroup.objects.create(organization=self.org,code='SYSTEM',name='시스템 코드',locked=True)
        self.assertEqual(self.items({'id':str(locked.id)}).status_code,409)
        with self.assertRaises(IntegrityError),transaction.atomic():
            CommonCodeItem.objects.create(organization=self.other_org,group_id=group['id'],code='BAD',label='잘못된 조직')

    def test_entity_code_choices_usage_and_inactive_values_preserved(self):
        group=self.code_group()
        self.items(group)
        field=entity_helpers.field('priority','choice',code_group_id=group['id'])
        entity=self.post('entities',dict(code='REQUEST',name='업무',fields=[field],expected_version=0,reason='선택형'))
        self.assertEqual(entity.status_code,201,entity.content)
        entity=self.post('entities/'+entity.json()['id']+'/publish',dict(expected_version=1,reason='게시')).json()
        payload=dict(schema_version_id=entity['published']['id'],values={'priority':'HIGH'})
        self.assertEqual(self.post('entities/'+entity['id']+'/records',payload).status_code,201)
        self.assertEqual(self.client.get('/api/v1/admin/code-groups/'+group['id']).json()['usage'][0]['code'],'REQUEST')
        self.assertContains(self.client.get('/console/entities/'+entity['id']),'>높음</option>',html=False)
        self.assertEqual(self.items(group,version=2,active=False).status_code,200)
        self.assertEqual(self.post('entities/'+entity['id']+'/records',payload).status_code,422)
        self.assertEqual(EntityRecord.objects.get().values['priority'],'HIGH')
        self.client.force_login(self.foreign.user)
        bad=self.post('entities',dict(code='BAD',name='BAD',fields=[field],expected_version=0,reason='조직 경계'))
        self.assertEqual(bad.status_code,404)

    def test_number_preview_does_not_consume_and_issue_retries_are_stable(self):
        self.assertEqual(self.configure_number().status_code,200)
        with patch('desk.plugin_service.timezone.localdate',return_value=date(2026,11,9)):
            for _ in range(2):
                self.assertEqual(self.number().json()['output']['text'],'SR-202611-00001')
            self.assertFalse(NumberSequence.objects.exists())
            first=self.number(True,key='issue-once')
            self.assertEqual(first.status_code,200,first.content)
            self.assertEqual(self.number(True,key='issue-once').json(),first.json())
            self.assertEqual(self.number().json()['output']['text'],'SR-202611-00002')
            self.assertEqual(self.number(True).json()['output']['text'],'SR-202611-00002')
        self.assertEqual(NumberIssue.objects.count(),2)
        self.assertEqual(NumberSequence.objects.get().last_value,2)
        with self.assertRaises(IntegrityError),transaction.atomic():
            NumberIssue.objects.all().update(value='changed')

    def test_number_period_reset_and_org_isolation(self):
        self.configure_number()
        with patch('desk.plugin_service.timezone.localdate',return_value=date(2026,11,30)):
            self.assertEqual(self.number(True).json()['output']['text'],'SR-202611-00001')
        with patch('desk.plugin_service.timezone.localdate',return_value=date(2026,12,1)):
            self.assertEqual(self.number(True).json()['output']['text'],'SR-202612-00001')
            self.client.force_login(self.foreign.user)
            self.assertEqual(self.configure_number().status_code,200)
            self.assertEqual(self.number(True).json()['output']['text'],'SR-202612-00001')
        self.assertEqual(NumberSequence.objects.count(),3)

    def test_number_invalid_config_and_exhaustion_fail_without_allocating(self):
        for values in [{**DEFAULTS,'digits':True},{**DEFAULTS,'prefix':'../x'},
                       {**DEFAULTS,'date_format':'NONE'},{**DEFAULTS,'reset':'day'}]:
            self.assertEqual(self.configure_number(values).status_code,422)
        self.assertEqual(self.configure_number({**DEFAULTS,'digits':1}).status_code,200)
        for _ in range(9):
            self.assertEqual(self.number(True).status_code,200)
        for _ in range(2):
            response=self.number(True,key='exhausted')
            self.assertEqual(response.status_code,409)
            self.assertEqual(response.json()['error']['code'],'SEQUENCE_EXHAUSTED')
        self.assertEqual(NumberIssue.objects.count(),9)
        self.assertEqual(NumberSequence.objects.get().last_value,9)
        self.assertEqual(PluginFailure.objects.count(),1)
        self.assertContains(self.client.get('/console/plugins/number.generate?tab=runs'),'SEQUENCE_EXHAUSTED')

    def test_plugin_failure_history_redacts_input_and_is_immutable(self):
        self.configure_number()
        for _ in range(2):
            self.assertEqual(self.number(data={'secret':'private-input'},key='bad-input').status_code,400)
        self.assertEqual(PluginFailure.objects.count(),1)
        self.assertFalse(NumberIssue.objects.exists())
        self.assertNotContains(self.client.get('/console/plugins/number.generate?tab=runs'),'private-input')
        with self.assertRaises(IntegrityError),transaction.atomic():
            PluginFailure.objects.all().delete()

    def test_plugins_detail_generic_settings_and_tabs(self):
        self.assertContains(self.client.get('/console/plugins'),'업무번호 생성')
        self.assertNotContains(self.client.get('/console/plugins'),'data-kind="plugin-configure"')
        self.assertContains(self.client.get('/console/plugins/number.generate?tab=settings'),'data-plugin-setting="prefix"')
        self.assertContains(self.client.get('/console/plugins/text.normalize?tab=settings'),'data-plugin-setting="trim"')
        self.assertEqual(self.client.get('/console/plugins/missing').status_code,404)
        self.assertEqual(self.client.get('/console/plugins/number.generate?tab=unknown').status_code,404)
        for tab in ['users','roles','groups','accounts','history']:
            self.assertContains(self.client.get('/console/access?tab='+tab),'aria-selected="true"')
        self.assertContains(self.client.get('/console/access?tab=accounts'),'모든 기존 세션 회수')
        self.assertNotContains(self.client.get('/console/access?tab=users'),'모든 기존 세션 회수')
        self.assertContains(self.client.get('/console'),'href="/console/codes"')

    def test_ordinary_users_blocked_and_operators_cannot_edit_access(self):
        self.client.force_login(self.employee.user)
        for path in ['/console/codes','/console/plugins/number.generate','/api/v1/admin/code-groups']:
            self.assertEqual(self.client.get(path).status_code,403)
        self.assertEqual(self.number().status_code,403)
        RoleGrant.objects.create(organization=self.org,person=self.employee,role='SOLUTION_OPERATOR')
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/console/codes').status_code,200)
        self.assertEqual(self.client.get('/console/access?tab=roles').status_code,403)


from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from django.db import connection, close_old_connections
from django.test import TransactionTestCase
from . import services as s
from .models import Person


@skipUnless(connection.vendor=='postgresql', 'PostgreSQL row locking')
class NumberConcurrencyTests(Fixtures, TransactionTestCase):
    def setUp(self):
        self.build_fixtures()
        s.execute(self.admin, 'plugin_configure', dict(expected_version=0,enabled=True,configuration=DEFAULTS,
            reason='동시성 검증',manifest_digest=REGISTRY['number.generate'].manifest()['digest']),
            'setup',uuid.uuid4(),'number.generate')

    def race(self, same_key):
        barrier=Barrier(2)
        def worker(index):
            close_old_connections()
            try:
                actor=Person.objects.get(id=self.admin.id)
                barrier.wait(timeout=10)
                value,_=s.execute(actor,'plugin_issue',dict(expected_version=1,
                    manifest_digest=REGISTRY['number.generate'].manifest()['digest'],input={}),
                    'same' if same_key else str(index),uuid.uuid4(),'number.generate')
                return value['output']['text']
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker,range(2)))

    def test_two_concurrent_issues_are_unique(self):
        values=self.race(False)
        self.assertEqual(len(set(values)),2)
        self.assertEqual(NumberIssue.objects.count(),2)
        self.assertEqual(NumberSequence.objects.get().last_value,2)

    def test_concurrent_retries_issue_once(self):
        values=self.race(True)
        self.assertEqual(values[0],values[1])
        self.assertEqual(NumberIssue.objects.count(),1)
        self.assertEqual(NumberSequence.objects.get().last_value,1)
