"""Audited organization graph mutations and signed, revalidated allocation copy previews."""
import hashlib,json,uuid
from types import SimpleNamespace
from django.core import signing
from django.db.models import Q
from . import services as s
from .models import (Organization,Person,Department,Group,Membership,GroupDepartment,RoleDefinition,RoleGrant,CustomRoleGrant,ScopedRoleGrant,RoleMenuPolicy,Ticket)
from .permissions import require,effective,BUILTIN
from .access_graph import role_rows,effective_groups,role_capabilities
from .menu_access import MENUS,PROTECTED,mapped_capabilities
from .security_policy import require_recent


def sysadmin(actor):return RoleGrant.objects.filter(person=actor,role='ORG_ADMIN').exists()
def department(actor,id):
    value=Department.objects.filter(organization=actor.organization,id=s.identifier(id)).first()
    if not value:s.fail('NOT_FOUND','부서를 찾을 수 없습니다.',404)
    return value


def role_object(actor,key):
    if key in BUILTIN:return None
    value=RoleDefinition.objects.filter(organization=actor.organization,id=s.identifier(key),active=True).first()
    if not value:s.fail('NOT_FOUND','활성 역할을 찾을 수 없습니다.',404)
    return value


def delegation(actor,key):
    role_object(actor,key)
    if key=='EVERYONE':s.fail('IMPLICIT_ROLE','기본 사용자 역할은 모든 사용자에게 자동 적용됩니다.')
    capabilities=role_capabilities(actor.organization,key)|mapped_capabilities(actor.organization,key)
    if (key=='ORG_ADMIN' and not sysadmin(actor)) or (not sysadmin(actor) and not capabilities<=effective(actor)):s.fail('CANNOT_DELEGATE','배정 권한이 없는 역할입니다.',403)


def group_delegation(actor,group):
    for grant in ScopedRoleGrant.objects.filter(organization=actor.organization,group=group):delegation(actor,grant.role_key)


def ids(data,key):
    value=data.get(key,[])
    if not isinstance(value,list) or len(value)>500 or any(not isinstance(item,str) for item in value) or len(set(value))!=len(value):s.fail('INVALID_SELECTION','선택 항목은 중복 없이 최대 500개입니다.')
    return value


def selected(actor,model,values):
    rows=list(model.objects.filter(organization=actor.organization,id__in=[s.identifier(v) for v in values]))
    if len(rows)!=len(values) or any(hasattr(x,'active') and not x.active for x in rows):s.fail('INVALID_SELECTION','현재 조직의 활성 항목만 선택하십시오.')
    return rows


def source_allocations(actor,kind,id):
    if kind=='user':
        from .identity_management import person
        source=person(actor,id)
        if not source.active:s.fail('INACTIVE_SOURCE','중지된 사용자는 복제할 수 없습니다.')
    elif kind=='department':
        dep=department(actor,id)
        if not dep.active:s.fail('INACTIVE_SOURCE','중지된 부서는 복제할 수 없습니다.')
        source=SimpleNamespace(id=None,organization=actor.organization,organization_id=actor.organization_id,department_id=dep.id)
    else:s.fail('INVALID_SOURCE','사용자 또는 부서를 선택하십시오.')
    roles=[]
    for row in role_rows(source):
        if row['key']=='EVERYONE':continue
        try:delegation(actor,row['key'])
        except s.BusinessError:continue
        from .menu_access import role_menus
        roles.append({**row,'capabilities':sorted(role_capabilities(actor.organization,row['key'])|mapped_capabilities(actor.organization,row['key'])),'menus':sorted(role_menus(actor.organization,row['key'])[0])})
    groups=[]
    for item in effective_groups(source).values():
        try:group_delegation(actor,item['group'])
        except s.BusinessError:continue
        groups.append(dict(id=str(item['group'].id),name=item['group'].name,paths=item['paths']))
    return {'roles':sorted(roles,key=lambda x:x['key']),'groups':sorted(groups,key=lambda x:x['id'])}


