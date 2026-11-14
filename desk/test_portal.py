from django.test import TestCase, override_settings
from .tests import Fixtures
from .models import ConfigurationItem, RoleGrant, Ticket


@override_settings(SECURE_SSL_REDIRECT=False)
class IntegratedPortalTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        ConfigurationItem.objects.create(organization=cls.org,ci_no='PRIVATE',name='Hidden resource',type='SERVER')
        ConfigurationItem.objects.create(organization=cls.other_org,ci_no='FOREIGN',name='Other organization resource',type='SERVER',portal_visible=True)
        Ticket.objects.create(organization=cls.org,number='INC-PRIVATE',title='Peer private incident',description='private',requested_by=cls.peer,group=cls.group)

    def test_authentication_required_and_login_opens_portal(self):
        for url in ['/','/systems/service','/systems/asset','/systems/resource']:
            self.assertEqual(self.client.get(url).status_code,302)
        response=self.client.post('/login/',{'username':'employee','password':'test-only-password'})
        self.assertRedirects(response,'/')
        self.assertContains(self.client.get('/'),'통합 ITSM')
        self.assertNotContains(self.client.get('/'),'IT 운영을 하나의 흐름으로.')

    def test_system_navigation_does_not_mix_asset_and_service_menus(self):
        self.client.force_login(self.manager.user)
        response=self.client.get('/portal/incidents')
        self.assertEqual(response.context['active_area'],'service')
        links=[x['url'] for g in response.context['nav_groups'] for x in g['links']]
        self.assertIn('/work/incidents',links)
        self.assertNotIn('/assets',links)
        self.assertContains(response,'aria-label="시스템 전환"')
        response=self.client.get('/assets')
        self.assertEqual(response.context['active_area'],'asset')
        links=[x['url'] for g in response.context['nav_groups'] for x in g['links']]
        self.assertIn('/my-assets',links)
        self.assertNotIn('/work/incidents',links)

    def test_dashboard_counts_and_recent_items_respect_visibility_and_tenant(self):
        self.client.force_login(self.employee.user)
        response=self.client.get('/systems/asset')
        self.assertEqual(response.context['metrics'][0]['value'],1)
        self.assertNotContains(response,'Private laptop')
        self.assertNotContains(response,'Secret beta')
        response=self.client.get('/cis')
        self.assertEqual(response.context['active_area'],'service')
        self.assertNotContains(response,'Hidden resource')
        self.assertNotContains(response,'Other organization resource')
        response=self.client.get('/systems/service')
        self.assertEqual(response.context['metrics'][0]['value'],0)
        self.assertNotContains(response,'Peer private incident')
        self.client.force_login(self.manager.user)
        response=self.client.get('/systems/service')
        self.assertEqual(response.context['metrics'][0]['value'],1)
        self.assertContains(response,'Peer private incident')
        response=self.client.get('/cis')
        self.assertContains(response,'Hidden resource')
        self.assertNotContains(response,'Other organization resource')

    def test_employee_menus_and_existing_routes_remain_available(self):
        self.client.force_login(self.employee.user)
        for url in ['/systems/service','/systems/asset','/systems/resource','/catalog','/my-assets','/cis']:
            response=self.client.get(url)
            self.assertEqual(response.status_code,200,url)
            self.assertNotContains(response,'href="/admin/access"')
            self.assertNotContains(response,'href="/work/sla"')
            self.assertNotContains(response,'href="/inventory"')

    def test_nested_route_has_one_selected_navigation_item(self):
        RoleGrant.objects.create(organization=self.org,person=self.manager,role='STOCK_MANAGER')
        self.client.force_login(self.manager.user)
        response=self.client.get('/inventory/movements')
        selected=[x['url'] for g in response.context['nav_groups'] for x in g['links'] if x['active']]
        self.assertEqual(selected,['/inventory/movements'])
