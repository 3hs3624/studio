import json,uuid,time,hashlib
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import connection,IntegrityError,transaction
from django.test import TestCase,Client,override_settings
from django.utils import timezone
from .tests import Fixtures
from .models import (Person,UserProfile,RoleDefinition,CustomRoleGrant,Group,CredentialState,LoginSession,
 SecurityPolicy,PrivacyAccessEvent,PasswordHistory,IdempotencyRecord,AuditEvent)
from .security_policy import policy,state
from . import mfa


@override_settings(SECURE_SSL_REDIRECT=False)
class IdentitySecurityTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):cls.build_fixtures()
    def setUp(self):self.client.force_login(self.admin.user)
    def post(self,kind,value,id=None,key=None):
        return self.client.post('/api/v1/management/'+kind+('/'+str(id) if id else ''),json.dumps(value),content_type='application/json',HTTP_IDEMPOTENCY_KEY=key or str(uuid.uuid4()))
    def role(self,permissions=None,code='READ_ENTITY'):
        result=self.post('roles',dict(code=code,name='조회 담당',description='',permissions=permissions or ['console.access','entity.read'],active=True,expected_version=0,reason='정의'))
        self.assertEqual(result.status_code,200,result.content);return RoleDefinition.objects.get(id=result.json()['id'])
    def apply(self,category,values):
        current=policy(self.org,category);current.update(values)
        saved=SecurityPolicy.objects.filter(organization=self.org,category=category).first()
        return self.post('policies',dict(configuration=current,expected_version=saved.row_version if saved else 0,reason='정책 적용',apply_confirmed=True),category)
    def test_profile_separation_and_database_rejection(self):
        self.assertEqual(self.admin.display_name,self.admin.profile.full_name)
        self.assertNotIn('display_name',[field.name for field in Person._meta.fields])
        with connection.cursor() as cursor:
            cursor.execute('SELECT display_name FROM desk_person WHERE id=%s',[self.admin.id.hex if connection.vendor=='sqlite' else self.admin.id])
            self.assertEqual(cursor.fetchone()[0],'')
        with self.assertRaises(IntegrityError),transaction.atomic():
            get_user_model().objects.filter(id=self.admin.user_id).update(email='leak@example.com')
        with self.assertRaises(IntegrityError),transaction.atomic():
            UserProfile.objects.filter(person=self.admin).update(organization=self.other_org)
    def test_masked_contact_read_reveal_and_access_audit(self):
        UserProfile.objects.filter(person=self.employee).update(email='alice@example.com',phone='01012345678')
        response=self.client.get('/console/users/'+str(self.employee.id))
        self.assertNotContains(response,'alice@example.com');self.assertContains(response,'a***@example.com')
        self.assertContains(self.client.get('/console/users/'+str(self.employee.id)+'?reveal=1'),'alice@example.com')
        self.assertEqual(PrivacyAccessEvent.objects.filter(subject=self.employee).count(),2)
        self.assertContains(self.client.get('/console/users?q=employee'),'employee')
        self.client.force_login(self.foreign.user)
        self.assertEqual(self.client.get('/console/users/'+str(self.employee.id)).status_code,404)
    def test_create_user_and_force_password_change(self):
        value=dict(username='new-user',full_name='신규 사용자',email='new@example.com',invite=False,password='Fresh-Secret-8391!',reason='생성')
        result=self.post('users',value)
        self.assertEqual(result.status_code,200,result.content)
        member=Person.objects.get(id=result.json()['id'])
        self.assertEqual(member.profile.email,'new@example.com');self.assertEqual(member.user.email,'')
        cache=IdempotencyRecord.objects.filter(operation__startswith='manage_user_create').get()
        self.assertNotIn('Fresh-Secret',str(cache.response_body));self.assertNotIn('new@example.com',str(cache.response_body))
        client=Client();self.assertTrue(client.login(username='new-user',password=value['password']))
        self.assertEqual(client.get('/api/v1/me').json()['error']['code'],'PASSWORD_CHANGE_REQUIRED')
        response=client.post('/account/security',dict(action='password',current_password=value['password'],new_password='Better-Secret-9102!',confirm_password='Better-Secret-9102!'))
        self.assertEqual(response.status_code,200);self.assertEqual(client.get('/api/v1/me').status_code,200)
        self.assertEqual(PasswordHistory.objects.filter(person=member).count(),2)
    def test_invitation_does_not_store_token_and_is_one_use(self):
        result=self.post('users',dict(username='invited',full_name='초대 사용자',invite=True,reason='초대'))
        member=Person.objects.get(id=result.json()['id'])
        response=self.post('user-invite',dict(expected_version=member.row_version,reason='링크 발급'),member.id)
        self.assertEqual(response.status_code,200,response.content)
        url=response.json()['invitation_url'];from urllib.parse import urlsplit
        token=urlsplit(url).fragment;url=urlsplit(url).path
        self.assertFalse(IdempotencyRecord.objects.filter(response_body__icontains=token).exists())
        client=Client();response=client.post(url,dict(token=token,new_password='Invite-Secret-4910!',confirm_password='Invite-Secret-4910!'))
        self.assertEqual(response.status_code,302,response.content)
        self.assertEqual(client.post(url,dict(token=token,new_password='Other-Secret-9102!',confirm_password='Other-Secret-9102!')).status_code,400)
    def test_custom_roles_enforce_read_write_and_scope(self):
        role=self.role()
        result=self.post('role-grant',dict(person_id=str(self.employee.id),active=True,expected_version=1,reason='배정'),role.id)
        self.assertEqual(result.status_code,200,result.content)
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/console/entities').status_code,200)
        self.assertEqual(self.client.get('/console/codes').status_code,403)
        self.assertEqual(self.client.get('/admin/plugins').status_code,403)
        response=self.client.post('/api/v1/admin/entities','{}',content_type='application/json',HTTP_IDEMPOTENCY_KEY='denied')
        self.assertEqual(response.status_code,403)
        self.client.force_login(self.admin.user)
        role.refresh_from_db()
        self.assertEqual(self.post('role-delete',dict(expected_version=role.row_version,reason='삭제'),role.id).status_code,409)
        result=self.post('roles',dict(code=role.code,name=role.name,description='',permissions=role.permissions,active=False,expected_version=role.row_version,reason='중지'),role.id)
        self.assertEqual(result.status_code,200)
    def test_delegated_iam_cannot_escalate_or_reset_sysadmin(self):
        role=self.role(['console.access','iam.manage'],'IAM_DELEGATE')
        self.post('role-grant',dict(person_id=str(self.employee.id),active=True,expected_version=1,reason='배정'),role.id)
        self.client.force_login(self.employee.user)
        result=self.post('roles',dict(code='BAD',name='상위 권한',description='',permissions=['console.access','security.manage'],active=True,expected_version=0,reason='시도'))
        self.assertEqual(result.status_code,403)
        result=self.client.put('/api/v1/admin/persons/'+str(self.employee.id)+'/roles',json.dumps(dict(roles=['ORG_ADMIN'],expected_version=2,reason='시도')),content_type='application/json',HTTP_IDEMPOTENCY_KEY='escalate')
        self.assertEqual(result.status_code,403)
        self.assertEqual(self.post('user-reset',dict(password='Fake-Secret-1910!',expected_version=1,reason='시도'),self.admin.id).status_code,403)
    def test_group_lifecycle_and_triage_protection(self):
        result=self.post('groups',dict(code='NETWORK',name='네트워크 운영',description='',active=True,expected_version=0,reason='생성'))
        self.assertEqual(result.status_code,200,result.content);group=Group.objects.get(id=result.json()['id'])
        self.assertEqual(self.post('group-delete',dict(expected_version=group.row_version,reason='삭제'),group.id).status_code,200)
        self.assertFalse(Group.objects.filter(id=group.id).exists())
        self.assertEqual(self.post('group-delete',dict(expected_version=1,reason='삭제'),self.group.id).status_code,409)
    def test_policy_preview_and_floor(self):
        config=policy(self.org,'password');config['min_length']=12
        result=self.post('policy-preview',dict(configuration=config,expected_version=0,reason='검증'), 'password')
        self.assertEqual(result.status_code,200,result.content);self.assertFalse(SecurityPolicy.objects.exists())
        self.assertEqual(self.apply('password',{'min_length':7}).status_code,422)
        self.assertEqual(self.apply('audit',{'mask_contacts':False}).status_code,422)
        self.assertEqual(self.apply('password',{'min_length':12}).status_code,200)
        self.assertEqual(policy(self.org,'password')['min_length'],12)
        for path in ['/console/security','/console/security/password','/console/security/password?tab=checks']:
            self.assertEqual(self.client.get(path).status_code,200,path)
    def test_shared_lockout_and_admin_unlock(self):
        self.apply('login',{'max_failures':3})
        for _ in range(3):
            client=Client();self.assertFalse(client.login(username=self.employee.user.username,password='wrong'))
        self.assertFalse(Client().login(username=self.employee.user.username,password='test-only-password'))
        self.employee.refresh_from_db()
        self.assertEqual(self.post('user-unlock',dict(expected_version=self.employee.row_version,reason='해제'),self.employee.id).status_code,200)
        self.assertTrue(Client().login(username=self.employee.user.username,password='test-only-password'))
    def test_password_rules_history_and_expiration(self):
        breached='Compromised-Password-930!'
        self.apply('password',dict(min_length=12,require_digit=True,blocked_sha256=hashlib.sha256(breached.encode()).hexdigest(),max_age_days=30))
        client=Client();client.force_login(self.employee.user)
        for value in ['short',breached,'NoDigits-Long-Password!']:
            result=client.post('/account/security',dict(action='password',current_password='test-only-password',new_password=value,confirm_password=value))
            self.assertContains(result,'error',html=False)
            self.employee.user.refresh_from_db();self.assertTrue(self.employee.user.check_password('test-only-password'))
        CredentialState.objects.filter(person=self.employee).update(password_changed_at=timezone.now()-timedelta(days=31))
        self.assertEqual(client.get('/api/v1/me').json()['error']['code'],'PASSWORD_CHANGE_REQUIRED')
    def test_sessions_reauth_and_period_expiry(self):
        self.apply('session',{'idle_minutes':5,'max_sessions':1})
        client=Client();client.force_login(self.employee.user)
        other=Client();other.force_login(self.employee.user)
        self.assertEqual(client.get('/api/v1/me').status_code,403)
        LoginSession.objects.filter(person=self.employee,revoked=False).update(last_seen_at=timezone.now()-timedelta(minutes=6))
        self.assertEqual(other.get('/api/v1/me').status_code,403)
        session=self.client.session;session['recent_auth_at']=0;session.save()
        self.assertEqual(self.apply('session',{'idle_minutes':10}).json()['error']['code'],'REAUTH_REQUIRED')
        self.client.force_login(self.admin.user)
        self.assertEqual(self.post('users',dict(full_name=self.admin.display_name,expires_on=timezone.localdate().isoformat(),expected_version=self.admin.row_version,reason='종료'),self.admin.id).status_code,409)
    def test_mfa_encryption_replay_and_required_policy(self):
        self.assertEqual(self.apply('access',{'admin_mfa_required':True}).status_code,409)
        response=self.client.get('/account/security');secret=response.context['mfa_secret']
        otp=mfa.token(secret,int(time.time())//30)
        response=self.client.post('/account/security',dict(action='mfa_enroll',current_password='test-only-password',otp=otp))
        self.assertContains(response,'MFA를 등록했습니다')
        credential=state(self.admin);self.assertNotIn(secret,credential.mfa_secret)
        self.assertGreaterEqual(credential.mfa_last_counter,int(time.time())//30-1)
        self.assertIsNone(mfa.verify(secret,otp,credential.mfa_last_counter))
        self.assertEqual(self.apply('access',{'admin_mfa_required':True}).status_code,200)
        other=Client();response=other.post('/login/',dict(username=self.admin.user.username,password='test-only-password'))
        self.assertEqual(response.status_code,302);self.assertEqual(response.url,'/login/mfa/')
        self.assertFalse(other.session.get('_auth_user_id'))
        self.assertTrue(response.context is None)
    def test_ip_policy_self_lockout_and_forwarded_spoof(self):
        self.assertEqual(self.apply('access',{'admin_allowed_cidrs':'192.0.2.0/24'}).status_code,409)
        self.assertEqual(self.apply('access',{'admin_allowed_cidrs':'127.0.0.1/32'}).status_code,200)
        response=self.client.get('/console/security',REMOTE_ADDR='192.0.2.12',HTTP_X_FORWARDED_FOR='127.0.0.1')
        self.assertEqual(response.status_code,403)
    def test_personal_names_are_not_in_idempotency_cache(self):
        response=self.client.post('/api/v1/incidents',json.dumps(dict(title='request',description='x',impact=1,urgency=1)),content_type='application/json',HTTP_IDEMPOTENCY_KEY='privacy')
        self.assertEqual(response.status_code,201,response.content)
        saved=IdempotencyRecord.objects.get(operation__startswith='create:')
        self.assertNotIn(self.admin.display_name,str(saved.response_body))
        repeat=self.client.post('/api/v1/incidents',json.dumps(dict(title='request',description='x',impact=1,urgency=1)),content_type='application/json',HTTP_IDEMPOTENCY_KEY='privacy')
        self.assertEqual(repeat.json(),response.json())

    def test_mfa_recovery_code_login_and_single_use(self):
        self.client.get('/account/security')
        secret=mfa.decrypt(self.client.session['pending_mfa_seed'])
        otp=mfa.token(secret,int(time.time())//30)
        response=self.client.post('/account/security',dict(action='mfa_enroll',current_password='test-only-password',otp=otp))
        recovery=response.context['recovery_codes'][0]
        client=Client();self.assertEqual(client.post('/login/',dict(username=self.admin.user.username,password='test-only-password')).url,'/login/mfa/')
        self.assertEqual(client.post('/login/mfa/',dict(otp=recovery)).status_code,302)
        self.assertEqual(client.get('/api/v1/me').status_code,200)
        second=Client();second.post('/login/',dict(username=self.admin.user.username,password='test-only-password'))
        self.assertEqual(second.post('/login/mfa/',dict(otp=recovery)).status_code,200)
        self.assertFalse(second.session.get('_auth_user_id'))
    def test_existing_policy_forces_change_and_erasure_preserves_identity(self):
        self.assertEqual(self.apply('password',{'enforce_existing':True,'min_length':12}).status_code,200)
        self.assertEqual(self.client.get('/api/v1/me').json()['error']['code'],'PASSWORD_CHANGE_REQUIRED')
        response=self.client.post('/account/security',dict(action='password',current_password='test-only-password',new_password='Strong-New-Password-1930!',confirm_password='Strong-New-Password-1930!'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.client.get('/api/v1/me').status_code,200)
        self.employee.active=False;self.employee.save(update_fields=['active'])
        UserProfile.objects.filter(person=self.employee).update(email='remove@example.com')
        result=self.post('user-erase',dict(expected_version=self.employee.row_version,reason='파기 요청'),self.employee.id)
        self.assertEqual(result.status_code,200,result.content)
        self.employee.refresh_from_db();self.assertEqual(self.employee.id,self.employee.profile.person_id)
        self.assertEqual(self.employee.profile.email,'');self.assertEqual(self.employee.display_name,'삭제된 사용자')
    def test_stale_replayed_role_operation_does_not_restore_revoked_access(self):
        role=self.role(['console.access','code.read'],'READ_CODE')
        grant=dict(person_id=str(self.employee.id),active=True,expected_version=1,reason='배정')
        first=self.post('role-grant',grant,role.id,key='role-once')
        self.assertEqual(first.status_code,200)
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/api/v1/admin/code-groups').status_code,200)
        self.assertEqual(self.client.post('/api/v1/admin/code-groups','{}',content_type='application/json',HTTP_IDEMPOTENCY_KEY='write').status_code,403)
        role.active=False;role.save(update_fields=['active'])
        self.assertEqual(self.client.get('/api/v1/admin/code-groups').status_code,403)
