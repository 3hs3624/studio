import json
import uuid
from dataclasses import replace
from unittest.mock import patch
from django.db import IntegrityError, transaction
from django.test import TestCase, SimpleTestCase, Client, override_settings
from .tests import Fixtures
from . import services as s
from .models import PluginBinding, PluginRun, AuditEvent, OutboxEvent, RoleGrant
from .plugins.bundled import REGISTRY
from .plugins.registry import build_registry


class RegistryTests(SimpleTestCase):
    def test_manifest_digest_and_registry_are_stable_and_immutable(self):
        plugin = REGISTRY['text.normalize']
        self.assertEqual(plugin.manifest(), plugin.manifest())
        self.assertNotEqual(plugin.manifest()['digest'], replace(plugin, code_digest='a'*64).manifest()['digest'])
        with self.assertRaises(TypeError):
            REGISTRY['unsafe'] = plugin

    def test_invalid_duplicate_incompatible_missing_and_cyclic_manifests_are_rejected(self):
        plugin = REGISTRY['text.normalize']
        for candidate in [replace(plugin, plugin_id='../module'), replace(plugin, version='latest'),
                          replace(plugin, api_version='99'), replace(plugin, code_digest='unverified'),
                          replace(plugin, dependencies=(('missing', '1.0.0'),))]:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    build_registry((candidate,))
        with self.assertRaises(ValueError):
            build_registry((plugin, plugin))
        a = replace(plugin, plugin_id='a', dependencies=(('b', '1.0.0'),))
        b = replace(plugin, plugin_id='b', dependencies=(('a', '1.0.0'),))
        with self.assertRaises(ValueError):
            build_registry((a, b))
        self.assertEqual(len(build_registry((replace(plugin, plugin_id='b'), a))), 2)


