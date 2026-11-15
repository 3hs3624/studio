"""Read-only impact reports; published versions and running work are never rewritten."""
from .models import ProcessVersion,ProcessRun,EntityRecord,EntitySchemaVersion


def field_changes(before,after):
    def entries(value):
        return {f['key']:f for f in value if isinstance(f,dict) and isinstance(f.get('key'),str) and 'type' in f} if isinstance(value,list) else {}
    old=entries(before);new=entries(after);result=[]
    for key in sorted(old.keys()|new.keys()):
        if key not in old:result.append(dict(key=key,kind='추가',risk='확인',detail='필수 항목이면 기존 데이터의 기본값·이관을 확인하십시오.' if new[key].get('required') else '신규 버전부터 적용됩니다.'))
        elif key not in new:result.append(dict(key=key,kind='제거',risk='주의',detail='기존 게시 버전과 데이터는 보존됩니다. 참조 규칙·매핑을 확인하십시오.'))
        elif old[key]!=new[key]:
            incompatible=old[key]['type']!=new[key]['type'] or new[key].get('required',False) and not old[key].get('required',False) or new[key].get('max_length',65535)<old[key].get('max_length',65535) or any(new[key].get(k,38)<old[key].get(k,38) for k in ('precision','scale'))
            result.append(dict(key=key,kind='변경',risk='주의' if incompatible else '확인',detail='유형·필수·길이·정밀도 변경의 데이터 호환성을 확인하십시오.' if incompatible else '표시·설정 변경입니다. 새 버전에서 검증하십시오.'))
    return result


def process_impact(definition):
    if definition.validation_errors:
        return dict(changes=[],references=[],active_runs=0)
    published=definition.published
    if not published:return dict(changes=[],references=[],active_runs=0)
    changes=field_changes(published.graph.get('fields',[]),definition.draft.get('fields',[]))
    refs=[]
    if definition.kind=='SCREEN':
        ids=set(str(v) for v in definition.versions.values_list('id',flat=True))
        for version in ProcessVersion.objects.filter(organization=definition.organization,definition__kind='WORKFLOW').select_related('definition').iterator(chunk_size=100):
            used=set()
            if version.graph.get('screen_version_id') in ids:used.add(version.graph['screen_version_id'])
            for node in version.graph.get('nodes',[]):
                if node.get('screen_version_id') in ids:used.add(node['screen_version_id'])
            if used:refs.append(dict(name=version.definition.name,version=version.version,current=version.definition.published_id==version.id))
    active=ProcessRun.objects.filter(organization=definition.organization,version__definition=definition,status__in=['ACTIVE','BLOCKED']).count() if definition.kind!='SCREEN' else 0
    return dict(changes=changes,references=refs,active_runs=active)


def entity_impact(entity):
    previous=entity.schema_versions.order_by('-version').first()
    refs=[]
    for schema in EntitySchemaVersion.objects.filter(organization=entity.organization).select_related('entity').iterator(chunk_size=100):
        keys=[f['key'] for f in schema.fields if f.get('target_entity_id')==str(entity.id)]
        if keys:refs.append(dict(name=schema.entity.name,version=schema.version,fields=', '.join(keys)))
    return dict(changes=field_changes(previous.fields,entity.draft_fields) if previous else [],references=refs,records=EntityRecord.objects.filter(organization=entity.organization,entity=entity).count())
