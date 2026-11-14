import json,uuid
from django.test import TestCase,override_settings
from django.db import IntegrityError,transaction
from django.contrib.auth import get_user_model
from .tests import Fixtures
from .models import Department,GroupDepartment,ScopedRoleGrant,RoleMenuPolicy,RoleGrant,CustomRoleGrant,Membership,RoleDefinition,Person,Organization
from .permissions import effective,allowed
from .access_graph import role_rows,effective_groups
from .menu_access import PUBLIC,menu_keys
from . import services as s

@override_settings(SECURE_SSL_REDIRECT=False)
class OrganizationAccessTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):cls.build_fixtures()
    def setUp(self):
        self.client.force_login(self.admin.user)
        self.dep=Department.objects.create(organization=self.org,code='IT',name='IT부서')
        self.child=Department.objects.create(organization=self.org,code='DEV',name='개발팀',parent=self.dep)
    def post(self,kind,data,id=None):
        return self.client.post('/api/v1/management/'+kind+('/'+str(id) if id else ''),json.dumps(data),content_type='application/json',HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()))
    def orgpost(self,kind,data,id=None):
        self.org.refresh_from_db();return self.post('org-'+kind,{'expected_version':self.org.access_version,'reason':'구성 변경',**data},id)
    def target(self,key,**kwargs):
        return self.orgpost('role-targets',{'person_ids':[],'department_ids':[],'group_ids':[],'include_children':False,**kwargs},key)
    def preview(self,kind,id):return self.client.get('/api/v1/organization-access/copy',{'kind':kind,'id':str(id)})
    def new(self,**kwargs):return self.post('users',dict(username='new-copy',full_name='새 사용자',email='new@example.com',invite=True,reason='복제 생성',**kwargs))
    def test_department_inheritance_and_provenance(self):
        self.employee.department=self.child;self.employee.save()
        grant=ScopedRoleGrant.objects.create(organization=self.org,role_key='RESOURCE_READER',department=self.dep)
        self.assertFalse(allowed(self.employee,'asset.read'))
        grant.include_children=True;grant.save()
        self.assertTrue(allowed(self.employee,'asset.read'))
        row=next(r for r in role_rows(self.employee) if r['key']=='RESOURCE_READER')
        self.assertIn('부서 IT부서 (하위 포함)',row['paths'])
        RoleGrant.objects.create(organization=self.org,person=self.employee,role='RESOURCE_READER')
        grant.delete();self.assertTrue(allowed(self.employee,'asset.read'))
    def test_group_department_inheritance_does_not_grant_processing(self):
        self.employee.department=self.dep;self.employee.save()
        GroupDepartment.objects.create(organization=self.org,group=self.other_group,department=self.dep)
        ScopedRoleGrant.objects.create(organization=self.org,group=self.other_group,role_key='ASSET_MANAGER')
        self.assertIn(str(self.other_group.id),effective_groups(self.employee))
        self.assertTrue(allowed(self.employee,'asset.manage'));self.assertEqual(s.group_ids(self.employee),[])
        ScopedRoleGrant.objects.create(organization=self.org,department=self.dep,role_key='AGENT')
        self.assertIn(self.other_group.id,s.group_ids(self.employee))
    def test_role_and_group_assignment_endpoints(self):
        result=self.target('RESOURCE_READER',department_ids=[str(self.dep.id)])
        self.assertEqual(result.status_code,200,result.content)
        self.assertTrue(ScopedRoleGrant.objects.filter(department=self.dep).exists())
        result=self.orgpost('group-targets',dict(person_ids=[str(self.employee.id)],department_ids=[str(self.dep.id)],include_children=True),self.other_group.id)
        self.assertEqual(result.status_code,200,result.content)
        self.assertTrue(Membership.objects.filter(group=self.other_group,person=self.employee).exists())
        for tab in ('roles','groups','menus','departments','history'):
            self.assertEqual(self.client.get('/console/access?tab='+tab).status_code,200,tab)
    def test_menu_mapping_blocks_url_and_api(self):
        result=self.orgpost('menus',dict(menu_keys=sorted(PUBLIC-{'incidents'}),console_button=False),'EVERYONE')
        self.assertEqual(result.status_code,200,result.content)
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/portal/incidents').status_code,403)
        self.assertEqual(self.client.get('/api/v1/incidents').status_code,403)
        self.assertNotContains(self.client.get('/systems/service'),'href="/portal/incidents"')
    def test_console_button_mapping_and_admin_recovery(self):
        RoleGrant.objects.create(organization=self.org,person=self.employee,role='DEVELOPER')
        result=self.orgpost('menus',dict(menu_keys=['entities'],console_button=False),'DEVELOPER')
        self.assertEqual(result.status_code,200,result.content)
        self.assertFalse(allowed(self.employee,'console.access'))
        self.client.force_login(self.employee.user);self.assertEqual(self.client.get('/console/entities').status_code,403)
        self.client.force_login(self.admin.user)
        self.assertEqual(self.orgpost('menus',dict(menu_keys=[],console_button=False),'ORG_ADMIN').status_code,409)
    def test_copy_user_allocations_only_and_independent(self):
        data=self.preview('user',self.manager.id).json()
        result=self.new(allocation_token=data['token'],role_keys=[r['key'] for r in data['roles']],group_ids=[g['id'] for g in data['groups']])
        self.assertEqual(result.status_code,200,result.content)
        member=Person.objects.get(id=result.json()['id']);self.assertEqual(member.profile.email,'new@example.com')
        self.assertFalse(member.user.has_usable_password());self.assertTrue(allowed(member,'service.manage'))
        RoleGrant.objects.filter(person=self.manager).delete();Membership.objects.filter(person=self.manager).delete()
        self.assertTrue(allowed(member,'service.manage'));self.assertTrue(effective_groups(member))
    def test_department_copy_and_automatic_inheritance(self):
        ScopedRoleGrant.objects.create(organization=self.org,role_key='RESOURCE_READER',department=self.dep)
        GroupDepartment.objects.create(organization=self.org,group=self.other_group,department=self.dep)
        data=self.preview('department',self.dep.id).json();self.assertEqual(len(data['roles']),1)
        result=self.new(department_id=str(self.dep.id))
        self.assertEqual(result.status_code,200,result.content)
        member=Person.objects.get(id=result.json()['id']);self.assertTrue(allowed(member,'asset.read'))
        self.assertFalse(RoleGrant.objects.filter(person=member).exists())
        response=self.client.get('/console/access?tab=departments&selected='+str(self.dep.id))
        self.assertContains(response,self.other_group.name);self.assertContains(response,'자산·구성 조회')
    def test_copy_stale_or_foreign_rolls_back_new_user(self):
        data=self.preview('user',self.manager.id).json()
        RoleGrant.objects.filter(person=self.manager,role='AGENT').delete()
        result=self.new(allocation_token=data['token'],role_keys=['SERVICE_MANAGER'],group_ids=[])
        self.assertEqual(result.status_code,409,result.content);self.assertFalse(get_user_model().objects.filter(username='new-copy').exists())
        self.assertEqual(self.preview('user',self.foreign.id).status_code,404)
    def test_department_cycle_and_foreign_guard(self):
        with self.assertRaises(IntegrityError),transaction.atomic():Department.objects.filter(pk=self.dep.id).update(parent=self.child)
        other=Department.objects.create(organization=self.other_org,code='OTHER',name='다른 조직')
        with self.assertRaises(IntegrityError),transaction.atomic():Department.objects.filter(pk=self.dep.id).update(parent=other)
        with self.assertRaises(IntegrityError),transaction.atomic():Person.objects.filter(pk=self.employee.id).update(department=other)
        response=self.orgpost('department',dict(code='IT',name='IT',parent_id=str(self.child.id),active=True),self.dep.id)
        self.assertEqual(response.status_code,422)
    def test_delegation_cannot_gain_admin_through_department_or_group(self):
        role=RoleDefinition.objects.create(organization=self.org,code='IAM',name='위임 관리자',permissions=['console.access','iam.manage','users.manage'])
        CustomRoleGrant.objects.create(organization=self.org,person=self.employee,role=role)
        self.client.force_login(self.employee.user)
        response=self.target('ORG_ADMIN',person_ids=[str(self.employee.id)])
        self.assertEqual(response.status_code,403)
        ScopedRoleGrant.objects.create(organization=self.org,role_key='ASSET_MANAGER',group=self.other_group)
        response=self.orgpost('group-targets',dict(person_ids=[str(self.employee.id)],department_ids=[],include_children=False),self.other_group.id)
        self.assertEqual(response.status_code,403)
    def test_profile_modal_endpoint_and_user_layout(self):
        response=self.client.get('/account/profile');self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['username'],self.admin.user.username)
        self.assertIn('no-store',response['Cache-Control'])
        response=self.client.get('/console/users/new');self.assertContains(response,'user-create-grid');self.assertContains(response,'name="department_id"');self.assertContains(response,'data-copy-load')
        self.assertContains(self.client.get('/'),'data-profile-open')
