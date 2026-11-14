import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from unittest.mock import patch
from unittest import skipUnless
from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction, close_old_connections
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from .models import (Organization, Person, Group, Membership, RoleGrant, Asset, ConfigurationItem,
                     Ticket, TicketResource, Comment, StatusHistory, AuditEvent, OutboxEvent, IdempotencyRecord)
from . import services as s
from .outbox import process_one

class Fixtures:
    @classmethod
    def build_fixtures(cls):
        cls.org=Organization.objects.create(name='Alpha')
        cls.other_org=Organization.objects.create(name='Beta')
        cls.group=Group.objects.create(organization=cls.org,name='Helpdesk',triage=True)
        cls.other_group=Group.objects.create(organization=cls.org,name='Other')
        cls.foreign_group=Group.objects.create(organization=cls.other_org,name='Beta desk',triage=True)
        def person(name,org,roles=(),group=None):
            user=get_user_model().objects.create_user(username=name,password='test-only-password')
            p=Person.objects.create(user=user,organization=org,display_name=name)
            for role in roles:
                RoleGrant.objects.create(organization=org,person=p,role=role)
            if group:
                Membership.objects.create(organization=org,person=p,group=group)
            return p
        cls.employee=person('employee',cls.org)
        cls.peer=person('peer',cls.org)
        cls.agent=person('agent',cls.org,['AGENT','RESOURCE_READER'],cls.group)
        cls.other_agent=person('other-agent',cls.org,['AGENT'],cls.other_group)
        cls.manager=person('manager',cls.org,['SERVICE_MANAGER','AGENT','RESOURCE_READER'],cls.group)
        cls.admin=person('orgadmin',cls.org,['ORG_ADMIN'])
        cls.foreign=person('foreign-manager',cls.other_org,['SERVICE_MANAGER','ORG_ADMIN'],cls.foreign_group)
        cls.asset=Asset.objects.create(organization=cls.org,asset_no='A1',name='Public laptop',portal_visible=True)
        cls.private_asset=Asset.objects.create(organization=cls.org,asset_no='A2',name='Private laptop')
        cls.ci=ConfigurationItem.objects.create(organization=cls.org,ci_no='C1',name='Network',type='NETWORK',portal_visible=True)
        cls.foreign_asset=Asset.objects.create(organization=cls.other_org,asset_no='B1',name='Secret beta',portal_visible=True)

