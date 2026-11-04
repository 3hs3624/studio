from django import template
register=template.Library()

@register.filter
def state_label(value):
    return {'NEW':'접수','ASSIGNED':'배정','IN_PROGRESS':'처리 중','PENDING':'대기',
            'RESOLVED':'해결','CLOSED':'종료','PENDING_APPROVAL':'승인 대기','APPROVED':'승인 완료',
            'FULFILLED':'처리 완료','REJECTED':'반려','CANCELLED':'취소'}.get(value,value)

@register.filter
def sla_label(value):
    return {'RUNNING':'진행 중','AT_RISK':'기한 임박','OVERDUE':'기한 초과',
            'PAUSED':'시간 정지','MET':'목표 달성'}.get(value,value)

@register.filter
def local_time(value):
    from django.utils.dateparse import parse_datetime
    from django.utils import timezone
    moment=parse_datetime(value) if isinstance(value,str) else value
    return timezone.localtime(moment).strftime('%m.%d %H:%M %Z') if moment else '—'
