from hashlib import sha256
from pathlib import Path
from . import text_normalizer
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
),))
