"""Row restrictions compose with existing business authorization; they never bypass it."""
from django.db.models import Q
from .models import Department,RoleDataPolicy
from .access_graph import role_rows
from .access_cache import cached

SUPPORTED={'workflow-inbox','requests','incidents','entities','assets'}
SCOPES={'LEGACY':'기존 기능 권한 범위','SELF':'본인','ASSIGNED':'본인·할당 건','DEPARTMENT':'소속 부서','SUBTREE':'소속·하위 부서','NONE':'허용 안 함'}

@cached('row_policies')
def policies(person,key):return list(RoleDataPolicy.objects.filter(organization=person.organization,role_key__in=[r['key'] for r in role_rows(person)],menu_key=key))

def departments(person,subtree=False):
    if not person.department_id:return []
    values={person.department_id};pending=[person.department_id]
    if subtree:
        while pending:
            pending=list(Department.objects.filter(organization=person.organization,active=True,parent_id__in=pending).exclude(id__in=values).values_list('id',flat=True));values.update(pending)
    return list(values)

def restrict(person,key,query,owner,assignment=None,write=False):
    entries=policies(person,key)
    if not entries:return query
    condition=Q(pk__in=[])
    for entry in entries:
        scope=entry.write_scope if write else entry.read_scope
        if scope=='LEGACY':return query
        if scope in ('SELF','ASSIGNED'):
            condition|=Q(**{owner+'_id':person.id})
            if scope=='ASSIGNED' and assignment:condition|=Q(**{assignment:person.id})
        elif scope in ('DEPARTMENT','SUBTREE'):condition|=Q(**{owner+'__department_id__in':departments(person,scope=='SUBTREE')})
    return query.filter(condition).distinct()

def can_write(person,key,obj,owner,assignment=None):
    return restrict(person,key,type(obj).objects.filter(pk=obj.pk,organization=person.organization),owner,assignment,True).exists()
