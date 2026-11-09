"""Versioned, immutable registry of trusted bundled code, validated at startup."""
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from types import MappingProxyType
from typing import Callable

PLATFORM_API = '1.0'


@dataclass(frozen=True)
class Plugin:
    plugin_id: str
    version: str
    name: str
    description: str
    api_version: str
    code_digest: str
    dependencies: tuple
    configuration_schema: str
    validate_configuration: Callable
    execute: Callable
    settings_fields: tuple = ()
    input_fields: tuple = ()
    kind: str = 'transform'
    capabilities: tuple = ('plugin.preview',)

    def manifest(self):
        value = dict(plugin_id=self.plugin_id, version=self.version, name=self.name,
                     description=self.description, api_version=self.api_version,
                     code_digest=self.code_digest, dependencies=dict(self.dependencies),
                     configuration_schema=self.configuration_schema,
                     capability='plugin.preview', kind=self.kind, capabilities=list(self.capabilities),
                     settings_fields=[dict(field) for field in self.settings_fields],
                     input_fields=[dict(field) for field in self.input_fields])
        value['digest'] = sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return value


def build_registry(plugins):
    result = {}
    for plugin in plugins:
        if not re.fullmatch(r'[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*', plugin.plugin_id):
            raise ValueError('Invalid plugin identifier')
        if not re.fullmatch(r'\d+\.\d+\.\d+', plugin.version):
            raise ValueError('Invalid plugin version')
        if (plugin.api_version != PLATFORM_API or not re.fullmatch(r'[0-9a-f]{64}', plugin.code_digest)
                or not callable(plugin.validate_configuration) or not callable(plugin.execute)):
            raise ValueError('Incompatible plugin contract')
        if plugin.kind not in ('transform','numbering') or not set(plugin.capabilities) <= {'plugin.preview','plugin.issue'} or 'plugin.preview' not in plugin.capabilities:
            raise ValueError('Invalid plugin capability')
        keys = [field.get('key') for field in plugin.settings_fields]
        if len(set(keys)) != len(keys) or any(not isinstance(key,str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',key) for key in keys):
            raise ValueError('Invalid settings field')
        if any(field.get('type') not in ('string','integer','enum','boolean') for field in plugin.settings_fields):
            raise ValueError('Invalid settings type')
        if plugin.plugin_id in result or len(dict(plugin.dependencies)) != len(plugin.dependencies):
            raise ValueError('Duplicate plugin or dependency')
        result[plugin.plugin_id] = plugin
    visiting, visited = set(), set()

    def visit(plugin_id):
        if plugin_id in visiting:
            raise ValueError('Cyclic plugin dependency')
        if plugin_id in visited:
            return
        visiting.add(plugin_id)
        for dep_id, version in result[plugin_id].dependencies:
            if dep_id not in result or result[dep_id].version != version:
                raise ValueError('Missing or incompatible plugin dependency')
            visit(dep_id)
        visiting.remove(plugin_id)
        visited.add(plugin_id)
    for plugin_id in result:
        visit(plugin_id)
    return MappingProxyType(result)
