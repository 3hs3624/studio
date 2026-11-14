"""First reusable element: bounded text normalization, with no external effects."""
import re
from .. import services as s


def validate_configuration(value):
    if not isinstance(value, dict):
        s.fail('INVALID_PLUGIN_CONFIG', '설정은 JSON 객체여야 합니다.')
    if set(value) != {'trim', 'collapse_spaces'} or any(type(v) is not bool for v in value.values()):
        s.fail('INVALID_PLUGIN_CONFIG', 'trim과 collapse_spaces에 true 또는 false를 지정하십시오.')
    return dict(value)


def execute(payload, configuration):
    s.check_fields(payload, ['text'], ['text'])
    value = payload['text']
    if not isinstance(value, str) or len(value) > 4000:
        s.fail('INVALID_PLUGIN_INPUT', '텍스트는 4,000자 이내여야 합니다.')
    if configuration['trim']:
        value = value.strip()
    if configuration['collapse_spaces']:
        value = re.sub(r'\s+', ' ', value)
    return {'text': value}
