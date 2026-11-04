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

@register.filter
def asset_label(value):
    return {'UNVERIFIED':'미확인','STOCK':'보관 중','IN_USE':'사용 중','RETIRED':'폐기 처리',
        'REGISTER':'등록','UPDATE':'정보 수정','VERIFY':'입고 확인','ISSUE':'지급','RETURN':'반납',
        'MOVE':'위치 이동','RETIRE':'폐기 처리'}.get(value,value)

@register.filter
def role_label(value):
    return {'SERVICE_MANAGER':'서비스 관리자','AGENT':'처리 담당자','ORG_ADMIN':'조직 관리자',
            'RESOURCE_READER':'자산·구성 조회','ASSET_MANAGER':'자산 관리자'}.get(value,value)
