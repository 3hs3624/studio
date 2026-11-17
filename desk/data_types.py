"""Shared, finite data-type catalogue. No operator supplied Python or SQL."""
import json,math,re,uuid
from datetime import date,datetime,time
from decimal import Decimal,InvalidOperation
from django.core.exceptions import ValidationError
from django.core.validators import validate_email,URLValidator
from . import services as s

TYPE_META = {
 'text':('문자','Aa','문자열'), 'textarea':('긴 문자','¶','문자열'),
 'integer':('정수','123','숫자'), 'number':('실수','1.2','숫자'), 'decimal':('고정소수','0.00','숫자'),
 'boolean':('논리값','✓','논리'), 'date':('날짜','▦','날짜·시간'), 'datetime':('날짜·시간','▦◷','날짜·시간'),
 'time':('시간','◷','날짜·시간'), 'month':('연월','MM','날짜·시간'), 'year':('연도','YY','날짜·시간'),
 'json':('JSON','{ }','구조화'), 'entityset':('JSON 목록','[ ]','구조화'),
 'choice':('선택','☷','연결'), 'code':('공통코드','#','연결'), 'reference':('엔티티 참조','↗','연결'), 'person':('사용자','◎','연결'),
 'uuid':('UUID','ID','문자열'), 'email':('이메일','@','문자열'), 'phone':('전화번호','☎','문자열'), 'url':('URL','↗','문자열'),
}
STRING_TYPES={'text','textarea','uuid','email','phone','url','choice','code','month','year','date','datetime','time'}
NUMERIC_TYPES={'number','integer','decimal'}
SCREEN_TYPES=set(TYPE_META)-{'choice','code','reference'}

def catalogue():return [dict(key=k,label=v[0],icon=v[1],category=v[2]) for k,v in TYPE_META.items()]

def metadata(field):
    result={}
    if 'description' in field:result['description']=s.text(field,'description',500,required=False)
    if 'max_length' in field:
        if field['type'] not in {'text','textarea','email','phone','url'} or type(field['max_length']) is not int or not 1<=field['max_length']<=65535:s.fail('INVALID_FIELD_OPTIONS','문자열 최대 길이는 1~65535입니다.')
        result['max_length']=field['max_length']
    if 'precision' in field or 'scale' in field:
        p=field.get('precision',18);scale=field.get('scale',2)
        if field['type']!='decimal' or type(p) is not int or type(scale) is not int or not 1<=p<=38 or not 0<=scale<=min(p,18):s.fail('INVALID_FIELD_OPTIONS','고정소수의 정밀도(1~38)와 소수 자리(0~18)를 확인하십시오.')
        result.update(precision=p,scale=scale)
    for bound in ('minimum','maximum'):
        if bound in field:
            v=field[bound]
            if field['type'] not in ('integer','number') or type(v) not in (int,float) or abs(v)>9007199254740991 or not math.isfinite(v) or (field['type']=='integer' and type(v) is not int):s.fail('INVALID_FIELD_OPTIONS','숫자 범위의 자료형을 확인하십시오.')
            result[bound]=v
    if result.get('minimum',-math.inf)>result.get('maximum',math.inf):s.fail('INVALID_FIELD_OPTIONS','최소값은 최대값 이하여야 합니다.')
    if 'default' in field and 'default_function' in field:s.fail('INVALID_FIELD_OPTIONS','기본값과 자동 기본값은 하나만 설정하십시오.')
    if 'default' in field:
        if field['type'] in ('person','reference','choice','code'):s.fail('INVALID_FIELD_OPTIONS','참조·선택 항목의 기본값은 연결 규칙으로 설정하십시오.')
        result['default']=scalar(field,field['default'])
    if 'default_function' in field:
        allowed={'CURRENT_TIMESTAMP':'datetime','CURRENT_DATE':'date','UUID':'uuid'}
        fn=field['default_function']
        if not isinstance(fn,str) or allowed.get(fn)!=field['type']:s.fail('INVALID_FIELD_OPTIONS','해당 유형에서 허용된 자동 기본값을 선택하십시오.')
        result['default_function']=fn
    return result

def default_value(field):
    from django.utils import timezone
    fn=field.get('default_function')
    if fn=='CURRENT_TIMESTAMP':return timezone.now().isoformat()
    if fn=='CURRENT_DATE':return timezone.localdate().isoformat()
    if fn=='UUID':return str(uuid.uuid4())
    return json.loads(json.dumps(field['default'])) if 'default' in field else None

def scalar(field,value):
    kind=field['type'];label=field.get('label','값')
    def fail():s.fail('INVALID_ENTITY_VALUE',label+': 데이터타입·길이·범위를 확인하십시오.')
    if kind in ('integer','number') and type(value) in (int,float) and not field.get('minimum',-math.inf)<=value<=field.get('maximum',math.inf):fail()
    if kind in ('json','entityset'):
        if not isinstance(value,(dict,list)) or kind=='entityset' and not isinstance(value,list):fail()
        try:
            encoded=json.dumps(value,allow_nan=False,ensure_ascii=False)
            if len(encoded)>65535:fail()
            def depth(v,n=0):
                if n>12:fail()
                if isinstance(v,dict):
                    if any(not isinstance(k,str) for k in v):fail()
                    for x in v.values():depth(x,n+1)
                elif isinstance(v,list):
                    for x in v:depth(x,n+1)
            depth(value)
        except (ValueError,TypeError,RecursionError):fail()
        return value
    if kind=='integer':
        if type(value) is not int or abs(value)>9007199254740991:fail()
        return value
    if kind=='number':
        if type(value) not in (int,float) or abs(value)>10**15 or not math.isfinite(value):fail()
        return value
    if kind=='decimal':
        if type(value) not in (str,int) or isinstance(value,bool):fail()
        try:
            
            if len(str(value))>100:fail()
            number=Decimal(value);p=field.get('precision',18);scale=field.get('scale',2)
            if not number.is_finite() or max(0,-number.as_tuple().exponent)>scale or max(0,number.adjusted()+1)>p-scale:fail()
            return format(number,'f')
        except (InvalidOperation,ValueError):fail()
    if kind=='boolean':
        if type(value) is not bool:fail()
        return value
    if not isinstance(value,str) or len(value)>field.get('max_length',16384 if kind=='textarea' else 4000):fail()
    try:
        if kind=='date':
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):fail()
            date.fromisoformat(value)
        elif kind=='datetime':
            item=datetime.fromisoformat(value.replace('Z','+00:00'))
            if item.tzinfo is None:fail()
        elif kind=='time':
            if not re.fullmatch(r'\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?',value):fail()
            time.fromisoformat(value)
        elif kind=='month':
            if not re.fullmatch(r'\d{4}-\d{2}',value):fail()
            date.fromisoformat(value+'-01')
        elif kind=='year':
            if not re.fullmatch(r'\d{4}',value) or not 1<=int(value)<=9999:fail()
        elif kind=='uuid':value=str(uuid.UUID(value))
        elif kind=='email':validate_email(value)
        elif kind=='url':URLValidator(schemes=['http','https'])(value)
        elif kind=='phone':
            if not re.fullmatch(r'\+?[0-9 ()\-\.]{3,30}',value):fail()
    except (ValueError,TypeError,ValidationError):fail()
    return value
