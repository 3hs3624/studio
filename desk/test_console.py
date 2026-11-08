from django.test import TestCase, override_settings
from .tests import Fixtures
from .models import EntityDefinition, RoleGrant


@override_settings(SECURE_SSL_REDIRECT=False)
class ConsoleTests(Fixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()

    def test_anonymous_and_regular_users_cannot_enter_console(self):
        paths=['/console','/console/access','/console/entities','/console/plugins','/console/catalog','/console/sla']
        for path in paths:
            self.assertEqual(self.client.get(path).status_code,302,path)
        self.client.force_login(self.employee.user)
        self.assertNotContains(self.client.get('/'),'href="/console"')
        for path in paths:
            self.assertEqual(self.client.get(path).status_code,403,path)

    def test_admin_console_is_separate_from_business_portal(self):
        self.client.force_login(self.admin.user)
        self.assertContains(self.client.get('/'),'href="/console"')
        response=self.client.get('/console')
        self.assertContains(response,'aria-label="운영 콘솔 메뉴"')
        self.assertNotContains(response,'aria-label="시스템 전환"')
        self.assertContains(response,'href="/console/entities"')
        self.assertContains(response,'href="/console/plugins"')
        self.assertNotContains(response,'href="/work/incidents"')
        self.assertNotContains(response,'href="/console/catalog"')
        self.assertContains(response,'target="_blank" rel="noopener"')
        self.assertEqual(response.context['active_area'],'console')
        portal=self.client.get('/systems/service')
        self.assertContains(portal,'aria-label="시스템 전환"')
        self.assertNotContains(portal,'href="/console/entities"')
        self.assertFalse(portal.context['console_mode'])

    def test_console_permissions_follow_existing_role_boundaries(self):
        self.client.force_login(self.admin.user)
        for path in ['/console/access','/console/entities','/console/plugins']:
            self.assertEqual(self.client.get(path).status_code,200,path)
        for path in ['/console/catalog','/console/sla']:
            self.assertEqual(self.client.get(path).status_code,403,path)
        self.client.force_login(self.manager.user)
        response=self.client.get('/console')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'href="/console/catalog"')
        self.assertContains(response,'href="/console/sla"')
        self.assertNotContains(response,'href="/console/access"')
        for path in ['/console/catalog','/console/sla']:
            self.assertEqual(self.client.get(path).status_code,200,path)
        for path in ['/console/access','/console/plugins','/console/entities']:
            self.assertEqual(self.client.get(path).status_code,403,path)

    def test_combined_roles_get_combined_console_features(self):
        RoleGrant.objects.create(organization=self.org,person=self.admin,role='SERVICE_MANAGER')
        self.client.force_login(self.admin.user)
        response=self.client.get('/console')
        for url in ['/console/access','/console/entities','/console/plugins','/console/catalog','/console/sla']:
            self.assertContains(response,'href="'+url+'"')
            self.assertEqual(self.client.get(url).status_code,200,url)

    def test_legacy_management_routes_use_console_and_one_selected_link(self):
        self.client.force_login(self.admin.user)
        for path,url in [('/admin/access','/console/access'),('/admin/plugins','/console/plugins'),('/admin/entities','/console/entities')]:
            response=self.client.get(path)
            self.assertEqual(response.status_code,200,path)
            self.assertTrue(response.context['console_mode'])
            selected=[link['url'] for group in response.context['console_groups'] for link in group['links'] if link['active']]
            self.assertEqual(selected,[url])
        self.client.force_login(self.manager.user)
        for path in ['/work/catalog','/work/sla']:
            response=self.client.get(path)
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.context['console_mode'])

    def test_entity_navigation_keeps_console_mode_and_org_boundary(self):
        entity=EntityDefinition.objects.create(organization=self.org,code='LOCAL',name='Local')
        foreign=EntityDefinition.objects.create(organization=self.other_org,code='SECRET',name='Foreign hidden')
        self.client.force_login(self.admin.user)
        response=self.client.get('/console/entities/'+str(entity.id))
        self.assertContains(response,'data-detail-base="/console/entities"')
        self.assertContains(response,'href="/console/entities/'+str(entity.id)+'"')
        self.assertNotContains(response,'Foreign hidden')
        self.assertEqual(self.client.get('/console/entities/'+str(foreign.id)).status_code,404)
        self.assertEqual(response.context['org'],self.org)

    @override_settings(STUDIO_ENVIRONMENT='staging')
    def test_environment_and_organization_are_visible_in_console(self):
        self.client.force_login(self.admin.user)
        response=self.client.get('/console/plugins')
        self.assertContains(response,'검증 환경')
        self.assertContains(response,self.org.name)
        self.assertNotContains(response,'운영 환경')
        self.assertEqual(response.context['console_environment_key'],'staging')

    @override_settings(STUDIO_ENVIRONMENT='unspecified')
    def test_unspecified_environment_is_not_mislabeled_production(self):
        self.client.force_login(self.admin.user)
        self.assertContains(self.client.get('/console'),'환경 미지정')
