"""Business calendar arithmetic on UTC instants; local windows are resolved explicitly."""
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MICROSECOND = timedelta(microseconds=1)
HORIZON_DAYS = 3660

class CalendarError(ValueError):
    pass

def validate_calendar(data):
    try:
        ZoneInfo(data['timezone'])
        weekdays=data['weekdays']
        if not isinstance(weekdays,list) or not weekdays or len(weekdays)>7 or any(type(d) is not int or d not in range(7) for d in weekdays) or len(set(weekdays))!=len(weekdays):
            raise ValueError()
        for key in ('starts_at','ends_at'):
            value=data[key]
            if not isinstance(value,str) or len(value)!=5 or time.fromisoformat(value).strftime('%H:%M')!=value:
                raise ValueError()
        if data['starts_at']>=data['ends_at']:
            raise ValueError()
        holidays=data['holidays']
        if not isinstance(holidays,list) or len(holidays)>3660 or any(not isinstance(d,str) or date.fromisoformat(d).isoformat()!=d for d in holidays) or len(set(holidays))!=len(holidays):
            raise ValueError()
    except (KeyError,ValueError,TypeError,ZoneInfoNotFoundError):
        raise CalendarError('시간대·요일·업무시간·휴일 형식을 확인하십시오.') from None

def local_boundary(day, value, zone):
    # Ambiguous times use the first occurrence. Nonexistent times advance to the first valid minute.
    naive=datetime.combine(day,time.fromisoformat(value))
    for _ in range(181):
        local=naive.replace(tzinfo=zone,fold=0)
        utc=local.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None)==naive:
            return utc
        naive+=timedelta(minutes=1)
    raise CalendarError('해당 날짜의 시간대 전환을 해석할 수 없습니다.')

def window(day, calendar, zone, holidays):
    if day.weekday() not in calendar['weekdays'] or day.isoformat() in holidays:
        return None
    start=local_boundary(day,calendar['starts_at'],zone)
    end=local_boundary(day,calendar['ends_at'],zone)
    return (start,end) if end>start else None

def utc_instant(value):
    if not isinstance(value,datetime) or value.tzinfo is None:
        raise CalendarError('시간대가 포함된 시각이 필요합니다.')
    return value.astimezone(timezone.utc)

def business_microseconds(start,end,calendar):
    start,end=utc_instant(start),utc_instant(end)
    if end<start:
        raise CalendarError('시계가 이전 처리 시점보다 과거입니다.')
    zone=ZoneInfo(calendar['timezone'])
    day=start.astimezone(zone).date()
    last=end.astimezone(zone).date()
    if (last-day).days>HORIZON_DAYS:
        raise CalendarError('계산 범위가 10년을 넘었습니다.')
    holidays=set(calendar['holidays'])
    result=0
    while day<=last:
        span=window(day,calendar,zone,holidays)
        if span:
            a,b=max(start,span[0]),min(end,span[1])
            if b>a:
                result+=(b-a)//MICROSECOND
        day+=timedelta(days=1)
    return result

def add_business_microseconds(start,amount,calendar):
    start=utc_instant(start)
    if type(amount) is not int or amount<0:
        raise CalendarError('업무시간은 음수가 아닌 정수여야 합니다.')
    if amount==0:
        return start
    zone=ZoneInfo(calendar['timezone'])
    day=start.astimezone(zone).date()
    holidays=set(calendar['holidays'])
    for _ in range(HORIZON_DAYS+1):
        span=window(day,calendar,zone,holidays)
        if span:
            a,b=max(start,span[0]),span[1]
            available=max(0,(b-a)//MICROSECOND)
            if available>=amount:
                return a+timedelta(microseconds=amount)
            amount-=available
        day+=timedelta(days=1)
    raise CalendarError('10년 안에 목표 시간을 배정할 수 없습니다.')
