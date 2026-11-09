import json
import uuid
from django.db import IntegrityError, transaction
from django.test import TestCase, Client, override_settings
from .tests import Fixtures
from .models import EntityDefinition, EntitySchemaVersion, EntityRecord, AuditEvent, RoleGrant


def field(key='title', kind='text', required=True, **extra):
    return dict(key=key, label=key, type=kind, required=required, **extra)


@override_settings(SECURE_SSL_REDIRECT=False)
class EntityTests(Fixtures, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()

    def setUp(self):
        self.client.force_login(self.admin.user)

    def post(self, path, payload, key=None):
        return self.client.post('/api/v1/admin/entities'+path, json.dumps(payload),
            content_type='application/json', HTTP_IDEMPOTENCY_KEY=key or str(uuid.uuid4()))

    def save(self, code='EXAMPLE', fields=None, version=0, key=None):
        return self.post('', dict(code=code, name='검증 엔티티', fields=fields or [field()],
                                 expected_version=version, reason='초안 저장'), key)

    def publish(self, entity, version=1, key=None):
        return self.post('/'+entity['id']+'/publish', dict(expected_version=version, reason='정의 게시'), key)

    def create(self, entity, values=None, schema_id=None, key=None):
        return self.post('/'+entity['id']+'/records', dict(schema_version_id=schema_id or entity['published']['id'],
                         values={'title':'원본'} if values is None else values), key)

    def published(self, code='EXAMPLE', fields=None):
        draft=self.save(code, fields).json()
        result=self.publish(draft)
        self.assertEqual(result.status_code,201,result.content)
        return result.json()

    def test_draft_publish_form_and_actual_record(self):
        entity=self.published()
        self.assertEqual(entity['published']['version'],1)
        self.assertContains(self.client.get('/admin/entities/'+entity['id']), '입력 검증')
        response=self.create(entity)
        self.assertEqual(response.status_code,201,response.content)
        self.assertEqual(response.json()['values'],{'title':'원본'})
        self.assertEqual(self.client.get('/api/v1/admin/entities/'+entity['id']+'/records').json()['items'][0]['schema_version'],1)
        self.assertEqual(AuditEvent.objects.filter(action='ENTITY_SCHEMA_PUBLISHED').count(),1)
        audit=AuditEvent.objects.get(action='ENTITY_RECORD_CREATED')
        self.assertNotIn('원본',json.dumps(audit.after_data,ensure_ascii=False))

    def test_draft_changes_do_not_change_published_or_existing_records(self):
        v1=self.published()
        self.create(v1)
        draft=self.save(fields=[field('count','integer')],version=2).json()
        self.assertEqual(draft['published']['fields'][0]['key'],'title')
        v2=self.publish(draft,version=3).json()
        self.assertEqual(v2['published']['version'],2)
        self.assertEqual(self.create(v2,{'count':5}).status_code,201)
        old=EntityRecord.objects.filter(schema_version__version=1).get()
        self.assertEqual(old.values,{'title':'원본'})
        self.assertEqual(old.schema_version.fields,[field()])
        self.assertEqual(self.create(v1).json()['error']['code'],'VERSION_CONFLICT')

    def test_publish_and_save_versions_conflict(self):
        draft=self.save().json()
        self.assertEqual(self.save(version=0).status_code,409)
        self.assertEqual(self.publish(draft).status_code,201)
        self.assertEqual(self.publish(draft).status_code,409)
        self.assertEqual(EntitySchemaVersion.objects.count(),1)

    def test_required_unknown_fields_and_primitive_types(self):
        fields=[field(),field('count','integer'),field('enabled','boolean'),field('day','date'),
                field('kind','choice',options=['A','B']),field('note','textarea',False)]
        entity=self.published(fields=fields)
        valid={'title':'입력','count':0,'enabled':False,'day':'2026-11-08','kind':'A'}
        self.assertEqual(self.create(entity,valid).status_code,201)
        for changes in [{'title':''},{'title':'   '},{'count':True},{'count':'3'},{'count':2**53},
                        {'enabled':'false'},{'day':'2026-02-30'},{'day':'20261108'},
                        {'kind':'C'},{'secret':'x'},{'title':'a'*4001}]:
            with self.subTest(changes=changes):
                self.assertEqual(self.create(entity,{**valid,**changes}).status_code,422)
        self.assertEqual(EntityRecord.objects.count(),1)

    def test_schema_rejects_duplicate_invalid_and_unregistered_types(self):
        for fields in [[field(),field()], [field('UPPER')], [field(kind='python')],
                       [field(required='yes')], [field(kind='choice',options=['A',' A '])],
                       [field(options=['bad'])], [field(target_entity_id=str(uuid.uuid4()))],
                       [field(kind='choice',options=[])], [field()]*31, ['invalid']]:
            with self.subTest(fields=fields):
                self.assertEqual(self.save(fields=fields).status_code,422)
        self.assertEqual(EntityDefinition.objects.count(),0)
        self.assertEqual(self.post('',dict(code='A',name='A',fields=[],expected_version=0,reason='empty')).status_code,201)

    def test_reference_accepts_only_records_of_published_target_same_org(self):
        target=self.published(code='TARGET')
        target_record=self.create(target).json()
        other=self.published(code='OTHER')
        other_record=self.create(other).json()
        source=self.published(code='SOURCE',fields=[field('target','reference',target_entity_id=target['id'])])
        self.assertEqual(self.create(source,{'target':target_record['id']}).status_code,201)
        self.assertEqual(self.create(source,{'target':other_record['id']}).status_code,422)
        self.client.force_login(self.foreign.user)
        foreign=self.published(code='FOREIGN')
        foreign_record=self.create(foreign).json()
        self.client.force_login(self.admin.user)
        self.assertEqual(self.create(source,{'target':foreign_record['id']}).status_code,422)
        self.assertEqual(self.save(code='BADREF',fields=[field('ref','reference',target_entity_id=foreign['id'])]).status_code,404)

    def test_reference_to_draft_is_not_publishable(self):
        draft=self.save(code='TARGET').json()
        self.assertEqual(self.save(code='SOURCE',fields=[field('ref','reference',target_entity_id=draft['id'])]).status_code,422)

    def test_schema_and_records_are_append_only_and_definition_identity_preserved(self):
        entity=self.published()
        self.create(entity)
        with self.assertRaises(IntegrityError),transaction.atomic():
            EntitySchemaVersion.objects.update(fields=[field('changed')])
        with self.assertRaises(IntegrityError),transaction.atomic():
            EntityRecord.objects.update(values={'title':'changed'})
        with self.assertRaises(IntegrityError),transaction.atomic():
            EntityRecord.objects.get().delete()
        with self.assertRaises(IntegrityError),transaction.atomic():
            EntityDefinition.objects.update(code='CHANGED')

    def test_db_guards_cross_org_and_wrong_schema_entity(self):
        a=self.published(code='FIRST')
        b=self.published(code='SECOND')
        for org,actor,entity_id,schema_id in [
            (self.other_org,self.foreign,a['id'],a['published']['id']),
            (self.org,self.foreign,a['id'],a['published']['id']),
            (self.org,self.admin,a['id'],b['published']['id'])]:
            with self.assertRaises(IntegrityError),transaction.atomic():
                EntityRecord.objects.create(organization=org,entity_id=entity_id,schema_version_id=schema_id,
                    values={'title':'bad'},created_by=actor,request_id=uuid.uuid4())

    def test_org_scoped_reads_and_api_authorization(self):
        entity=self.published()
        self.create(entity)
        self.client.force_login(self.foreign.user)
        self.assertEqual(self.client.get('/api/v1/admin/entities').json()['items'],[])
        self.assertEqual(self.client.get('/api/v1/admin/entities/'+entity['id']).status_code,404)
        self.assertEqual(self.client.get('/api/v1/admin/entities/'+entity['id']+'/records').status_code,404)
        self.assertEqual(self.publish(entity,2).status_code,404)
        self.assertEqual(self.save().status_code,201)
        for user in [self.employee,self.manager]:
            self.client.force_login(user.user)
            self.assertEqual(self.client.get('/admin/entities').status_code,403)
            self.assertEqual(self.client.get('/api/v1/admin/entities').status_code,403)
            self.assertEqual(self.save().status_code,403)
            self.assertEqual(self.create(entity).status_code,403)

    def test_repeated_commands_have_one_effect_and_changed_payload_is_rejected(self):
        key=str(uuid.uuid4())
        draft=self.save(key=key)
        self.assertEqual(self.save(key=key).json(),draft.json())
        pub_key=str(uuid.uuid4())
        pub=self.publish(draft.json(),key=pub_key)
        self.assertEqual(self.publish(draft.json(),key=pub_key).json(),pub.json())
        run_key=str(uuid.uuid4())
        first=self.create(pub.json(),key=run_key)
        self.assertEqual(self.create(pub.json(),key=run_key).json(),first.json())
        self.assertEqual(self.create(pub.json(),{'title':'changed'},key=run_key).status_code,409)
        self.assertEqual(EntityDefinition.objects.count(),1)
        self.assertEqual(EntitySchemaVersion.objects.count(),1)
        self.assertEqual(EntityRecord.objects.count(),1)

    def test_permission_revocation_blocks_replay(self):
        key=str(uuid.uuid4())
        self.save(key=key)
        RoleGrant.objects.filter(person=self.admin).delete()
        self.assertEqual(self.save(key=key).status_code,403)

    def test_csrf_and_missing_idempotency(self):
        self.assertEqual(self.client.post('/api/v1/admin/entities','{}',content_type='application/json').status_code,400)
        client=Client(enforce_csrf_checks=True)
        client.force_login(self.admin.user)
        self.assertEqual(client.post('/api/v1/admin/entities','{}',content_type='application/json',HTTP_IDEMPOTENCY_KEY='csrf').status_code,403)
