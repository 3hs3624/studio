import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q

ROLES = ['SERVICE_MANAGER', 'AGENT', 'ORG_ADMIN', 'RESOURCE_READER']
STATUSES = ['NEW', 'ASSIGNED', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED']

class Base(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True

class Organization(Base):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

class Person(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='person')
    display_name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    row_version = models.PositiveIntegerField(default=1)

class Group(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    triage = models.BooleanField(default=False)
    row_version = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'name'], name='group_org_name'),
                       models.UniqueConstraint(fields=['organization'], condition=Q(triage=True, active=True), name='one_active_triage')]

class Membership(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['group', 'person'], name='member_unique')]

class RoleGrant(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    role = models.CharField(max_length=40, choices=[(x, x) for x in ROLES])
    class Meta:
        constraints = [models.UniqueConstraint(fields=['person', 'role'], name='role_unique'),
                       models.CheckConstraint(condition=Q(role__in=ROLES), name='role_allowlist')]

class Asset(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    asset_no = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    portal_visible = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'asset_no'], name='asset_org_number')]

class ConfigurationItem(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ci_no = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=80)
    status = models.CharField(max_length=40, default='ACTIVE')
    portal_visible = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'ci_no'], name='ci_org_number')]

class Ticket(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    number = models.CharField(max_length=40, unique=True)
    type = models.CharField(max_length=20, default='INCIDENT', editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    requested_by = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='requested_tickets')
    status = models.CharField(max_length=30, default='NEW')
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    assignee = models.ForeignKey(Person, on_delete=models.PROTECT, null=True, related_name='assigned_tickets')
    row_version = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(status__in=STATUSES), name='ticket_status'),
                       models.CheckConstraint(condition=Q(type='INCIDENT'), name='ticket_type')]
        indexes = [models.Index(fields=['organization', 'requested_by', '-created_at', '-id']),
                   models.Index(fields=['organization', 'group', 'status', '-created_at']),
                   models.Index(fields=['organization', 'assignee', 'status', '-created_at'])]

class Incident(models.Model):
    ticket = models.OneToOneField(Ticket, primary_key=True, on_delete=models.PROTECT)
    impact = models.PositiveSmallIntegerField()
    urgency = models.PositiveSmallIntegerField()
    priority = models.PositiveSmallIntegerField()
    pending_reason = models.TextField(blank=True)
    resolution = models.TextField(blank=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(impact__range=(1,3)), name='impact_range'),
                       models.CheckConstraint(condition=Q(urgency__range=(1,3)), name='urgency_range'),
                       models.CheckConstraint(condition=Q(priority__range=(1,5)), name='priority_range')]

class TicketResource(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT, related_name='resources')
    asset = models.ForeignKey(Asset, null=True, on_delete=models.PROTECT)
    ci = models.ForeignKey(ConfigurationItem, null=True, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.CheckConstraint(condition=(Q(asset__isnull=False,ci__isnull=True)|Q(asset__isnull=True,ci__isnull=False)), name='one_resource_target'),
                       models.UniqueConstraint(fields=['ticket', 'asset'], condition=Q(asset__isnull=False), name='ticket_asset_unique'),
                       models.UniqueConstraint(fields=['ticket', 'ci'], condition=Q(ci__isnull=False), name='ticket_ci_unique')]

class Comment(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)
    author = models.ForeignKey(Person, on_delete=models.PROTECT)
    visibility = models.CharField(max_length=10)
    body = models.TextField()
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(visibility__in=['PUBLIC','INTERNAL']), name='comment_visibility')]

class StatusHistory(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30)
    reason = models.TextField(blank=True)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)

class AuditEvent(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    entity_type = models.CharField(max_length=80)
    entity_id = models.UUIDField()
    before_data = models.JSONField(default=dict)
    after_data = models.JSONField(default=dict)
    request_id = models.UUIDField()

class OutboxEvent(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    event_type = models.CharField(max_length=80)
    entity_id = models.UUIDField()
    payload = models.JSONField(default=dict)
    processed_at = models.DateTimeField(null=True)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True)
    last_error = models.CharField(max_length=200, blank=True)
    class Meta:
        indexes = [models.Index(fields=['processed_at','next_attempt_at'])]

class IdempotencyRecord(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    operation = models.CharField(max_length=200)
    key = models.CharField(max_length=128)
    request_hash = models.CharField(max_length=64)
    response_code = models.PositiveSmallIntegerField()
    response_body = models.JSONField(default=dict)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','actor','operation','key'], name='idempotency_unique')]
