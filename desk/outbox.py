import logging
from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from .models import OutboxEvent

logger = logging.getLogger(__name__)

def deliver(event):
    """Local event sink only; external notification adapters are not implemented."""
    logger.info('outbox event=%s type=%s',event.id,event.event_type)

def process_one(event_id):
    with transaction.atomic():
        event=OutboxEvent.objects.select_for_update().get(id=event_id)
        now=timezone.now()
        if event.processed_at or event.attempts>=5 or (event.next_attempt_at and event.next_attempt_at>now):
            return False
        event.attempts+=1
        try:
            deliver(event)
            event.processed_at=now
            event.last_error=''
            event.next_attempt_at=None
        except Exception as exc:
            # Persist class only: exception text may contain external credentials or payloads.
            event.last_error=type(exc).__name__[:200]
            event.next_attempt_at=now+timedelta(seconds=2**event.attempts) if event.attempts<5 else None
        event.save()
        return event.processed_at is not None

def drain(limit=100):
    now=timezone.now()
    ids=list(OutboxEvent.objects.filter(processed_at__isnull=True,attempts__lt=5)
             .filter(Q(next_attempt_at__isnull=True)|Q(next_attempt_at__lte=now))
             .order_by('created_at').values_list('id',flat=True)[:limit])
    return sum(process_one(i) for i in ids)
