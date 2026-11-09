from hashlib import sha256
from pathlib import Path
from . import text_normalizer, number_generator
from .registry import Plugin, build_registry

# Hash actual bundled implementation and contract modules, not a client-supplied digest.
_code = sha256(b''.join(Path(__file__).with_name(name).read_bytes() for name in
                       ['text_normalizer.py', 'registry.py', 'bundled.py'])).hexdigest()
REGISTRY = build_registry((Plugin(
    plugin_id='text.normalize', version='1.0.0', name='텍스트 정규화',
    description='앞뒤 공백과 연속 공백을 설정에 따라 정리합니다. 외부 호출은 수행하지 않습니다.',
    api_version='1.0', code_digest=_code, dependencies=(),
    configuration_schema='{"trim":"boolean","collapse_spaces":"boolean"}',
    validate_configuration=text_normalizer.validate_configuration,
    execute=text_normalizer.execute,
    settings_fields=(dict(key='trim',label='앞뒤 공백 제거',type='boolean',default=True),
                     dict(key='collapse_spaces',label='연속 공백 합치기',type='boolean',default=True)),
    input_fields=(dict(key='text',label='입력 텍스트',type='textarea',default=''),),
), Plugin(
    plugin_id='number.generate', version='1.0.0', name='업무번호 생성',
    description='조직별 업무번호를 미리 확인하거나 중복 없이 발급합니다. 미리보기는 순번을 소비하지 않습니다.',
    api_version='1.0', code_digest=sha256(Path(number_generator.__file__).read_bytes()).hexdigest(), dependencies=(),
    configuration_schema='number-generator-v1', validate_configuration=number_generator.validate_configuration,
    execute=number_generator.execute, settings_fields=number_generator.SETTINGS, input_fields=(),
    kind='numbering', capabilities=('plugin.preview','plugin.issue'),
)))
