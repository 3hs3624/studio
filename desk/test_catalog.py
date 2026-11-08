import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless
from unittest.mock import patch
from django.db import connection, transaction, IntegrityError, close_old_connections
from django.test import TestCase, TransactionTestCase, override_settings
from .tests import Fixtures
from .models import (Ticket, CatalogVersion, CatalogAudience, ServiceRequest, RequestApproval, ApprovalDecision,
    Person, Membership, Notification, AuditEvent, OutboxEvent, Comment, RoleGrant)
from . import services as s
from . import catalog

FIELDS=[{'key':'reason','label':'사유','type':'textarea','required':True},
        {'key':'device','label':'유형','type':'choice','required':True,'options':['노트북','데스크톱']},
        {'key':'quantity','label':'수량','type':'integer','required':False},
        {'key':'delivery','label':'희망일','type':'date','required':False},
        {'key':'remote','label':'원격 근무','type':'boolean','required':False}]
VALUES={'reason':'업무 장비가 필요합니다.','device':'노트북'}

class CatalogFixtures(Fixtures):
    @classmethod
    def build_catalog(cls):
        cls.build_fixtures()
        data=cls.publication()
        result,_=s.execute(cls.manager,'catalog_publish',data,'initial',uuid.uuid4())
        cls.version_id=result['catalog_version_id'];cls.item_id=result['id']

    @classmethod
    def publication(cls,**changes):
        return {'code':'LAPTOP','name':'노트북 신청','description':'업무용 장비 신청',
            'fulfillment_group_id':str(cls.group.id),'approval_required':True,'approver_id':str(cls.peer.id),
            'public_to_org':True,'audience_group_ids':[],'available':True,'fields':FIELDS,'expected_version':0,**changes}

