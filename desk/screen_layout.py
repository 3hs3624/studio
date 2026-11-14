"""Validated, versioned screen layout; authorization remains in the workflow engine."""
import re
from . import services as s


def validate_layout(raw,fields,columns):
    if not isinstance(raw,dict):s.fail('INVALID_LAYOUT','화면 배치를 확인하십시오.')
    s.check_fields(raw,['mode','groups'],['mode','groups'])
    if raw['mode'] not in ('sections','tabs') or not isinstance(raw['groups'],list) or not 1<=len(raw['groups'])<=20:s.fail('INVALID_LAYOUT','그룹 표시 방식과 그룹 개수를 확인하십시오.')
    keys={f['key'] for f in fields};seen=set();groups=[];group_keys=set()
    for group in raw['groups']:
        if not isinstance(group,dict):s.fail('INVALID_LAYOUT','그룹 정의를 확인하십시오.')
        s.check_fields(group,['key','label','fields'],['key','label','fields'])
        key=s.text(group,'key',40)
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,39}',key) or key in group_keys or not isinstance(group['fields'],list):s.fail('INVALID_LAYOUT','그룹 식별자는 중복 없이 입력하십시오.')
        group_keys.add(key);items=[]
        for item in group['fields']:
            if not isinstance(item,dict):s.fail('INVALID_LAYOUT','필드 배치를 확인하십시오.')
            s.check_fields(item,['key','span','height'],['key','span','height'])
            field=item['key'];span=item['span'];height=item['height']
            if not isinstance(field,str) or field not in keys or field in seen or type(span) is not int or not 1<=span<=columns or type(height) is not int or not 1<=height<=5:s.fail('INVALID_LAYOUT','필드는 한 그룹에만 배치하고 너비·높이 범위를 확인하십시오.')
            seen.add(field);items.append(dict(key=field,span=span,height=height))
        groups.append(dict(key=key,label=s.text(group,'label',100),fields=items))
    if seen!=keys:s.fail('INVALID_LAYOUT','모든 화면 항목을 그룹에 배치하십시오.')
    return dict(mode=raw['mode'],groups=groups)


def visible_groups(screen,fields):
    """Only already-authorized fields enter the layout, including tab labels."""
    if not screen or not screen.get('layout'):return []
    values={f['key']:f for f in fields};groups=[]
    for group in screen['layout']['groups']:
        items=[dict(values[item['key']],span=item['span'],height=item['height'],pixel_height=item['height']*48) for item in group['fields'] if item['key'] in values]
        if items:groups.append(dict(key=group['key'],label=group['label'],fields=items))
    return groups
