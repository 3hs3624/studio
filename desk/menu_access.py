from .access_cache import cached
"""One route catalogue drives menu visibility and direct page/API checks."""
# key: label, UI prefixes, API prefixes, read capability. Empty capability is self-service.
MENUS={
 'integrations':('콘솔 · API·데이터 연계',('/console/integrations',),('/api/v1/integrations',),'integration.manage'),
 'screens':('콘솔 · 화면 관리',('/console/screens',),(),'workflow.manage'),
 'workflow-admin':('콘솔 · 워크플로우 관리',('/console/workflows',),('/api/v1/processes',),'workflow.manage'),
 'approval-lines':('콘솔 · 결재선 관리',('/console/approval-lines',),(),'workflow.manage'),
 'workflow-inbox':('워크플로우 업무·결재',('/processes',),('/api/v1/process-runs',),'workflow.use'),
 'service':('IT서비스 현황',('/systems/service',),(),''),
 'catalog':('서비스 카탈로그',('/catalog',),('/api/v1/catalog/items',),''),
 'requests':('내 서비스 요청',('/portal/requests',),('/api/v1/requests',),''),
 'incidents':('내 장애 요청',('/portal/incidents',),('/api/v1/incidents',),''),
 'approvals':('서비스 승인함',('/approvals',),(),''),
 'work-incidents':('장애 처리',('/work/incidents',),(),'service.work'),
 'work-requests':('서비스 요청 처리',('/work/requests',),(),'service.work'),
 'ci':('구성항목 대장',('/cis',),('/api/v1/cis',),''),
 'asset-home':('IT자산 현황',('/systems/asset',),(),''),
 'assets':('자산 대장',('/assets',),('/api/v1/assets',),''),
 'my-assets':('내 지급 자산',('/my-assets',),('/api/v1/my-assets',),''),
 'procurement':('구매 요청·발주·계약',('/procurement','/contracts'),('/api/v1/procurement','/api/v1/contracts'),'procurement.manage'),
 'inventory':('창고·재고',('/inventory',),('/api/v1/inventory',),'inventory.manage'),
 'resource-home':('IT자원 현황',('/systems/resource',),(),''),
 'source':('소스 변경 목록',('/resources/changes',),(),'delivery.read'),
 'deployments':('배포 목록',('/resources/deployments',),(),'delivery.read'),
 'notifications':('알림함',('/notifications',),('/api/v1/notifications',),''),
 'entities':('콘솔 · 엔티티',('/console/entities','/admin/entities'),('/api/v1/admin/entities',),'entity.read'),
 'plugins':('콘솔 · 플러그인',('/console/plugins','/admin/plugins'),('/api/v1/admin/plugins','/api/v1/admin/plugin-runs'),'plugin.read'),
 'codes':('콘솔 · 공통코드',('/console/codes',),('/api/v1/admin/code-groups',),'code.read'),
 'users':('콘솔 · 사용자 관리',('/console/users',),(),'users.manage'),
 'access':('콘솔 · 조직·권한',('/console/access','/console/roles','/console/groups','/admin/access'),('/api/v1/organization-access','/api/v1/admin/persons','/api/v1/admin/groups'),'iam.manage'),
 'security':('콘솔 · 보안 관리',('/console/security',),(),'security.manage'),
 'catalog-admin':('콘솔 · 카탈로그 설정',('/console/catalog','/work/catalog'),('/api/v1/catalog/versions',),'service.manage'),
 'sla':('콘솔 · SLA 설정',('/console/sla','/work/sla','/console/slm'),('/api/v1/sla','/api/v1/timeliness'),'service.manage'),
}
PUBLIC={'workflow-inbox','service','catalog','requests','incidents','approvals','asset-home','my-assets','resource-home','notifications','assets','ci'}
PROTECTED={'access','users','security'}


def match(path):
    if path.startswith('/api/v1/admin/persons/') and path.endswith(('/account','/revoke-sessions')):return 'users'
    matches=[]
    for key,(_,pages,apis,_) in MENUS.items():
        for prefix in pages+apis:
            if path==prefix or path.startswith(prefix+'/'):matches.append((len(prefix),key))
    if path.startswith('/api/v1/management/'):
        kind=path.split('/')[4]
        return 'users' if kind.startswith('user') else 'security' if kind.startswith('polic') else 'access'
    return max(matches)[1] if matches else None


@cached('role_menus')
def role_menus(organization,key):
    from .models import RoleMenuPolicy
    from .access_graph import role_capabilities
    saved=RoleMenuPolicy.objects.filter(organization=organization,role_key=key).first()
    if saved:return set(saved.menu_keys),saved.console_button
    if key=='EVERYONE':return set(PUBLIC),False
    caps=role_capabilities(organization,key)
    return {key for key,(_,_,_,cap) in MENUS.items() if cap and (cap in caps or (cap=='service.work' and 'service.manage' in caps) or (key=='procurement' and bool(caps&{'inventory.manage','service.manage','asset.manage'})) or (key=='inventory' and 'procurement.manage' in caps))},'console.access' in caps


@cached('menu_keys')
def menu_keys(person):
    from .access_graph import role_rows
    value=set()
    for role in role_rows(person):value.update(role_menus(person.organization,role['key'])[0])
    # Recovery access cannot be removed from a directly assigned system administrator.
    if person.rolegrant_set.filter(role='ORG_ADMIN').exists():value.update(PROTECTED)
    return value


@cached('console_access')
def console_access(person):
    from .access_graph import role_rows
    return any(role_menus(person.organization,row['key'])[1] for row in role_rows(person))


def path_allowed(person,path):
    key=match(path)
    if key in {'sla','catalog-admin'} and path.startswith('/api/'):
        from .models import RoleMenuPolicy
        from .access_graph import role_rows
        if not RoleMenuPolicy.objects.filter(organization=person.organization,role_key__in=[r['key'] for r in role_rows(person)]).exists():return True
    if (key in {'integrations','screens','workflow-admin','approval-lines','entities','plugins','codes','users','access','security','catalog-admin','sla'} or path=='/console' or path.startswith(('/console/','/admin/','/work/catalog','/work/sla'))) and not console_access(person):return False
    if not key or key in menu_keys(person):return True
    if path.startswith('/api/'):
        from .models import RoleMenuPolicy
        from .access_graph import role_rows
        if not RoleMenuPolicy.objects.filter(organization=person.organization,role_key__in=[r['key'] for r in role_rows(person)]).exists():return True
    return False


@cached('mapped_capabilities')
def mapped_capabilities(organization,key):
    from .models import RoleMenuPolicy
    saved=RoleMenuPolicy.objects.filter(organization=organization,role_key=key).first()
    if not saved:return set()
    return {MENUS[menu][3] for menu in saved.menu_keys if menu in MENUS and MENUS[menu][3]}|({'console.access'} if saved.console_button else set())