@override_settings(SECURE_SSL_REDIRECT=False)
class WorkflowTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()

    def login(self,p):
        self.client.force_login(p.user)

    def write(self,p,path,data,key=None,method='post',expected=200):
        self.login(p)
        response=getattr(self.client,method)(path,data=json.dumps(data),content_type='application/json',
                            HTTP_IDEMPOTENCY_KEY=key or uuid.uuid4().hex)
        self.assertEqual(response.status_code,expected,response.content.decode())
        return response.json() if expected!=204 else {}

    def create(self,**kwargs):
        return self.write(self.employee,'/api/v1/incidents',{'title':'접속 장애','description':'연결이 되지 않습니다.',
                           'impact':3,'urgency':2,**kwargs},expected=201)

    def assign(self,t):
        return self.write(self.manager,f'/api/v1/incidents/{t["id"]}/assign',{'group_id':str(self.group.id),
                       'assignee_id':str(self.agent.id),'expected_version':t['version']})

    def transition(self,p,t,action,**kwargs):
        return self.write(p,f'/api/v1/incidents/{t["id"]}/transitions',
                          {'action':action,'expected_version':t['version'],**kwargs})

    def started(self):
        return self.transition(self.agent,self.assign(self.create()),'START')

    def test_end_to_end(self):
        t=self.create()
        self.assertEqual(t['priority'],'P4')
        t=self.assign(t)
        t=self.transition(self.agent,t,'START')
        t=self.transition(self.agent,t,'WAIT',reason='내부 대기 사유')
        t=self.transition(self.agent,t,'RESUME')
        t=self.transition(self.agent,t,'RESOLVE',resolution='설정 복구')
        t=self.transition(self.employee,t,'CLOSE',reason='확인했습니다.')
        self.assertEqual(t['status'],'CLOSED')
        self.assertEqual(StatusHistory.objects.count(),7)
        self.assertEqual(AuditEvent.objects.count(),7)
        self.assertEqual(OutboxEvent.objects.count(),7)

    def test_peer_and_foreign_cannot_read(self):
        t=self.create()
        for p in (self.peer,self.foreign,self.admin,self.other_agent):
            self.login(p)
            for suffix in ('','/comments','/activity'):
                r=self.client.get(f'/api/v1/incidents/{t["id"]}'+suffix)
                self.assertEqual(r.status_code,404)
                self.assertNotContains(r,'접속 장애',status_code=404)
            self.assertEqual(self.client.get('/api/v1/incidents?scope=queue').json()['items'],[])

    def test_new_queue_only_triage_manager(self):
        t=self.create()
        self.login(self.agent)
        self.assertEqual(self.client.get('/api/v1/incidents?scope=queue').json()['items'],[])
        self.login(self.manager)
        self.assertEqual(len(self.client.get('/api/v1/incidents?scope=queue').json()['items']),1)

    def test_internal_comments_and_wait_reason_hidden_everywhere(self):
        t=self.started()
        c=self.write(self.agent,f'/api/v1/incidents/{t["id"]}/comments',
                     {'body':'INTERNAL-SECRET','visibility':'INTERNAL','expected_version':t['version']},expected=201)
        t['version']=c['ticket_version']
        t=self.transition(self.agent,t,'WAIT',reason='WAIT-SECRET')
        self.login(self.employee)
        for url in (f'/api/v1/incidents/{t["id"]}',f'/api/v1/incidents/{t["id"]}/comments',
                    f'/api/v1/incidents/{t["id"]}/activity',f'/portal/incidents/{t["id"]}'):
            r=self.client.get(url)
            self.assertEqual(r.status_code,200)
            self.assertNotIn('INTERNAL-SECRET',r.content.decode())
            self.assertNotIn('WAIT-SECRET',r.content.decode())

    def test_internal_comment_injection(self):
        t=self.create()
        self.write(self.employee,f'/api/v1/incidents/{t["id"]}/comments',
                   {'body':'secret','visibility':'INTERNAL','expected_version':1},expected=403)
        self.assertEqual(Comment.objects.count(),0)

    def test_server_owned_field_and_bad_json_rejected(self):
        for field,value in [('priority','P1'),('requested_by',str(self.manager.id)),('organization_id',str(self.other_org.id)),('status','CLOSED')]:
            self.write(self.employee,'/api/v1/incidents',{'title':'x','description':'x','impact':1,'urgency':1,field:value},expected=400)
        self.login(self.employee)
        self.assertEqual(self.client.post('/api/v1/incidents',data='{',content_type='application/json').status_code,400)
        self.assertEqual(Ticket.objects.count(),0)

    def test_create_retry_and_different_payload(self):
        data={'title':'x','description':'y','impact':1,'urgency':1}
        a=self.write(self.employee,'/api/v1/incidents',data,key='same',expected=201)
        b=self.write(self.employee,'/api/v1/incidents',data,key='same',expected=201)
        self.assertEqual(a,b)
        self.write(self.employee,'/api/v1/incidents',{**data,'title':'changed'},key='same',expected=409)
        self.assertEqual(Ticket.objects.count(),1)
        self.assertEqual(StatusHistory.objects.count(),1)

    def test_command_retry_ignores_stale_version_only_for_same_key(self):
        t=self.assign(self.create())
        data={'action':'START','expected_version':t['version']}
        path=f'/api/v1/incidents/{t["id"]}/transitions'
        a=self.write(self.agent,path,data,key='retry')
        b=self.write(self.agent,path,data,key='retry')
        self.assertEqual(a,b)
        self.write(self.agent,path,data,key='new-key',expected=409)
        self.assertEqual(StatusHistory.objects.count(),3)

    def test_invalid_state_and_missing_resolution(self):
        t=self.create()
        self.write(self.employee,f'/api/v1/incidents/{t["id"]}/transitions',{'action':'CLOSE','expected_version':1},expected=409)
        t=self.transition(self.agent,self.assign(t),'START')
        self.write(self.agent,f'/api/v1/incidents/{t["id"]}/transitions',{'action':'RESOLVE','expected_version':t['version']},expected=422)
        self.assertEqual(StatusHistory.objects.count(),3)

    def test_reopen_and_closed_final(self):
        t=self.transition(self.agent,self.started(),'RESOLVE',resolution='done')
        t=self.transition(self.employee,t,'REOPEN',reason='아직 장애가 있습니다.')
        self.assertEqual(t['assignee']['id'],str(self.agent.id))
        self.assertEqual(t['status'],'IN_PROGRESS')
        t=self.transition(self.agent,t,'RESOLVE',resolution='fixed again')
        t=self.transition(self.employee,t,'CLOSE')
        self.write(self.employee,f'/api/v1/incidents/{t["id"]}/transitions',{'action':'REOPEN','reason':'again','expected_version':t['version']},expected=409)

    def test_resource_visibility_cross_org_and_link_lifecycle(self):
        for asset in (self.private_asset,self.foreign_asset):
            self.write(self.employee,'/api/v1/incidents',{'title':'x','description':'x','impact':1,'urgency':1,
                    'resources':[{'resource_type':'ASSET','resource_id':str(asset.id)}]},expected=404)
        t=self.create(resources=[{'resource_type':'ASSET','resource_id':str(self.asset.id)}])
        t=self.assign(t)
        t=self.write(self.agent,f'/api/v1/incidents/{t["id"]}/resources',
                     {'resource_type':'CI','resource_id':str(self.ci.id),'expected_version':t['version']})
        self.assertEqual(len(t['resources']),2)
        link=t['resources'][0]['link_id']
        self.login(self.agent)
        r=self.client.delete(f'/api/v1/incidents/{t["id"]}/resources/{link}?expected_version={t["version"]}',HTTP_IDEMPOTENCY_KEY='delete')
        self.assertEqual(r.status_code,204)
        self.assertEqual(TicketResource.objects.count(),1)

    def test_resource_replay_is_redacted_after_visibility_change(self):
        data={'title':'x','description':'x','impact':1,'urgency':1,
              'resources':[{'resource_type':'ASSET','resource_id':str(self.asset.id)}]}
        self.write(self.employee,'/api/v1/incidents',data,key='create',expected=201)
        Asset.objects.filter(id=self.asset.id).update(portal_visible=False)
        r=self.write(self.employee,'/api/v1/incidents',data,key='create',expected=201)
        self.assertEqual(r['resources'],[])

    def test_membership_and_agent_role_removal_with_open_assignment_blocked(self):
        self.assign(self.create())
        self.write(self.admin,f'/api/v1/admin/groups/{self.group.id}/members/{self.agent.id}',
                   {'active':False,'expected_version':1},method='put',expected=409)
        self.write(self.admin,f'/api/v1/admin/persons/{self.agent.id}/roles',
                   {'roles':[],'expected_version':1},method='put',expected=409)

    def test_admin_protected_and_no_automatic_business_access(self):
        self.write(self.admin,f'/api/v1/admin/persons/{self.admin.id}/roles',{'roles':[],'expected_version':1},method='put',expected=409)
        self.login(self.employee)
        self.assertEqual(self.client.get('/api/v1/admin/access').status_code,403)
        self.login(self.admin)
        self.assertEqual(self.client.get('/api/v1/admin/access').status_code,200)
        self.assertEqual(self.client.get('/api/v1/admin/groups').status_code,200)

    def test_access_mutations(self):
        self.write(self.admin,f'/api/v1/admin/persons/{self.peer.id}/roles',
                   {'roles':['AGENT'],'expected_version':1},method='put')
        self.write(self.admin,f'/api/v1/admin/groups/{self.group.id}/members/{self.peer.id}',
                   {'active':True,'expected_version':1},method='put')
        self.assertIn('AGENT',s.roles(self.peer))
        self.assertTrue(Membership.objects.filter(group=self.group,person=self.peer).exists())

    def test_role_revoked_cannot_replay_admin_response(self):
        path=f'/api/v1/admin/persons/{self.peer.id}/roles'
        data={'roles':['RESOURCE_READER'],'expected_version':1}
        self.write(self.admin,path,data,key='grant',method='put')
        RoleGrant.objects.filter(person=self.admin).delete()
        self.write(self.admin,path,data,key='grant',method='put',expected=403)

    def test_transaction_rolls_back_when_audit_fails(self):
        with patch('desk.services.record',side_effect=IntegrityError('forced')):
            self.write(self.employee,'/api/v1/incidents',{'title':'x','description':'x','impact':1,'urgency':1},expected=409)
        self.assertEqual(Ticket.objects.count(),0)
        self.assertEqual(StatusHistory.objects.count(),0)
        self.assertEqual(IdempotencyRecord.objects.count(),0)

    def test_transaction_rolls_back_after_audit_when_outbox_fails(self):
        with patch('desk.services.OutboxEvent.objects.create',side_effect=IntegrityError('forced')):
            self.write(self.employee,'/api/v1/incidents',{'title':'x','description':'x','impact':1,'urgency':1},expected=409)
        self.assertEqual(Ticket.objects.count(),0)
        self.assertEqual(AuditEvent.objects.count(),0)
        self.assertEqual(StatusHistory.objects.count(),0)

    def test_outbox_retry_and_duplicate_processing(self):
        self.create()
        event=OutboxEvent.objects.get()
        with patch('desk.outbox.deliver',side_effect=RuntimeError('do not store secret')):
            self.assertFalse(process_one(event.id))
        event.refresh_from_db()
        self.assertEqual(event.attempts,1)
        self.assertEqual(event.last_error,'RuntimeError')
        self.assertFalse(process_one(event.id))
        OutboxEvent.objects.filter(id=event.id).update(next_attempt_at=timezone.now()-timedelta(seconds=1))
        with patch('desk.outbox.deliver') as deliver:
            self.assertTrue(process_one(event.id))
            self.assertFalse(process_one(event.id))
            deliver.assert_called_once()

    def test_cursor_scope_filter_endpoint_and_no_duplicates(self):
        for _ in range(3):
            self.create()
        self.login(self.employee)
        first=self.client.get('/api/v1/incidents?limit=1').json()
        cursor=first['next_cursor']
        second=self.client.get('/api/v1/incidents',{'limit':1,'cursor':cursor}).json()
        self.assertNotEqual(first['items'][0]['id'],second['items'][0]['id'])
        self.assertEqual(self.client.get('/api/v1/incidents',{'limit':1,'cursor':cursor,'status':'NEW'}).status_code,400)
        self.assertEqual(self.client.get('/api/v1/assets',{'limit':1,'cursor':cursor}).status_code,400)
        self.login(self.peer)
        self.assertEqual(self.client.get('/api/v1/incidents',{'limit':1,'cursor':cursor}).status_code,400)

    def test_db_organization_guards_and_append_only(self):
        t=self.create()
        with self.assertRaises(IntegrityError),transaction.atomic():
            Ticket.objects.filter(id=t['id']).update(requested_by=self.foreign)
        with self.assertRaises(IntegrityError),transaction.atomic():
            Person.objects.filter(id=self.employee.id).update(organization=self.other_org)
        with self.assertRaises(IntegrityError),transaction.atomic():
            AuditEvent.objects.all().update(action='TAMPERED')
        with self.assertRaises(IntegrityError),transaction.atomic():
            AuditEvent.objects.all().delete()

    def test_csrf_and_origin(self):
        client=Client(enforce_csrf_checks=True)
        client.force_login(self.employee.user)
        url='/api/v1/incidents'
        data=json.dumps({'title':'x','description':'x','impact':1,'urgency':1})
        self.assertEqual(client.post(url,data=data,content_type='application/json').status_code,403)
        client.get('/portal/incidents/new')
        token=client.cookies['csrftoken'].value
        self.assertEqual(client.post(url,data=data,content_type='application/json',HTTP_X_CSRFTOKEN=token,
                 HTTP_IDEMPOTENCY_KEY='csrf',HTTP_ORIGIN='https://evil.example').status_code,403)
        self.assertEqual(client.post(url,data=data,content_type='application/json',HTTP_X_CSRFTOKEN=token,
                 HTTP_IDEMPOTENCY_KEY='csrf').status_code,201)

    def test_anonymous_and_inactive(self):
        self.assertEqual(self.client.get('/api/v1/me').status_code,401)
        self.login(self.employee)
        Person.objects.filter(id=self.employee.id).update(active=False)
        self.assertEqual(self.client.get('/api/v1/me').status_code,403)

    def test_read_resource_and_me(self):
        self.login(self.employee)
        self.assertEqual(self.client.get('/api/v1/me').json()['organization']['name'],'Alpha')
        for url in ('/api/v1/assets','/api/v1/cis',f'/api/v1/assets/{self.asset.id}',f'/api/v1/cis/{self.ci.id}'):
            self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(len(self.client.get('/api/v1/assets').json()['items']),1)
        self.assertEqual(self.client.get(f'/api/v1/assets/{self.private_asset.id}').status_code,404)

    def test_html_all_views_and_escaping(self):
        t=self.create(title='<script>alert(1)</script>')
        for p,urls in [(self.employee,['/portal/incidents','/portal/incidents/new',f'/portal/incidents/{t["id"]}','/assets','/cis']),
                       (self.manager,['/work/incidents',f'/work/incidents/{t["id"]}']),
                       (self.admin,['/admin/access'])]:
            self.login(p)
            for url in urls:
                response=self.client.get(url)
                self.assertEqual(response.status_code,200,response.content.decode())
                self.assertNotIn('<script>alert(1)</script>',response.content.decode())

    def test_empty_and_oversize_fields_and_type_validation(self):
        for data in ({'title':' '},{'impact':True},{'urgency':4},{'title':'x'*201},{'resources':{}}, {'resources':[None]}):
            self.write(self.employee,'/api/v1/incidents',{'title':'x','description':'x','impact':1,'urgency':1,**data},expected=400 if data=={'resources':[None]} else 422)
        self.assertEqual(Ticket.objects.count(),0)

    def test_missing_key_and_wrong_method(self):
        self.login(self.employee)
        self.assertEqual(self.client.post('/api/v1/incidents',data='{}',content_type='application/json').status_code,400)
        self.assertEqual(self.client.delete('/api/v1/me').status_code,405)

    def test_login_and_logout_require_real_session_and_csrf(self):
        client=Client(enforce_csrf_checks=True)
        client.get('/login/')
        token=client.cookies['csrftoken'].value
        r=client.post('/login/',{'username':'employee','password':'test-only-password','csrfmiddlewaretoken':token})
        self.assertEqual(r.status_code,302)
        self.assertEqual(client.get('/api/v1/me').status_code,200)
        self.assertEqual(client.get('/logout/').status_code,405)
        token=client.cookies['csrftoken'].value
        self.assertEqual(client.post('/logout/',{'csrfmiddlewaretoken':token}).status_code,302)
        self.assertEqual(client.get('/api/v1/me').status_code,401)

