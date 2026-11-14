import argparse
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'control.py'
spec = importlib.util.spec_from_file_location('local_control', SOURCE)
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


class LocalConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        for name in ('build-ca.pem', 'init-db.sql', 'Caddyfile'):
            (self.root / name).write_text('')
        self.root_patch = patch.object(control, 'ROOT', self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.directory.cleanup()

    def configure(self, **overrides):
        args = dict(name='isolated-test', hostname='localhost',
                    http_port=18080, https_port=18443, build_ca=None)
        args.update(overrides)
        with patch('builtins.print'):
            control.configure(argparse.Namespace(**args))

    def test_configuration_is_private_and_preserves_existing_credentials(self):
        self.configure()
        ap = control.read_values('ap')
        db = control.read_values('db')
        self.assertNotEqual(ap['DB_PASSWORD'], ap['MIGRATION_PASSWORD'])
        self.assertNotIn(db['DB_OWNER_PASSWORD'], ap.values())
        self.assertEqual(ap['DB_PASSWORD'], db['DB_PASSWORD'])
        self.assertEqual(ap['MIGRATION_PASSWORD'], db['MIGRATION_PASSWORD'])
        self.assertGreater(int(ap['APP_UID']), 0)
        self.assertGreater(int(ap['APP_GID']), 0)
        if os.name == 'posix':
            self.assertEqual((self.root / '.env.ap').stat().st_mode & 0o777, 0o600)
            self.assertEqual((self.root / '.env.db').stat().st_mode & 0o777, 0o600)
        original = (self.root / '.env.ap').read_bytes()
        with self.assertRaises(SystemExit):
            self.configure()
        self.assertEqual((self.root / '.env.ap').read_bytes(), original)

    def test_invalid_ports_and_remote_host_do_not_write_partial_configuration(self):
        for values in ({'http_port': 18443}, {'https_port': 80},
                       {'hostname': 'public.example'}, {'name': '../other'}):
            with self.assertRaises(SystemExit):
                self.configure(**values)
            self.assertFalse((self.root / '.env.ap').exists())
            self.assertFalse((self.root / '.env.db').exists())

    def test_unrelated_host_settings_cannot_override_local_secrets(self):
        self.configure()
        with patch.dict(os.environ, {
                'DB_PASSWORD': 'unrelated-secret', 'STACK_NAME': 'hosted',
                'PATH': os.environ.get('PATH', '')}):
            environment = control.docker_env()
        self.assertNotIn('DB_PASSWORD', environment)
        self.assertNotIn('STACK_NAME', environment)
        self.assertIn('PATH', environment)


if __name__ == '__main__':
    unittest.main()
