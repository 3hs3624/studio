from django import template
register=template.Library()

@register.filter
def state_label(value):
    return {'NEW':'접수','ASSIGNED':'배정','IN_PROGRESS':'처리 중','PENDING':'대기',
            'RESOLVED':'해결','CLOSED':'종료'}.get(value,value)