@skipUnless(connection.vendor=='postgresql','Real concurrent row-lock validation requires PostgreSQL.')
@override_settings(SECURE_SSL_REDIRECT=False)
class ConcurrencyTests(Fixtures,TransactionTestCase):
    def setUp(self):
        self.build_fixtures()

    def test_two_real_connections_one_version_wins(self):
        t,_=s.execute(self.employee,'create',{'title':'concurrent','description':'x','impact':1,'urgency':1},'create',uuid.uuid4())
        t,_=s.execute(self.manager,'assign',{'group_id':str(self.group.id),'assignee_id':str(self.agent.id),'expected_version':1},'assign',uuid.uuid4(),uuid.UUID(t['id']))
        def work(key):
            close_old_connections()
            try:
                p=Person.objects.get(id=self.agent.id)
                try:
                    s.execute(p,'transition',{'action':'START','expected_version':2},key,uuid.uuid4(),uuid.UUID(t['id']))
                    return 200
                except s.BusinessError as exc:
                    return exc.status
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(work,['a','b']))
        self.assertEqual(sorted(results),[200,409])
        self.assertEqual(StatusHistory.objects.count(),3)

    def test_concurrent_same_key_creates_once(self):
        def work(_):
            close_old_connections()
            try:
                p=Person.objects.get(id=self.employee.id)
                result,_=s.execute(p,'create',{'title':'same','description':'x','impact':1,'urgency':1},'same',uuid.uuid4())
                return result['id']
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(work,range(2)))
        self.assertEqual(results[0],results[1])
        self.assertEqual(Ticket.objects.count(),1)
        self.assertEqual(AuditEvent.objects.count(),1)