@override_settings(SECURE_SSL_REDIRECT=False)
class PluginTests(Fixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()

    def setUp(self):
        self.client.force_login(self.admin.user)
        self.digest = REGISTRY['text.normalize'].manifest()['digest']

    def post(self, operation, payload, key=None):
        return self.client.post('/api/v1/admin/plugins/text.normalize/'+operation,
                                json.dumps(payload), content_type='application/json',
                                HTTP_IDEMPOTENCY_KEY=key or str(uuid.uuid4()))

    def configure(self, enabled=True, version=0, key=None, **changes):
        return self.post('configuration', dict(expected_version=version, enabled=enabled,
            configuration={'trim':True, 'collapse_spaces':True}, reason='테스트 설정',
            manifest_digest=self.digest, **changes), key)

    def preview(self, text='  Hello\n  World  ', version=1, key=None):
        return self.post('preview', dict(expected_version=version, manifest_digest=self.digest, input={'text':text}), key)

    def test_catalog_page_navigation_and_preview(self):
        response = self.client.get('/admin/plugins')
        self.assertContains(response, '텍스트 정규화')
        self.assertContains(response, '플러그인 관리')
        items = self.client.get('/api/v1/admin/plugins').json()['items']
        self.assertIsNone(items[0]['binding'])
        self.assertEqual(self.configure().status_code, 200)
        response = self.preview()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['output']['text'], 'Hello World')
        self.assertContains(self.client.get('/admin/plugins'), '기능 미리보기')

    def test_configuration_revision_and_disabled_execution(self):
        self.assertEqual(self.preview().status_code, 409)
        self.assertEqual(self.configure().status_code, 200)
        self.assertEqual(self.configure().json()['error']['code'], 'VERSION_CONFLICT')
        self.assertEqual(self.configure(False, 1).status_code, 200)
        self.assertEqual(self.preview(version=2).json()['error']['code'], 'PLUGIN_DISABLED')
        self.assertEqual(PluginRun.objects.count(), 0)

    def test_configuration_and_run_idempotency_and_conflicting_payload(self):
        configure_key, run_key = str(uuid.uuid4()), str(uuid.uuid4())
        first = self.configure(key=configure_key)
        self.assertEqual(self.configure(key=configure_key).json(), first.json())
        self.assertEqual(PluginBinding.objects.get().row_version, 1)
        first = self.preview(key=run_key)
        self.assertEqual(self.preview(key=run_key).json(), first.json())
        self.assertEqual(PluginRun.objects.count(), 1)
        self.assertEqual(self.preview('different', key=run_key).status_code, 409)
        self.assertEqual(AuditEvent.objects.filter(action='PLUGIN_PREVIEWED').count(), 1)

    def test_authorization_is_rechecked_on_replay(self):
        key = str(uuid.uuid4())
        self.configure()
        self.assertEqual(self.preview(key=key).status_code, 200)
        RoleGrant.objects.filter(person=self.admin).delete()
        self.assertEqual(self.preview(key=key).status_code, 403)
        self.assertEqual(self.client.get('/admin/plugins').status_code, 302)

    def test_regular_users_and_service_managers_cannot_manage_plugins(self):
        for user in [self.employee, self.manager]:
            self.client.force_login(user.user)
            for url in ['/api/v1/admin/plugins', '/api/v1/admin/plugin-runs', '/admin/plugins']:
                self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.configure().status_code, 403)

    def test_org_scoping_and_cross_organization_database_guards(self):
        self.configure()
        self.preview()
        binding = PluginBinding.objects.get()
        self.client.force_login(self.foreign.user)
        self.assertIsNone(self.client.get('/api/v1/admin/plugins').json()['items'][0]['binding'])
        self.assertEqual(self.client.get('/api/v1/admin/plugin-runs').json()['items'], [])
        self.assertEqual(self.preview().status_code, 409)
        self.assertEqual(self.configure().status_code, 200)
        self.assertEqual(PluginBinding.objects.count(), 2)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PluginRun.objects.create(organization=self.other_org, binding=binding, actor=self.foreign,
                plugin_id='text.normalize', plugin_version='1.0.0', manifest_digest=self.digest,
                binding_version=1, configuration={}, input_length=0, output_length=0, request_id=uuid.uuid4())

    def test_unknown_plugin_client_code_or_invalid_config_is_rejected(self):
        self.assertEqual(self.client.post('/api/v1/admin/plugins/os.system/configuration', '{}',
            content_type='application/json', HTTP_IDEMPOTENCY_KEY='unknown').status_code, 404)
        for value in [{'trim':True, 'collapse_spaces':'yes'}, {'trim':True}, {'trim':True,'collapse_spaces':True,'script':'x'}, []]:
            payload=dict(expected_version=0, enabled=True, configuration=value,
                         reason='invalid', manifest_digest=self.digest)
            self.assertEqual(self.post('configuration', payload).status_code, 422)
        self.assertFalse(PluginBinding.objects.exists())

    def test_digest_drift_stale_run_and_invalid_inputs_reject_before_effect(self):
        self.configure()
        self.assertEqual(self.preview(version=0).json()['error']['code'], 'VERSION_CONFLICT')
        for value in [500, 'x'*4001, None]:
            self.assertEqual(self.preview(value).status_code, 422)
        PluginBinding.objects.update(manifest_digest='0'*64)
        self.assertEqual(self.preview().json()['error']['code'], 'PLUGIN_INCOMPATIBLE')
        self.assertFalse(PluginRun.objects.exists())
        self.assertEqual(self.configure(version=1).status_code, 200)
        self.assertEqual(self.preview(version=2).status_code, 200)

    def test_configuration_rejects_stale_manifest_and_wrong_types(self):
        payload=dict(expected_version=0, enabled=True, configuration={'trim':True,'collapse_spaces':True},
                     reason='check', manifest_digest='0'*64)
        self.assertEqual(self.post('configuration', payload).status_code, 409)
        payload['manifest_digest']=self.digest
        payload['expected_version']=False
        self.assertEqual(self.post('configuration', payload).status_code, 422)
        payload['expected_version']=0
        payload['enabled']='true'
        self.assertEqual(self.post('configuration', payload).status_code, 422)
        self.assertEqual(PluginBinding.objects.count(), 0)

    def test_preview_snapshots_are_append_only_and_do_not_log_text(self):
        self.configure()
        response = self.preview(' private payload ')
        self.assertEqual(response.status_code, 200)
        self.configure(False, 1)
        run = PluginRun.objects.get()
        self.assertEqual(run.binding_version, 1)
        self.assertEqual(run.manifest_digest, self.digest)
        history = self.client.get('/api/v1/admin/plugin-runs').json()
        self.assertNotIn('private payload', json.dumps(history))
        self.assertNotIn('private payload', json.dumps(list(AuditEvent.objects.values('after_data','before_data'))))
        self.assertNotIn('private payload', json.dumps(list(OutboxEvent.objects.values('payload'))))
        with self.assertRaises(IntegrityError), transaction.atomic():
            PluginRun.objects.filter(pk=run.pk).update(output_length=100)
        with self.assertRaises(IntegrityError), transaction.atomic():
            run.delete()
        with self.assertRaises(IntegrityError), transaction.atomic():
            PluginBinding.objects.update(plugin_id='different')

    def test_preview_uses_configured_behavior_and_does_not_create_business_data(self):
        response=self.post('configuration', dict(expected_version=0, enabled=True,
            configuration={'trim':False,'collapse_spaces':False}, reason='preserve', manifest_digest=self.digest))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.preview(' A\n B ').json()['output']['text'], ' A\n B ')

    def test_dependency_activation_and_reverse_disable_checks(self):
        base=REGISTRY['text.normalize']
        dep=replace(base, plugin_id='dependent', dependencies=(('text.normalize','1.0.0'),))
        registry=build_registry((base, dep))
        with patch('desk.plugin_service.REGISTRY', registry):
            payload=dict(expected_version=0, enabled=True, configuration={'trim':True,'collapse_spaces':True},
                         reason='dependency', manifest_digest=dep.manifest()['digest'])
            url='/api/v1/admin/plugins/dependent/configuration'
            self.assertEqual(self.client.post(url,json.dumps(payload),content_type='application/json',
                HTTP_IDEMPOTENCY_KEY='missing-dependency').status_code,409)
            self.configure()
            self.assertEqual(self.client.post(url,json.dumps(payload),content_type='application/json',
                HTTP_IDEMPOTENCY_KEY='enable-dependent').status_code,200)
            self.assertEqual(self.configure(False,1).json()['error']['code'],'PLUGIN_IN_USE')

    def test_csrf_and_missing_idempotency_are_enforced(self):
        self.assertEqual(self.client.post('/api/v1/admin/plugins/text.normalize/preview', '{}',
            content_type='application/json').status_code,400)
        client=Client(enforce_csrf_checks=True)
        client.force_login(self.admin.user)
        self.assertEqual(client.post('/api/v1/admin/plugins/text.normalize/configuration', '{}',
            content_type='application/json', HTTP_IDEMPOTENCY_KEY='csrf').status_code,403)
