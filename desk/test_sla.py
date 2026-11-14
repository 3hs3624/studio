import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from unittest import skipUnless
from unittest.mock import patch
from django.db import connection, transaction, IntegrityError, close_old_connections
from django.test import TestCase, TransactionTestCase, override_settings
from .tests import Fixtures
from .models import (BusinessCalendar, SLAPolicy, SLAInstance, SLAClockEvent, SLAAlert, Notification,
                     OutboxEvent, Ticket, Person, RoleGrant, StatusHistory)
from .business_time import business_microseconds, add_business_microseconds, validate_calendar, CalendarError
from . import services as s
from .sla import evaluate_due, summary, visible_notifications, MINUTE_US, calendar_data, advance

def instant(value):
    return datetime.fromisoformat(value)

MONDAY=instant('2026-11-02T09:00:00+09:00')
CALENDAR={'timezone':'Asia/Seoul','weekdays':[0,1,2,3,4],'starts_at':'09:00','ends_at':'18:00','holidays':[]}

class CalendarTests(TestCase):
    def test_weekend_and_holiday(self):
        calendar={**CALENDAR,'holidays':['2026-11-09']}
        start=instant('2026-11-06T17:00:00+09:00')
        end=add_business_microseconds(start,120*MINUTE_US,calendar)
        self.assertEqual(end,instant('2026-11-10T10:00:00+09:00'))
        self.assertEqual(business_microseconds(start,end,calendar),120*MINUTE_US)

    def test_exact_close_and_after_hours(self):
        close=instant('2026-11-02T18:00:00+09:00')
        self.assertEqual(add_business_microseconds(MONDAY,540*MINUTE_US,CALENDAR),close)
        self.assertEqual(add_business_microseconds(close,MINUTE_US,CALENDAR),instant('2026-11-03T09:01:00+09:00'))
        self.assertEqual(business_microseconds(close,instant('2026-11-03T09:00:00+09:00'),CALENDAR),0)

    def test_dst_spring_and_fall_elapsed_real_time(self):
        calendar={**CALENDAR,'timezone':'America/New_York','weekdays':[6],'starts_at':'01:00','ends_at':'04:00'}
        for start,end,minutes in [('2026-03-08T01:00:00-05:00','2026-03-08T04:00:00-04:00',120),
                                  ('2026-11-01T01:00:00-04:00','2026-11-01T04:00:00-05:00',240)]:
            self.assertEqual(business_microseconds(instant(start),instant(end),calendar),minutes*MINUTE_US)
            self.assertEqual(add_business_microseconds(instant(start),minutes*MINUTE_US,calendar),instant(end))

    def test_nonexistent_dst_boundary_advances_to_valid_minute(self):
        calendar={**CALENDAR,'timezone':'America/New_York','weekdays':[6],'starts_at':'02:30','ends_at':'03:30'}
        self.assertEqual(business_microseconds(instant('2026-03-08T00:00:00-05:00'),instant('2026-03-08T05:00:00-04:00'),calendar),30*MINUTE_US)

    def test_invalid_calendar_and_unbounded_horizon(self):
        for delta in [{'weekdays':[]},{'weekdays':[True]},{'weekdays':[0,0]},{'timezone':'Invalid/Zone'},
                      {'starts_at':'18:00'},{'starts_at':'9:00'},{'holidays':['2026-02-30']},{'holidays':['2026-01-01']*2}]:
            with self.assertRaises(CalendarError):
                validate_calendar({**CALENDAR,**delta})
        with self.assertRaises(CalendarError):
            add_business_microseconds(MONDAY,10080*MINUTE_US,{**CALENDAR,'weekdays':[0],'ends_at':'09:01'})

    def test_microseconds_are_not_lost(self):
        end=MONDAY+timedelta(microseconds=713)
        self.assertEqual(business_microseconds(MONDAY,end,CALENDAR),713)
        self.assertEqual(add_business_microseconds(MONDAY,713,CALENDAR),end)

