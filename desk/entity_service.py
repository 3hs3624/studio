"""Versioned logical entities; no operator-controlled SQL or DDL."""
import hashlib
import json
import re
from . import services as s
from .models import EntityDefinition, EntitySchemaVersion, EntityRecord, EntityRecordLink
from .entities.system_fields import RESERVED_KEYS, RELATIONSHIPS, system_fields, relationship, multiple
from django.db import IntegrityError, transaction
from django.db.models import Q
from .entities.fields import FIELD_TYPES


def get_entity(actor, entity_id):
    entity = EntityDefinition.objects.filter(organization=actor.organization, id=s.identifier(entity_id)).first()
    if not entity:
        s.fail('NOT_FOUND', '엔티티를 찾을 수 없습니다.', 404)
    return entity


def latest(entity):
    return EntitySchemaVersion.objects.filter(entity=entity).order_by('-version').first()


def validate_fields(actor, fields):
    if not isinstance(fields, list) or not 0 <= len(fields) <= 30:
        s.fail('INVALID_ENTITY_SCHEMA', '업무 필드는 최대 30개로 구성하십시오.')
    seen, result = set(), []
    for field in fields:
        if not isinstance(field, dict):
            s.fail('INVALID_ENTITY_SCHEMA', '필드 정의는 객체여야 합니다.')
        s.check_fields(field, ['key','label','type','required','options','target_entity_id','relationship'],
                       ['key','label','type','required'])
        key, kind = field['key'], field['type']
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,39}', key) or key in seen or key in RESERVED_KEYS:
            s.fail('INVALID_ENTITY_SCHEMA', '필드 식별자는 중복 없는 영문 소문자·숫자·밑줄이어야 하며 시스템 필드를 사용할 수 없습니다.')
        if not isinstance(kind, str) or kind not in FIELD_TYPES or type(field['required']) is not bool:
            s.fail('INVALID_ENTITY_SCHEMA', '지원 필드 종류와 필수 여부를 확인하십시오.')
        value = dict(key=key, label=s.text(field, 'label', 100), type=kind, required=field['required'])
        if kind == 'choice':
            options = field.get('options')
            if (not isinstance(options, list) or not 1 <= len(options) <= 30 or
                    any(not isinstance(v, str) or not v.strip() or len(v) > 100 for v in options)):
                s.fail('INVALID_ENTITY_SCHEMA', '선택지는 1~30개, 각 100자 이내여야 합니다.')
            value['options'] = [v.strip() for v in options]
            if len(set(value['options'])) != len(options):
                s.fail('INVALID_ENTITY_SCHEMA', '선택지가 중복되었습니다.')
        elif 'options' in field:
            s.fail('INVALID_ENTITY_SCHEMA', '선택 필드에만 선택지를 지정하십시오.')
        if kind == 'reference':
            target = get_entity(actor, field.get('target_entity_id'))
            if not latest(target):
                s.fail('INVALID_ENTITY_SCHEMA', '게시된 대상 엔티티를 선택하십시오.')
            value['target_entity_id'] = str(target.id)
            relation = field.get('relationship', 'many_to_one')
            if not isinstance(relation, str) or relation not in RELATIONSHIPS:
                s.fail('INVALID_ENTITY_SCHEMA', '지원하지 않는 관계 유형입니다.')
            if 'relationship' in field:
                value['relationship'] = relation
        elif 'target_entity_id' in field or 'relationship' in field:
            s.fail('INVALID_ENTITY_SCHEMA', '참조 필드에만 대상을 지정하십시오.')
        seen.add(key)
        result.append(value)
    return result


def schema_data(schema):
    return dict(id=str(schema.id), version=schema.version, name=schema.name, fields=schema.fields, system_fields=system_fields(), junction=schema.junction,
                digest=schema.schema_digest, reason=schema.reason, created_at=schema.created_at.isoformat())