@override_settings(SECURE_SSL_REDIRECT=False)
class CatalogTests(CatalogFixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_catalog()

    def call(self,p,op,data,target=None,key=None):
        return s.execute(p,op,data,key or uuid.uuid4().hex,uuid.uuid4(),target)[0]

    def submit(self,**changes):
        return self.call(self.employee,'req_create',{'catalog_version_id':self.version_id,'values':VALUES,**changes})

    def decision(self,r,decision='APPROVE',p=None,key=None):
        return self.call(p or self.peer,'req_decision',{'decision':decision,'reason':'확인 사유','expected_version':r['version']},uuid.UUID(r['id']),key)

    def assign(self,r):
        return self.call(self.manager,'req_assign',{'assignee_id':str(self.agent.id),'expected_version':r['version']},uuid.UUID(r['id']))

    def action(self,r,action,p=None,key=None):
        return self.call(p or self.agent,'req_action',{'action':action,'reason':'처리 내용','expected_version':r['version']},uuid.UUID(r['id']),key)

    def test_complete_request_flow_and_notifications(self):
        r=self.submit()
        self.assertEqual(r['status'],'PENDING_APPROVAL')
        self.assertEqual(Notification.objects.filter(recipient=self.peer,kind='APPROVAL_REQUESTED').count(),1)
        r=self.decision(r)
        self.assertEqual(r['status'],'APPROVED')
        r=self.assign(r);r=self.action(r,'START');r=self.action(r,'FULFILL');r=self.action(r,'CLOSE',self.employee)
        self.assertEqual(r['status'],'CLOSED')
        self.assertEqual(ApprovalDecision.objects.count(),1)
        self.assertTrue(Notification.objects.filter(recipient=self.employee,kind='REQUEST_FULFILLED').exists())
        self.assertEqual(RequestApproval.objects.get(ticket_id=r['id']).status,'APPROVED')

    def test_pending_request_hidden_from_agent_and_approval_required_before_assignment(self):
        r=self.submit();ident=uuid.UUID(r['id'])
        with self.assertRaises(s.BusinessError) as error:
            catalog.get_request(self.agent,ident)
        self.assertEqual(error.exception.status,404)
        self.assertEqual(catalog.request_query(self.agent,'queue').count(),0)
        with self.assertRaises(s.BusinessError):
            self.assign(r)
        with self.assertRaises(s.BusinessError):
            self.action(r,'START',self.manager)
        self.assertEqual(Ticket.objects.get(id=ident).status,'PENDING_APPROVAL')

    def test_only_designated_approver_including_manager(self):
        r=self.submit()
        for actor in (self.employee,self.manager,self.admin):
            with self.assertRaises(s.BusinessError) as error:
                self.decision(r,p=actor)
            self.assertEqual(error.exception.status,404 if actor==self.admin else 403)
        self.assertTrue(catalog.request_data(self.peer,catalog.get_request(self.peer,uuid.UUID(r['id'])))['can_decide'])

    def test_self_approval_and_inactive_approver_block_submission(self):
        with self.assertRaises(s.BusinessError):
            self.call(self.peer,'req_create',{'catalog_version_id':self.version_id,'values':VALUES})
        Person.objects.filter(id=self.peer.id).update(active=False)
        with self.assertRaises(s.BusinessError):
            self.submit()
        self.assertEqual(ServiceRequest.objects.count(),0)

    def test_approval_skipped_when_published(self):
        version=self.call(self.manager,'catalog_publish',self.publication(expected_version=1,approval_required=False,approver_id=None))
        r=self.submit(catalog_version_id=version['catalog_version_id'])
        self.assertEqual(r['status'],'APPROVED')
        self.assertFalse(RequestApproval.objects.exists())

    def test_rejection_requires_reason_and_resubmission_preserves_original(self):
        r=self.submit()
        with self.assertRaises(s.BusinessError):
            self.call(self.peer,'req_decision',{'decision':'REJECT','expected_version':1},uuid.UUID(r['id']))
        r=self.decision(r,'REJECT')
        newer=self.submit(resubmission_of=r['id'],values={**VALUES,'reason':'수정된 사유'})
        self.assertEqual(newer['resubmission_of'],r['id'])
        self.assertEqual(Ticket.objects.get(id=r['id']).status,'REJECTED')
        self.assertEqual(ServiceRequest.objects.get(ticket_id=r['id']).values['reason'],VALUES['reason'])
        self.assertEqual(ApprovalDecision.objects.count(),1)

    def test_resubmit_other_person_or_active_request_forbidden(self):
        r=self.submit()
        with self.assertRaises(s.BusinessError):
            self.submit(resubmission_of=r['id'])
        self.decision(r,'REJECT')
        with self.assertRaises(s.BusinessError):
            self.call(self.other_agent,'req_create',{'catalog_version_id':self.version_id,'values':VALUES,'resubmission_of':r['id']})

    def test_cancel_and_stale_decision_cannot_revive(self):
        r=self.submit();r=self.action(r,'CANCEL',self.employee)
        self.assertEqual(r['status'],'CANCELLED')
        self.assertEqual(RequestApproval.objects.get(ticket_id=r['id']).status,'CANCELLED')
        with self.assertRaises(s.BusinessError):
            self.decision(r)
        self.assertEqual(ApprovalDecision.objects.count(),0)

    def test_cancellation_after_processing_not_allowed(self):
        r=self.action(self.assign(self.decision(self.submit())),'START')
        with self.assertRaises(s.BusinessError):
            self.action(r,'CANCEL',self.employee)

    def test_versioned_catalog_stale_form_and_snapshot(self):
        r=self.submit()
        updated=self.call(self.manager,'catalog_publish',self.publication(expected_version=1,approver_id=str(self.manager.id),fields=[]))
        with self.assertRaises(s.BusinessError) as error:
            self.submit()
        self.assertEqual(error.exception.status,409)
        original=ServiceRequest.objects.get(ticket_id=r['id'])
        self.assertEqual(original.snapshot['version'],1)
        self.assertEqual(original.values,VALUES)
        self.assertEqual(RequestApproval.objects.get(ticket_id=r['id']).approver_id,self.peer.id)
        self.assertEqual(self.submit(catalog_version_id=updated['catalog_version_id'],values={})['catalog_version'],2)

    def test_audience_for_ordinary_employee_and_withdrawal(self):
        updated=self.call(self.manager,'catalog_publish',self.publication(expected_version=1,public_to_org=False,audience_group_ids=[str(self.group.id)]))
        self.assertEqual(catalog.latest_versions(self.employee).count(),0)
        Membership.objects.create(organization=self.org,person=self.employee,group=self.group)
        self.assertEqual(catalog.latest_versions(self.employee).count(),1)
        r=self.submit(catalog_version_id=updated['catalog_version_id'])
        self.call(self.manager,'catalog_publish',self.publication(expected_version=2,available=False))
        self.assertEqual(catalog.latest_versions(self.employee).count(),0)
        self.assertEqual(catalog.get_request(self.employee,uuid.UUID(r['id'])).requested_by_id,self.employee.id)

    def test_cross_organization_and_audience_publication_checks(self):
        for changes in ({'fulfillment_group_id':str(self.foreign_group.id)}, {'approver_id':str(self.foreign.id)},
                        {'public_to_org':False,'audience_group_ids':[str(self.foreign_group.id)]}):
            with self.assertRaises(s.BusinessError):
                self.call(self.manager,'catalog_publish',self.publication(expected_version=1,**changes))
        with self.assertRaises(s.BusinessError) as error:
            self.call(self.foreign,'req_create',{'catalog_version_id':self.version_id,'values':VALUES})
        self.assertEqual(error.exception.status,404)

    def test_all_field_types_and_strict_validation(self):
        values={**VALUES,'quantity':2,'delivery':'2026-12-01','remote':False}
        r=self.submit(values=values)
        self.assertEqual(r['values'],values)
        for bad in ({'quantity':True},{'quantity':1.5},{'device':'その他'},{'delivery':'2026-02-30'},{'remote':'false'}, {'unknown':'x'},{'reason':' '}):
            with self.assertRaises(s.BusinessError):
                self.submit(values={**VALUES,**bad})

    def test_invalid_form_schema(self):
        bads=[[{'key':'invalid key','label':'x','type':'text','required':True}],FIELDS+[FIELDS[0]],
              [{'key':'choice','label':'x','type':'choice','required':True,'options':['same','same']}],
              [{'key':'x','label':'x','type':'script','required':True}]]
        for fields in bads:
            with self.assertRaises(s.BusinessError):
                self.call(self.manager,'catalog_publish',self.publication(expected_version=1,fields=fields))

    def test_idempotent_submit_decision_and_stale_version(self):
        data={'catalog_version_id':self.version_id,'values':VALUES}
        a=self.call(self.employee,'req_create',data,key='same')
        b=self.call(self.employee,'req_create',data,key='same')
        self.assertEqual(a,b)
        decided=self.decision(a,key='decision')
        self.assertEqual(decided,self.decision(a,key='decision'))
        with self.assertRaises(s.BusinessError):
            self.decision(a,key='other')
        self.assertEqual(ServiceRequest.objects.count(),1)
        self.assertEqual(ApprovalDecision.objects.count(),1)

    def test_internal_comments_hidden_from_requester_and_nonstaff_approver(self):
        r=self.assign(self.decision(self.submit()))
        self.call(self.agent,'req_comment',{'body':'INTERNAL-PRIVATE','visibility':'INTERNAL','expected_version':r['version']},uuid.UUID(r['id']))
        for actor in (self.employee,self.peer):
            self.client.force_login(actor.user)
            self.assertNotIn('INTERNAL-PRIVATE',self.client.get(f'/portal/requests/{r["id"]}').content.decode())
            self.assertEqual(self.client.get(f'/api/v1/requests/{r["id"]}/comments').json()['items'],[])

    def test_notification_authority_and_request_links(self):
        r=self.submit()
        self.client.force_login(self.peer.user)
        items=self.client.get('/api/v1/notifications').json()['items']
        self.assertEqual(items[0]['kind'],'APPROVAL_REQUESTED')
        self.assertEqual(items[0]['ticket_url'],'/portal/requests/'+r['id'])
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/api/v1/notifications').json()['items'],[])

    def test_incident_apis_never_expose_service_requests(self):
        r=self.submit();self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get('/api/v1/incidents?scope=queue').json()['items'],[])
        for suffix in ('','/comments','/activity'):
            self.assertEqual(self.client.get(f'/api/v1/incidents/{r["id"]}'+suffix).status_code,404)
        incident=self.call(self.employee,'create',{'title':'incident','description':'x','impact':1,'urgency':1})
        self.assertEqual(self.client.get('/api/v1/requests/'+incident['id']).status_code,404)

    def test_atomic_failure_rolls_back_request_approval_and_notifications(self):
        before=AuditEvent.objects.count()
        with patch('desk.catalog.notify',side_effect=IntegrityError('forced')):
            with self.assertRaises(IntegrityError): self.submit()
        self.assertEqual(ServiceRequest.objects.count(),0)
        self.assertEqual(RequestApproval.objects.count(),0)
        self.assertEqual(AuditEvent.objects.count(),before)

    def test_db_guards_immutable_records_and_type_status(self):
        r=self.submit();self.decision(r)
        for model,field,value in [(CatalogVersion,'name','tamper'),(ServiceRequest,'values',{}),(ApprovalDecision,'reason','tamper')]:
            with self.assertRaises(IntegrityError),transaction.atomic(): model.objects.all().update(**{field:value})
        with self.assertRaises(IntegrityError),transaction.atomic():
            CatalogAudience.objects.create(organization=self.org,catalog_version_id=self.version_id,group=self.foreign_group)
        with self.assertRaises(IntegrityError),transaction.atomic():
            Ticket.objects.filter(id=r['id']).update(status='NEW')

    def test_html_pages_and_resubmission_prefill(self):
        RoleGrant.objects.create(organization=self.org,person=self.manager,role='SOLUTION_OPERATOR')
        r=self.decision(self.submit(),'REJECT')
        for actor,paths in [(self.employee,['/catalog','/catalog/items/'+self.item_id,'/portal/requests','/portal/requests/'+r['id'],
                 '/catalog/items/'+self.item_id+'?resubmission_of='+r['id']]),
                 (self.peer,['/approvals','/portal/requests/'+r['id']]),(self.manager,['/work/catalog','/work/requests'])]:
            self.client.force_login(actor.user)
            for path in paths:
                response=self.client.get(path)
                self.assertEqual(response.status_code,200,response.content)
        self.client.force_login(self.employee.user)
        self.assertContains(self.client.get('/portal/requests/'+r['id']),'다시 신청하기')

    def test_api_intake_fields_and_catalog_admin_permissions(self):
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/api/v1/catalog/versions').status_code,403)
        self.assertEqual(self.client.get('/api/v1/catalog/items/'+self.item_id).status_code,200)
        result=self.client.post('/api/v1/requests',data={'catalog_version_id':self.version_id,'values':VALUES},content_type='application/json',HTTP_IDEMPOTENCY_KEY='api')
        self.assertEqual(result.status_code,201,result.content)
        self.assertEqual(result['Location'],'/api/v1/requests/'+result.json()['id'])
        self.client.force_login(self.peer.user)
        self.assertEqual(len(self.client.get('/api/v1/approvals').json()['items']),1)

