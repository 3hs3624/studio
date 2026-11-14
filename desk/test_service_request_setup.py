import json,uuid
from django.test import TestCase,override_settings
from django.utils import timezone
from .tests import Fixtures
from .service_request_setup import configure,USERNAMES
from .models import Person,Membership,Group,Ticket,ProcessRun,ProcessTask,ProcessVersion,RoleGrant,TimelinessTarget,SecurityEvent
from . import services as s

@override_settings(SECURE_SSL_REDIRECT=False)
class ServiceRequestSetupTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        cls.passwords={name:'Test!'+uuid.uuid4().hex+'aZ1' for name in USERNAMES}
        cls.setup=configure(cls.org.id,cls.passwords,force_change=False)
    def setUp(self):
        from .access_cache import clear
        clear();self.people={name:Person.objects.get(user__username=name) for name in USERNAMES}
    def submit(self):
        from .models import CatalogVersion
        v=CatalogVersion.objects.get(item_id=self.setup['catalog_id'])
        result,_=s.execute(self.people['user1'],'req_create',dict(catalog_version_id=str(v.id),values={'title':'지원 요청','description':'업무 시스템 사용 지원'}),uuid.uuid4().hex,uuid.uuid4())
        return ProcessRun.objects.get(ticket_id=result['id'])
    def act(self,run,name,values=None,decision='COMPLETE',status=200):
        run.refresh_from_db();task=run.tasks.get(status='OPEN');self.client.force_login(self.people.get(name,self.agent).user)
        r=self.client.post('/api/v1/process-runs/act/'+str(run.id),json.dumps(dict(expected_version=run.row_version,task_id=str(task.id),decision=decision,values=values or {},reason='검증 의견')),content_type='application/json',HTTP_IDEMPOTENCY_KEY=uuid.uuid4().hex)
        self.assertEqual(r.status_code,status,r.content);run.refresh_from_db();return r
    def test_requested_accounts_departments_group_and_idempotency(self):
        self.assertEqual(self.people['user1'].department_id,self.people['user_auth1'].department_id)
        members=set(Membership.objects.filter(group_id=self.setup['group_id']).values_list('person__user__username',flat=True));self.assertEqual(members,{'worker1','worker2','worker3'})
        old={k:p.user.password for k,p in self.people.items()};again=configure(self.org.id,{},force_change=True);self.assertTrue(again['retained'])
        for key,p in self.people.items():p.user.refresh_from_db();self.assertEqual(p.user.password,old[key])
        self.assertFalse(RoleGrant.objects.filter(person__user__username__in=USERNAMES,role__in=['ORG_ADMIN','DEVELOPER','SOLUTION_OPERATOR']).exists())
    def test_full_process_assignment_confirmation_and_closed_ticket(self):
        run=self.submit();self.client.force_login(self.people['user_auth1'].user);response=self.client.get('/approvals');self.assertEqual(response.status_code,200);self.assertContains(response,str(run.ticket_id));self.assertEqual(response.context['pending_approvals'],1);self.assertEqual(run.ticket.status,'PENDING_APPROVAL');self.assertEqual(run.tasks.get(status='OPEN').person_ids,[str(self.people['user_auth1'].id)])
        self.act(run,'worker1',decision='APPROVE',status=404)
        self.act(run,'user_auth1',decision='APPROVE');self.assertEqual(set(run.tasks.get(status='OPEN').person_ids),{str(self.people[n].id) for n in ('worker1','worker2','worker3')})
        self.act(run,'worker1',{'assignee':str(self.people['worker2'].id),'receipt_note':'운영자2 배정'})
        run.ticket.refresh_from_db();self.assertEqual(run.ticket.assignee_id,self.people['worker2'].id);self.assertEqual(run.tasks.get(status='OPEN').person_ids,[str(self.people['worker2'].id)])
        self.act(run,'worker3',{'resolution':'권한 없음'},status=403)
        self.act(run,'worker2',{'resolution':'처리 완료'});self.assertEqual(run.tasks.get(status='OPEN').person_ids,[str(self.people['user1'].id)])
        self.act(run,'user1',{'confirmed':True,'feedback':'정상 확인'})
        run.ticket.refresh_from_db();self.assertEqual(run.status,'COMPLETED');self.assertEqual(run.ticket.status,'CLOSED');self.assertIsNotNone(TimelinessTarget.objects.get(ticket=run.ticket).completed_at)
    def test_reject_and_user_rework_route(self):
        run=self.submit();self.act(run,'user_auth1',decision='REJECT');self.assertEqual(run.status,'REJECTED')
        run=self.submit();self.act(run,'user_auth1',decision='APPROVE');self.act(run,'worker3',{'assignee':str(self.people['worker1'].id)})
        self.act(run,'worker1',{'resolution':'1차 조치'});self.act(run,'user1',{'confirmed':False,'feedback':'추가 조치 요청'});self.assertEqual(run.tasks.get(status='OPEN').node_key,'action')
        self.act(run,'worker1',{'resolution':'재조치'});self.act(run,'user1',{'confirmed':True});self.assertEqual(run.status,'COMPLETED')
    def test_invalid_outside_group_assignee_is_rejected_and_fields_hidden(self):
        run=self.submit();self.act(run,'user_auth1',decision='APPROVE')
        self.act(run,'worker1',{'assignee':str(self.people['user_auth1'].id)},status=422)
        self.act(run,'worker1',{'assignee':str(self.foreign.id)},status=422)
        self.act(run,'worker1',{'assignee':str(self.people['worker2'].id),'resolution':'hidden injection'},status=422)
        self.act(run,'worker1',{},status=422)
    def test_initial_password_is_forced_to_change_when_enabled(self):
        from .models import CredentialState
        # Unit-test the normal policy marker without exposing any password.
        person=self.people['user1'];from .security_policy import change_password
        change_password(person,'Initial!'+uuid.uuid4().hex+'Aa1',force=True)
        self.assertTrue(CredentialState.objects.get(person=person).force_change)

    def test_production_style_verification_rolls_back_all_test_requests(self):
        from .service_request_setup import verify_configuration
        from .models import Ticket
        before=Ticket.objects.count();result=verify_configuration(self.org.id,self.passwords);self.assertTrue(result['verified']);self.assertEqual(Ticket.objects.count(),before)

    def test_catalog_only_workflow_cannot_bypass_request_entry(self):
        self.client.force_login(self.people['worker1'].user)
        response=self.client.post('/api/v1/process-runs/start',json.dumps(dict(version_id=self.setup['workflow_version_id'],title='우회 시도',values={'title':'우회','description':'카탈로그 경유 안 함'})),content_type='application/json',HTTP_IDEMPOTENCY_KEY=uuid.uuid4().hex)
        self.assertEqual(response.status_code,422);self.assertEqual(response.json()['error']['code'],'CATALOG_REQUIRED')
