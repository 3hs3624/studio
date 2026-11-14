import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless
from unittest.mock import patch
from django.db import connection, transaction, IntegrityError, close_old_connections
from django.test import TestCase, TransactionTestCase, override_settings
from .test_catalog import CatalogFixtures, VALUES
from .models import Asset, AssetCustody, AssetHistory, RoleGrant, Person, Ticket, TicketResource
from . import services as s
from . import assets

class AssetFixtures(CatalogFixtures):
    @classmethod
    def build_inventory(cls):
        cls.build_catalog()
        RoleGrant.objects.create(organization=cls.org,person=cls.admin,role='ASSET_MANAGER')
        cls.inventory_manager=cls.admin

    @classmethod
    def registration(cls,**changes):
        return {'asset_no':'PC-100','name':'업무용 노트북','manufacturer':'Example','serial_number':'SERIAL-100',
                'model':'Business 14','location':'IT 창고','portal_visible':False,'reason':'신규 입고',**changes}

@override_settings(SECURE_SSL_REDIRECT=False)
class AssetTests(AssetFixtures,TestCase):
    @classmethod
    def setUpTestData(cls): cls.build_inventory()

    def call(self,op,payload,target=None,p=None,key=None):
        return s.execute(p or self.inventory_manager,op,payload,key or uuid.uuid4().hex,uuid.uuid4(),uuid.UUID(target) if target else None)[0]

    def create(self,**changes): return self.call('asset_create',self.registration(**changes))

    def action(self,a,action,**changes):
        payload={'action':action,'reason':'업무 처리','expected_version':a['version']}
        if action in ('ISSUE','RETURN','MOVE','VERIFY'): payload['location']='서울 사무실'
        if action=='ISSUE': payload['person_id']=str(self.employee.id)
        payload.update(changes)
        return self.call('asset_action',payload,a['id'])

    def prepare_request(self):
        t,_=s.execute(self.employee,'req_create',{'catalog_version_id':self.version_id,'values':VALUES},uuid.uuid4().hex,uuid.uuid4())
        t,_=s.execute(self.peer,'req_decision',{'decision':'APPROVE','expected_version':t['version']},uuid.uuid4().hex,uuid.uuid4(),uuid.UUID(t['id']))
        t,_=s.execute(self.manager,'req_assign',{'assignee_id':str(self.agent.id),'expected_version':t['version']},uuid.uuid4().hex,uuid.uuid4(),uuid.UUID(t['id']))
        t,_=s.execute(self.agent,'req_action',{'action':'START','expected_version':t['version']},uuid.uuid4().hex,uuid.uuid4(),uuid.UUID(t['id']))
        return t

    def test_registration_and_issue_return_reissue_history(self):
        a=self.create()
        self.assertEqual(a['status'],'STOCK')
        self.assertEqual(AssetHistory.objects.get(asset_id=a['id']).kind,'REGISTER')
        a=self.action(a,'ISSUE')
        self.assertEqual(a['custodian']['id'],str(self.employee.id))
        first=AssetCustody.objects.get(asset_id=a['id'])
        a=self.action(a,'RETURN')
        self.assertEqual(a['status'],'STOCK');self.assertIsNone(a['custodian'])
        first.refresh_from_db();self.assertIsNotNone(first.returned_at)
        a=self.action(a,'ISSUE',person_id=str(self.peer.id))
        self.assertEqual(a['custodian']['id'],str(self.peer.id))
        self.assertEqual(AssetCustody.objects.filter(asset_id=a['id'],returned_at__isnull=True).count(),1)
        self.assertEqual(AssetHistory.objects.filter(asset_id=a['id']).count(),4)

    def test_legacy_asset_requires_explicit_verification(self):
        self.assertEqual(self.asset.status,'UNVERIFIED')
        a=assets.data(self.asset,self.admin)
        with self.assertRaises(s.BusinessError): self.action(a,'ISSUE')
        a=self.action(a,'VERIFY')
        self.assertEqual(a['status'],'STOCK')
        self.assertEqual(list(AssetHistory.objects.filter(asset=self.asset).values_list('kind',flat=True)),['VERIFY'])

    def test_asset_manager_separate_from_service_and_org_roles(self):
        for p in (self.employee,self.manager,self.agent):
            with self.assertRaises(s.BusinessError) as error: self.call('asset_create',self.registration(),p=p)
            self.assertEqual(error.exception.status,403)
        RoleGrant.objects.filter(person=self.admin,role='ASSET_MANAGER').delete()
        with self.assertRaises(s.BusinessError): self.create()

    def test_duplicate_numbers_and_serials_rollback(self):
        self.create()
        for changes in ({'serial_number':'DIFFERENT'},{'asset_no':'PC-101'}):
            with self.assertRaises(IntegrityError): self.create(**changes)
        self.assertEqual(Asset.objects.filter(asset_no__startswith='PC-10').count(),1)
        self.assertEqual(AssetHistory.objects.count(),1)
        other=self.create(asset_no='PC-102',manufacturer='Other')
        self.assertEqual(other['status'],'STOCK')

    def test_unknown_and_server_owned_fields_rejected(self):
        for key,value in [('status','IN_USE'),('custodian_id',str(self.employee.id)),('organization_id',str(self.other_org.id))]:
            with self.assertRaises(s.BusinessError): self.create(**{key:value})
        for changes in ({'portal_visible':'true'},{'manufacturer':''},{'asset_no':' '}):
            with self.assertRaises(s.BusinessError): self.create(**changes)

    def test_move_preserves_holder_and_retirement_terminal(self):
        a=self.create();a=self.action(a,'MOVE',location='보관실 B')
        self.assertEqual(a['location'],'보관실 B')
        a=self.action(a,'ISSUE');a=self.action(a,'MOVE',location='본사 3층')
        self.assertEqual(a['custodian']['id'],str(self.employee.id))
        with self.assertRaises(s.BusinessError): self.action(a,'RETIRE')
        a=self.action(a,'RETURN');a=self.action(a,'RETIRE')
        self.assertEqual(a['allowed_actions'],[])
        with self.assertRaises(s.BusinessError): self.action(a,'ISSUE')
        self.assertEqual(Asset.objects.get(id=a['id']).status,'RETIRED')

    def test_metadata_correction_and_identity_lock(self):
        a=self.create()
        payload={'name':'수정 자산','manufacturer':'Example','serial_number':'SERIAL-100','model':'Updated',
                 'portal_visible':False,'reason':'모델 정보 정정','expected_version':a['version']}
        a=self.call('asset_update',payload,a['id'])
        self.assertEqual(a['name'],'수정 자산')
        a=self.action(a,'ISSUE')
        with self.assertRaises(s.BusinessError):
            self.call('asset_update',{**payload,'serial_number':'OTHER','expected_version':a['version']},a['id'])
        with self.assertRaises(s.BusinessError):
            self.call('asset_update',{**payload,'asset_no':'NEW','expected_version':a['version']},a['id'])

    def test_foreign_asset_and_recipient_blocked(self):
        a=self.create()
        with self.assertRaises(s.BusinessError): self.action(a,'ISSUE',person_id=str(self.foreign.id))
        with self.assertRaises(s.BusinessError) as error:
            self.call('asset_action',{'action':'VERIFY','location':'x','reason':'x','expected_version':1},str(self.foreign_asset.id))
        self.assertEqual(error.exception.status,404)
        self.assertEqual(Asset.objects.get(id=a['id']).status,'STOCK')

    def test_inactive_recipient_cannot_receive_but_can_return(self):
        a=self.create();Person.objects.filter(id=self.employee.id).update(active=False)
        with self.assertRaises(s.BusinessError): self.action(a,'ISSUE')
        Person.objects.filter(id=self.employee.id).update(active=True)
        a=self.action(a,'ISSUE')
        Person.objects.filter(id=self.employee.id).update(active=False)
        a=self.action(a,'RETURN')
        self.assertEqual(a['status'],'STOCK')

    def test_public_view_excludes_other_holder_serial_and_history(self):
        a=self.action(self.create(portal_visible=True),'ISSUE',person_id=str(self.peer.id))
        self.client.force_login(self.employee.user)
        response=self.client.get('/api/v1/assets/'+a['id'])
        self.assertEqual(response.status_code,200)
        self.assertNotIn('custodian',response.json());self.assertNotIn('serial_number',response.json())
        self.assertEqual(self.client.get('/api/v1/assets/'+a['id']+'/history').status_code,404)
        text=self.client.get('/assets/'+a['id']).content.decode()
        self.assertNotIn('SERIAL-100',text);self.assertNotIn(self.peer.display_name,text)

    def test_personal_history_survives_return_without_new_holder_leak(self):
        a=self.action(self.create(),'ISSUE');a=self.action(a,'RETURN')
        a=self.action(a,'ISSUE',person_id=str(self.peer.id))
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/api/v1/my/assets').json()['items'],[])
        history=self.client.get('/api/v1/my/asset-history').json()['items']
        self.assertEqual(len(history),2)
        self.assertTrue(all('after' not in h and 'reason' not in h for h in history))
        self.assertEqual(self.client.get('/api/v1/assets/'+a['id']).status_code,404)
        self.assertNotIn(self.peer.display_name,self.client.get('/my-assets').content.decode())

    def test_personal_current_private_asset_visible(self):
        a=self.action(self.create(),'ISSUE')
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/api/v1/assets/'+a['id']).status_code,200)
        self.assertEqual(len(self.client.get('/api/v1/my/assets').json()['items']),1)
        self.assertContains(self.client.get('/my-assets'),'업무용 노트북')

    def test_request_link_requires_both_roles_correct_person_and_versions(self):
        r=self.prepare_request();a=self.create()
        payload={'action':'ISSUE','person_id':str(self.employee.id),'location':'서울','reason':'장비 지급',
            'expected_version':a['version'],'service_request_id':r['id'],'expected_request_version':r['version']}
        with self.assertRaises(s.BusinessError): self.call('asset_action',payload,a['id'])
        RoleGrant.objects.create(organization=self.org,person=self.manager,role='ASSET_MANAGER')
        for changes in ({'person_id':str(self.peer.id)},{'expected_request_version':1}):
            with self.assertRaises(s.BusinessError): self.call('asset_action',{**payload,**changes},a['id'],p=self.manager)
        a=self.call('asset_action',payload,a['id'],p=self.manager)
        self.assertEqual(AssetCustody.objects.get(asset_id=a['id']).issue_request_id,uuid.UUID(r['id']))
        self.assertTrue(TicketResource.objects.filter(ticket_id=r['id'],asset_id=a['id']).exists())
        self.assertEqual(Ticket.objects.get(id=r['id']).row_version,r['version']+1)
        self.client.force_login(self.employee.user)
        events=self.client.get('/api/v1/requests/'+r['id']).json()['asset_events']
        self.assertEqual(events[0]['asset_no'],'PC-100')

    def test_request_link_refuses_pending_request(self):
        RoleGrant.objects.create(organization=self.org,person=self.manager,role='ASSET_MANAGER')
        r,_=s.execute(self.employee,'req_create',{'catalog_version_id':self.version_id,'values':VALUES},'pending',uuid.uuid4())
        a=self.create()
        with self.assertRaises(s.BusinessError): self.call('asset_action',{'action':'ISSUE','person_id':str(self.employee.id),
            'location':'서울','reason':'x','expected_version':1,'service_request_id':r['id'],'expected_request_version':1},a['id'],p=self.manager)

    def test_issue_idempotency_and_stale_version(self):
        a=self.create()
        payload={'action':'ISSUE','person_id':str(self.employee.id),'location':'서울','reason':'x','expected_version':1}
        first=self.call('asset_action',payload,a['id'],key='same')
        self.assertEqual(first,self.call('asset_action',payload,a['id'],key='same'))
        with self.assertRaises(s.BusinessError): self.call('asset_action',payload,a['id'])
        self.assertEqual(AssetHistory.objects.filter(kind='ISSUE').count(),1)
        self.assertEqual(AssetCustody.objects.count(),1)

    def test_role_revocation_blocks_replay(self):
        payload=self.registration();self.call('asset_create',payload,key='same')
        RoleGrant.objects.filter(person=self.admin,role='ASSET_MANAGER').delete()
        with self.assertRaises(s.BusinessError) as error: self.call('asset_create',payload,key='same')
        self.assertEqual(error.exception.status,403)

    def test_issue_failure_rolls_back_custody_and_asset(self):
        a=self.create()
        with patch('desk.assets.log',side_effect=IntegrityError('forced')):
            with self.assertRaises(IntegrityError): self.action(a,'ISSUE')
        self.assertEqual(Asset.objects.get(id=a['id']).status,'STOCK')
        self.assertEqual(AssetCustody.objects.count(),0)
        self.assertEqual(AssetHistory.objects.filter(kind='ISSUE').count(),0)

    def test_db_single_active_custody_and_immutable_history(self):
        a=self.action(self.create(),'ISSUE')
        with self.assertRaises(IntegrityError),transaction.atomic():
            AssetCustody.objects.create(organization=self.org,asset_id=a['id'],person=self.peer,issued_by=self.admin,issue_location='x',issue_reason='x')
        with self.assertRaises(IntegrityError),transaction.atomic(): AssetHistory.objects.all().update(reason='tamper')
        with self.assertRaises(IntegrityError),transaction.atomic(): AssetCustody.objects.all().update(person=self.peer)
        a=self.action(a,'RETURN')
        with self.assertRaises(IntegrityError),transaction.atomic(): AssetCustody.objects.all().update(return_reason='tamper')
        with self.assertRaises(IntegrityError),transaction.atomic(): Asset.objects.filter(id=a['id']).update(status='IN_USE')

    def test_inconsistent_imported_custody_cannot_be_retired_or_issued(self):
        a=self.create()
        AssetCustody.objects.create(organization=self.org,asset_id=a['id'],person=self.employee,issued_by=self.admin,
                                    issue_location='legacy',issue_reason='imported inconsistent row')
        for action in ('RETIRE','ISSUE','MOVE'):
            with self.assertRaises(s.BusinessError) as error: self.action(a,action)
            self.assertEqual(error.exception.code,'INVALID_CUSTODY')
        self.assertEqual(Asset.objects.get(id=a['id']).status,'STOCK')

    def test_api_registration_update_actions_and_html(self):
        self.client.force_login(self.admin.user)
        r=self.client.post('/api/v1/assets',data=self.registration(),content_type='application/json',HTTP_IDEMPOTENCY_KEY='register')
        self.assertEqual(r.status_code,201,r.content);a=r.json()
        self.assertEqual(r['Location'],'/api/v1/assets/'+a['id'])
        for path in ('/assets','/assets/new','/assets/'+a['id'],'/my-assets','/api/v1/assets/'+a['id']+'/history'):
            self.assertEqual(self.client.get(path).status_code,200,path)
        r=self.client.put('/api/v1/assets/'+a['id'],data={'name':'수정','manufacturer':'Example','serial_number':'SERIAL-100',
            'model':'New','portal_visible':False,'reason':'정정','expected_version':1},content_type='application/json',HTTP_IDEMPOTENCY_KEY='update')
        self.assertEqual(r.status_code,200,r.content)
        r=self.client.post('/api/v1/assets/'+a['id']+'/actions',data={'action':'ISSUE','person_id':str(self.employee.id),
            'location':'서울','reason':'지급','expected_version':2},content_type='application/json',HTTP_IDEMPOTENCY_KEY='issue')
        self.assertEqual(r.status_code,200,r.content)

    def test_request_personal_history_does_not_show_future_holder(self):
        r=self.prepare_request();a=self.create()
        RoleGrant.objects.create(organization=self.org,person=self.manager,role='ASSET_MANAGER')
        a=self.call('asset_action',{'action':'ISSUE','person_id':str(self.employee.id),'location':'서울','reason':'x',
            'expected_version':1,'service_request_id':r['id'],'expected_request_version':r['version']},a['id'],p=self.manager)
        a=self.action(a,'RETURN');self.action(a,'ISSUE',person_id=str(self.peer.id))
        self.client.force_login(self.employee.user)
        response=self.client.get('/api/v1/requests/'+r['id'])
        self.assertNotIn(self.peer.display_name,str(response.json()['asset_events']))
        self.assertEqual(len(response.json()['asset_events']),2)

