"""Server-owned metadata shared by every logical entity; never user JSON keys."""
SYSTEM_FIELDS = (
    {'key': 'id', 'label': '고유 식별자', 'type': 'uuid'},
    {'key': 'organization_id', 'label': '소속 조직', 'type': 'organization'},
    {'key': 'created_at', 'label': '생성일', 'type': 'datetime'},
    {'key': 'created_by', 'label': '생성자', 'type': 'actor'},
    {'key': 'updated_at', 'label': '수정일', 'type': 'datetime'},
    {'key': 'updated_by', 'label': '수정자', 'type': 'actor'},
    {'key': 'row_version', 'label': '데이터 버전', 'type': 'integer'},
    {'key': 'schema_version_id', 'label': '엔티티 정의 버전', 'type': 'schema'},
)
# Internal attributes and optional capabilities cannot be shadowed by business keys.
RESERVED_KEYS = frozenset(f['key'] for f in SYSTEM_FIELDS) | {
    'created_by_id', 'updated_by_id', 'entity_id', 'request_id',
    'junction_left_id', 'junction_right_id', 'deleted_at', 'deleted_by',
}
RELATIONSHIPS = {
    'many_to_one': '다대일 (N:1)', 'one_to_one': '일대일 (1:1)',
    'one_to_many': '일대다 (1:N)', 'many_to_many': '다대다 (N:M)',
}


def system_fields():
    return [{**field, 'system': True, 'readonly': True} for field in SYSTEM_FIELDS]


def relationship(field):
    return field.get('relationship', 'many_to_one')


def multiple(field):
    return relationship(field) in ('one_to_many', 'many_to_many')