def entity_data(entity):
    published = latest(entity)
    return dict(id=str(entity.id), code=entity.code, name=entity.name, version=entity.row_version,
                draft_fields=entity.draft_fields, system_fields=system_fields(), draft_junction=entity.draft_junction, published=schema_data(published) if published else None)


def record_data(record):
    return dict(id=str(record.id), entity_id=str(record.entity_id), schema_version_id=str(record.schema_version_id),
                schema_version=record.schema_version.version, values=record.values,
                organization_id=str(record.organization_id), created_by=str(record.created_by_id),
                updated_at=record.updated_at.isoformat(), updated_by=str(record.updated_by_id),
                row_version=record.row_version, created_at=record.created_at.isoformat())


def authorize(actor, operation, target):
    s.require_console(actor)
    if operation not in ('entity_save', 'entity_publish', 'entity_record'):
        s.fail('INVALID_OPERATION', '허용되지 않은 엔티티 작업입니다.')
    if operation != 'entity_save':
        get_entity(actor, target)


def save(actor, payload, request_id):
    s.check_fields(payload, ['code','name','fields','expected_version','reason','junction'],
                   ['code','name','fields','expected_version','reason'])
    code = s.text(payload, 'code', 40).upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,39}', code):
        s.fail('INVALID_ENTITY_SCHEMA', '엔티티 코드는 영문 대문자·숫자·밑줄로 입력하십시오.')
    if type(payload['expected_version']) is not int:
        s.fail('INVALID_VERSION', '설정 버전은 정수여야 합니다.')
    reason = s.text(payload, 'reason', 500)
    entity = EntityDefinition.objects.select_for_update().filter(organization=actor.organization, code=code).first()
    expected = entity.row_version if entity else 0
    if payload['expected_version'] != expected:
        s.fail('VERSION_CONFLICT', '엔티티 설정이 변경되었습니다. 새로고침하십시오.', 409)
    fields = validate_fields(actor, payload['fields'])
    junction = validate_junction(payload.get('junction', entity.draft_junction if entity else {}), fields)
    before = {'name':entity.name, 'fields':entity.draft_fields, 'junction':entity.draft_junction, 'version':expected} if entity else {}
    if not entity:
        entity = EntityDefinition(organization=actor.organization, code=code)
    entity.name = s.text(payload, 'name', 200)
    entity.draft_fields = fields
    entity.draft_junction = junction
    entity.row_version = expected + 1
    entity.save()
    s.record(actor, entity, 'ENTITY_DRAFT_SAVED', request_id, before=before,
             after={'name':entity.name, 'fields':fields, 'junction':junction, 'version':entity.row_version, 'reason':reason})
    return entity_data(entity), 200 if expected else 201


def publish(actor, payload, request_id, target):
    s.check_fields(payload, ['expected_version','reason'], ['expected_version','reason'])
    entity = get_entity(actor, target)
    s.version(entity, payload)
    reason = s.text(payload, 'reason', 500)
    fields = validate_fields(actor, entity.draft_fields)
    junction = validate_junction(entity.draft_junction, fields)
    validate_relation_changes(entity, fields, junction)
    previous = latest(entity)
    version = previous.version + 1 if previous else 1
    snapshot = dict(entity_id=str(entity.id), version=version, name=entity.name, fields=fields, junction=junction, system_fields=system_fields())
    digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    schema = EntitySchemaVersion.objects.create(organization=actor.organization, entity=entity,
        version=version, name=entity.name, fields=fields, junction=junction, schema_digest=digest,
        published_by=actor, reason=reason, request_id=request_id)
    s.bump(entity)
    s.record(actor, schema, 'ENTITY_SCHEMA_PUBLISHED', request_id,
             after={'entity_id':str(entity.id), 'version':version, 'schema_digest':digest, 'reason':reason})
    return entity_data(entity), 201


