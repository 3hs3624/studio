import json
import uuid
from django.test import Client, TestCase, override_settings
from django.db import IntegrityError, transaction
from .tests import Fixtures
from .models import Person, RoleGrant, SecurityEvent, AuditEvent
from . import services as s
from .security import SESSION_KEY

@override_settings(SECURE_SSL_REDIRECT=False)
class AccountSecurityTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls): cls.build_fixtures()

    def command(self,op,person,data,key=None):
        return s.execute(self.admin,op,data,key or uuid.uuid4().hex,str(uuid.uuid4()),person.id)

    def test_all_sessions_revoked_and_new_login_allowed(self):
        clients=[Client(),Client()]
        for c in clients:
            c.force_login(self.employee.user)
            self.assertEqual(c.get('/api/v1/me').status_code,200)
        self.command('admin_revoke_sessions',self.employee,{'expected_version':1,'reason':'단말 분실'})
        for c in clients:
            response=c.get('/api/v1/me')
            self.assertEqual(response.json()['error']['code'],'SESSION_REVOKED')
            self.assertEqual(c.get('/api/v1/me').status_code,401)
        clients[0].force_login(self.employee.user)
        self.assertEqual(clients[0].get('/api/v1/me').status_code,200)
        self.assertEqual(SecurityEvent.objects.filter(action='SESSION_REVOKED').count(),2)

    def test_suspend_reactivate_does_not_restore_old_session(self):
        c=Client();c.force_login(self.employee.user)
        self.command('admin_account',self.employee,{'active':False,'expected_version':1,'reason':'퇴사'})
        self.command('admin_account',self.employee,{'active':True,'expected_version':2,'reason':'재입사'})
        self.assertEqual(c.get('/api/v1/me').status_code,403)
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.active)
        event=AuditEvent.objects.filter(action='ACCOUNT_CHANGED').last()
        self.assertNotIn('session_epoch',event.after_data)

    def test_role_remove_and_restore_cannot_restore_old_session(self):
        c=Client();c.force_login(self.agent.user)
        self.command('admin_roles',self.agent,{'roles':[],'expected_version':1})
        self.command('admin_roles',self.agent,{'roles':['AGENT'],'expected_version':2})
        self.assertEqual(c.get('/api/v1/me').status_code,403)

    def test_unbound_legacy_session_and_org_shutdown(self):
        c=Client();c.force_login(self.employee.user)
        session=c.session;session.pop(SESSION_KEY);session.save()
        self.assertEqual(c.get('/api/v1/me').status_code,403)
        c.force_login(self.employee.user)
        self.org.active=False;self.org.save()
        self.assertEqual(c.get('/api/v1/me').status_code,403)

    def test_admin_only_org_scope_and_version(self):
        c=Client();c.force_login(self.employee.user)
        url=f'/api/v1/admin/persons/{self.peer.id}/account'
        response=c.post(url,json.dumps({'active':False,'reason':'x','expected_version':1}),content_type='application/json',HTTP_IDEMPOTENCY_KEY='a')
        self.assertEqual(response.status_code,403)
        for person,version,code in [(self.foreign,1,'NOT_FOUND'),(self.peer,99,'VERSION_CONFLICT')]:
            with self.assertRaises(s.BusinessError) as err:
                self.command('admin_account',person,{'active':False,'reason':'x','expected_version':version})
            self.assertEqual(err.exception.code,code)

    def test_self_and_last_admin_protected(self):
        with self.assertRaises(s.BusinessError) as err:
            self.command('admin_account',self.admin,{'active':False,'expected_version':1,'reason':'x'})
        self.assertEqual(err.exception.code,'ADMIN_PROTECTED')

    def test_revoke_idempotency_does_not_rotate_again(self):
        data={'expected_version':1,'reason':'x'}
        a=self.command('admin_revoke_sessions',self.peer,data,'same')
        self.peer.refresh_from_db();epoch=self.peer.session_epoch
        self.assertEqual(a,self.command('admin_revoke_sessions',self.peer,data,'same'))
        self.peer.refresh_from_db();self.assertEqual(epoch,self.peer.session_epoch)
        self.assertEqual(AuditEvent.objects.filter(action='SESSIONS_REVOKED').count(),1)

    def test_command_rechecks_binding_under_lock(self):
        from .security import binding
        self.employee._session_binding=binding(self.employee)
        self.command('admin_revoke_sessions',self.employee,{'expected_version':1,'reason':'x'})
        with self.assertRaises(s.BusinessError) as err:
            s.execute(self.employee,'create',{'title':'x','description':'x','impact':1,'urgency':1},'stale',str(uuid.uuid4()))
        self.assertEqual(err.exception.code,'SESSION_REVOKED')

    def test_login_failure_has_no_credentials_and_event_is_immutable(self):
        c=Client()
        c.post('/login/',{'username':'sensitive-username','password':'sensitive-password'})
        event=SecurityEvent.objects.get(action='LOGIN_FAILED')
        self.assertIsNone(event.organization_id);self.assertIsNone(event.person_id)
        self.assertNotIn('sensitive',str(event.__dict__))
        with self.assertRaises(IntegrityError),transaction.atomic():
            SecurityEvent.objects.filter(id=event.id).update(action='TAMPERED')

    def test_events_and_management_ui_organization_scoped(self):
        c=Client();c.force_login(self.foreign.user)
        c.force_login(self.admin.user)
        result=c.get('/api/v1/admin/security-events')
        self.assertEqual(result.status_code,200)
        self.assertNotIn(str(self.foreign.id),result.content.decode())
        html=c.get('/admin/access?tab=accounts')
        self.assertContains(html,'모든 기존 세션 회수')

    def test_open_assignment_blocks_suspension(self):
        ticket,_=s.execute(self.employee,'create',{'title':'x','description':'x','impact':1,'urgency':1},'new',str(uuid.uuid4()))
        s.execute(self.manager,'assign',{'group_id':str(self.group.id),'assignee_id':str(self.agent.id),'expected_version':1},'assign',str(uuid.uuid4()),s.identifier(ticket['id']))
        with self.assertRaises(s.BusinessError) as err:
            self.command('admin_account',self.agent,{'active':False,'expected_version':1,'reason':'x'})
        self.assertEqual(err.exception.code,'OPEN_ASSIGNMENTS')
        self.agent.refresh_from_db();self.assertTrue(self.agent.active)

    def test_group_change_revokes_existing_session(self):
        c=Client();c.force_login(self.agent.user)
        s.execute(self.admin,'admin_members',{'active':False,'expected_version':1},'remove',str(uuid.uuid4()),self.group.id,self.agent.id)
        self.assertEqual(c.get('/api/v1/me').status_code,403)

    def test_api_csrf_is_required_for_revocation(self):
        c=Client(enforce_csrf_checks=True);c.force_login(self.admin.user)
        response=c.post(f'/api/v1/admin/persons/{self.peer.id}/revoke-sessions',json.dumps({'expected_version':1,'reason':'x'}),content_type='application/json',HTTP_IDEMPOTENCY_KEY='csrf')
        self.assertEqual(response.status_code,403)
        self.peer.refresh_from_db();self.assertEqual(self.peer.row_version,1)