@override_settings(SECURE_SSL_REDIRECT=False)
class SLATests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures()
        cls.calendar=BusinessCalendar.objects.create(organization=cls.org,name='Office hours',**CALENDAR)
        cls.policy=SLAPolicy.objects.create(organization=cls.org,calendar=cls.calendar,name='P4 initial',priority=4,
                    version=1,response_minutes=60,resolution_minutes=120,warning_percent=80,pause_on_pending=True)

    def command(self,p,op,data,at=MONDAY,target=None,key=None):
        with patch('django.utils.timezone.now',return_value=at):
            return s.execute(p,op,data,key or uuid.uuid4().hex,uuid.uuid4(),target)[0]

    def create(self,at=MONDAY):
        result=self.command(self.employee,'create',{'title':'SLA incident','description':'Network failure','impact':3,'urgency':2},at)
        return Ticket.objects.get(id=result['id'])

    def assign(self,t,at=MONDAY):
        self.command(self.manager,'assign',{'group_id':str(self.group.id),'assignee_id':str(self.agent.id),
                     'expected_version':t.row_version},at,t.id)
        t.refresh_from_db()

    def transition(self,t,action,at,actor=None):
        data={'action':action,'expected_version':t.row_version}
        if action in ('WAIT','REOPEN'):
            data['reason']='reason'
        if action=='RESOLVE':
            data['resolution']='fixed'
        result=self.command(actor or self.agent,'transition',data,at,t.id)
        t.refresh_from_db()
        return result

    def test_policy_applied_with_deadlines_and_frozen_snapshot(self):
        t=self.create()
        clock=SLAInstance.objects.get(ticket=t)
        self.assertEqual(clock.response_due_at,MONDAY+timedelta(hours=1))
        self.assertEqual(clock.resolution_due_at,MONDAY+timedelta(hours=2))
        data={'name':'new','calendar_id':str(self.calendar.id),'priority':4,'response_minutes':5,
              'resolution_minutes':10,'warning_percent':50,'pause_on_pending':False}
        new=self.command(self.manager,'sla_policy',data,MONDAY+timedelta(minutes=5))
        self.assertEqual(new['version'],2)
        another=self.create(MONDAY+timedelta(minutes=6))
        self.assertEqual(another.sla_instance.snapshot['response_minutes'],5)
        clock.refresh_from_db()
        self.assertEqual(clock.snapshot['response_minutes'],60)

    def test_no_retroactive_sla(self):
        data={'title':'No policy','description':'x','impact':1,'urgency':1}
        r=self.command(self.employee,'create',data)
        self.assertIsNone(r['sla'])
        self.assertFalse(SLAInstance.objects.filter(ticket_id=r['id']).exists())

    def test_start_stops_response_assignment_does_not(self):
        t=self.create()
        self.assign(t,MONDAY+timedelta(minutes=5))
        self.assertIsNone(t.sla_instance.response_completed_at)
        self.transition(t,'START',MONDAY+timedelta(minutes=10))
        clock=SLAInstance.objects.get(ticket=t)
        self.assertEqual(clock.response_elapsed_us,10*MINUTE_US)
        self.assertEqual(clock.response_completed_at,MONDAY+timedelta(minutes=10))
        self.assertEqual(summary(Ticket.objects.get(id=t.id),MONDAY+timedelta(minutes=20))['response']['state'],'MET')

    def test_pause_resume_preserves_budget_and_moves_deadline(self):
        t=self.create(); self.assign(t)
        self.transition(t,'START',MONDAY+timedelta(minutes=10))
        self.transition(t,'WAIT',MONDAY+timedelta(minutes=30))
        state=summary(Ticket.objects.get(id=t.id),MONDAY+timedelta(hours=3))
        self.assertEqual(state['resolution']['state'],'PAUSED')
        self.assertEqual(state['resolution']['elapsed_seconds'],1800)
        self.assertIsNone(state['resolution']['due_at'])
        self.transition(t,'RESUME',MONDAY+timedelta(hours=3))
        clock=SLAInstance.objects.get(ticket=t)
        self.assertEqual(clock.resolution_due_at,MONDAY+timedelta(hours=4,minutes=30))
        self.transition(t,'RESOLVE',MONDAY+timedelta(hours=3,minutes=20))
        clock.refresh_from_db()
        self.assertEqual(clock.resolution_elapsed_us,50*MINUTE_US)

    def test_pending_does_not_pause_when_policy_disables_it(self):
        self.command(self.manager,'sla_policy',{'name':'No pause','calendar_id':str(self.calendar.id),'priority':4,
                    'response_minutes':60,'resolution_minutes':120,'warning_percent':80,'pause_on_pending':False})
        t=self.create(); self.assign(t)
        self.transition(t,'START',MONDAY+timedelta(minutes=10))
        self.transition(t,'WAIT',MONDAY+timedelta(minutes=20))
        result=summary(Ticket.objects.get(id=t.id),MONDAY+timedelta(minutes=40))
        self.assertEqual(result['resolution']['elapsed_seconds'],2400)
        self.assertEqual(result['resolution']['state'],'RUNNING')

    def test_reopen_excludes_resolved_gap_and_does_not_reset_response(self):
        t=self.create(); self.assign(t)
        self.transition(t,'START',MONDAY+timedelta(minutes=10))
        self.transition(t,'RESOLVE',MONDAY+timedelta(minutes=30))
        self.transition(t,'REOPEN',MONDAY+timedelta(hours=3),self.employee)
        clock=SLAInstance.objects.get(ticket=t)
        self.assertEqual(clock.response_elapsed_us,10*MINUTE_US)
        self.assertEqual(clock.resolution_elapsed_us,30*MINUTE_US)
        self.assertEqual(clock.resolution_due_at,MONDAY+timedelta(hours=4,minutes=30))

    def test_warning_breach_deduplication_and_recipients(self):
        t=self.create(); self.assign(t)
        self.assertEqual(evaluate_due(MONDAY+timedelta(minutes=50)),1)
        self.assertEqual(SLAAlert.objects.filter(goal='RESPONSE',level='WARNING').count(),1)
        self.assertEqual(Notification.objects.count(),2)
        self.assertEqual(evaluate_due(MONDAY+timedelta(minutes=50)),0)
        evaluate_due(MONDAY+timedelta(minutes=61))
        evaluate_due(MONDAY+timedelta(minutes=62))
        self.assertEqual(SLAAlert.objects.filter(goal='RESPONSE',level='BREACH').count(),1)
        self.assertEqual(Notification.objects.count(),4)
        self.assertEqual(visible_notifications(self.employee).count(),0)
        self.assertEqual(visible_notifications(self.foreign).count(),0)
        self.assertEqual(visible_notifications(self.agent).count(),2)

    def test_wait_cannot_hide_already_missed_deadline(self):
        t=self.create(); self.assign(t)
        self.transition(t,'START',MONDAY+timedelta(minutes=10))
        self.transition(t,'WAIT',MONDAY+timedelta(minutes=130))
        self.assertTrue(SLAAlert.objects.filter(goal='RESOLUTION',level='BREACH').exists())
        self.transition(t,'RESUME',MONDAY+timedelta(minutes=140))
        self.assertEqual(summary(Ticket.objects.get(id=t.id),MONDAY+timedelta(minutes=140))['resolution']['state'],'OVERDUE')

    def test_completion_exactly_on_deadline_and_late_outside_business_hours(self):
        self.command(self.manager,'sla_policy',{'name':'Day','calendar_id':str(self.calendar.id),'priority':4,
                    'response_minutes':60,'resolution_minutes':540,'warning_percent':80,'pause_on_pending':True})
        t=self.create(); self.assign(t)
        self.transition(t,'START',MONDAY+timedelta(minutes=60))
        self.transition(t,'RESOLVE',MONDAY+timedelta(hours=9))
        self.assertEqual(summary(Ticket.objects.get(id=t.id),MONDAY+timedelta(hours=10))['resolution']['state'],'MET')
        other=self.create(); self.assign(other)
        self.transition(other,'START',MONDAY+timedelta(minutes=10))
        self.transition(other,'RESOLVE',MONDAY+timedelta(hours=10))
        self.assertEqual(summary(Ticket.objects.get(id=other.id),MONDAY+timedelta(hours=10))['resolution']['state'],'OVERDUE')

    def test_publish_permissions_validation_and_idempotency(self):
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.get('/api/v1/sla/policies').status_code,403)
        self.client.force_login(self.admin.user)
        self.assertEqual(self.client.get('/work/sla').status_code,403)
        self.client.force_login(self.manager.user)
        data={'name':'Holiday calendar',**CALENDAR}
        for _ in range(2):
            r=self.client.post('/api/v1/sla/calendars',data=data,content_type='application/json',HTTP_IDEMPOTENCY_KEY='calendar')
            self.assertEqual(r.status_code,201,r.content)
        self.assertEqual(BusinessCalendar.objects.count(),2)
        self.assertEqual(self.client.post('/api/v1/sla/calendars',data={**data,'weekdays':[]},content_type='application/json',HTTP_IDEMPOTENCY_KEY='invalid').status_code,422)
        self.assertEqual(self.client.get('/api/v1/sla/policies').status_code,200)

    def test_notification_visibility_read_and_revocation(self):
        t=self.create(); self.assign(t)
        evaluate_due(MONDAY+timedelta(minutes=50))
        n=Notification.objects.get(recipient=self.agent)
        self.client.force_login(self.agent.user)
        self.assertEqual(len(self.client.get('/api/v1/notifications').json()['items']),1)
        for _ in range(2):
            r=self.client.post(f'/api/v1/notifications/{n.id}/read',data={},content_type='application/json',HTTP_IDEMPOTENCY_KEY='read')
            self.assertEqual(r.status_code,200,r.content)
        self.client.force_login(self.employee.user)
        self.assertEqual(self.client.post(f'/api/v1/notifications/{n.id}/read',data={},content_type='application/json',HTTP_IDEMPOTENCY_KEY='read').status_code,404)
        RoleGrant.objects.filter(person=self.agent,role='AGENT').delete()
        self.client.force_login(self.agent.user)
        self.assertEqual(self.client.get('/api/v1/notifications').json()['items'],[])
        self.assertEqual(self.client.post(f'/api/v1/notifications/{n.id}/read',data={},content_type='application/json',HTTP_IDEMPOTENCY_KEY='read').status_code,404)

    def test_sla_update_is_atomic_with_ticket(self):
        t=self.create(); self.assign(t)
        count=StatusHistory.objects.count()
        with patch('desk.sla.clock_event',side_effect=IntegrityError('forced')):
            with self.assertRaises(IntegrityError):
                self.transition(t,'START',MONDAY+timedelta(minutes=10))
        t.refresh_from_db()
        self.assertEqual(t.status,'ASSIGNED')
        self.assertIsNone(SLAInstance.objects.get(ticket=t).response_completed_at)
        self.assertEqual(StatusHistory.objects.count(),count)

    def test_db_guards_calendar_policy_events_and_cross_org(self):
        t=self.create()
        for model in (BusinessCalendar,SLAPolicy,SLAClockEvent):
            obj=model.objects.first()
            with self.assertRaises(IntegrityError),transaction.atomic():
                model.objects.filter(pk=obj.pk).delete()
        with self.assertRaises(IntegrityError),transaction.atomic():
            BusinessCalendar.objects.filter(id=self.calendar.id).update(name='tampered')
        with self.assertRaises(IntegrityError),transaction.atomic():
            SLAPolicy.objects.create(organization=self.other_org,calendar=self.calendar,name='cross',priority=1,version=1,response_minutes=1,resolution_minutes=1)

    def test_sla_clock_rejects_backward_time_without_data_loss(self):
        t=self.create()
        instance=SLAInstance.objects.get(ticket=t)
        with self.assertRaises(CalendarError):
            advance(instance,MONDAY-timedelta(seconds=1))
        self.assertEqual(SLAInstance.objects.get(ticket=t).response_elapsed_us,0)

    def test_html_views_and_policy_snapshot_on_ticket(self):
        RoleGrant.objects.create(organization=self.org,person=self.manager,role='SOLUTION_OPERATOR')
        t=self.create()
        self.client.force_login(self.manager.user)
        for path in ('/work/sla','/notifications',f'/work/incidents/{t.id}','/work/incidents'):
            r=self.client.get(path)
            self.assertEqual(r.status_code,200,r.content)
        self.client.force_login(self.employee.user)
        self.assertContains(self.client.get(f'/portal/incidents/{t.id}'),'서비스 처리 목표')

