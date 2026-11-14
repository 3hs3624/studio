"""Pure formatting contract. Sequence allocation stays in the transactional host."""
from datetime import date
import re
from .. import services as s

DEFAULTS = dict(prefix='SR', date_format='YYYYMM', separator='-', digits=5, reset='month')
SETTINGS = (
    dict(key='prefix', label='접두어', type='string', default='SR', maxlength=12),
    dict(key='date_format', label='날짜 형식', type='enum', default='YYYYMM', options=['NONE','YYYY','YYYYMM','YYYYMMDD']),
    dict(key='separator', label='구분자', type='enum', default='-', options=['-','_','/','']),
    dict(key='digits', label='순번 자릿수', type='integer', default=5, minimum=1, maximum=10),
    dict(key='reset', label='순번 초기화', type='enum', default='month', options=['never','year','month','day']),
)


def validate_configuration(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULTS):
        s.fail('INVALID_PLUGIN_CONFIG', '접두어·날짜 형식·구분자·순번 자릿수·초기화를 설정하십시오.')
    if not isinstance(value['prefix'], str) or not re.fullmatch(r'[A-Z][A-Z0-9]{0,11}', value['prefix']):
        s.fail('INVALID_PLUGIN_CONFIG', '접두어는 대문자 영문·숫자 1~12자로 입력하십시오.')
    if type(value['digits']) is not int or not 1 <= value['digits'] <= 10:
        s.fail('INVALID_PLUGIN_CONFIG', '순번 자릿수는 1~10 사이의 정수여야 합니다.')
    for key in ['date_format', 'separator', 'reset']:
        if not isinstance(value[key], str) or value[key] not in next(f['options'] for f in SETTINGS if f['key']==key):
            s.fail('INVALID_PLUGIN_CONFIG', '허용된 날짜·구분자·초기화 값을 선택하십시오.')
    precision = {'NONE':0,'YYYY':1,'YYYYMM':2,'YYYYMMDD':3}
    if precision[value['date_format']] < {'never':0,'year':1,'month':2,'day':3}[value['reset']]:
        s.fail('INVALID_PLUGIN_CONFIG', '순번 초기화 주기는 표시되는 날짜 범위 안에 있어야 합니다.')
    return dict(value)


def execute(payload, configuration):
    day = date.fromisoformat(payload['on_date'])
    count = payload['sequence']
    if count >= 10**configuration['digits']:
        s.fail('SEQUENCE_EXHAUSTED', '해당 기간의 순번 자릿수를 모두 사용했습니다.', 409)
    pattern = {'NONE':'','YYYY':'%Y','YYYYMM':'%Y%m','YYYYMMDD':'%Y%m%d'}[configuration['date_format']]
    parts = [configuration['prefix']]
    if pattern:
        parts.append(day.strftime(pattern))
    parts.append(str(count).zfill(configuration['digits']))
    return {'text':configuration['separator'].join(parts)}