def validate_values(actor, schema, values):
    if not isinstance(values, dict) or set(values) - {f['key'] for f in schema.fields}:
        s.fail('INVALID_ENTITY_VALUE', '정의에 없는 입력 항목입니다.')
    cleaned = {}
    for field in schema.fields:
        key = field['key']
        value = values.get(key)
        if value is None or value == '' or (value == [] and field['type'] == 'reference' and multiple(field)):
            if field['required']:
                s.fail('INVALID_ENTITY_VALUE', f"{field['label']}: 필수 입력입니다.")
            continue
        kind = field['type']
        if kind == 'reference':
            cleaned[key] = validate_reference(actor, schema, field, value)
            continue
        value = FIELD_TYPES[kind][1](value)
        if field['required'] and isinstance(value, str) and not value.strip():
            s.fail('INVALID_ENTITY_VALUE', f"{field['label']}: 공백만 입력할 수 없습니다.")
        if kind == 'choice' and value not in field['options']:
            s.fail('INVALID_ENTITY_VALUE', f"{field['label']}: 허용된 선택지가 아닙니다.")
        cleaned[key] = value
    return cleaned


def create_record(actor, payload, request_id, target):
    s.check_fields(payload, ['schema_version_id','values'], ['schema_version_id','values'])
    entity = get_entity(actor, target)
    schema = latest(entity)
    if schema is None:
        s.fail('ENTITY_UNPUBLISHED', '엔티티를 먼저 게시하십시오.', 409)
    if str(schema.id) != str(s.identifier(payload['schema_version_id'])):
        s.fail('VERSION_CONFLICT', '게시된 정의가 변경되었습니다. 입력 화면을 다시 확인하십시오.', 409)
    values = validate_values(actor, schema, payload['values'])
    junction_values = {}
    if schema.junction:
        junction_values = dict(junction_left_id=values[schema.junction['left_field']],
                               junction_right_id=values[schema.junction['right_field']])
        if EntityRecord.objects.filter(entity=entity, **junction_values).exists():
            s.fail('RELATION_CONFLICT', '이미 등록된 중간 엔티티 연결 쌍입니다.', 409)
    try:
        with transaction.atomic():
            record = EntityRecord.objects.create(organization=actor.organization, entity=entity, schema_version=schema,
                values=values, created_by=actor, updated_by=actor, request_id=request_id, **junction_values)
            for field in schema.fields:
                if field['type'] != 'reference' or field['key'] not in values:
                    continue
                targets = values[field['key']] if multiple(field) else [values[field['key']]]
                EntityRecordLink.objects.bulk_create([
                    EntityRecordLink(organization=actor.organization, source_entity=entity, source=record,
                        target_id=target_id, field_key=field['key'], scalar=not multiple(field),
                        exclusive=relationship(field) in ('one_to_one', 'one_to_many'))
                    for target_id in targets])
    except IntegrityError:
        s.fail('RELATION_CONFLICT', '관계 제약과 중복 연결 여부를 확인하십시오.', 409)
    s.record(actor, record, 'ENTITY_RECORD_CREATED', request_id,
             after={'entity_id':str(entity.id), 'schema_version_id':str(schema.id), 'field_keys':list(values)})
    return record_data(record), 201


def mutate(actor, operation, payload, request_id, target):
    if operation == 'entity_save':
        return save(actor, payload, request_id)
    if operation == 'entity_publish':
        return publish(actor, payload, request_id, target)
    return create_record(actor, payload, request_id, target)


def validate_junction(junction, fields):
    if not isinstance(junction, dict):
        s.fail('INVALID_ENTITY_SCHEMA', '중간 엔티티 설정은 객체여야 합니다.')
    if not junction:
        return {}
    s.check_fields(junction, ['left_field', 'right_field'], ['left_field', 'right_field'])
    keys = [junction['left_field'], junction['right_field']]
    if any(not isinstance(key, str) for key in keys) or keys[0] == keys[1]:
        s.fail('INVALID_ENTITY_SCHEMA', '서로 다른 두 참조 필드를 선택하십시오.')
    definitions = {field['key']: field for field in fields}
    for key in keys:
        field = definitions.get(key, {})
        if field.get('type') != 'reference' or not field.get('required') or relationship(field) != 'many_to_one':
            s.fail('INVALID_ENTITY_SCHEMA', '중간 엔티티의 양쪽 필드는 필수 다대일 참조여야 합니다.')
    return dict(junction)