@skipUnless(connection.vendor=='postgresql','Asset custody races require PostgreSQL row locks.')
class AssetRaceTests(AssetFixtures,TransactionTestCase):
    def setUp(self): self.build_inventory()

    def test_concurrent_issue_to_two_people_only_one_wins(self):
        a,_=s.execute(self.admin,'asset_create',self.registration(),'new',uuid.uuid4())
        def issue(person_id):
            close_old_connections()
            try:
                p=Person.objects.get(id=self.admin.id)
                try:
                    s.execute(p,'asset_action',{'action':'ISSUE','person_id':str(person_id),'location':'서울','reason':'race','expected_version':1},str(person_id),uuid.uuid4(),uuid.UUID(a['id']))
                    return 200
                except s.BusinessError as error: return error.status
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(issue,[self.employee.id,self.peer.id]))
        self.assertEqual(sorted(results),[200,409])
        self.assertEqual(AssetCustody.objects.filter(returned_at__isnull=True).count(),1)
        self.assertEqual(AssetHistory.objects.filter(kind='ISSUE').count(),1)

    def test_concurrent_return_and_move_keep_asset_and_custody_consistent(self):
        a,_=s.execute(self.admin,'asset_create',self.registration(),'new',uuid.uuid4())
        a,_=s.execute(self.admin,'asset_action',{'action':'ISSUE','person_id':str(self.employee.id),'location':'서울','reason':'x','expected_version':1},'issue',uuid.uuid4(),uuid.UUID(a['id']))
        def act(action):
            close_old_connections()
            try:
                p=Person.objects.get(id=self.admin.id)
                try:
                    s.execute(p,'asset_action',{'action':action,'location':'반납실','reason':'race','expected_version':2},action,uuid.uuid4(),uuid.UUID(a['id']))
                    return 200
                except s.BusinessError as error: return error.status
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(act,['RETURN','MOVE']))
        self.assertEqual(sorted(results),[200,409])
        asset=Asset.objects.get(id=a['id']);active=AssetCustody.objects.filter(asset=asset,returned_at__isnull=True).count()
        self.assertEqual(active,1 if asset.status=='IN_USE' else 0)
