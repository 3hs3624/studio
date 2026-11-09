import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

ROLES = ['SERVICE_MANAGER', 'AGENT', 'ORG_ADMIN', 'RESOURCE_READER', 'ASSET_MANAGER', 'PROCUREMENT_MANAGER', 'STOCK_MANAGER', 'DEVELOPER', 'SOLUTION_OPERATOR']
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
    session_epoch = models.UUIDField(default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='person')
    active = models.BooleanField(default=True)
    row_version = models.PositiveIntegerField(default=1)
    expires_on = models.DateField(null=True, blank=True)

    @property
    def display_name(self):
        if hasattr(self, '_pending_display_name'):
            return self._pending_display_name
        try:
            return self.profile.full_name
        except UserProfile.DoesNotExist:
            return ''

    @display_name.setter
    def display_name(self, value):
        self._pending_display_name = value

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self, '_pending_display_name'):
            UserProfile.objects.update_or_create(person=self, defaults=dict(organization_id=self.organization_id,full_name=self._pending_display_name))
            del self._pending_display_name

def group_code():
    return 'G_' + uuid.uuid4().hex[:20].upper()

class Group(Base):
    code = models.CharField(max_length=40, default=group_code)
    description = models.CharField(max_length=500, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    triage = models.BooleanField(default=False)
    row_version = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'code'], name='group_org_code'), models.UniqueConstraint(fields=['organization', 'name'], name='group_org_name'),
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

class Supplier(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=200, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='supplier_code')]

class Contract(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    starts_on = models.DateField()
    ends_on = models.DateField()
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    notes = models.TextField(blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='contract_code'),
            models.CheckConstraint(condition=Q(ends_on__gte=models.F('starts_on')),name='contract_dates'),
            models.CheckConstraint(condition=Q(amount__gt=0),name='contract_amount')]

class Stockroom(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='stockroom_code')]

class StockItem(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=80)
    name = models.CharField(max_length=200)
    tracking = models.CharField(max_length=12)
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='stock_item_code'),
            models.CheckConstraint(condition=Q(tracking__in=['BULK','SERIALIZED']),name='stock_tracking')]

class StockBalance(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    stockroom = models.ForeignKey(Stockroom, on_delete=models.PROTECT)
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    quantity = models.PositiveBigIntegerField(default=0)
    row_version = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['stockroom','item'],name='stock_balance_pair')]

class PurchaseRequisition(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)
    max_unit_price = models.DecimalField(max_digits=16, decimal_places=2)
    requester = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='purchase_requests')
    approver = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='purchase_approvals')
    source_request = models.ForeignKey(Ticket, null=True, on_delete=models.PROTECT)
    reason = models.TextField()
    status = models.CharField(max_length=15, default='PENDING')
    row_version = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(quantity__gt=0,max_unit_price__gt=0),name='purchase_request_positive'),
            models.CheckConstraint(condition=~Q(requester=models.F('approver')),name='purchase_no_self_approval'),
            models.CheckConstraint(condition=Q(status__in=['PENDING','APPROVED','REJECTED','ORDERED','CANCELLED']),name='purchase_request_status')]

class PurchaseDecision(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    requisition = models.OneToOneField(PurchaseRequisition, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    decision = models.CharField(max_length=10)
    reason = models.TextField(blank=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(decision__in=['APPROVE','REJECT']),name='purchase_decision_value')]

class PurchaseOrder(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    contract = models.ForeignKey(Contract, null=True, on_delete=models.PROTECT)
    number = models.CharField(max_length=40, unique=True)
    currency = models.CharField(max_length=3)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=16, decimal_places=2)
    total = models.DecimalField(max_digits=16, decimal_places=2)
    received_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, default='DRAFT')
    row_version = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['requisition'],condition=~Q(status='CANCELLED'),name='one_active_order'),
            models.CheckConstraint(condition=Q(quantity__gt=0,unit_price__gt=0,total__gt=0),name='purchase_order_positive'),
            models.CheckConstraint(condition=Q(received_quantity__lte=models.F('quantity')),name='purchase_no_overreceipt'),
            models.CheckConstraint(condition=Q(status__in=['DRAFT','ORDERED','PART_RECEIVED','RECEIVED','CANCELLED']),name='purchase_order_status')]

class GoodsReceipt(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT)
    stockroom = models.ForeignKey(Stockroom, on_delete=models.PROTECT)
    reference = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField()
    received_by = models.ForeignKey(Person, on_delete=models.PROTECT)
    serials = models.JSONField(default=list)
    reason = models.TextField()
    class Meta:
        constraints = [models.UniqueConstraint(fields=['order','reference'],name='receipt_reference_unique'),
            models.CheckConstraint(condition=Q(quantity__gt=0),name='receipt_quantity_positive')]