def preview(actor,kind,id):
    require(actor,'users.manage');require(actor,'iam.manage');require_recent(actor)
    values=source_allocations(actor,kind,id)
    token=signing.dumps({'kind':kind,'id':str(id),'org':str(actor.organization_id),'actor':str(actor.id),'values':values},salt='allocation-copy',compress=True)
    return {**values,'token':token}


def assign_direct(actor,member,role_keys,group_ids):
    require(actor,'iam.manage')
    for key in role_keys:
        delegation(actor,key)
        if key in BUILTIN:RoleGrant.objects.get_or_create(organization=actor.organization,person=member,role=key)
        else:CustomRoleGrant.objects.update_or_create(organization=actor.organization,person=member,role=role_object(actor,key),defaults={'active':True})
    for group in selected(actor,Group,group_ids):
        group_delegation(actor,group)
        Membership.objects.get_or_create(organization=actor.organization,person=member,group=group)


def apply_new_user(actor,member,data):
    dep=data.get('department_id')
    if dep:
        value=department(actor,dep)
        if not value.active:s.fail('INACTIVE_DEPARTMENT','활성 부서를 선택하십시오.')
        member.department=value;member.save(update_fields=['department'])
        # Department assignment is also a privilege grant, even without explicit copy.
        for row in role_rows(member):
            if row['key']!='EVERYONE':delegation(actor,row['key'])
        for entry in effective_groups(member).values():group_delegation(actor,entry['group'])
    roles=ids(data,'role_keys');groups=ids(data,'group_ids');token=data.get('allocation_token','')
    if roles or groups:
        require(actor,'iam.manage')
        if not token:s.fail('COPY_PREVIEW_REQUIRED','복제 원본을 먼저 조회하십시오.')
    if token:
        try:payload=signing.loads(token,salt='allocation-copy',max_age=600)
        except signing.BadSignature:s.fail('COPY_EXPIRED','복제 조회가 만료되었습니다. 다시 조회하십시오.',409)
        if payload.get('org')!=str(actor.organization_id) or payload.get('actor')!=str(actor.id):s.fail('INVALID_COPY','현재 사용자의 복제 조회가 아닙니다.',403)
        current=source_allocations(actor,payload['kind'],payload['id'])
        if current!=payload['values']:s.fail('COPY_CHANGED','원본 할당 정보가 변경되었습니다. 다시 조회하십시오.',409)
        if not set(roles)<={row['key'] for row in current['roles']} or not set(groups)<={row['id'] for row in current['groups']}:s.fail('INVALID_COPY','조회한 원본의 항목만 복제할 수 있습니다.')
        assign_direct(actor,member,roles,groups)
    return {'department_id':str(member.department_id) if member.department_id else None,'copy_source':{'kind':payload['kind'],'id':payload['id']} if token else None,'role_keys':roles,'group_ids':groups}


