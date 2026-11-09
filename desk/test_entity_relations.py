import json
import uuid
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from .tests import Fixtures
from . import test_entities as helpers
field = helpers.field
from .models import EntityRecord, EntityRecordLink, EntitySchemaVersion
from .entities.system_fields import SYSTEM_FIELDS


@override_settings(SECURE_SSL_REDIRECT=False)
class EntityRelationTests(Fixtures, TestCase):
    post = helpers.EntityTests.post
    save = helpers.EntityTests.save
    publish = helpers.EntityTests.publish
    create = helpers.EntityTests.create
    published = helpers.EntityTests.published

    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()

    def setUp(self):
        self.client.force_login(self.admin.user)

    def targets(self):
        entity = self.published(code='TARGET')
        return entity, [self.create(entity, {'title': str(i)}).json() for i in range(3)]

    def source(self, target, relationship):
        return self.published(code='SOURCE', fields=[
            field('target', 'reference', target_entity_id=target['id'], relationship=relationship)])

    def test_system_fields_created_and_protected_from_business_inputs(self):
        draft = self.post('', dict(code='EMPTY', name='빈 엔티티', fields=[], expected_version=0, reason='생성')).json()
        self.assertEqual(len(draft['system_fields']), 8)
        entity = self.publish(draft).json()
        record = self.create(entity, {}).json()
        for definition in SYSTEM_FIELDS:
            self.assertIn(definition['key'], record)
            self.assertTrue(record[definition['key']])
            invalid = self.save(code='INVALID', fields=[field(definition['key'])])
            self.assertEqual(invalid.status_code, 422)
            self.assertEqual(self.create(entity, {definition['key']: 'forged'}).status_code, 422)
        self.assertEqual(record['created_by'], str(self.admin.id))
        self.assertEqual(record['updated_by'], str(self.admin.id))
        self.assertEqual(record['row_version'], 1)

    def test_one_to_one_exclusive_target_and_database_constraints(self):
        target, records = self.targets()
        source = self.source(target, 'one_to_one')
        first = self.create(source, {'target': records[0]['id']})
        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(self.create(source, {'target': records[0]['id']}).status_code, 409)
        self.assertEqual(self.create(source, {'target': records[1]['id']}).status_code, 201)
        link = EntityRecordLink.objects.first()
        with self.assertRaises(IntegrityError), transaction.atomic():
            EntityRecordLink.objects.create(organization=self.org, source_entity_id=source['id'],
                source=link.source, target_id=records[2]['id'], field_key='target', scalar=True, exclusive=True)
        # A caller cannot bypass exclusivity by lying about relationship flags.
        with self.assertRaises(IntegrityError), transaction.atomic():
            EntityRecordLink.objects.create(organization=self.org, source_entity_id=source['id'],
                source=link.source, target_id=records[2]['id'], field_key='target', scalar=False, exclusive=False)
        self.assertEqual(EntityRecord.objects.filter(entity_id=source['id']).count(), 2)

    def test_many_to_one_reuses_targets_and_reverse_relation_query(self):
        target, records = self.targets()
        source = self.source(target, 'many_to_one')
        for _ in range(2):
            self.assertEqual(self.create(source, {'target': records[0]['id']}).status_code, 201)
        response = self.client.get(f"/api/v1/admin/entities/{target['id']}/records/{records[0]['id']}/relations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['links']), 2)
        self.assertTrue(all(link['direction'] == 'incoming' for link in response.json()['links']))
        self.client.force_login(self.foreign.user)
        self.assertEqual(self.client.get(response.request['PATH_INFO']).status_code, 404)

    def test_one_to_many_exclusive_children_and_array_validation(self):
        target, records = self.targets()
        source = self.source(target, 'one_to_many')
        ids = [r['id'] for r in records]
        self.assertEqual(self.create(source, {'target': ids[:2]}).status_code, 201)
        self.assertEqual(self.create(source, {'target': ids[1:]}).status_code, 409)
        for value in [ids[2], [ids[2], ids[2]], [str(uuid.uuid4())], [], [False], 'bad']:
            self.assertEqual(self.create(source, {'target': value}).status_code, 422)
        self.assertEqual(EntityRecordLink.objects.count(), 2)

    def test_many_to_many_materializes_junction_links_and_reuses_children(self):
        target, records = self.targets()
        source = self.source(target, 'many_to_many')
        ids = [r['id'] for r in records]
        for values in [ids[:2], ids[1:]]:
            self.assertEqual(self.create(source, {'target': values}).status_code, 201)
        self.assertEqual(EntityRecordLink.objects.count(), 4)
        response = self.client.get('/console/entities/' + source['id'])
        self.assertContains(response, 'multiple size="4"')
        self.assertContains(response, '연결 보기')

    def test_explicit_junction_has_attributes_and_unique_pair(self):
        target, records = self.targets()
        fields = [field('left', 'reference', target_entity_id=target['id']),
                  field('right', 'reference', target_entity_id=target['id']), field('role')]
        payload = dict(code='MEMBERSHIP', name='연결 정보', fields=fields, expected_version=0,
                       reason='중간 엔티티', junction={'left_field': 'left', 'right_field': 'right'})
        draft = self.post('', payload).json()
        entity = self.publish(draft).json()
        values = {'left': records[0]['id'], 'right': records[1]['id'], 'role': '담당'}
        self.assertEqual(self.create(entity, values).status_code, 201)
        self.assertEqual(self.create(entity, {**values, 'role': '중복'}).status_code, 409)
        response = self.client.get(f"/api/v1/admin/entities/{target['id']}/records/{records[0]['id']}/relations")
        self.assertEqual(response.json()['junctions'][0]['values']['role'], '담당')
        payload['junction'] = {'left_field': 'left', 'right_field': 'role'}
        payload['code'] = 'BAD'
        self.assertEqual(self.post('', payload).status_code, 422)
        existing = EntityRecord.objects.get(entity_id=entity['id'])
        with self.assertRaises(IntegrityError), transaction.atomic():
            EntityRecord.objects.create(organization=self.org, entity=existing.entity,
                schema_version=existing.schema_version, created_by=self.admin, updated_by=self.admin,
                values=values, request_id=uuid.uuid4(), junction_left_id=values['left'], junction_right_id=values['right'])

    def test_reference_semantics_cannot_change_after_data_exists(self):
        target, records = self.targets()
        source = self.source(target, 'many_to_one')
        self.create(source, {'target': records[0]['id']})
        draft = self.save(code='SOURCE', fields=[field('target', 'reference',
            target_entity_id=target['id'], relationship='one_to_one')], version=2).json()
        response = self.publish(draft, version=3)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['error']['code'], 'RELATION_SCHEMA_IN_USE')
        self.assertEqual(EntitySchemaVersion.objects.filter(entity_id=source['id']).count(), 1)

    def test_normalized_links_reject_wrong_organization_target_and_mutation(self):
        target, records = self.targets()
        source = self.source(target, 'many_to_one')
        self.create(source, {'target': records[0]['id']})
        link = EntityRecordLink.objects.get()
        for values in [dict(organization=self.other_org), dict(source_entity=link.target.entity),
                       dict(field_key='not_a_field')]:
            with self.assertRaises(IntegrityError), transaction.atomic():
                EntityRecordLink.objects.create(organization=values.get('organization', self.org),
                    source_entity=values.get('source_entity', link.source_entity), source=link.source,
                    target_id=records[1]['id'], field_key=values.get('field_key', 'target'), scalar=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EntityRecordLink.objects.filter(id=link.id).update(exclusive=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            link.delete()

    def test_list_create_and_grid_are_separate_and_system_fields_visible(self):
        response = self.client.get('/console/entities')
        self.assertContains(response, '엔티티 목록')
        self.assertNotContains(response, 'data-kind="entity-save"')
        response = self.client.get('/console/entities?new=1')
        self.assertContains(response, '시스템 필드')
        entity = self.published()
        response = self.client.get('/console/entities/' + entity['id'])
        self.assertContains(response, 'class="entity-grid"')
        for text in ['일대일', '다대일', '일대다', '다대다', '중간 엔티티 설정', 'updated_by']:
            self.assertContains(response, text)
