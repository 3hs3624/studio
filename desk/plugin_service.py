"""Organization-scoped configuration and preview commands through the common executor."""
from . import services as s
from .models import PluginBinding, PluginRun, NumberSequence, NumberIssue
from django.utils import timezone
from hashlib import sha256
import json
from .plugins.bundled import REGISTRY


def definition(plugin_id):
    plugin = REGISTRY.get(plugin_id)
    if plugin is None:
        s.fail('PLUGIN_NOT_INSTALLED', '설치된 플러그인이 아닙니다.', 404)
    return plugin


def binding_data(binding):
    return dict(id=str(binding.id), version=binding.row_version, enabled=binding.enabled,
                configuration=binding.configuration, plugin_version=binding.plugin_version,
                manifest_digest=binding.manifest_digest)


def catalog(actor):
    s.require_console(actor)
    bindings = {b.plugin_id: b for b in PluginBinding.objects.filter(organization=actor.organization)}
    items = []
    for plugin in REGISTRY.values():
        binding = bindings.get(plugin.plugin_id)
        manifest = plugin.manifest()
        items.append(dict(manifest=manifest, binding=binding_data(binding) if binding else None,
                          compatible=not binding or (binding.plugin_version == plugin.version and
                                                     binding.manifest_digest == manifest['digest'])))
    return items


def require_active(actor, plugin_id, trail=()):
    plugin = definition(plugin_id)
    binding = PluginBinding.objects.filter(organization=actor.organization, plugin_id=plugin_id).first()
    if not binding or not binding.enabled:
        s.fail('PLUGIN_DISABLED', '활성화된 플러그인이 필요합니다.', 409)
    if binding.plugin_version != plugin.version or binding.manifest_digest != plugin.manifest()['digest']:
        s.fail('PLUGIN_INCOMPATIBLE', '설치 코드가 변경되었습니다. 설정을 검증하고 다시 저장하십시오.', 409)
    if plugin_id in trail:
        s.fail('PLUGIN_INCOMPATIBLE', '플러그인 의존성 순환을 확인하십시오.', 409)
    for dep_id, dep_version in plugin.dependencies:
        dep, _ = require_active(actor, dep_id, (*trail, plugin_id))
        if dep.version != dep_version:
            s.fail('PLUGIN_INCOMPATIBLE', '의존 플러그인 버전을 확인하십시오.', 409)
    return plugin, binding


def authorize(actor, operation, plugin_id):
    s.require_console(actor)
    definition(plugin_id)
    if operation in ('plugin_preview', 'plugin_issue'):
        require_active(actor, plugin_id)
    elif operation != 'plugin_configure':
        s.fail('INVALID_OPERATION', '허용되지 않은 플러그인 작업입니다.')


def configure(actor, payload, request_id, plugin_id):
    s.check_fields(payload, ['expected_version', 'enabled', 'configuration', 'reason', 'manifest_digest'],
                   ['expected_version', 'enabled', 'configuration', 'reason', 'manifest_digest'])
    plugin = definition(plugin_id)
    manifest = plugin.manifest()
    if payload['manifest_digest'] != manifest['digest']:
        s.fail('PLUGIN_INCOMPATIBLE', '플러그인 정보를 새로 불러와 확인하십시오.', 409)
    if type(payload['expected_version']) is not int or type(payload['enabled']) is not bool:
        s.fail('INVALID_INPUT', '버전과 활성 여부를 확인하십시오.')
    reason = s.text(payload, 'reason', 500)
    configuration = plugin.validate_configuration(payload['configuration'])
    binding = PluginBinding.objects.select_for_update().filter(organization=actor.organization, plugin_id=plugin_id).first()
    expected = binding.row_version if binding else 0
    if payload['expected_version'] != expected:
        s.fail('VERSION_CONFLICT', '다른 설정 변경이 있습니다. 새로고침하십시오.', 409)
    if payload['enabled']:
        for dep_id, _ in plugin.dependencies:
            require_active(actor, dep_id)
    else:
        for installed in REGISTRY.values():
            if plugin_id in dict(installed.dependencies) and PluginBinding.objects.filter(
                    organization=actor.organization, plugin_id=installed.plugin_id, enabled=True).exists():
                s.fail('PLUGIN_IN_USE', '활성 종속 플러그인을 먼저 중지하십시오.', 409)
    before = binding_data(binding) if binding else {}
    if not binding:
        binding = PluginBinding(organization=actor.organization, plugin_id=plugin_id)
    binding.plugin_version = plugin.version
    binding.manifest_digest = manifest['digest']
    binding.configuration = configuration
    binding.enabled = payload['enabled']
    binding.row_version = expected + 1
    binding.save()
    result = binding_data(binding)
    s.record(actor, binding, 'PLUGIN_CONFIGURED', request_id, before=before, after={**result, 'reason':reason})
    return result, 200