def validate_relation_changes(entity, fields, junction):
    # Historical rows retain their schema; a reused relationship key must retain semantics.
    ids = EntityRecord.objects.filter(entity=entity).values_list('schema_version_id', flat=True).distinct()
    new = {field['key']: field for field in fields}
    for schema in EntitySchemaVersion.objects.filter(id__in=ids):
        if schema.junction != junction:
            s.fail('RELATION_SCHEMA_IN_USE', '데이터가 있는 중간 엔티티의 연결 필드는 변경할 수 없습니다.', 409)
        for old in schema.fields:
            field = new.get(old['key'])
            if not field:
                continue
            if old['type'] == 'reference' or field['type'] == 'reference':
                signature = lambda value: (value['type'], value.get('target_entity_id'), relationship(value))
                if signature(old) != signature(field):
                    s.fail('RELATION_SCHEMA_IN_USE', '사용 중인 참조 필드의 관계 유형·대상은 새 필드로 구성하십시오.', 409)


def validate_reference(actor, schema, field, value):
    values = value if multiple(field) else [value]
    if (not isinstance(values, list) or not 1 <= len(values) <= 100 or
            any(not isinstance(item, str) for item in values)):
        s.fail('INVALID_ENTITY_VALUE', '복수 관계는 최대 100개의 식별자 목록을 입력하십시오.')
    ids = [str(s.identifier(item)) for item in values]
    if len(set(ids)) != len(ids):
        s.fail('INVALID_ENTITY_VALUE', '같은 대상을 중복 연결할 수 없습니다.')
    count = EntityRecord.objects.filter(id__in=ids, organization=actor.organization,
                                       entity_id=field['target_entity_id']).count()
    if count != len(ids):
        s.fail('INVALID_ENTITY_VALUE', '현재 조직의 올바른 대상 레코드를 선택하십시오.')
    if relationship(field) in ('one_to_one', 'one_to_many'):
        if EntityRecordLink.objects.filter(source_entity=schema.entity, field_key=field['key'], target_id__in=ids).exists():
            s.fail('RELATION_CONFLICT', '다른 데이터에 이미 연결된 대상입니다.', 409)
    return ids if multiple(field) else ids[0]


def related_data(actor, entity, record_id):
    record = EntityRecord.objects.filter(organization=actor.organization, entity=entity,
                                         id=s.identifier(record_id)).first()
    if not record:
        s.fail('NOT_FOUND', '데이터를 찾을 수 없습니다.', 404)
    links = EntityRecordLink.objects.filter(organization=actor.organization).filter(
        Q(source=record) | Q(target=record)).select_related('source', 'target').order_by('field_key', 'id')[:200]
    junctions = EntityRecord.objects.filter(organization=actor.organization).filter(
        Q(junction_left=record) | Q(junction_right=record)).order_by('id')[:200]
    return dict(record=record_data(record), links=[dict(
        id=str(link.id), field=link.field_key,
        direction='outgoing' if link.source_id == record.id else 'incoming',
        source_id=str(link.source_id), source_entity_id=str(link.source.entity_id),
        target_id=str(link.target_id), target_entity_id=str(link.target.entity_id),
        scalar=link.scalar, exclusive=link.exclusive) for link in links],
        junctions=[dict(id=str(item.id), entity_id=str(item.entity_id),
                        left_id=str(item.junction_left_id), right_id=str(item.junction_right_id),
                        values=item.values) for item in junctions])