class StockAsset(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    asset = models.OneToOneField(Asset, on_delete=models.PROTECT, related_name='stock_record')
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    stockroom = models.ForeignKey(Stockroom, null=True, on_delete=models.PROTECT)
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.PROTECT)

class StockMovement(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    item = models.ForeignKey(StockItem, on_delete=models.PROTECT)
    source = models.ForeignKey(Stockroom, null=True, on_delete=models.PROTECT, related_name='outgoing_stock')
    target = models.ForeignKey(Stockroom, null=True, on_delete=models.PROTECT, related_name='incoming_stock')
    quantity = models.PositiveIntegerField()
    kind = models.CharField(max_length=10)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    recipient = models.ForeignKey(Person, null=True, on_delete=models.PROTECT, related_name='stock_issues')
    request = models.ForeignKey(Ticket, null=True, on_delete=models.PROTECT)
    receipt = models.ForeignKey(GoodsReceipt, null=True, on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, null=True, on_delete=models.PROTECT)
    asset_ids = models.JSONField(default=list)
    destination = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(quantity__gt=0),name='stock_move_positive'),
            models.CheckConstraint(condition=(Q(kind__in=['RECEIPT','RETURN'],source__isnull=True,target__isnull=False)|
                Q(kind__in=['ISSUE','RETIRE'],source__isnull=False,target__isnull=True)|
                Q(kind='TRANSFER',source__isnull=False,target__isnull=False)&~Q(source=models.F('target'))),name='stock_move_direction')]
        indexes = [models.Index(fields=['organization','item','-created_at'])]

class AssetContractLink(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT)
    reason = models.TextField()
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['asset','contract'],name='asset_contract_unique')]

class SecurityEvent(Base):
    organization = models.ForeignKey(Organization, null=True, on_delete=models.PROTECT)
    person = models.ForeignKey(Person, null=True, on_delete=models.PROTECT)
    action = models.CharField(max_length=40)
    request_id = models.UUIDField()
    class Meta:
        indexes = [models.Index(fields=['organization','-created_at'])]

class PluginBinding(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    plugin_id = models.CharField(max_length=100)
    plugin_version = models.CharField(max_length=30)
    manifest_digest = models.CharField(max_length=64)
    configuration = models.JSONField(default=dict)
    enabled = models.BooleanField(default=False)
    row_version = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'plugin_id'], name='plugin_binding_unique')]


class PluginRun(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    binding = models.ForeignKey(PluginBinding, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    plugin_id = models.CharField(max_length=100)
    plugin_version = models.CharField(max_length=30)
    manifest_digest = models.CharField(max_length=64)
    binding_version = models.PositiveIntegerField()
    configuration = models.JSONField()
    input_length = models.PositiveIntegerField()
    output_length = models.PositiveIntegerField()
    request_id = models.UUIDField()

    class Meta:
        indexes = [models.Index(fields=['organization', '-created_at'], name='plugin_runs_org_created')]

class EntityDefinition(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    draft_fields = models.JSONField(default=list)
    draft_junction = models.JSONField(default=dict)
    row_version = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'code'], name='entity_definition_code')]


class EntitySchemaVersion(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    entity = models.ForeignKey(EntityDefinition, on_delete=models.PROTECT, related_name='schema_versions')
    version = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    fields = models.JSONField()
    junction = models.JSONField(default=dict)
    schema_digest = models.CharField(max_length=64)
    published_by = models.ForeignKey(Person, on_delete=models.PROTECT)
    reason = models.CharField(max_length=500)
    request_id = models.UUIDField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['entity', 'version'], name='entity_schema_version')]


class EntityRecord(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    entity = models.ForeignKey(EntityDefinition, on_delete=models.PROTECT)
    schema_version = models.ForeignKey(EntitySchemaVersion, on_delete=models.PROTECT)
    values = models.JSONField()
    created_by = models.ForeignKey(Person, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_by = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='updated_entity_records')
    row_version = models.PositiveIntegerField(default=1, editable=False)
    junction_left = models.ForeignKey('self', on_delete=models.PROTECT, null=True, editable=False, related_name='left_junctions')
    junction_right = models.ForeignKey('self', on_delete=models.PROTECT, null=True, editable=False, related_name='right_junctions')
    request_id = models.UUIDField()

    class Meta:
        indexes = [models.Index(fields=['organization', 'entity', '-created_at'], name='entity_records_org_entity')]
        constraints = [
            models.UniqueConstraint(fields=['entity', 'junction_left', 'junction_right'], name='entity_junction_pair'),
            models.CheckConstraint(condition=Q(junction_left__isnull=True, junction_right__isnull=True) | Q(junction_left__isnull=False, junction_right__isnull=False), name='entity_junction_both'),
            models.CheckConstraint(condition=Q(row_version__gte=1), name='entity_record_version_positive'),
        ]


class EntityRecordLink(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    source_entity = models.ForeignKey(EntityDefinition, on_delete=models.PROTECT)
    source = models.ForeignKey(EntityRecord, on_delete=models.PROTECT, related_name='outgoing_links')
    target = models.ForeignKey(EntityRecord, on_delete=models.PROTECT, related_name='incoming_links')
    field_key = models.CharField(max_length=40)
    scalar = models.BooleanField(default=True)
    exclusive = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'field_key', 'target'], name='entity_link_pair'),
            models.UniqueConstraint(fields=['source', 'field_key'], condition=Q(scalar=True), name='entity_link_single_source'),
            models.UniqueConstraint(fields=['source_entity', 'field_key', 'target'], condition=Q(exclusive=True), name='entity_link_single_target'),
        ]


