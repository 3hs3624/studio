from .access_cache import cached
"""Additive assignments with explicit provenance; no implicit department subtree grants."""
from .models import (Department,Group,GroupDepartment,Membership,ScopedRoleGrant,RoleGrant,CustomRoleGrant,RoleDefinition,RoleMenuPolicy)


@cached('chain')
def chain(person):
    values=[];seen=set();current=person.department_id
    while current:
        if current in seen:return []
        seen.add(current)
        department=Department.objects.filter(id=current,organization_id=person.organization_id,active=True).first()
        if not department:return []
        values.append(department);current=department.parent_id
    return values


@cached('effective_groups')
def effective_groups(person):
    values={str(m.group_id):{'group':m.group,'paths':['직접 배정']} for m in Membership.objects.filter(person_id=person.id,organization_id=person.organization_id,group__active=True).select_related('group')}
    departments=chain(person)
    for index,dep in enumerate(departments):
        for link in GroupDepartment.objects.filter(organization_id=person.organization_id,department=dep,group__active=True).select_related('group'):
            if index and not link.include_children:continue
            entry=values.setdefault(str(link.group_id),{'group':link.group,'paths':[]})
            entry['paths'].append('부서 '+dep.name+(' (하위 포함)' if index else ''))
    return values


@cached('role_rows')
def role_rows(person):
    from .permissions import BUILTIN
    from .templatetags.desk_tags import role_label
    values={'EVERYONE':{'key':'EVERYONE','name':'기본 사용자','paths':['모든 사용자'],'system':True}}
    def add(key,path):
        if key in BUILTIN:name=role_label(key);system=True
        else:
            role=RoleDefinition.objects.filter(id=key,organization_id=person.organization_id,active=True).first()
            if not role:return
            name=role.name;system=False
        row=values.setdefault(key,dict(key=key,name=name,paths=[],system=system))
        if path not in row['paths']:row['paths'].append(path)
    for grant in RoleGrant.objects.filter(person_id=person.id,organization_id=person.organization_id):add(grant.role,'직접 배정')
    for grant in CustomRoleGrant.objects.filter(person_id=person.id,organization_id=person.organization_id,active=True,role__active=True).select_related('role'):add(str(grant.role_id),'직접 배정')
    for index,dep in enumerate(chain(person)):
        for grant in ScopedRoleGrant.objects.filter(organization_id=person.organization_id,department=dep):
            if index and not grant.include_children:continue
            add(grant.role_key,'부서 '+dep.name+(' (하위 포함)' if index else ''))
    for entry in effective_groups(person).values():
        for grant in ScopedRoleGrant.objects.filter(organization_id=person.organization_id,group=entry['group']):
            add(grant.role_key,'그룹 '+entry['group'].name+' ← '+', '.join(entry['paths']))
    return list(values.values())


@cached('role_capabilities')
def role_capabilities(organization,key):
    from .permissions import BUILTIN
    if key in BUILTIN:return set(BUILTIN[key])
    role=RoleDefinition.objects.filter(organization=organization,id=key,active=True).first()
    return set(role.permissions) if role else set()


def group_ids(person):return [entry['group'].id for entry in effective_groups(person).values()]


def departments_tree(organization):
    rows=list(Department.objects.filter(organization=organization).order_by('name','id'));children={}
    for row in rows:children.setdefault(row.parent_id,[]).append(row)
    result=[]
    def visit(parent,depth,seen):
        for row in children.get(parent,[]):
            if row.id in seen:continue
            row.depth=depth;row.indent='　'*depth;result.append(row);visit(row.id,depth+1,seen|{row.id})
    visit(None,0,set());return result
