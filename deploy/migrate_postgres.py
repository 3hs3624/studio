"""One-time, same-major PostgreSQL cutover; secrets never enter argv or logs.

Run inside the Render private network. The original database is retained and
frozen, never dropped. Only an empty, dedicated destination is accepted.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict


class MigrationError(Exception):
    pass


def identity(dsn):
    values = conninfo_to_dict(dsn)
    return hashlib.sha256(json.dumps({k: values.get(k, '') for k in
        ('host', 'port', 'dbname', 'user')}, sort_keys=True).encode()).hexdigest()


def pg_run(binary, args, dsn, **kwargs):
    values = conninfo_to_dict(dsn)
    env = {k: v for k, v in os.environ.items() if not k.startswith('PG')}
    for key, value in values.items():
        env['PG' + {'dbname': 'DATABASE', 'channel_binding': 'CHANNELBINDING'}.get(key, key.upper())] = value
    result = subprocess.run([binary, *args], env=env, stderr=subprocess.PIPE,
                            check=False, **kwargs)
    if result.returncode:
        # pg tools may include connection details and row contents in stderr.
        raise MigrationError(binary + ' failed; sensitive diagnostics withheld.')
    return result


def tables(conn):
    return [r[0] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")]


def table_hash(conn, table):
    keys = [r[0] for r in conn.execute("""SELECT a.attname FROM pg_index i
        CROSS JOIN LATERAL unnest(i.indkey) WITH ORDINALITY k(attnum, ord)
        JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=k.attnum
        WHERE i.indrelid=%s::regclass AND i.indisprimary ORDER BY k.ord""", ('public.' + table,))]
    if not keys:
        raise MigrationError('A source table lacks a primary key.')
    statement = sql.SQL('COPY (SELECT * FROM {} ORDER BY {}) TO STDOUT WITH (FORMAT binary)').format(
        sql.Identifier('public', table), sql.SQL(',').join(map(sql.Identifier, keys)))
    digest = hashlib.sha256()
    with conn.cursor().copy(statement) as stream:
        for block in stream:
            digest.update(block)
    count = conn.execute(sql.SQL('SELECT count(*) FROM {}').format(sql.Identifier('public', table))).fetchone()[0]
    return {'count': count, 'sha256': digest.hexdigest()}


def catalog(conn):
    triggers = conn.execute("""SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid),t.tgenabled
        FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND NOT t.tgisinternal ORDER BY 1,2""").fetchall()
    constraints = conn.execute("""SELECT c.relname,p.conname,pg_get_constraintdef(p.oid),p.convalidated,p.contype,pg_get_expr(p.conbin,p.conrelid)
        FROM pg_constraint p JOIN pg_class c ON c.oid=p.conrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' ORDER BY 1,2""").fetchall()
    normalized = []
    for table, name, definition, validated, kind, expression in constraints:
        if kind == 'c':
            # pg_dump reparses varchar[] casts into equivalent per-item casts.
            # Let PostgreSQL fold constants, retaining operator/group semantics.
            plan = conn.execute(sql.SQL('EXPLAIN (VERBOSE,FORMAT JSON,COSTS FALSE) SELECT {} FROM {} WHERE false').format(
                sql.SQL(expression),sql.Identifier('public',table))).fetchone()[0]
            definition = plan[0]['Plan']['Output']
        normalized.append((table,name,definition,validated))
    functions = conn.execute("""SELECT p.proname,pg_get_functiondef(p.oid) FROM pg_proc p
        JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' ORDER BY 1,2""").fetchall()
    sequences = {}
    for (name,) in conn.execute("SELECT sequencename FROM pg_sequences WHERE schemaname='public' ORDER BY 1").fetchall():
        sequences[name] = conn.execute(sql.SQL('SELECT last_value,is_called FROM {}').format(sql.Identifier('public', name))).fetchone()
    return {'triggers': triggers, 'constraints': normalized, 'functions': functions, 'sequences': sequences}


