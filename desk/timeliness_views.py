from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .views import context
from . import timeliness as kpi,services as s
from .models import TimelinessPolicy,TimelinessReport,BusinessCalendar

@login_required
def manage(request,report_id=None,csv=False):
    try:
        c=context(request);actor=c['actor'];kpi.require_manager(actor)
        if report_id:return kpi.export(actor,report_id)
        today=timezone.localdate();starts,ends=kpi.period(request.GET.get('from',today.replace(day=1).isoformat()),request.GET.get('to',today.isoformat()));cohort=request.GET.get('cohort','COMPLETION')
        totals,rows,asof=kpi.calculate(actor,starts,ends,cohort)
        policies=[]
        for kind,label in [('SERVICE_REQUEST','서비스요청'),('INCIDENT','장애')]:
            current=TimelinessPolicy.objects.filter(organization=actor.organization,ticket_type=kind).order_by('-version').first();policies.append(dict(kind=kind,label=label,current=current))
        c.update(kpi_totals=totals,kpi_rows=rows[:100],kpi_asof=asof,kpi_from=starts.isoformat(),kpi_to=ends.isoformat(),kpi_cohort=cohort,kpi_policies=policies,kpi_bases=kpi.BASES.items(),kpi_calendars=BusinessCalendar.objects.filter(organization=actor.organization).order_by('name'),kpi_reports=TimelinessReport.objects.filter(organization=actor.organization).order_by('-created_at')[:30])
        return render(request,'desk/timeliness.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)

@login_required
def agreement(request,id):
    try:
        c=context(request);kpi.require_manager(c['actor']);ticket=kpi.visible_tickets(c['actor']).filter(id=s.identifier(id)).first()
        if not ticket:s.fail('NOT_FOUND','요청을 찾을 수 없습니다.',404)
        target=kpi.ensure(ticket);c.update(kpi_ticket=ticket,kpi_target=target,kpi_basis=kpi.BASES[target.snapshot['basis']])
        return render(request,'desk/timeliness-agreement.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)
