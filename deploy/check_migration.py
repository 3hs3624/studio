"""Integration check against disposable local PostgreSQL databases, never production."""
import os
import subprocess
import uuid
import sys
from unittest.mock import patch
sys.path.insert(0, '/app/deploy')
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from migrate_postgres import migrate, MigrationError, table_hash, catalog


def check():
    # Dedicated created databases are owned by a non-superuser to mirror hosting.
    admin = make_conninfo(host='database',dbname='studio',user='studio_owner',password=os.environ['DB_OWNER_PASSWORD'])
    suffix = uuid.uuid4().hex[:10]
    role = 'migration_' + suffix
    databases = ['migration_source_'+suffix,'migration_target_'+suffix,'migration_occupied_'+suffix]
    password = uuid.uuid4().hex
    with psycopg.connect(admin, autocommit=True) as conn:
        conn.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
        for name in databases:
            conn.execute(sql.SQL('CREATE DATABASE {} OWNER {}').format(sql.Identifier(name),sql.Identifier(role)))
    dsns = [make_conninfo(host='database',dbname=n,user=role,password=password) for n in databases]
    try:
        env={**os.environ,'DEBUG':'1','DATABASE_URL':'','DB_ENGINE':'postgresql','DB_HOST':'database','DB_NAME':databases[0],'DB_USER':role,'DB_PASSWORD':password}
        subprocess.run(['python','manage.py','migrate','--noinput'],env=env,check=True,stdout=subprocess.DEVNULL)
        # Real auth hashes, organization, histories and all model tables.
        subprocess.run(['python','manage.py','bootstrap_local_access','--credential-file','/tmp/migration-test-accounts-'+suffix+'.json'],env=env,check=True,stdout=subprocess.DEVNULL)
        with psycopg.connect(dsns[2], autocommit=True) as occupied:
            occupied.execute('CREATE TABLE existing_data(id integer PRIMARY KEY)')
        try:
            migrate(dsns[0],dsns[2])
        except MigrationError:
            pass
        else:
            raise AssertionError('Nonempty destination was accepted')
        with patch('migrate_postgres.pg_run',side_effect=MigrationError('Simulated export failure')):
            try:
                migrate(dsns[0],dsns[1])
            except MigrationError:
                pass
            else:
                raise AssertionError('Export failure was ignored')
        with psycopg.connect(dsns[0]) as source:
            assert source.execute('SHOW default_transaction_read_only').fetchone()==('off',)
        migrate(dsns[0],dsns[1])
        with psycopg.connect(dsns[0], autocommit=True) as source, psycopg.connect(dsns[1], autocommit=True) as target:
            assert source.execute('SHOW default_transaction_read_only').fetchone()==('on',)
            assert target.execute('SHOW default_transaction_read_only').fetchone()==('off',)
            assert table_hash(source,'auth_user')==table_hash(target,'auth_user')
            assert catalog(source)==catalog(target)
            before=table_hash(target,'desk_userprofile')
            # Target can continue independently; retry must not overwrite it.
            target.execute("UPDATE desk_userprofile SET full_name='after-cutover' WHERE person_id=(SELECT p.id FROM desk_person p JOIN auth_user u ON u.id=p.user_id WHERE u.username='temp-admin')")
            assert table_hash(target,'desk_userprofile')!=before
        migrate(dsns[0],dsns[1])
        with psycopg.connect(dsns[1]) as target:
            assert target.execute("SELECT profile.full_name FROM desk_userprofile profile JOIN desk_person p ON p.id=profile.person_id JOIN auth_user u ON u.id=p.user_id WHERE u.username='temp-admin'").fetchone()==('after-cutover',)
        print('Disposable PostgreSQL migration verified: non-superuser restore, exact data/protections, frozen source, writable destination and safe retry.')
    finally:
        with psycopg.connect(admin, autocommit=True) as conn:
            for name in databases:
                conn.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))
            conn.execute(sql.SQL('DROP ROLE {}').format(sql.Identifier(role)))
        try:
            os.unlink('/tmp/migration-test-accounts-'+suffix+'.json')
        except FileNotFoundError:
            pass


if __name__=='__main__':
    check()