def preview(actor, payload, request_id, plugin_id, issue=False):
    s.check_fields(payload, ['expected_version', 'manifest_digest', 'input'],
                   ['expected_version', 'manifest_digest', 'input'])
    plugin, binding = require_active(actor, plugin_id)
    if type(payload['expected_version']) is not int or payload['expected_version'] != binding.row_version:
        s.fail('VERSION_CONFLICT', '실행할 설정 버전이 변경되었습니다.', 409)
    if payload['manifest_digest'] != binding.manifest_digest:
        s.fail('PLUGIN_INCOMPATIBLE', '플러그인 실행 버전을 확인하십시오.', 409)
    if not isinstance(payload['input'], dict):
        s.fail('INVALID_PLUGIN_INPUT', '입력은 JSON 객체여야 합니다.')
    # Validate stored configuration again; ORM bypasses must not execute unchecked settings.
    configuration = plugin.validate_configuration(binding.configuration)
    sequence = None
    if issue and 'plugin.issue' not in plugin.capabilities:
        s.fail('INVALID_OPERATION', '실제 발급을 지원하는 플러그인이 아닙니다.')
    if plugin.kind == 'numbering':
        s.check_fields(payload['input'], [], [])
        day = timezone.localdate()
        pattern = {'never':'','year':'%Y','month':'%Y%m','day':'%Y%m%d'}[configuration['reset']]
        period = day.strftime(pattern) if pattern else 'all'
        namespace = sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()
        sequence = NumberSequence.objects.select_for_update().filter(
            organization=actor.organization, namespace=namespace, period=period).first()
        next_value = sequence.last_value + 1 if sequence else 1
        result = plugin.execute(dict(sequence=next_value, on_date=day.isoformat()), configuration)
        if NumberIssue.objects.filter(organization=actor.organization, value=result['text']).exists():
            s.fail('NUMBER_COLLISION', '기존 발급 번호와 겹치는 설정입니다. 접두어·형식을 변경하십시오.', 409)
        if issue:
            if sequence is None:
                sequence = NumberSequence(organization=actor.organization, namespace=namespace, period=period)
            sequence.last_value = next_value
            sequence.save()
    else:
        result = plugin.execute(payload['input'], configuration)
    run = PluginRun.objects.create(organization=actor.organization, binding=binding, actor=actor,
        plugin_id=plugin_id, plugin_version=plugin.version, manifest_digest=binding.manifest_digest,
        binding_version=binding.row_version, configuration=configuration,
        input_length=len(payload['input'].get('text','')), output_length=len(result['text']), request_id=request_id)
    if issue:
        NumberIssue.objects.create(organization=actor.organization, binding=binding, actor=actor, run=run,
                                   value=result['text'], request_id=request_id)
    # No input/output text in run history, audit, or outbox.
    summary = dict(run_id=str(run.id), plugin_id=plugin_id, binding_version=binding.row_version,
                   manifest_digest=binding.manifest_digest, input_length=run.input_length,
                   output_length=run.output_length)
    summary['operation'] = 'issue' if issue else 'preview'
    s.record(actor, run, 'PLUGIN_NUMBER_ISSUED' if issue else 'PLUGIN_PREVIEWED', request_id, after=summary)
    return {**summary, 'output':result}, 200


def mutate(actor, operation, payload, request_id, plugin_id):
    if operation == 'plugin_configure':
        return configure(actor, payload, request_id, plugin_id)
    return preview(actor, payload, request_id, plugin_id, issue=operation=='plugin_issue')
