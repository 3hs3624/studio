"""Organization-scoped reusable code groups; stable identifiers, versioned edits."""
import re
from . import services as s
from .models import CommonCodeGroup, CommonCodeItem, EntityDefinition, EntitySchemaVersion


def group(actor, id):
    value = CommonCodeGroup.objects.filter(organization=actor.organization, id=s.identifier(id)).first()
    if not value:
        s.fail('NOT_FOUND', '코드 그룹을 찾을 수 없습니다.', 404)
    return value


def identifier(data):
    value = s.text(data, 'code', 40)
    if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,39}', value):
        s.fail('INVALID_CODE', '코드는 대문자 영문·숫자·밑줄로 입력하십시오.')
    return value


def uses(actor, value):
    results = {}
    for entity in EntityDefinition.objects.filter(organization=actor.organization):
        if any(f.get('code_group_id') == str(value.id) for f in entity.draft_fields):
            results[entity.id] = dict(id=str(entity.id), code=entity.code, name=entity.name)
    for schema in EntitySchemaVersion.objects.filter(organization=actor.organization).select_related('entity'):
        if any(f.get('code_group_id') == str(value.id) for f in schema.fields):
            results[schema.entity_id] = dict(id=str(schema.entity_id), code=schema.entity.code, name=schema.entity.name)
    return list(results.values())


def data(value):
    return dict(id=str(value.id), code=value.code, name=value.name, description=value.description,
                active=value.active, locked=value.locked, version=value.row_version,
                items=[dict(code=item.code, label=item.label, description=item.description,
                            sort_order=item.sort_order, active=item.active) for item in value.items.all()])


def authorize(actor, operation, target):
    s.require_console(actor)
    if operation not in ('code_group', 'code_items'):
        s.fail('INVALID_OPERATION', '허용되지 않은 코드 관리 작업입니다.')
    if target:
        if group(actor, target).locked:
            s.fail('SYSTEM_CODE_LOCKED', '시스템 필수 코드 그룹은 변경할 수 없습니다.', 409)


def mutate(actor, operation, payload, request_id, target):
    if operation == 'code_group':
        s.check_fields(payload, ['code','name','description','active','expected_version','reason'],
                       ['code','name','description','active','expected_version','reason'])
        if type(payload['active']) is not bool or type(payload['expected_version']) is not int:
            s.fail('INVALID_INPUT', '사용 여부·설정 버전을 확인하십시오.')
        code = identifier(payload)
        reason = s.text(payload, 'reason', 500)
        value = group(actor, target) if target else None
        if value:
            s.version(value, payload)
            if value.code != code:
                s.fail('IMMUTABLE_CODE', '코드 그룹 식별자는 변경할 수 없습니다.')
        elif payload['expected_version'] != 0:
            s.fail('VERSION_CONFLICT', '새 코드 그룹의 버전은 0이어야 합니다.', 409)
        elif CommonCodeGroup.objects.filter(organization=actor.organization, code=code).exists():
            s.fail('CODE_EXISTS', '이미 존재하는 코드 그룹입니다.', 409)
        before = data(value) if value else {}
        if not value:
            value = CommonCodeGroup(organization=actor.organization, code=code, row_version=0)
        value.name = s.text(payload, 'name', 100)
        value.description = s.text(payload, 'description', 500, required=False)
        value.active = payload['active']
        value.row_version += 1
        value.save()
    else:
        s.check_fields(payload, ['expected_version','items','reason'], ['expected_version','items','reason'])
        value = group(actor, target)
        s.version(value, payload)
        reason = s.text(payload, 'reason', 500)
        items = payload['items']
        if not isinstance(items, list) or not 1 <= len(items) <= 100:
            s.fail('INVALID_INPUT', '코드는 한 번에 1~100개를 저장하십시오.')
        before = data(value)
        seen = set()
        for item in items:
            if not isinstance(item, dict):
                s.fail('INVALID_INPUT', '코드 항목 형식을 확인하십시오.')
            s.check_fields(item, ['code','label','description','sort_order','active'], ['code','label','description','sort_order','active'])
            code = identifier(item)
            if code in seen or type(item['active']) is not bool or type(item['sort_order']) is not int or not 0 <= item['sort_order'] <= 99999:
                s.fail('INVALID_INPUT', '중복 코드·순서·사용 여부를 확인하십시오.')
            seen.add(code)
            CommonCodeItem.objects.update_or_create(organization=actor.organization, group=value, code=code,
                defaults=dict(label=s.text(item, 'label', 100), description=s.text(item, 'description', 500, required=False),
                              sort_order=item['sort_order'], active=item['active']))
        s.bump(value)
    result = data(value)
    s.record(actor, value, 'COMMON_CODE_CHANGED', request_id, before=before, after={**result,'reason':reason})
    return result, 200 if target else 201
