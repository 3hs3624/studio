from django.db import migrations, models


def role_guards(apps, editor, remove=False):
    from importlib import import_module
    from types import SimpleNamespace
    gen = import_module('desk.migrations.0002_integrity_guards')
    selected = [apps.get_model('desk', 'RoleGrant')]
    filtered = SimpleNamespace(get_app_config=lambda name: SimpleNamespace(get_models=lambda: selected))
    gen.guards(filtered, editor, remove=remove)


def remove_guards(apps, editor):
    role_guards(apps, editor, True)


def install_guards(apps, editor):
    role_guards(apps, editor)


class Migration(migrations.Migration):
    dependencies = [('desk', '0010_entitydefinition_entityschemaversion_entityrecord_and_more')]
    operations = [
        migrations.RunPython(remove_guards, install_guards),
        migrations.RemoveConstraint(model_name='rolegrant', name='role_allowlist'),
        migrations.AlterField(
            model_name='rolegrant', name='role',
            field=models.CharField(choices=[
                ('SERVICE_MANAGER', 'SERVICE_MANAGER'), ('AGENT', 'AGENT'),
                ('ORG_ADMIN', 'ORG_ADMIN'), ('RESOURCE_READER', 'RESOURCE_READER'),
                ('ASSET_MANAGER', 'ASSET_MANAGER'), ('PROCUREMENT_MANAGER', 'PROCUREMENT_MANAGER'),
                ('STOCK_MANAGER', 'STOCK_MANAGER'), ('DEVELOPER', 'DEVELOPER'),
                ('SOLUTION_OPERATOR', 'SOLUTION_OPERATOR')], max_length=40)),
        migrations.AddConstraint(
            model_name='rolegrant',
            constraint=models.CheckConstraint(condition=models.Q(role__in=[
                'SERVICE_MANAGER','AGENT','ORG_ADMIN','RESOURCE_READER','ASSET_MANAGER',
                'PROCUREMENT_MANAGER','STOCK_MANAGER','DEVELOPER','SOLUTION_OPERATOR']),
                name='role_allowlist')),
        migrations.RunPython(install_guards, remove_guards),
    ]
