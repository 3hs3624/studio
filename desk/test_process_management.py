"""List/detail routing, scope and create-to-detail regression tests."""
import json,uuid
from django.test import TestCase,override_settings
from .tests import Fixtures
from .models import ProcessDefinition

@override_settings(SECURE_SSL_REDIRECT=False)
class ProcessManagementTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        cls.items={}
        for kind in ('SCREEN','WORKFLOW','APPROVAL'):
            cls.items[kind]=ProcessDefinition.objects.create(organization=cls.org,kind=kind,code='EXISTING_'+kind,name='현재 '+kind,draft_author=cls.admin,draft={'fields':[],'read_only':[],'columns':3} if kind=='SCREEN' else {'stages':[]} if kind=='APPROVAL' else {'fields':[],'start':'start','nodes':[{'key':'start','label':'시작','type':'START','next':'end'},{'key':'end','label':'종료','type':'END'}]})
        cls.foreign_item=ProcessDefinition.objects.create(organization=cls.other_org,kind='SCREEN',code='FOREIGN',name='외부 조직 비공개',draft_author=cls.foreign,draft={})
    def setUp(self):self.client.force_login(self.admin.user)
    def paths(self):return [('SCREEN','/console/screens'),('WORKFLOW','/console/workflows'),('APPROVAL','/console/approval-lines')]
    def test_base_routes_show_only_list_for_each_kind(self):
        for kind,base in self.paths():
            with self.subTest(kind=kind):
                response=self.client.get(base);self.assertEqual(response.status_code,200)
                self.assertContains(response,'현재 '+kind);self.assertContains(response,base+'/new')
                self.assertNotContains(response,'id="process-editor"');self.assertNotContains(response,'id="screen-designer"')
                self.assertNotContains(response,'외부 조직 비공개')
                for other in set(self.items)-{kind}:self.assertNotContains(response,'현재 '+other)
    def test_detail_does_not_render_other_definitions(self):
        for kind,base in self.paths():
            with self.subTest(kind=kind):
                response=self.client.get(base+'/'+str(self.items[kind].id));self.assertEqual(response.status_code,200)
                self.assertContains(response,'id="process-editor"');self.assertContains(response,'설계·초안');self.assertContains(response,'목록</a>')
                self.assertNotContains(response,'definition-switcher');self.assertNotContains(response,'다른 정의 선택')
    def test_search_state_and_pagination(self):
        item=self.items['SCREEN'];item.active=False;item.save(update_fields=['active'])
        self.assertContains(self.client.get('/console/screens?state=inactive'),'현재 SCREEN')
        self.assertNotContains(self.client.get('/console/screens?state=active'),'현재 SCREEN')
        self.assertContains(self.client.get('/console/screens?q=EXISTING_SCREEN'),'현재 SCREEN')
        self.assertNotContains(self.client.get('/console/screens?q=missing'),'현재 SCREEN')
        ProcessDefinition.objects.bulk_create([ProcessDefinition(organization=self.org,kind='SCREEN',code='PAGE_'+str(i),name='페이지 '+str(i).zfill(2),draft_author=self.admin,draft={}) for i in range(27)])
        response=self.client.get('/console/screens?q=PAGE_');self.assertEqual(len(response.context['definition_page']),25)
        self.assertContains(response,'q=PAGE_&amp;page=2')
        self.assertEqual(len(self.client.get('/console/screens?q=PAGE_&page=2').context['definition_page']),2)
    def test_new_minimal_form_creates_then_opens_detail(self):
        for kind,base in self.paths():
            with self.subTest(kind=kind):
                response=self.client.get(base+'/new');self.assertEqual(response.status_code,200)
                self.assertContains(response,'id="process-create"');self.assertNotContains(response,'id="process-editor"')
                graph=response.context['initial_graph']
                result=self.client.post('/api/v1/processes/save',json.dumps(dict(kind=kind,code='NEW_'+kind,name='새 정의 '+kind,active=True,expected_version=0,reason='생성 검사',graph=graph)),content_type='application/json',HTTP_IDEMPOTENCY_KEY=uuid.uuid4().hex)
                self.assertEqual(result.status_code,200,result.content)
                detail=self.client.get(base+'/'+result.json()['id']);self.assertContains(detail,'새 정의 '+kind)
    def test_wrong_kind_foreign_and_unauthorized_access_denied(self):
        self.assertEqual(self.client.get('/console/screens/'+str(self.items['WORKFLOW'].id)).status_code,404)
        self.assertEqual(self.client.get('/console/screens/'+str(self.foreign_item.id)).status_code,404)
        self.client.force_login(self.employee.user)
        for _,base in self.paths():
            self.assertEqual(self.client.get(base).status_code,403)
            self.assertEqual(self.client.get(base+'/new').status_code,403)
