import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q

ROLES = ['SERVICE_MANAGER', 'AGENT', 'ORG_ADMIN', 'RESOURCE_READER', 'ASSET_MANAGER']
ASSET_STATUSES = ['UNVERIFIED','STOCK','IN_USE','RETIRED']
STATUSES = ['NEW', 'ASSIGNED', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED']
REQUEST_STATUSES = ['PENDING_APPROVAL','APPROVED','IN_PROGRESS','FULFILLED','CLOSED','REJECTED','CANCELLED']

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
    manufacturer = models.CharField(max_length=200, blank=True)
    serial_number = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='UNVERIFIED')
    custodian = models.ForeignKey(Person, null=True, on_delete=models.PROTECT, related_name='held_assets')
    row_version = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'asset_no'], name='asset_org_number'),
            models.UniqueConstraint(fields=['organization','manufacturer','serial_number'],condition=~Q(serial_number=''),name='asset_serial_unique'),
            models.CheckConstraint(condition=Q(status__in=ASSET_STATUSES),name='asset_status'),
            models.CheckConstraint(condition=(Q(status='IN_USE',custodian__isnull=False)|(~Q(status='IN_USE')&Q(custodian__isnull=True))),name='asset_custodian_state')]
        indexes = [models.Index(fields=['organization','status','-created_at']),models.Index(fields=['organization','custodian'])]

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
        constraints = [models.CheckConstraint(condition=Q(status__in=STATUSES+REQUEST_STATUSES), name='ticket_status'),
                       models.CheckConstraint(condition=Q(type__in=['INCIDENT','SERVICE_REQUEST']), name='ticket_type'),
                       models.CheckConstraint(condition=(Q(type='INCIDENT',status__in=STATUSES)|Q(type='SERVICE_REQUEST',status__in=REQUEST_STATUSES)),name='ticket_type_status')]
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

class BusinessCalendar(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    timezone = models.CharField(max_length=80)
    weekdays = models.JSONField()
    starts_at = models.CharField(max_length=5)
    ends_at = models.CharField(max_length=5)
    holidays = models.JSONField(default=list)

class SLAPolicy(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    calendar = models.ForeignKey(BusinessCalendar, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    priority = models.PositiveSmallIntegerField()
    version = models.PositiveIntegerField()
    response_minutes = models.PositiveIntegerField()
    resolution_minutes = models.PositiveIntegerField()
    warning_percent = models.PositiveSmallIntegerField(default=80)
    pause_on_pending = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','priority','version'],name='sla_policy_version'),
            models.CheckConstraint(condition=Q(priority__range=(1,5)),name='sla_priority_range'),
            models.CheckConstraint(condition=Q(response_minutes__gt=0,resolution_minutes__gt=0),name='sla_positive_budgets'),
            models.CheckConstraint(condition=Q(warning_percent__range=(1,99)),name='sla_warning_range')]

class SLAInstance(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ticket = models.OneToOneField(Ticket, on_delete=models.PROTECT, related_name='sla_instance')
    policy = models.ForeignKey(SLAPolicy, on_delete=models.PROTECT)
    snapshot = models.JSONField()
    accounted_at = models.DateTimeField()
    response_elapsed_us = models.PositiveBigIntegerField(default=0)
    resolution_elapsed_us = models.PositiveBigIntegerField(default=0)
    response_due_at = models.DateTimeField()
    resolution_due_at = models.DateTimeField()
    response_completed_at = models.DateTimeField(null=True)
    resolved_at = models.DateTimeField(null=True)
    paused_at = models.DateTimeField(null=True)
    next_evaluation_at = models.DateTimeField(null=True)
    class Meta:
        indexes = [models.Index(fields=['response_due_at'],condition=Q(response_completed_at__isnull=True),name='sla_response_pending'),
                   models.Index(fields=['resolution_due_at'],condition=Q(resolved_at__isnull=True,paused_at__isnull=True),name='sla_resolution_pending'),
                   models.Index(fields=['next_evaluation_at'],condition=Q(next_evaluation_at__isnull=False),name='sla_next_evaluation')]

class SLAClockEvent(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    instance = models.ForeignKey(SLAInstance, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, null=True, on_delete=models.PROTECT)
    kind = models.CharField(max_length=30)
    occurred_at = models.DateTimeField()
    detail = models.JSONField(default=dict)

class SLAAlert(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    instance = models.ForeignKey(SLAInstance, on_delete=models.PROTECT)
    goal = models.CharField(max_length=20)
    level = models.CharField(max_length=10)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['instance','goal','level'],name='sla_alert_once'),
                       models.CheckConstraint(condition=Q(goal__in=['RESPONSE','RESOLUTION']),name='sla_goal'),
                       models.CheckConstraint(condition=Q(level__in=['WARNING','BREACH']),name='sla_alert_level')]

class Notification(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    recipient = models.ForeignKey(Person, on_delete=models.PROTECT)
    ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT)
    alert = models.ForeignKey(SLAAlert, null=True, on_delete=models.PROTECT)
    event = models.ForeignKey(AuditEvent, null=True, on_delete=models.PROTECT)
    kind = models.CharField(max_length=30, default='SLA')
    read_at = models.DateTimeField(null=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['recipient','alert'],name='notification_recipient_alert'),
            models.UniqueConstraint(fields=['recipient','event'],condition=Q(event__isnull=False),name='notification_recipient_event'),
            models.CheckConstraint(condition=(Q(kind='SLA',alert__isnull=False,event__isnull=True)|
                Q(kind__in=['APPROVAL_REQUESTED','APPROVAL_DECIDED','REQUEST_READY','REQUEST_FULFILLED','REQUEST_CANCELLED'],alert__isnull=True,event__isnull=False)),name='notification_source')]
        indexes = [models.Index(fields=['recipient','-created_at','-id'])]

class CatalogItem(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=40)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='catalog_item_code')]

