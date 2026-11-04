from django.core.management.base import BaseCommand
from desk.outbox import drain

class Command(BaseCommand):
    help = 'Process one batch of local outbox events. Schedule periodically; no external notifications yet.'
    def handle(self,*args,**options):
        self.stdout.write(f'Processed: {drain()}')
