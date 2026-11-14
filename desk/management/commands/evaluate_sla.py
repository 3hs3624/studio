from django.core.management.base import BaseCommand
from desk.sla import evaluate_due

class Command(BaseCommand):
    help='Evaluate one bounded batch of due SLA clocks and create in-app notifications.'
    def handle(self,*args,**options):
        self.stdout.write(f'Evaluated: {evaluate_due()}')