def migrate(source_dsn, target_dsn):
    if identity(source_dsn) == identity(target_dsn):
        raise MigrationError('Source and destination must differ.')
    with psycopg.connect(source_dsn, autocommit=True, connect_timeout=20) as source, \
         psycopg.connect(target_dsn, autocommit=True, connect_timeout=20) as target:
        # Session override permits restoring the source default after an early failure.
        source.execute('SET default_transaction_read_only=off')
        if not source.execute('SELECT pg_try_advisory_lock(65020261106)').fetchone()[0]:
            raise MigrationError('Another migration is running.')
        receipt_exists = target.execute("SELECT to_regclass('studio_migration.receipt') IS NOT NULL").fetchone()[0]
        if receipt_exists:
            receipt = target.execute('SELECT source_id FROM studio_migration.receipt WHERE id=1').fetchone()
            if receipt != (identity(source_dsn),):
                raise MigrationError('Destination receipt does not match the source.')
            print('NEON_MIGRATION previously verified; destination reused without copying.')
            return
        if tables(target) or target.execute("SELECT count(*) FROM pg_namespace WHERE nspname NOT IN ('public','information_schema') AND nspname NOT LIKE 'pg_%'").fetchone()[0]:
            raise MigrationError('Destination must be empty; no existing data was changed.')
        for conn in (source, target):
            if int(conn.execute('SHOW server_version_num').fetchone()[0]) // 10000 != 16:
                raise MigrationError('Both databases must run PostgreSQL 16.')
        if source.execute("SELECT count(*) FROM pg_extension WHERE extname <> 'plpgsql'").fetchone()[0]:
            raise MigrationError('Source extensions require a separate compatibility review.')
        source_tables = tables(source)
        if not source_tables or 'auth_user' not in source_tables:
            raise MigrationError('Source application schema is missing.')
        prior_default = source.execute("SELECT setting FROM pg_db_role_setting s CROSS JOIN LATERAL unnest(s.setconfig) setting WHERE s.setdatabase=(SELECT oid FROM pg_database WHERE datname=current_database()) AND s.setrole=0 AND setting LIKE 'default_transaction_read_only=%'").fetchall()
        if prior_default:
            raise MigrationError('Source already has a read-only override; review before retrying.')
        frozen = False
        verified = False
        database = source.execute('SELECT current_database()').fetchone()[0]
        try:
            source.execute(sql.SQL('ALTER DATABASE {} SET default_transaction_read_only=on').format(sql.Identifier(database)))
            frozen = True
            # Drain existing app transactions. New connections inherit read-only.
            if source.execute("SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid() AND backend_type='client backend' AND usename<>current_user").fetchone()[0]:
                raise MigrationError('Unexpected source database clients; no sessions terminated.')
            source.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid() AND backend_type='client backend' AND usename=current_user")
            with source.transaction():
                source.execute('SET LOCAL lock_timeout=\'20s\'')
                source.execute(sql.SQL('LOCK TABLE {} IN SHARE MODE').format(sql.SQL(',').join(sql.Identifier('public', t) for t in source_tables)))
                manifest = {t: table_hash(source, t) for t in source_tables}
                source_catalog = catalog(source)
                with tempfile.TemporaryDirectory(prefix='studio-pg-') as directory:
                    dump = str(Path(directory) / 'backup.dump')
                    pg_run('pg_dump', ['--format=custom','--no-owner','--no-acl','--file',dump], source_dsn, stdout=subprocess.DEVNULL)
                    os.chmod(dump, 0o600)
                    toc = pg_run('pg_restore', ['--list',dump], target_dsn, stdout=subprocess.PIPE).stdout.decode()
                    # Neon already owns an empty public schema. Preserve that ownership.
                    toc = '\n'.join(line for line in toc.splitlines() if ' SCHEMA - public ' not in line)
                    toc_path = Path(directory) / 'restore.list'
                    toc_path.write_text(toc + '\n')
                    pg_run('pg_restore', ['--no-owner','--no-acl','--no-comments','--exit-on-error','--single-transaction','--use-list',str(toc_path),'--dbname',conninfo_to_dict(target_dsn)['dbname'],dump], target_dsn, stdout=subprocess.DEVNULL)
                if tables(target) != source_tables or {t: table_hash(target,t) for t in source_tables} != manifest:
                    raise MigrationError('Table contents differ; cutover stopped.')
                if catalog(target) != source_catalog:
                    raise MigrationError('Sequences, constraints, functions or triggers differ; cutover stopped.')
                with target.transaction():
                    target.execute('CREATE SCHEMA studio_migration')
                    target.execute('CREATE TABLE studio_migration.receipt (id integer PRIMARY KEY CHECK(id=1),source_id text NOT NULL,manifest jsonb NOT NULL,verified_at timestamptz NOT NULL DEFAULT now())')
                    target.execute('INSERT INTO studio_migration.receipt(id,source_id,manifest) VALUES(1,%s,%s::jsonb)',(identity(source_dsn),json.dumps(manifest)))
                verified = True
            print('NEON_MIGRATION verified: '+str(len(manifest))+' tables, '+str(sum(t['count'] for t in manifest.values()))+' rows; sequences, constraints and protection triggers matched. Source retained read-only.')
        finally:
            if frozen and not verified:
                source.execute(sql.SQL('ALTER DATABASE {} RESET default_transaction_read_only').format(sql.Identifier(database)))
                print('NEON_MIGRATION stopped; source write access restored. Destination requires review.')


if __name__ == '__main__':
    try:
        migrate(os.environ['DATABASE_URL'], os.environ['NEON_MIGRATION_TARGET_URL'])
    except Exception as error:
        # Do not emit exception text: DSNs, passwords and data may be included.
        print('NEON_MIGRATION failed ('+type(error).__name__+'); credentials and data withheld.', file=sys.stderr)
        sys.exit(1)
