"""Fixed capability catalogue; operators compose roles, never executable rules."""
PERMISSIONS = {
 'console.access':('운영 콘솔 접근','조직'),
 'entity.read':('엔티티 조회','조직'),'entity.write':('엔티티 구성·게시·데이터 등록','조직'),
 'plugin.read':('플러그인 조회','조직'),'plugin.configure':('플러그인 설정','조직'),'plugin.execute':('플러그인 실행·번호 발급','조직'),
 'code.read':('공통코드 조회','조직'),'code.write':('공통코드 구성','조직'),
 'asset.read':('자산 전체 조회','조직'),'asset.manage':('자산 등록·변경','조직'),
 'resource.read':('구성항목 전체 조회','조직'),
 'service.work':('소속 그룹 업무 처리','그룹·담당 건'),'service.manage':('서비스 운영 관리','조직'),
 'procurement.manage':('구매 관리','조직'),'inventory.manage':('재고 관리','조직'),
 'users.manage':('사용자·개인정보 관리','조직'),'iam.manage':('역할·그룹 관리','조직'),'security.manage':('보안 정책 관리','조직'),
}
CORE = {'console.access','entity.read','entity.write','plugin.read','plugin.configure','plugin.execute','code.read','code.write'}
BUILTIN = {
 'ORG_ADMIN': CORE | {'users.manage','iam.manage','security.manage'},
 'DEVELOPER': CORE, 'SOLUTION_OPERATOR': CORE,
 'SERVICE_MANAGER': {'service.manage'}, 'AGENT': {'service.work'},
 'RESOURCE_READER': {'asset.read','resource.read'}, 'ASSET_MANAGER': {'asset.read','asset.manage'},
 'PROCUREMENT_MANAGER': {'procurement.manage'}, 'STOCK_MANAGER': {'inventory.manage'},
}
ALIASES = {'service.manage':'SERVICE_MANAGER','service.work':'AGENT','asset.manage':'ASSET_MANAGER',
           'asset.read':'ASSET_READER','resource.read':'CI_READER','procurement.manage':'PROCUREMENT_MANAGER','inventory.manage':'STOCK_MANAGER'}


def custom_grants(person):
    from .models import CustomRoleGrant
    return CustomRoleGrant.objects.filter(person=person,organization_id=person.organization_id,active=True,role__active=True)


def effective(person):
    from .models import RoleGrant
    value=set()
    for role in RoleGrant.objects.filter(person=person,organization_id=person.organization_id).values_list('role',flat=True):
        value.update(BUILTIN.get(role,set()))
    for grant in custom_grants(person).select_related('role'):
        value.update(grant.role.permissions)
    return value


def allowed(person, permission):
    return permission in effective(person)


def require(person, permission):
    if not allowed(person,permission):
        from .services import fail
        fail('FORBIDDEN','해당 기능에 대한 권한이 없습니다.',403)


def people_with(organization,permission):
    from django.db.models import Q
    from .models import Person,RoleDefinition
    builtins=[code for code,values in BUILTIN.items() if permission in values]
    custom=[role.id for role in RoleDefinition.objects.filter(organization=organization,active=True) if permission in role.permissions]
    return Person.objects.filter(organization=organization,active=True,user__is_active=True).filter(
        Q(rolegrant__role__in=builtins)|Q(customrolegrant__active=True,customrolegrant__role_id__in=custom)).distinct()
