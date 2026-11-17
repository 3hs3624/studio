import json, uuid
from django.test import TestCase, override_settings
from .tests import Fixtures
from .service_request_setup import configure as configure_standard, USERNAMES as STANDARD_USERS
from .sr_template_setup import configure, create_samples, USERNAMES, WORKFLOW_CODE, SCREEN_CODE, CATALOG_CODE
from .models import (Person, ProcessDefinition, ProcessRun, CatalogVersion, Ticket, SecurityEvent, CommonCodeGroup,
                     TimelinessPolicy, ProcessBinding)
from . import services as s


@override_settings(SECURE_SSL_REDIRECT=False)
class ServiceRequestTemplateTests(Fixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        configure_standard(cls.org.id, {n: 'Std!' + uuid.uuid4().hex + 'aZ1' for n in STANDARD_USERS}, force_change=False)
        cls.passwords = {'developer1': 'Dev!' + uuid.uuid4().hex + 'aZ1', 'designer1': 'Dsg!' + uuid.uuid4().hex + 'aZ1'}
        cls.result = configure(cls.org.id, cls.passwords, force_change=False)
        cls.samples = create_samples(cls.org.id)

    def setUp(self):
        from .access_cache import clear
        clear()
        self.people = {n: Person.objects.get(user__username=n) for n in USERNAMES}

    def act(self, run, name, values=None, decision='COMPLETE', status=200):
        run.refresh_from_db()
        task = run.tasks.get(status='OPEN')
        self.client.force_login(self.people[name].user)
        r = self.client.post('/api/v1/process-runs/act/' + str(run.id), json.dumps(dict(expected_version=run.row_version, task_id=str(task.id), decision=decision, values=values or {}, reason='검증')), content_type='application/json', HTTP_IDEMPOTENCY_KEY=uuid.uuid4().hex)
        self.assertEqual(r.status_code, status, r.content)
        run.refresh_from_db()

    def submit(self, title='검증 요청'):
        version = CatalogVersion.objects.get(item__code=CATALOG_CODE)
        values = dict(title=title, request_type='기능 개선', target_system='ERP', urgency='보통', description='검증용 요청 내용')
        result, _ = s.execute(self.people['user1'], 'req_create', dict(catalog_version_id=str(version.id), values=values), uuid.uuid4().hex, uuid.uuid4())
        return ProcessRun.objects.get(ticket_id=result['id'])

    def test_accounts_reused_created_and_review_separation(self):
        self.assertEqual(self.result['created_accounts'], ['developer1', 'designer1'])
        self.assertEqual(self.result['reused_accounts'], ['user1', 'user_auth1', 'worker1', 'worker2'])
        self.assertTrue(self.people['developer1'].user.check_password(self.passwords['developer1']))
        screen = ProcessDefinition.objects.get(code=SCREEN_CODE).published
        self.assertEqual((screen.published_by.user.username, screen.reviewed_by.user.username), ('designer1', 'developer1'))
        flow = ProcessDefinition.objects.get(code=WORKFLOW_CODE).published
        self.assertEqual(flow.published_by.user.username, 'developer1')
        self.assertNotEqual(flow.reviewed_by_id, flow.published_by_id)
        self.assertEqual(CommonCodeGroup.objects.filter(organization=self.org, code__startswith='SR_').count(), 3)
        self.assertTrue(TimelinessPolicy.objects.filter(organization=self.org, ticket_type='SERVICE_REQUEST').exists())
        from .menu_access import console_access
        self.assertTrue(console_access(self.manager))
        self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get('/console/catalog').status_code, 200)
        self.client.force_login(self.people['designer1'].user)
        self.assertEqual(self.client.get('/console/screens').status_code, 200)
        self.assertEqual(self.client.get('/console/users').status_code, 403)
        # 기존 서비스요청 메뉴 연결(SR_STANDARD)은 그대로 둔다.
        self.assertEqual(ProcessBinding.objects.get(organization=self.org, menu_key='service-request').version.definition.code, 'SR_STANDARD')

    def test_idempotent_rerun_keeps_passwords_and_data(self):
        before = self.people['developer1'].user.password
        tickets = Ticket.objects.filter(organization=self.org).count()
        self.assertTrue(configure(self.org.id, {})['retained'])
        self.assertTrue(create_samples(self.org.id)['retained'])
        self.people['developer1'].user.refresh_from_db()
        self.assertEqual(self.people['developer1'].user.password, before)
        self.assertEqual(Ticket.objects.filter(organization=self.org).count(), tickets)

    def test_samples_cover_each_stage(self):
        stages = [row['stage'] for row in self.samples['samples']]
        self.assertEqual(stages, ['department_approval', 'intake', 'development', 'confirmation', 'close'])
        self.assertEqual([row['status'] for row in self.samples['samples']], ['PENDING_APPROVAL', 'IN_PROGRESS', 'IN_PROGRESS', 'IN_PROGRESS', 'CLOSED'])
        self.assertEqual(Ticket.objects.get(process_run__id=self.samples['samples'][0]['run_id']).title, '신규 입사자 그룹웨어 계정·결재 권한 등록')

    def test_development_path_field_access_and_rework(self):
        run = self.submit()
        self.act(run, 'worker1', decision='APPROVE', status=404)
        self.act(run, 'user_auth1', decision='APPROVE')
        self.act(run, 'developer1', {'dev_required': True}, status=403)
        self.act(run, 'worker1', {'dev_required': True, 'operator': str(self.people['worker2'].id), 'intake_note': '개발 필요'})
        task = run.tasks.get(status='OPEN')
        self.assertEqual(task.node_key, 'development')
        self.assertEqual(task.person_ids, [str(self.people['developer1'].id)])
        self.client.force_login(self.people['developer1'].user)
        page = self.client.get('/processes/' + str(run.id))
        fields = {f['key']: f['read_only'] for f in page.context['run_tasks'][-1].fields}
        self.assertFalse(fields['dev_content'])
        self.assertTrue(fields['operator'])
        self.assertNotIn('action_content', fields)
        self.act(run, 'developer1', {'dev_content': '개발 완료', 'dev_done_date': '2026-11-17', 'action_content': '권한 밖 입력'}, status=422)
        self.act(run, 'developer1', {'dev_content': '개발 완료', 'dev_done_date': '2026-11-17'})
        self.assertEqual(run.tasks.get(status='OPEN').person_ids, [str(self.people['worker2'].id)])
        self.act(run, 'worker1', {'action_content': 'x', 'action_date': '2026-11-17'}, status=403)
        self.act(run, 'worker2', {'action_content': '운영 반영', 'action_date': '2026-11-17'})
        self.act(run, 'user1', {'confirmed': False, 'feedback': '재확인 필요'})
        self.assertEqual(run.tasks.get(status='OPEN').node_key, 'operation')
        self.act(run, 'worker2', {'action_content': '재조치', 'action_date': '2026-11-18'})
        self.act(run, 'user1', {'confirmed': True, 'satisfaction': 4})
        run.ticket.refresh_from_db()
        self.assertEqual((run.status, run.ticket.status, run.ticket.assignee_id), ('COMPLETED', 'CLOSED', self.people['worker2'].id))

    def test_operation_path_and_rejection(self):
        run = self.submit('운영 조치 요청')
        self.act(run, 'user_auth1', decision='APPROVE')
        self.act(run, 'worker2', {'dev_required': False, 'operator': str(self.people['worker1'].id)})
        self.assertEqual(run.tasks.get(status='OPEN').node_key, 'operation')
        rejected = self.submit('반려 요청')
        self.act(rejected, 'user_auth1', decision='REJECT')
        rejected.ticket.refresh_from_db()
        self.assertEqual(rejected.ticket.status, 'REJECTED')

    def test_missing_password_for_new_account_is_refused_without_changes(self):
        from .models import Organization
        other = self.other_org
        with self.assertRaises(s.BusinessError):
            configure(other.id, {})
        self.assertFalse(SecurityEvent.objects.filter(organization=other, action='SR_TEMPLATE_PROVISIONED').exists())