@skipUnless(connection.vendor=='postgresql','Approval races require PostgreSQL row locks.')
class RequestRaceTests(CatalogFixtures,TransactionTestCase):
    def setUp(self):
        self.build_catalog()

    def test_concurrent_approval_and_rejection_one_wins(self):
        r,_=s.execute(self.employee,'req_create',{'catalog_version_id':self.version_id,'values':VALUES},'create',uuid.uuid4())
        def decide(value):
            close_old_connections()
            try:
                p=Person.objects.get(id=self.peer.id)
                try:
                    s.execute(p,'req_decision',{'decision':value,'reason':'race','expected_version':1},value,uuid.uuid4(),uuid.UUID(r['id']))
                    return 200
                except s.BusinessError as error: return error.status
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(decide,['APPROVE','REJECT']))
        self.assertEqual(sorted(results),[200,409])
        self.assertEqual(ApprovalDecision.objects.count(),1)

    def test_concurrent_approval_and_cancellation_do_not_resurrect(self):
        r,_=s.execute(self.employee,'req_create',{'catalog_version_id':self.version_id,'values':VALUES},'create',uuid.uuid4())
        def action(kind):
            close_old_connections()
            try:
                p=Person.objects.get(id=self.peer.id if kind=='approve' else self.employee.id)
                data={'decision':'APPROVE','expected_version':1} if kind=='approve' else {'action':'CANCEL','reason':'cancel','expected_version':1}
                try:
                    s.execute(p,'req_decision' if kind=='approve' else 'req_action',data,kind,uuid.uuid4(),uuid.UUID(r['id']))
                    return 200
                except s.BusinessError as error: return error.status
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(action,['approve','cancel']))
        self.assertEqual(sorted(results),[200,409])
        ticket=Ticket.objects.get(id=r['id'])
        self.assertIn(ticket.status,['APPROVED','CANCELLED'])
        self.assertEqual(RequestApproval.objects.get(ticket=ticket).status,ticket.status)