class CatalogVersion(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    item = models.ForeignKey(CatalogItem, on_delete=models.PROTECT, related_name='versions')
    version = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField()
    fulfillment_group = models.ForeignKey(Group, on_delete=models.PROTECT)
    approval_required = models.BooleanField(default=True)
    approver = models.ForeignKey(Person, null=True, on_delete=models.PROTECT)
    public_to_org = models.BooleanField(default=True)
    available = models.BooleanField(default=True)
    fields = models.JSONField(default=list)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['item','version'],name='catalog_version_unique'),
            models.CheckConstraint(condition=(Q(approval_required=True,approver__isnull=False)|Q(approval_required=False,approver__isnull=True)),name='catalog_approval_config')]

class CatalogAudience(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    catalog_version = models.ForeignKey(CatalogVersion, on_delete=models.PROTECT, related_name='audiences')
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['catalog_version','group'],name='catalog_audience_unique')]

class ServiceRequest(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ticket = models.OneToOneField(Ticket, on_delete=models.PROTECT, related_name='service_request')
    catalog_version = models.ForeignKey(CatalogVersion, on_delete=models.PROTECT)
    values = models.JSONField(default=dict)
    snapshot = models.JSONField()
    resubmission_of = models.ForeignKey(Ticket, null=True, on_delete=models.PROTECT, related_name='resubmissions')

class RequestApproval(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    ticket = models.OneToOneField(Ticket, on_delete=models.PROTECT, related_name='request_approval')
    approver = models.ForeignKey(Person, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='PENDING')
    closed_at = models.DateTimeField(null=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(status__in=['PENDING','APPROVED','REJECTED','CANCELLED']),name='request_approval_status')]
        indexes = [models.Index(fields=['approver','-created_at'],condition=Q(status='PENDING'),name='request_approval_pending')]

class ApprovalDecision(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    approval = models.OneToOneField(RequestApproval, on_delete=models.PROTECT, related_name='decision')
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    decision = models.CharField(max_length=10)
    reason = models.TextField(blank=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(decision__in=['APPROVE','REJECT']),name='approval_decision_value')]

class AssetCustody(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='custodies')
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    issued_by = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='issued_custodies')
    issue_request = models.ForeignKey(Ticket, null=True, on_delete=models.PROTECT)
    issue_location = models.CharField(max_length=200)
    issue_reason = models.TextField()
    returned_at = models.DateTimeField(null=True)
    returned_by = models.ForeignKey(Person, null=True, on_delete=models.PROTECT, related_name='returned_custodies')
    return_location = models.CharField(max_length=200, blank=True)
    return_reason = models.TextField(blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['asset'],condition=Q(returned_at__isnull=True),name='asset_single_active_custody'),
            models.CheckConstraint(condition=(Q(returned_at__isnull=True,returned_by__isnull=True)|Q(returned_at__isnull=False,returned_by__isnull=False)),name='asset_return_fields')]
        indexes = [models.Index(fields=['organization','person','-created_at'])]

class AssetHistory(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='history')
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    custody = models.ForeignKey(AssetCustody, null=True, on_delete=models.PROTECT)
    request = models.ForeignKey(Ticket, null=True, on_delete=models.PROTECT)
    kind = models.CharField(max_length=20)
    reason = models.TextField()
    before_data = models.JSONField(default=dict)
    after_data = models.JSONField()
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(kind__in=['REGISTER','UPDATE','VERIFY','ISSUE','RETURN','MOVE','RETIRE']),name='asset_history_kind')]
        indexes = [models.Index(fields=['asset','-created_at','-id'])]
