import json,uuid
from unittest.mock import patch
from django.test import TestCase,override_settings
from django.db import IntegrityError,transaction
from .tests import Fixtures
from .models import IntegrationDefinition,IntegrationVersion,IntegrationJob,IntegrationNetworkPolicy,IntegrationCredential,IdempotencyRecord,ProcessDefinition,ProcessReview
from .integrations import service,specs
from .integrations.transport import unseal,address,TransportError
from .integrations.mapping import parse_xml,MappingError
from . import process_engine as engine

@override_settings(SECURE_SSL_REDIRECT=False)
class IntegrationTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        IntegrationNetworkPolicy.objects.create(organization=cls.org,allowed_hosts=['api.example.com'],updated_by=cls.admin)
    def post(self,action,data,id=None,actor=None,key=None):
        self.client.force_login((actor or self.admin).user)
        return self.client.post('/api/v1/integrations/'+action+('/'+str(id) if id else ''),json.dumps(data),content_type='application/json',HTTP_IDEMPOTENCY_KEY=key or uuid.uuid4().hex)
    def publish(self,protocol='REST',**settings):
        values=dict(input_fields=[dict(key='id',type='text',required=True)],response_mapping={'answer':{'path':'data.id','required':True}},url='https://api.example.com/tickets/{id}',method='GET',**settings)
        response=self.post('save',dict(code='API_'+uuid.uuid4().hex[:8],name='테스트 API',protocol=protocol,run_as=str(self.admin.id),active=True,settings=values,expected_version=0,reason='설정 검증'));self.assertEqual(response.status_code,200,response.content)
        value=IntegrationDefinition.objects.get(id=response.json()['id']);self.assertEqual(value.validation_errors,[])
        response=self.post('publish',dict(expected_version=value.row_version,reason='게시 검증'),value.id);self.assertEqual(response.status_code,200,response.content);value.refresh_from_db();return value.published
    def test_catalog_and_endpoint_permissions(self):
        self.client.force_login(self.admin.user);response=self.client.get('/console/integrations');self.assertEqual(response.status_code,200,response.content[:200]);self.assertContains(response,'API · 데이터 연계 관리')
        response=self.post('network',dict(allowed_hosts=[],allowed_private_cidrs=[],expected_version=1,reason='권한 시험'),actor=self.employee);self.assertEqual(response.status_code,403)
    def test_published_version_and_call_mapping(self):
        api=self.publish();response=self.post('invoke',{'inputs':{'id':'A/1'}},api.id);self.assertEqual(response.status_code,202,response.content)
        with patch('desk.integrations.service.request',return_value=(200,b'{"data":{"id":"accepted"}}','application/json')) as request:
            job=service.process_one(response.json()['id']);self.assertEqual(job.status,'SUCCESS');self.assertEqual(unseal(job.mapped_cipher),{'answer':'accepted'});self.assertIn('A%2F1',request.call_args.args[2])
        with self.assertRaises(IntegrityError),transaction.atomic():IntegrationVersion.objects.filter(id=api.id).update(settings={})
    def test_credentials_encrypted_and_never_cached(self):
        marker='synthetic-secret-for-encryption-test'
        response=self.post('credential',dict(name='보호 시험',auth_type='BEARER',secret={'token':marker},active=True,expected_version=0,reason='시험'));self.assertEqual(response.status_code,200,response.content)
        credential=IntegrationCredential.objects.get(id=response.json()['id']);self.assertNotIn(marker,credential.encrypted_secret);self.assertEqual(unseal(credential.encrypted_secret)['token'],marker)
        for record in IdempotencyRecord.objects.all():self.assertNotIn(marker,json.dumps(record.response_body));self.assertNotEqual(record.request_hash,marker)
    def test_allowlist_rebinding_and_xml_entities_denied(self):
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(TransportError):address(self.org,'https://api.example.com/x')
        for url in ['http://api.example.com/x','https://other.example.com/x','https://api.example.com@localhost/x']:
            with self.assertRaises(TransportError):address(self.org,url,False)
        with self.assertRaises(MappingError):parse_xml(b'<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><x>&a;</x>')
    def test_unknown_write_is_not_retried(self):
        api=self.publish(effect='WRITE');response=self.post('invoke',{'inputs':{'id':'a'},'confirm_write':True},api.id)
        with patch('desk.integrations.service.request',side_effect=TransportError('CONNECTION_FAILED',retryable=True)) as request:
            job=service.process_one(response.json()['id']);self.assertEqual(job.status,'UNKNOWN');service.process_one(job.id);self.assertEqual(request.call_count,1)
        retry=self.post('retry',{'reason':'안전하지 않은 재시도'},job.id);self.assertEqual(retry.status_code,409)
    def test_response_remap_does_not_call_remote_again(self):
        api=self.publish();response=self.post('invoke',{'inputs':{'id':'a'}},api.id)
        with patch('desk.integrations.service.request',return_value=(200,b'{"other":"x"}','application/json')) as request:
            job=service.process_one(response.json()['id']);self.assertEqual(job.status,'MAPPING_FAILED');self.assertTrue(job.response_cipher)
            definition=api.definition;definition.draft['response_mapping']={'answer':{'path':'other','required':True}};definition.save(update_fields=['draft'])
            response=self.post('publish',dict(expected_version=definition.row_version,reason='응답 매핑 수정'),definition.id);self.assertEqual(response.status_code,200,response.content);definition.refresh_from_db()
            response=self.post('remap',dict(mapping_version_id=str(definition.published_id),reason='보관 응답으로 재처리'),job.id);self.assertEqual(response.status_code,200,response.content);job.refresh_from_db();self.assertEqual(job.status,'SUCCESS');self.assertEqual(request.call_count,1)
    def test_openapi_import_and_external_reference_denied(self):
        document={'openapi':'3.0.3','servers':[{'url':'https://api.example.com'}],'paths':{'/x/{id}':{'get':{'parameters':[{'name':'id','in':'path','required':True,'schema':{'type':'string'}}]}}}}
        self.assertEqual(len(specs.operations(document)),1);self.assertEqual(specs.draft(document,'GET','/x/{id}')['input_fields'][0]['key'],'id')
        document['components']={'schemas':{'X':{'$ref':'https://evil.example/schema'}}}
        from .services import BusinessError
        with self.assertRaises(BusinessError):specs.operations(document)
    def test_api_workflow_waits_and_resumes_once(self):
        api=self.publish();definition=ProcessDefinition.objects.create(organization=self.org,code='WF_API',name='API 연계 업무',kind='WORKFLOW',draft={},draft_author=self.admin)
        api.settings['allowed_workflows']=[str(definition.id)]
        api2=IntegrationVersion.objects.create(organization=self.org,definition=api.definition,version=2,settings=api.settings,published_by=self.admin,reason='허용 워크플로우',digest='x')
        graph={'start':'start','fields':[dict(key='id',label='식별자',type='text',required=True),dict(key='result',label='결과',type='text',required=False)],'nodes':[dict(key='start',label='시작',type='START',next='call'),dict(key='call',label='API 호출',type='API',api_version_id=str(api2.id),input_mapping={'id':'id'},output_mapping={'result':'answer'},next='end'),dict(key='end',label='종료',type='END')]}
        compiled=engine.validate(self.admin,'WORKFLOW',graph)
        review=ProcessReview.objects.create(organization=self.org,definition=definition,reviewer=self.peer,revision=1,digest=engine.digest(compiled),reason='검토')
        from .models import ProcessVersion,ProcessRun
        version=ProcessVersion.objects.create(organization=self.org,definition=definition,version=1,graph=compiled,digest=engine.digest(compiled),published_by=self.admin,reviewed_by=self.peer,reason='게시')
        run=ProcessRun.objects.create(organization=self.org,version=version,started_by=self.employee,title='연계',data={'id':'x'},graph=compiled)
        engine.advance(self.employee,run,[('start',[])]);run.refresh_from_db();self.assertEqual(run.status,'ACTIVE');job=IntegrationJob.objects.get(process_task__run=run)
        with patch('desk.integrations.service.request',return_value=(200,b'{"data":{"id":"done"}}','application/json')):
            service.process_one(job.id);service.process_one(job.id)
        run.refresh_from_db();self.assertEqual(run.status,'COMPLETED');self.assertEqual(run.data['result'],'done');self.assertEqual(run.events.filter(action='API_COMPLETED').count(),1)
    def test_machine_client_key_is_once_only_and_scoped(self):
        api=self.publish(protocol='WEBHOOK')
        key=uuid.uuid4().hex
        response=self.post('client',dict(name='수신 시험',rate_limit=5,auth_mode='API_KEY',reason='시험'),api.id,key=key);self.assertEqual(response.status_code,201,response.content)
        token=response.json()['secret'];client=response.json()['id'];self.assertTrue(token)
        repeated=self.post('client',dict(name='수신 시험',rate_limit=5,auth_mode='API_KEY',reason='시험'),api.id,key=key);self.assertIsNone(repeated.json()['secret'])
        self.client.logout();url='/api/integration-clients/'+client+'/call'
        rejected=self.client.post(url,json.dumps({'id':'x'}),content_type='application/json',HTTP_IDEMPOTENCY_KEY='one');self.assertEqual(rejected.status_code,401)
        result=self.client.post(url,json.dumps({'id':'x'}),content_type='application/json',HTTP_IDEMPOTENCY_KEY='one',HTTP_AUTHORIZATION='Bearer '+token);self.assertEqual(result.status_code,202,result.content)
        repeated=self.client.post(url,json.dumps({'id':'x'}),content_type='application/json',HTTP_IDEMPOTENCY_KEY='one',HTTP_AUTHORIZATION='Bearer '+token);self.assertEqual(result.json()['id'],repeated.json()['id'])
        changed=self.client.post(url,json.dumps({'id':'different'}),content_type='application/json',HTTP_IDEMPOTENCY_KEY='one',HTTP_AUTHORIZATION='Bearer '+token);self.assertEqual(changed.status_code,409)
        for record in IdempotencyRecord.objects.all():self.assertNotIn(token,json.dumps(record.response_body))
