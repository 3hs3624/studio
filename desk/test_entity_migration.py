"""Upgrade an existing entity database and verify preservation plus new guards."""
import uuid
from django.db import connection, IntegrityError, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class EntityUpgradeTests(TransactionTestCase):
    migrate_from = ('desk', '0011_remove_rolegrant_role_allowlist_alter_rolegrant_role_and_more')
    migrate_to = ('desk', '0013_commoncodegroup_commoncodeitem_numberissue_and_more')

    def test_existing_records_metadata_and_references_are_backfilled(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        try:
            apps = executor.loader.project_state([self.migrate_from]).apps
            org = apps.get_model('desk', 'Organization').objects.create(name='기존 조직')
            user = apps.get_model('auth', 'User').objects.create(username='upgrade-user')
            actor = apps.get_model('desk', 'Person').objects.create(organization=org, user=user, display_name='기존 사용자')
            Definition = apps.get_model('desk', 'EntityDefinition')
            Schema = apps.get_model('desk', 'EntitySchemaVersion')
            Record = apps.get_model('desk', 'EntityRecord')
            target = Definition.objects.create(organization=org, code='TARGET', name='기존 대상')
            target_schema = Schema.objects.create(organization=org, entity=target, version=1, name='기존 대상',
                fields=[dict(key='title', label='제목', type='text', required=True)], schema_digest='target-original',
                published_by=actor, reason='기존 게시', request_id=uuid.uuid4())
            target_record = Record.objects.create(organization=org, entity=target, schema_version=target_schema,
                values={'title': '보존할 대상'}, created_by=actor, request_id=uuid.uuid4())
            source = Definition.objects.create(organization=org, code='SOURCE', name='기존 원본')
            source_schema = Schema.objects.create(organization=org, entity=source, version=1, name='기존 원본',
                fields=[dict(key='target', label='대상', type='reference', required=True, target_entity_id=str(target.id))],
                schema_digest='source-original', published_by=actor, reason='기존 게시', request_id=uuid.uuid4())
            source_record = Record.objects.create(organization=org, entity=source, schema_version=source_schema,
                values={'target': str(target_record.id)}, created_by=actor, request_id=uuid.uuid4())
            MigrationExecutor(connection).migrate([self.migrate_to])
            from .models import EntityRecord, EntityRecordLink, EntitySchemaVersion
            restored = EntityRecord.objects.get(id=source_record.id)
            self.assertEqual(restored.updated_at, restored.created_at)
            self.assertEqual(restored.updated_by_id, actor.id)
            self.assertEqual(restored.row_version, 1)
            self.assertEqual(restored.values, source_record.values)
            link = EntityRecordLink.objects.get()
            self.assertEqual(link.target_id, target_record.id)
            self.assertTrue(link.scalar)
            self.assertFalse(link.exclusive)
            self.assertEqual(EntitySchemaVersion.objects.get(id=source_schema.id).schema_digest, 'source-original')
            with self.assertRaises(IntegrityError), transaction.atomic():
                EntityRecord.objects.filter(id=restored.id).update(updated_by_id=actor.id)
        finally:
            MigrationExecutor(connection).migrate([self.migrate_to])
            if connection.vendor == 'sqlite':
                # SQLite flush uses DELETE, which correctly hits append-only guards.
                # Recreate only this disposable test schema before the standard flush.
                MigrationExecutor(connection).migrate([('desk', None)])
                MigrationExecutor(connection).migrate([self.migrate_to])
