"""Organization consistency and append-only history, supported on SQLite and PostgreSQL."""
from django.db import migrations

APPEND_ONLY = {'Comment','StatusHistory','AuditEvent'}

def guards(apps, editor, remove=False):
    vendor=editor.connection.vendor
    if vendor not in ('sqlite','postgresql'):
        raise RuntimeError('Only SQLite and PostgreSQL are supported.')
    for model in apps.get_app_config('desk').get_models():
        table=model._meta.db_table
        fields={f.name:f for f in model._meta.fields}
        if 'organization' not in fields:
            continue
        related=[f for f in model._meta.fields if f.is_relation and f.name!='organization'
                 and any(r.name=='organization' for r in f.related_model._meta.fields)]
        checks=[]
        for f in related:
            dest=f.related_model._meta.db_table
            checks.append(f'(NEW.{f.column} IS NOT NULL AND NOT EXISTS (SELECT 1 FROM {dest} d WHERE d.id=NEW.{f.column} AND d.organization_id=NEW.organization_id))')
        # Organization is immutable; therefore referenced rows cannot move across organizations later.
        immutable='NEW.organization_id IS DISTINCT FROM OLD.organization_id' if vendor=='postgresql' else 'NEW.organization_id IS NOT OLD.organization_id'
        if vendor=='sqlite':
            for event in ('INSERT','UPDATE'):
                name=f'{table}_org_{event.lower()}'
                editor.execute(f'DROP TRIGGER IF EXISTS {name}')
                if not remove:
                    predicates=checks+([immutable] if event=='UPDATE' else [])
                    if predicates:
                        condition=' OR '.join(predicates)
                        editor.execute(f"CREATE TRIGGER {name} BEFORE {event} ON {table} WHEN {condition} BEGIN SELECT RAISE(ABORT, 'organization boundary'); END")
            if model.__name__ in APPEND_ONLY:
                for event in ('UPDATE','DELETE'):
                    name=f'{table}_immutable_{event.lower()}'
                    editor.execute(f'DROP TRIGGER IF EXISTS {name}')
                    if not remove:
                        editor.execute(f"CREATE TRIGGER {name} BEFORE {event} ON {table} BEGIN SELECT RAISE(ABORT, 'append only'); END")
        else:
            name=f'{table}_org_guard'
            editor.execute(f'DROP TRIGGER IF EXISTS {name} ON {table}')
            if remove:
                editor.execute(f'DROP FUNCTION IF EXISTS {name}()')
            else:
                check=' OR '.join(checks) or 'FALSE'
                editor.execute(f"""CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$
                BEGIN
                  IF TG_OP='UPDATE' THEN
                    IF {immutable} THEN RAISE EXCEPTION 'organization boundary' USING ERRCODE='23514'; END IF;
                  END IF;
                  IF {check} THEN RAISE EXCEPTION 'organization boundary' USING ERRCODE='23514'; END IF;
                  RETURN NEW;
                END; $$""")
                editor.execute(f'CREATE TRIGGER {name} BEFORE INSERT OR UPDATE ON {table} FOR EACH ROW EXECUTE FUNCTION {name}()')
            if model.__name__ in APPEND_ONLY:
                name=f'{table}_immutable'
                editor.execute(f'DROP TRIGGER IF EXISTS {name} ON {table}')
                if remove:
                    editor.execute(f'DROP FUNCTION IF EXISTS {name}()')
                else:
                    editor.execute(f"""CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$
                    BEGIN RAISE EXCEPTION 'append only' USING ERRCODE='23514'; END; $$""")
                    editor.execute(f'CREATE TRIGGER {name} BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION {name}()')

def forward(apps,editor):
    guards(apps,editor)

def reverse(apps,editor):
    guards(apps,editor,remove=True)

class Migration(migrations.Migration):
    dependencies=[('desk','0001_initial')]
    operations=[migrations.RunPython(forward,reverse)]
