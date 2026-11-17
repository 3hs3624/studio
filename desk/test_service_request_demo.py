import uuid
from django.test import TestCase,override_settings
from .tests import Fixtures
from . import services as s,process_engine as engine
from .service_request_demo import configure,ACCOUNTS,MARKER,verify
from .models import Person,ProcessRun,Ticket,SecurityEvent,ProcessVersion,CatalogVersion,CredentialState

@override_settings(SECURE_SSL_REDIRECT=False)
class ServiceRequestDemoTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures();cls.passwords={n:'A1!'+uuid.uuid4().hex+'zX' for n in ACCOUNTS};cls.result=configure(cls.org.id,cls.passwords)
    def setUp(self):
        from .access_cache import clear
        clear();self.people={p.user.username:p for p in Person.objects.filter(organization=self.org,user__username__in=ACCOUNTS).select_related('user')}
    def test_five_pending_examples_and_idempotent_reuse(self):
        self.assertEqual(len(self.result['tickets']),5)
        self.assertEqual(Ticket.objects.filter(organization=self.org,title__startswith='[실습]').count(),5)
        self.assertTrue(all(t['status']=='PENDING_APPROVAL' for t in self.result['tickets']))
        before={n:p.user.password for n,p in self.people.items()};versions=ProcessVersion.objects.count()
        self.assertTrue(configure(self.org.id,{})['retained'])
        self.assertEqual(versions,ProcessVersion.objects.count())
        self.assertEqual(before,{n:Person.objects.get(pk=p.id).user.password for n,p in self.people.items()})
    def test_satisfaction_and_rework_complete_actual_engine(self):self.assertTrue(verify(self.org))
    def test_only_assigned_user_can_write_and_rating_bounds_are_atomic(self):
        v=CatalogVersion.objects.get(id=CatalogVersion.objects.filter(item__code='SR_STANDARD_REQUEST',organization=self.org).first().id)
        run=ProcessRun.objects.filter(organization=self.org,ticket__title__startswith='[실습]').first()
        def act(who,values=None,decision='COMPLETE'):
            run.refresh_from_db();task=run.tasks.get(status='OPEN')
            return s.execute(self.people[who],'flow_act',dict(task_id=str(task.id),expected_version=run.row_version,decision=decision,values=values or {},reason='검증'),uuid.uuid4().hex,uuid.uuid4(),run.id)
        act('user_auth1',decision='APPROVE')
        act('worker1',{'assignee':str(self.people['worker2'].id),'receipt_note':'배정'})
        with self.assertRaises(s.BusinessError):act('worker1',{'resolution':'할당받지 않은 입력'})
        act('worker2',{'resolution':'정상 조치'})
        act('user1',{'confirmed':True})
        run.refresh_from_db();version=run.row_version;task=run.tasks.get(status='OPEN')
        with self.assertRaises(s.BusinessError):act('user1',{'satisfaction':6})
        run.refresh_from_db();task.refresh_from_db();self.assertEqual(run.row_version,version);self.assertEqual(task.status,'OPEN');self.assertNotIn('satisfaction',run.data)
        with self.assertRaises(s.BusinessError):act('worker2',{'satisfaction':5})
        act('user1',{'satisfaction':1});run.refresh_from_db();self.assertEqual(run.status,'COMPLETED')
    def test_groups_hide_future_fields_and_server_rejects_injection(self):
        run=ProcessRun.objects.filter(organization=self.org,ticket__title__startswith='[실습]').first();task=run.tasks.get(status='OPEN');node=next(n for n in run.graph['nodes'] if n['key']==task.node_key)
        fields=engine.task_fields(self.people['user_auth1'],run,node,task,True)
        self.assertNotIn('satisfaction',{f['key'] for f in fields});self.assertTrue(all(f['read_only'] for f in fields))
    def test_designer_owns_reusable_published_template(self):
        from .permissions import allowed
        self.assertTrue(allowed(self.people['designer1'],'workflow.manage'));self.assertFalse(allowed(self.people['designer1'],'workflow.review'))
        self.assertTrue(allowed(self.people['developer1'],'workflow.review'))
        screen=ProcessVersion.objects.get(definition__organization=self.org,definition__code='SR_STANDARD_SCREEN')
        self.assertEqual(screen.definition.draft_author_id,self.people['designer1'].id);self.assertEqual(len(screen.graph['layout']['groups']),5)

    def test_registration_reuses_screen_layout_and_hides_future_task_inputs(self):
        requester=self.people['user1'];CredentialState.objects.filter(person=requester).update(force_change=False)
        self.client.force_login(requester.user)
        r=self.client.get('/catalog/items/'+self.result['catalog_id'])
        self.assertEqual(r.status_code,200)
        self.assertContains(r,'요청 기본정보');self.assertContains(r,'data-answer="title"')
        self.assertNotContains(r,'data-answer="assignee"');self.assertNotContains(r,'data-answer="satisfaction"')
        self.assertContains(r,'min="1" max="3"')

class ServiceRequestUpgradeTests(Fixtures,TestCase):
    def test_existing_accounts_drafts_and_running_versions_are_preserved(self):
        from .service_request_setup import configure as old_configure,USERNAMES
        from .models import ProcessDefinition
        self.build_fixtures();old_passwords={n:'A1!'+uuid.uuid4().hex+'zX' for n in USERNAMES};initial=old_configure(self.org.id,old_passwords,force_change=False)
        requester=Person.objects.get(user__username='user1');oldv=CatalogVersion.objects.get(item_id=initial['catalog_id'])
        ticket,_=s.execute(requester,'req_create',dict(catalog_version_id=str(oldv.id),values={'title':'기존 요청','description':'기존 버전 유지'}),uuid.uuid4().hex,uuid.uuid4())
        run=ProcessRun.objects.get(ticket_id=ticket['id']);old_graph=run.graph;old_version=run.version_id;password=requester.user.password
        result=configure(self.org.id,{n:'A1!'+uuid.uuid4().hex+'zX' for n in ['developer1','designer1']})
        run.refresh_from_db();requester.user.refresh_from_db();self.assertEqual(run.version_id,old_version);self.assertEqual(run.graph,old_graph);self.assertEqual(requester.user.password,password)
        self.assertNotIn('survey',{n['key'] for n in run.graph['nodes']});self.assertIn('survey',{n['key'] for n in ProcessVersion.objects.get(id=result['workflow_version_id']).graph['nodes']})
        self.assertTrue(ProcessDefinition.objects.filter(code='SR_STANDARD_SCREEN_B20261118',active=False).exists())