def mutate(actor,operation,data,request_id,target):
    require(actor,'iam.manage');require_recent(actor)
    org=Organization.objects.get(pk=actor.organization_id)
    if type(data.get('expected_version')) is not int or data['expected_version']!=org.access_version:s.fail('VERSION_CONFLICT','조직 설정이 변경되었습니다. 새로고침하십시오.',409)
    reason=s.text(data,'reason',500)
    action=operation.removeprefix('manage_org_');obj=org;after={'reason':reason}
    if action=='department':
        s.check_fields(data,['code','name','description','parent_id','active','expected_version','reason'],['code','name','active','expected_version','reason'])
        from .identity_management import code
        value=department(actor,target) if target else Department(organization=org,code=code(data))
        if value.code!=code(data):s.fail('IMMUTABLE_CODE','부서 코드는 변경할 수 없습니다.')
        parent=department(actor,data['parent_id']) if data.get('parent_id') else None
        cursor=parent;seen={value.id}
        while cursor:
            if cursor.id in seen:s.fail('DEPARTMENT_CYCLE','자기 자신 또는 하위 부서로 이동할 수 없습니다.')
            if not cursor.active:s.fail('INACTIVE_PARENT','활성 상위 부서를 선택하십시오.')
            seen.add(cursor.id);cursor=cursor.parent
        if type(data['active']) is not bool:s.fail('INVALID_INPUT','사용 여부를 확인하십시오.')
        if not data['active'] and (Person.objects.filter(department=value).exists() or Department.objects.filter(parent=value,active=True).exists() or ScopedRoleGrant.objects.filter(department=value).exists() or GroupDepartment.objects.filter(department=value).exists()):s.fail('DEPARTMENT_IN_USE','소속 사용자·하위 부서·할당을 먼저 이관하십시오.',409)
        value.parent=parent;value.name=s.text(data,'name',200);value.description=s.text(data,'description',500,False);value.active=data['active'];value.row_version+=1;value.save();obj=value
        if not sysadmin(actor):
            descendants={value.id};pending=[value.id]
            while pending:
                pending=list(Department.objects.filter(organization=org,parent_id__in=pending).values_list('id',flat=True));descendants.update(pending)
            for dep_id in descendants:
                proxy=SimpleNamespace(id=None,department_id=dep_id,organization=org,organization_id=org.id)
                for assignment in role_rows(proxy):
                    if assignment['key']!='EVERYONE':delegation(actor,assignment['key'])
                for entry in effective_groups(proxy).values():group_delegation(actor,entry['group'])
        after.update(code=value.code,parent_id=str(parent.id) if parent else None,active=value.active)
    elif action=='department-delete':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        value=department(actor,target)
        if Person.objects.filter(department=value).exists() or Department.objects.filter(parent=value).exists() or ScopedRoleGrant.objects.filter(department=value).exists() or GroupDepartment.objects.filter(department=value).exists():s.fail('DEPARTMENT_IN_USE','참조가 있는 부서는 삭제할 수 없습니다.',409)
        s.record(actor,value,'DEPARTMENT_DELETED',request_id,after=after);value.delete()
    elif action=='role-targets':
        s.check_fields(data,['person_ids','department_ids','group_ids','include_children','expected_version','reason'],['person_ids','department_ids','group_ids','include_children','expected_version','reason'])
        key=target;delegation(actor,key);role=role_object(actor,key)
        members=selected(actor,Person,ids(data,'person_ids'));deps=selected(actor,Department,ids(data,'department_ids'));groups=selected(actor,Group,ids(data,'group_ids'))
        if type(data['include_children']) is not bool:s.fail('INVALID_INPUT','하위 부서 포함 여부를 확인하십시오.')
        if key=='ORG_ADMIN':
            if deps or groups:s.fail('PROTECTED_ADMIN','시스템 관리자는 사용자에게 직접 배정하십시오.')
            existing=list(RoleGrant.objects.filter(organization=org,role=key).values_list('person_id',flat=True))
            if actor.id in existing and actor.id not in {p.id for p in members}:s.fail('SELF_LOCKOUT','현재 관리자의 시스템 관리자 역할은 이 화면에서 회수할 수 없습니다.',409)
            if not members:s.fail('LAST_ADMIN','시스템 관리자를 최소 한 명 유지하십시오.',409)
        if role:
            CustomRoleGrant.objects.filter(organization=org,role=role).exclude(person__in=members).update(active=False)
            for member in members:CustomRoleGrant.objects.update_or_create(organization=org,role=role,person=member,defaults={'active':True})
        else:
            RoleGrant.objects.filter(organization=org,role=key).exclude(person__in=members).delete()
            for member in members:RoleGrant.objects.get_or_create(organization=org,role=key,person=member)
        ScopedRoleGrant.objects.filter(organization=org,role_key=key).delete()
        for field,rows in [('department',deps),('group',groups)]:
            for value in rows:ScopedRoleGrant.objects.create(organization=org,role_key=key,role=role,include_children=data['include_children'] if field=='department' else False,**{field:value})
        after.update(role_key=key,person_ids=[str(p.id) for p in members],department_ids=[str(d.id) for d in deps],group_ids=[str(g.id) for g in groups],include_children=data['include_children'])
    elif action=='group-targets':
        s.check_fields(data,['person_ids','department_ids','include_children','expected_version','reason'],['person_ids','department_ids','include_children','expected_version','reason'])
        from .identity_management import group
        value=group(actor,target);group_delegation(actor,value)
        members=selected(actor,Person,ids(data,'person_ids'));deps=selected(actor,Department,ids(data,'department_ids'))
        if type(data['include_children']) is not bool:s.fail('INVALID_INPUT','하위 부서 포함 여부를 확인하십시오.')
        # Do not strand assigned work when removing inherited or direct members.
        for ticket in Ticket.objects.filter(organization=org,group=value).exclude(status__in=['CLOSED','REJECTED','CANCELLED','RESOLVED']).exclude(assignee__isnull=True):
            if ticket.assignee_id not in {p.id for p in members}:
                candidate=ticket.assignee;old=candidate.department_id
                included=False
                from .access_graph import chain
                for index,dep in enumerate(chain(candidate)):
                    if dep.id in {d.id for d in deps} and (index==0 or data['include_children']):included=True
                if not included:s.fail('OPEN_ASSIGNMENTS','진행 업무의 담당자를 먼저 이관하십시오.',409)
        Membership.objects.filter(organization=org,group=value).exclude(person__in=members).delete()
        for member in members:Membership.objects.get_or_create(organization=org,group=value,person=member)
        GroupDepartment.objects.filter(organization=org,group=value).delete()
        for dep in deps:GroupDepartment.objects.create(organization=org,group=value,department=dep,include_children=data['include_children'])
        value.row_version+=1;value.save(update_fields=['row_version']);obj=value
        after.update(person_ids=[str(p.id) for p in members],department_ids=[str(d.id) for d in deps],include_children=data['include_children'])
    elif action=='menus':
        s.check_fields(data,['menu_keys','console_button','data_scopes','expected_version','reason'],['menu_keys','console_button','expected_version','reason'])
        key=target;role=role_object(actor,key)
        if key!='EVERYONE':delegation(actor,key)
        keys=ids(data,'menu_keys')
        if any(key not in MENUS for key in keys) or type(data['console_button']) is not bool:s.fail('INVALID_MENUS','허용된 메뉴와 버튼을 선택하십시오.')
        caps={MENUS[k][3] for k in keys if MENUS[k][3]}|({'console.access'} if data['console_button'] else set())
        if key=='EVERYONE' and (data['console_button'] or caps-{'workflow.use'}):s.fail('PUBLIC_PRIVILEGE','기본 사용자 역할에는 공통 조회 메뉴만 허용됩니다.')
        if not sysadmin(actor) and not caps<=effective(actor):s.fail('CANNOT_DELEGATE','자신에게 없는 메뉴 권한을 부여할 수 없습니다.',403)
        if key=='ORG_ADMIN' and (not PROTECTED<=set(keys) or not data['console_button']):s.fail('ADMIN_RECOVERY','시스템 관리자의 사용자·권한·보안 메뉴와 콘솔 접근은 유지하십시오.',409)
        from .models import RoleDataPolicy
        from .data_access import SUPPORTED,SCOPES
        scopes=data.get('data_scopes',{})
        if not isinstance(scopes,dict) or set(scopes)-SUPPORTED:s.fail('INVALID_SCOPE','지원하지 않는 데이터 범위입니다.')
        for menu,rule in scopes.items():
            if not isinstance(rule,dict) or set(rule)!={'read','write'} or any(v not in SCOPES for v in rule.values()):s.fail('INVALID_SCOPE','조회·수정 범위를 확인하십시오.')
            RoleDataPolicy.objects.update_or_create(organization=org,role_key=key,menu_key=menu,defaults={'role':role,'read_scope':rule['read'],'write_scope':rule['write']})
        value,_=RoleMenuPolicy.objects.update_or_create(organization=org,role_key=key,defaults={'role':role,'menu_keys':keys,'console_button':data['console_button']})
        value.row_version+=1;value.save(update_fields=['row_version']);obj=value;after.update(role_key=key,menu_keys=keys,console_button=data['console_button'],data_scopes=scopes)
    else:s.fail('INVALID_OPERATION','지원하지 않는 조직 작업입니다.')
    org.access_version+=1;org.save(update_fields=['access_version'])
    if action!='department-delete':s.record(actor,obj,'ORGANIZATION_'+action.upper().replace('-','_'),request_id,after=after)
    return {'id':str(obj.id),'version':org.access_version},200
