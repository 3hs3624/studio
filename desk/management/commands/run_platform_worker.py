"""Run durable integration jobs and workflow timers outside HTTP requests."""
import signal,time,uuid
from django.core.management.base import BaseCommand
from django.db import transaction,close_old_connections,connection
from django.utils import timezone
from desk.models import ProcessTask,ProcessRun,Organization
from desk.integrations.service import process_one
from desk import process_engine as engine

class Command(BaseCommand):
    help='API 실행 큐·워크플로우 시간 대기 처리. --once는 1회만 실행합니다.'
    def add_arguments(self,parser):parser.add_argument('--once',action='store_true');parser.add_argument('--interval',type=float,default=2)
    def handle(self,*args,**options):
        stopped=False
        def stop(*args):
            nonlocal stopped
            stopped=True
        for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,stop)
        while not stopped:
            # A single-cycle caller may own a transaction (e.g. integration tests).
            # Closing its connection would discard that transaction on PostgreSQL.
            if not connection.in_atomic_block:close_old_connections()
            job=process_one();progress=bool(job)
            due=list(ProcessTask.objects.filter(kind='WAIT',status='OPEN',due_at__lte=timezone.now(),run__status__in=['ACTIVE','BLOCKED']).values_list('run_id',flat=True).distinct()[:50])
            for id in due:
                with transaction.atomic():
                    candidate=ProcessRun.objects.get(id=id);Organization.objects.select_for_update().get(pk=candidate.organization_id);run=ProcessRun.objects.select_for_update().get(pk=id)
                    if run.status not in ('ACTIVE','BLOCKED'):continue
                    tokens=[];actor=run.started_by
                    if not actor.active or not actor.user.is_active or not actor.organization.active:continue
                    for task in run.tasks.filter(kind='WAIT',status='OPEN',due_at__lte=timezone.now()):
                        task.status='COMPLETED';task.save(update_fields=['status']);node=next(n for n in run.graph['nodes'] if n['key']==task.node_key);tokens.append((node['next'],task.frames));engine.event(actor,run,'WAIT_ELAPSED',task.node_key,{'worker':True})
                    if tokens:run.row_version+=1;engine.advance(actor,run,tokens);progress=True
            if options['once']:break
            if not progress:time.sleep(max(.1,min(options['interval'],10)))
