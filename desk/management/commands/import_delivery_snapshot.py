"""Import a trusted export, without executing provider jobs or saving credentials."""
import json,uuid
from pathlib import Path
from django.core.management.base import BaseCommand,CommandError
from desk.models import Person
from desk.delivery import ingest
from desk.services import BusinessError

class Command(BaseCommand):
    help='Import a validated GitHub or Jenkins snapshot; no outgoing provider requests.'
    def add_arguments(self,parser):
        parser.add_argument('--organization',required=True,type=uuid.UUID)
        parser.add_argument('--actor',required=True)
        parser.add_argument('--provider',choices=['github','jenkins'],required=True)
        parser.add_argument('--file',required=True)
    def handle(self,*args,**options):
        actor=Person.objects.filter(organization_id=options['organization'],user__username=options['actor']).select_related('user','organization').first()
        if not actor:raise CommandError('Organization actor not found.')
        try:
            path=Path(options['file'])
            if path.stat().st_size>2*1024*1024:raise CommandError('Snapshot exceeds 2 MiB.')
            payload=json.loads(path.read_text(encoding='utf-8'))
            count=ingest(actor,options['provider'],payload,uuid.uuid4())
        except (OSError,ValueError,BusinessError) as exc:raise CommandError('Snapshot rejected: '+(exc.code if isinstance(exc,BusinessError) else type(exc).__name__)) from None
        self.stdout.write(f'Imported {count} observations. No build or deployment was triggered.')
