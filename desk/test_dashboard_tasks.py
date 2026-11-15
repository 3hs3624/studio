import uuid
from django.test import TestCase,override_settings
from .tests import Fixtures
from .models import (Department,Person,ProcessDefinition,ProcessVersion,ProcessRun,ProcessTask,ProcessAssignment,ProcessVote,RoleDataPolicy,Ticket,RequestApproval)

@override_settings(SECURE_SSL_REDIRECT=False)
class DashboardTaskTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        cls.dept=Department.objects.create(organization=cls.org,code='REQUEST',name='요청부서')
        cls.other_dept=Department.objects.create(organization=cls.org,code='OTHER',name='다른부서')
        Person.objects.filter(id__in=[cls.admin.id,cls.agent.id,cls.employee.id]).update(department=cls.dept)
        Person.objects.filter(id=cls.manager.id).update(department=cls.other_dept)
        definition=ProcessDefinition.objects.create(organization=cls.org,kind='WORKFLOW',code='DASH',name='검증 프로세스',draft_author=cls.admin,draft={})
        version=ProcessVersion.objects.create(organization=cls.org,definition=definition,version=1,graph={},digest='test',published_by=cls.admin,reviewed_by=cls.peer,reason='검증')
        cls.workflow_run=ProcessRun.objects.create(organization=cls.org,version=version,started_by=cls.employee,title='조회 가능한 할 일',graph={},data={})
        cls.tasks={}
        for key,people in [('mine',[cls.admin]),('dept',[cls.agent]),('other',[cls.manager]),('multi',[cls.admin,cls.agent])]:
            task=ProcessTask.objects.create(organization=cls.org,run=cls.workflow_run,node_key=key,label=key,kind='TASK',selector={'kind':'USER','ids':[str(p.id) for p in people]},person_ids=[str(p.id) for p in people],due_at=None)
            ProcessAssignment.objects.bulk_create([ProcessAssignment(organization=cls.org,task=task,person=p) for p in people]);cls.tasks[key]=task
        ProcessVote.objects.create(organization=cls.org,task=cls.tasks['multi'],actor=cls.admin,decision='COMPLETE')
        done=ProcessTask.objects.create(organization=cls.org,run=cls.workflow_run,node_key='done',label='완료 작업',kind='TASK',status='COMPLETED',due_at=None)
        ProcessAssignment.objects.create(organization=cls.org,task=done,person=cls.admin)
    def setUp(self):self.client.force_login(self.admin.user)
    def test_scope_counts_deduplicate_assignments_and_exclude_own_vote(self):
        for scope,count in [('all',4),('department',3),('mine',1)]:
            with self.subTest(scope=scope):
                response=self.client.get('/?todo_scope='+scope);self.assertEqual(response.status_code,200)
                self.assertEqual(response.context['todo_total'],count);self.assertEqual(len(response.context['todo_rows']),count)
        self.assertEqual(self.client.get('/').context['todo_scope'],'mine')
        self.assertEqual(self.client.get('/?todo_scope=invalid').context['todo_scope'],'mine')
    def test_missing_department_is_empty(self):
        Person.objects.filter(pk=self.admin.id).update(department=None)
        self.client.force_login(self.admin.user)
        response=self.client.get('/?todo_scope=department');self.assertEqual(response.context['todo_total'],0);self.assertContains(response,'소속 부서가 등록되지 않았습니다.')
    def test_all_never_bypasses_existing_run_read_policy(self):
        private=ProcessRun.objects.create(organization=self.org,version=self.workflow_run.version,started_by=self.peer,title='비공개 워크플로우',graph={},data={})
        task=ProcessTask.objects.create(organization=self.org,run=private,node_key='private',label='비공개 단계',kind='TASK',due_at=None)
        ProcessAssignment.objects.create(organization=self.org,task=task,person=self.manager)
        self.client.force_login(self.agent.user)
        response=self.client.get('/?todo_scope=all');self.assertNotContains(response,'비공개 워크플로우')
        RoleDataPolicy.objects.create(organization=self.org,role_key='AGENT',menu_key='workflow-inbox',read_scope='NONE',write_scope='NONE')
        from .access_cache import clear
        clear();self.client.force_login(self.agent.user);response=self.client.get('/?todo_scope=all');self.assertEqual(response.status_code,200);self.assertEqual(response.context['todo_total'],0)
    def test_legacy_requests_and_incidents_use_same_scope(self):
        pending=Ticket.objects.create(organization=self.org,type='SERVICE_REQUEST',number='SR-DASH-1',title='기존 결재',status='PENDING_APPROVAL',requested_by=self.employee,group=self.group)
        RequestApproval.objects.create(organization=self.org,ticket=pending,approver=self.agent,status='PENDING')
        response=self.client.get('/?todo_scope=department');self.assertEqual(response.context['todo_counts']['requests'],1)
        self.assertEqual(self.client.get('/?todo_scope=mine').context['todo_counts']['requests'],0)
        Ticket.objects.create(organization=self.org,number='INC-DASH-1',title='내 장애 처리',status='ASSIGNED',requested_by=self.admin,assignee=self.admin,group=self.group)
        self.assertEqual(self.client.get('/?todo_scope=mine').context['todo_counts']['incidents'],1)
    def test_widget_on_portal_and_service_dashboard_and_tenant_isolation(self):
        foreign_definition=ProcessDefinition.objects.create(organization=self.other_org,kind='WORKFLOW',code='FOREIGN_DASH',name='외부 프로세스',draft_author=self.foreign,draft={})
        foreign_version=ProcessVersion.objects.create(organization=self.other_org,definition=foreign_definition,version=1,graph={},digest='foreign',published_by=self.foreign,reviewed_by=self.foreign,reason='검증')
        foreign_run=ProcessRun.objects.create(organization=self.other_org,version=foreign_version,started_by=self.foreign,title='외부 조직 할 일',graph={},data={})
        foreign_task=ProcessTask.objects.create(organization=self.other_org,run=foreign_run,node_key='foreign',label='foreign',kind='TASK',due_at=None)
        ProcessAssignment.objects.create(organization=self.other_org,task=foreign_task,person=self.foreign)
        for path in ['/?todo_scope=all','/systems/service?todo_scope=all']:
            response=self.client.get(path);self.assertEqual(response.status_code,200);self.assertContains(response,'aria-label="할 일 조회 범위"');self.assertContains(response,'todo_scope=department');self.assertNotContains(response,'외부 조직 할 일')

    def test_linked_request_is_not_counted_twice_and_self_approval_excluded(self):
        ticket=Ticket.objects.create(organization=self.org,type='SERVICE_REQUEST',number='SR-LINKED',title='연결된 요청',status='IN_PROGRESS',requested_by=self.employee,assignee=self.admin,group=self.group)
        linked=ProcessRun.objects.create(organization=self.org,version=self.workflow_run.version,started_by=self.employee,title='연결 요청 태스크',graph={},data={},ticket=ticket)
        linked_task=ProcessTask.objects.create(organization=self.org,run=linked,node_key='linked',label='연결 업무',kind='TASK',due_at=None)
        ProcessAssignment.objects.create(organization=self.org,task=linked_task,person=self.admin)
        response=self.client.get('/?todo_scope=all');self.assertEqual(response.context['todo_counts']['requests'],0);self.assertEqual(response.context['todo_counts']['workflow'],5)
        own=ProcessRun.objects.create(organization=self.org,version=self.workflow_run.version,started_by=self.admin,title='본인 신청 결재',graph={},data={})
        task=ProcessTask.objects.create(organization=self.org,run=own,node_key='approval',label='자가 결재',kind='APPROVAL',due_at=None)
        ProcessAssignment.objects.create(organization=self.org,task=task,person=self.admin)
        self.assertNotContains(self.client.get('/?todo_scope=mine'),'본인 신청 결재')