class CommonCodeGroup(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False, editable=False)
    row_version = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'code'], name='common_group_code')]


class CommonCodeItem(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    group = models.ForeignKey(CommonCodeGroup, on_delete=models.PROTECT, related_name='items')
    code = models.CharField(max_length=40)
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['group', 'code'], name='common_item_code')]
        ordering = ['sort_order', 'code']


class NumberSequence(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    namespace = models.CharField(max_length=64)
    period = models.CharField(max_length=10)
    last_value = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'namespace', 'period'], name='number_sequence_scope')]


class NumberIssue(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    binding = models.ForeignKey(PluginBinding, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    run = models.OneToOneField(PluginRun, on_delete=models.PROTECT)
    value = models.CharField(max_length=100)
    request_id = models.UUIDField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'value'], name='number_issue_unique')]


class PluginFailure(Base):
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    binding = models.ForeignKey(PluginBinding, on_delete=models.PROTECT)
    actor = models.ForeignKey(Person, on_delete=models.PROTECT)
    operation = models.CharField(max_length=30)
    binding_version = models.PositiveIntegerField(default=1)
    error_code = models.CharField(max_length=60)
    key_digest = models.CharField(max_length=64)
    request_id = models.UUIDField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization', 'actor', 'binding', 'operation', 'key_digest'], name='plugin_failure_retry')]


class UserProfile(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    person = models.OneToOneField(Person,on_delete=models.PROTECT,related_name='profile')
    full_name = models.CharField(max_length=200)
    given_name = models.CharField(max_length=150,blank=True)
    family_name = models.CharField(max_length=150,blank=True)
    email = models.EmailField(max_length=254,blank=True)
    phone = models.CharField(max_length=40,blank=True)
    employee_id = models.CharField(max_length=80,blank=True)


class PrivacyAccessEvent(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    actor = models.ForeignKey(Person,on_delete=models.PROTECT,related_name='+')
    subject = models.ForeignKey(Person,on_delete=models.PROTECT,related_name='+')
    action = models.CharField(max_length=30)
    request_id = models.UUIDField()


class RoleDefinition(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    code = models.CharField(max_length=40)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500,blank=True)
    permissions = models.JSONField(default=list)
    system = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    row_version = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','code'],name='role_definition_code')]


class CustomRoleGrant(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    person = models.ForeignKey(Person,on_delete=models.PROTECT)
    role = models.ForeignKey(RoleDefinition,on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['person','role'],name='custom_role_person')]


class SecurityPolicy(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    category = models.CharField(max_length=20)
    configuration = models.JSONField(default=dict)
    row_version = models.PositiveIntegerField(default=1)
    applied_by = models.ForeignKey(Person,on_delete=models.PROTECT)
    applied_at = models.DateTimeField(default=timezone.now)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['organization','category'],name='organization_security_policy')]


class CredentialState(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    person = models.OneToOneField(Person,on_delete=models.PROTECT,related_name='credential_state')
    password_changed_at = models.DateTimeField(default=timezone.now)
    password_policy_version = models.PositiveIntegerField(default=0)
    force_change = models.BooleanField(default=False)
    reactivated_at = models.DateTimeField(null=True)
    failed_count = models.PositiveIntegerField(default=0)
    first_failed_at = models.DateTimeField(null=True)
    locked_until = models.DateTimeField(null=True)
    mfa_secret = models.TextField(blank=True)
    mfa_last_counter = models.BigIntegerField(default=-1)
    recovery_hashes = models.JSONField(default=list)


class PasswordHistory(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    person = models.ForeignKey(Person,on_delete=models.PROTECT)
    password_hash = models.CharField(max_length=128)


class LoginThrottle(Base):
    key = models.CharField(max_length=64,unique=True)
    count = models.PositiveIntegerField(default=0)
    since = models.DateTimeField(default=timezone.now)


class LoginSession(Base):
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT)
    person = models.ForeignKey(Person,on_delete=models.PROTECT)
    session_key = models.CharField(max_length=40,unique=True)
    started_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now)
    revoked = models.BooleanField(default=False)
