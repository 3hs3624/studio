"""Run through compose exec on web to verify runtime DB privilege boundaries."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection, transaction, ProgrammingError
from django.db.migrations.executor import MigrationExecutor
from django.contrib.auth import get_user_model
from desk.models import Organization

assert 'DB_OWNER_PASSWORD' not in os.environ
assert 'MIGRATION_PASSWORD' not in os.environ
assert not os.environ.get('DATABASE_URL')
assert not os.environ.get('NEON_MIGRATION_TARGET_URL')
with connection.cursor() as cursor:
    cursor.execute("SELECT current_user, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=current_user")
    role = cursor.fetchone()
    assert role == ('itsm_runtime', False, False, False), 'Unexpected runtime privileges'
    cursor.execute("SELECT has_schema_privilege(current_user, 'public', 'CREATE'), has_database_privilege(current_user, current_database(), 'TEMP')")
    assert cursor.fetchone() == (False, False), 'Runtime must not create schema objects'
assert not MigrationExecutor(connection).migration_plan(
    MigrationExecutor(connection).loader.graph.leaf_nodes()), 'Pending migrations'
assert get_user_model().objects.count() == 5
assert Organization.objects.count() == 1
with transaction.atomic():
    Organization.objects.create(name='local-docker-rollback-probe')
    assert Organization.objects.filter(name='local-docker-rollback-probe').exists()
    transaction.set_rollback(True)
assert not Organization.objects.filter(name='local-docker-rollback-probe').exists()
try:
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute('CREATE TABLE public.local_docker_forbidden (id integer)')
except ProgrammingError as error:
    assert getattr(error.__cause__, 'sqlstate', None) == '42501', 'Unexpected DDL failure'
else:
    raise AssertionError('Runtime unexpectedly created a table')
print('Verified runtime DML/rollback, no DDL/admin credentials, schema migration completion and preserved local data.')
