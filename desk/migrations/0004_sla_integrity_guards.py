from importlib import import_module
from types import SimpleNamespace
from django.db import migrations

NAMES={'BusinessCalendar','SLAPolicy','SLAInstance','SLAClockEvent','SLAAlert','Notification'}
IMMUTABLE={'BusinessCalendar','SLAPolicy','SLAClockEvent','SLAAlert'}

def install(apps,editor,remove=False):
    # Reuse the already-tested SQL generator, scoped only to this migration's new tables.
    models=[m for m in apps.get_app_config('desk').get_models() if m.__name__ in NAMES]
    scoped=SimpleNamespace(get_app_config=lambda _:SimpleNamespace(get_models=lambda:models))
    module=import_module('desk.migrations.0002_integrity_guards')
    original=module.APPEND_ONLY
    try:
        module.APPEND_ONLY=original | IMMUTABLE
        module.guards(scoped,editor,remove=remove)
    finally:
        module.APPEND_ONLY=original

def forward(apps,editor):
    install(apps,editor)

def reverse(apps,editor):
    install(apps,editor,remove=True)

class Migration(migrations.Migration):
    dependencies=[('desk','0003_businesscalendar_slainstance_slaclockevent_slaalert_and_more')]
    operations=[migrations.RunPython(forward,reverse)]
