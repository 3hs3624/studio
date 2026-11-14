import json,uuid
from datetime import datetime,timedelta,timezone as tz
from unittest.mock import patch
from django.test import TestCase,override_settings
from django.db import transaction,IntegrityError
from django.utils import timezone
from .tests import Fixtures
from .models import (Ticket,RoleGrant,TimelinessTarget,TimelinessPolicy,TimelinessReport,BusinessCalendar,Department,RoleDataPolicy)
from . import timeliness as kpi

@override_settings(SECURE_SSL_REDIRECT=False)
class TimelinessTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):cls.build_fixtures();RoleGrant.objects.create(organization=cls.org,person=cls.manager,role='SOLUTION_OPERATOR')
    def post(self,action,data,id=None):
        self.client.force_login(self.manager.user)
        return self.client.post('/api/v1/timeliness/'+action+('/'+str(id) if id else ''),json.dumps(data),content_type='application/json',HTTP_IDEMPOTENCY_KEY=uuid.uuid4().hex)
    def ticket(self,moment=None):
        moment=moment or timezone.now()
        with patch('django.utils.timezone.now',return_value=moment):return Ticket.objects.create(organization=self.org,type='SERVICE_REQUEST',number='KPI-'+uuid.uuid4().hex,title='KPI 요청',description='',requested_by=self.employee,group=self.group,status='IN_PROGRESS')
    def complete(self,ticket,moment):
        with patch('django.utils.timezone.now',return_value=moment):ticket.status='FULFILLED';ticket.save(update_fields=['status'])
    def policy(self,**kwargs):
        latest=TimelinessPolicy.objects.filter(organization=self.org,ticket_type='SERVICE_REQUEST').count()
        return self.post('policy',{'name':'고객 기준','ticket_type':'SERVICE_REQUEST','basis':'RECEIPT','target_minutes':60,'expected_version':latest,'reason':'협의',**kwargs})
    def test_default_receipt_and_completion_boundary(self):
        ticket=self.ticket();target=TimelinessTarget.objects.get(ticket=ticket)
        self.assertEqual(target.snapshot['basis'],'RECEIPT');self.assertEqual(target.due_at,ticket.created_at+timedelta(hours=24))
        self.complete(ticket,target.due_at);target.refresh_from_db();self.assertEqual(target.completed_at,target.due_at)
        with patch('django.utils.timezone.now',return_value=target.due_at+timedelta(seconds=1)):
            totals,rows,_=kpi.calculate(self.manager,timezone.localtime(ticket.created_at).date(),timezone.localtime(target.due_at).date(),'COMPLETION')
        self.assertEqual(totals['percentage'],100);self.assertEqual(rows[0]['result'],'ON_TIME')
    def test_policy_change_preserves_old_targets(self):
        old=self.ticket();before=TimelinessTarget.objects.get(ticket=old).due_at
        response=self.policy();self.assertEqual(response.status_code,201,response.content)
        new=self.ticket();a=TimelinessTarget.objects.get(ticket=old);b=TimelinessTarget.objects.get(ticket=new)
        self.assertEqual(a.snapshot['version'],0);self.assertEqual(a.due_at,before);self.assertEqual(b.snapshot['version'],1);self.assertEqual(b.due_at,new.created_at+timedelta(minutes=60))
        with self.assertRaises(IntegrityError),transaction.atomic():TimelinessTarget.objects.filter(ticket=new).update(snapshot={})
        with self.assertRaises(IntegrityError),transaction.atomic():TimelinessPolicy.objects.all().delete()
    def test_due_cohort_includes_overdue_open(self):
        now=timezone.now();ticket=self.ticket(now-timedelta(days=3));target=TimelinessTarget.objects.get(ticket=ticket)
        totals,rows,_=kpi.calculate(self.manager,(now-timedelta(days=4)).date(),now.date(),'DUE')
        self.assertEqual(totals['overdue_open'],1);self.assertEqual(totals['eligible'],1);self.assertEqual(totals['percentage'],0)
        completed_totals,_,_=kpi.calculate(self.manager,(now-timedelta(days=4)).date(),now.date(),'COMPLETION');self.assertEqual(completed_totals['eligible'],0)
    def test_agreement_basis_unscored_then_audited_deadline(self):
        self.assertEqual(self.policy(basis='AGREED_DUE').status_code,201)
        ticket=self.ticket();target=TimelinessTarget.objects.get(ticket=ticket);self.assertIsNone(target.due_at)
        due=timezone.now()+timedelta(hours=8)
        response=self.post('adjust',dict(expected_version=target.row_version,agreed_due_at=due.isoformat(),reason='고객과 완료 기한 협의'),ticket.id)
        self.assertEqual(response.status_code,200,response.content);target.refresh_from_db();self.assertEqual(target.due_at,due);self.assertTrue(target.timelinessevent_set.filter(action='AGREEMENT_CHANGED').exists())
        self.complete(ticket,timezone.now());target.refresh_from_db()
        response=self.post('adjust',dict(expected_version=target.row_version,agreed_due_at=(due+timedelta(days=1)).isoformat(),reason='완료 후 변경'),ticket.id);self.assertEqual(response.status_code,409)
    def test_business_calendar_and_holiday_snapshot(self):
        calendar=BusinessCalendar.objects.create(organization=self.org,name='업무시간',timezone='Asia/Seoul',weekdays=[0,1,2,3,4],starts_at='09:00',ends_at='18:00',holidays=[])
        self.assertEqual(self.policy(calendar_id=str(calendar.id)).status_code,201)
        # Friday 17:30 KST + 60 working minutes = Monday 09:30 KST.
        day=timezone.now().date()+timedelta(days=7)
        day+=timedelta(days=(4-day.weekday())%7)
        moment=datetime.combine(day,datetime.min.time(),tzinfo=tz.utc)+timedelta(hours=8,minutes=30);ticket=self.ticket(moment);target=TimelinessTarget.objects.get(ticket=ticket)
        self.assertEqual(target.due_at,datetime.combine(day+timedelta(days=3),datetime.min.time(),tzinfo=tz.utc)+timedelta(minutes=30))
    def test_reopen_tracks_final_completion_and_excludes_cancellation(self):
        ticket=self.ticket();self.complete(ticket,timezone.now());target=TimelinessTarget.objects.get(ticket=ticket);self.assertIsNotNone(target.completed_at)
        ticket.status='IN_PROGRESS';ticket.save(update_fields=['status']);target.refresh_from_db();self.assertIsNone(target.completed_at)
        ticket.status='CANCELLED';ticket.save(update_fields=['status']);totals,rows,_=kpi.calculate(self.manager,ticket.created_at.date(),(ticket.created_at+timedelta(days=2)).date(),'DUE');self.assertEqual(totals['excluded'],1);self.assertEqual(totals['eligible'],0)
    def test_fixed_report_csv_and_scope_change(self):
        ticket=self.ticket();self.complete(ticket,timezone.now());today=timezone.localdate().isoformat()
        response=self.post('report',dict(starts_on=today,ends_on=today,cohort='COMPLETION'));self.assertEqual(response.status_code,201,response.content)
        report=TimelinessReport.objects.get(id=response.json()['id']);self.client.force_login(self.manager.user);download=self.client.get('/console/slm/reports/'+str(report.id)+'/csv');self.assertEqual(download.status_code,200);self.assertTrue(download.content.startswith(b'\xef\xbb\xbf'))
        with self.assertRaises(IntegrityError),transaction.atomic():TimelinessReport.objects.filter(id=report.id).update(totals={})
        RoleDataPolicy.objects.create(organization=self.org,role_key='SERVICE_MANAGER',menu_key='requests',read_scope='NONE',write_scope='NONE');self.client.force_login(self.manager.user)
        self.assertEqual(self.client.get('/console/slm/reports/'+str(report.id)+'/csv').status_code,403)
    def test_unauthorized_and_cross_tenant(self):
        self.client.force_login(self.employee.user);self.assertEqual(self.client.get('/console/slm').status_code,403)
        ticket=self.ticket();self.client.force_login(self.foreign.user)
        response=self.client.post('/api/v1/timeliness/adjust/'+str(ticket.id),json.dumps(dict(expected_version=1,reason='타 조직')),content_type='application/json',HTTP_IDEMPOTENCY_KEY=uuid.uuid4().hex);self.assertEqual(response.status_code,404)