@skipUnless(connection.vendor=='postgresql','Concurrent SLA jobs require PostgreSQL row locks.')
class SLARaceTests(Fixtures,TransactionTestCase):
    def setUp(self):
        self.build_fixtures()
        self.calendar=BusinessCalendar.objects.create(organization=self.org,name='Office',**CALENDAR)
        SLAPolicy.objects.create(organization=self.org,calendar=self.calendar,name='P4',priority=4,version=1,response_minutes=60,resolution_minutes=120)

    def test_concurrent_evaluators_emit_one_alert_per_goal_level(self):
        with patch('django.utils.timezone.now',return_value=MONDAY):
            s.execute(self.employee,'create',{'title':'x','description':'x','impact':3,'urgency':2},'x',uuid.uuid4())
        def evaluate(_):
            close_old_connections()
            try:
                return evaluate_due(MONDAY+timedelta(minutes=50))
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(evaluate,range(2)))
        self.assertEqual(sum(results),1)
        self.assertEqual(SLAAlert.objects.count(),1)
        self.assertEqual(Notification.objects.count(),1)

    def test_concurrent_policy_publication_has_distinct_monotonic_versions(self):
        def publish(i):
            close_old_connections()
            try:
                manager=Person.objects.get(id=self.manager.id)
                result,_=s.execute(manager,'sla_policy',{'name':f'new {i}','calendar_id':str(self.calendar.id),
                    'priority':4,'response_minutes':10,'resolution_minutes':30,'warning_percent':80,'pause_on_pending':True},
                    str(i),uuid.uuid4())
                return result['version']
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            versions=list(pool.map(publish,range(2)))
        self.assertEqual(sorted(versions),[2,3])