from unittest import skipUnless
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from django.db import connection, close_old_connections
from django.test import TransactionTestCase

@skipUnless(connection.vendor=='postgresql','PostgreSQL row locking required')
class AccountSecurityRaceTests(Fixtures,TransactionTestCase):
    def setUp(self): self.build_fixtures()

    def test_waiting_command_is_rejected_after_revocation_commits(self):
        from .security import binding
        from .models import Organization, Ticket
        snapshot=binding(self.employee)
        started=Event()
        def write():
            close_old_connections()
            try:
                actor=Person.objects.get(id=self.employee.id)
                actor._session_binding=snapshot
                started.set()
                try:
                    s.execute(actor,'create',{'title':'stale','description':'x','impact':1,'urgency':1},'race-write',str(uuid.uuid4()))
                    return 'CREATED'
                except s.BusinessError as exc:
                    return exc.code
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=1) as pool:
            with transaction.atomic():
                Organization.objects.select_for_update().get(id=self.org.id)
                future=pool.submit(write)
                self.assertTrue(started.wait(5))
                s.execute(self.admin,'admin_revoke_sessions',{'expected_version':1,'reason':'race'},'race-revoke',str(uuid.uuid4()),self.employee.id)
            self.assertEqual(future.result(timeout=15),'SESSION_REVOKED')
        self.assertFalse(Ticket.objects.exists())
