"""Built-in field handlers. Operators select identifiers; never Python imports."""
from datetime import date
import re
from types import MappingProxyType
from .. import services as s


def string_value(value):
    if not isinstance(value, str) or len(value) > 4000:
        s.fail('INVALID_ENTITY_VALUE', '문자열은 4,000자 이내여야 합니다.')
    return value


def integer_value(value):
    if type(value) is not int or not -(2**53-1) <= value <= 2**53-1:
        s.fail('INVALID_ENTITY_VALUE', '정수 형식과 허용 범위를 확인하십시오.')
    return value


def boolean_value(value):
    if type(value) is not bool:
        s.fail('INVALID_ENTITY_VALUE', '참/거짓 형식이 필요합니다.')
    return value


def date_value(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        s.fail('INVALID_ENTITY_VALUE', '날짜는 YYYY-MM-DD 형식이어야 합니다.')
    try:
        date.fromisoformat(value)
    except ValueError:
        s.fail('INVALID_ENTITY_VALUE', '유효한 날짜가 필요합니다.')
    return value


from ..data_types import TYPE_META,scalar
FIELD_TYPES = MappingProxyType({key:(value[0],lambda v,k=key:scalar({'type':k},v)) for key,value in TYPE_META.items()})
