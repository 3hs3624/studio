"""Three application areas sharing identity and organization boundaries."""
SYSTEMS = [
    {'key':'service','name':'IT서비스','code':'ITSM','url':'/systems/service','description':'요청부터 승인, 장애 해결과 서비스 품질까지','icon':'01'},
    {'key':'asset','name':'IT자산','code':'ITAM','url':'/systems/asset','description':'구매부터 입고, 지급과 반납, 폐기까지','icon':'02'},
    {'key':'resource','name':'IT자원','code':'ITRM','url':'/systems/resource','description':'소스 형상과 빌드·배포 현황 관리','icon':'03'},
]


def navigation(path, c):
    key = 'portal'
    if path.startswith(('/systems/service','/portal/','/work/','/catalog','/approvals','/cis')): key='service'
    elif path.startswith(('/systems/asset','/assets','/my-assets','/procurement','/inventory','/contracts')): key='asset'
    elif path.startswith(('/systems/resource','/resources/')): key='resource'
    elif path.startswith('/admin/'): key='admin'
    elif path.startswith('/processes'): key='service'
    elif path.startswith('/notifications'): key='notifications'
    groups=[]
    def group(title, rows):
        links=[{'label':label,'url':url,'active':path==url or (url not in ['/systems/service','/systems/asset','/systems/resource'] and path.startswith(url+'/'))} for label,url,visible in rows if visible]
        if links: groups.append({'title':title,'links':links})
    if key=='service':
        group('서비스 이용', [('서비스 현황','/systems/service',True),('서비스 카탈로그','/catalog',True),('내 서비스 요청','/portal/requests',True),('내 장애 요청','/portal/incidents',True),('서비스 승인함','/approvals',True),('워크플로우 업무·결재','/processes',True)])
        group('서비스 운영',[('장애 처리','/work/incidents',c['can_work']),('서비스 요청 처리','/work/requests',c['can_work'])])
        group('구성 관리',[('구성항목 대장','/cis',True)])
    elif key=='asset':
        group('자산 관리',[('자산 현황','/systems/asset',True),('자산 대장','/assets',True),('내 지급 자산','/my-assets',True)])
        group('구매 · 계약',[('구매 요청 · 승인','/procurement/requisitions',c['can_purchase_request']),('발주 · 입고','/procurement/orders',c['can_stock_read']),('공급업체 · 계약','/contracts',c['can_contract_read'])])
        group('재고 관리',[('창고 · 재고','/inventory',c['can_stock_read']),('재고 이동 이력','/inventory/movements',c['can_stock_read'])])
    elif key=='resource':
        group('소스 · 배포 관리',[('자원 현황','/systems/resource',True),('소스 변경 목록','/resources/changes',c.get('delivery_can_read',False)),('배포 목록','/resources/deployments',c.get('delivery_can_read',False))])
    else:
        group('나의 업무',[('내 서비스 요청','/portal/requests',True),('서비스 승인함','/approvals',True),('워크플로우 업무·결재','/processes',True),('내 지급 자산','/my-assets',True)])
    all_links=[link for section in groups for link in section['links']]
    active=[link for link in all_links if link['active']]
    if active:
        longest=max(len(link['url']) for link in active)
        for link in active: link['active']=len(link['url'])==longest
    common=[{'label':'알림함','url':'/notifications','active':key=='notifications'}]
    system=next((s for s in SYSTEMS if s['key']==key),None)
    from .menu_access import path_allowed
    for section in groups:section['links']=[link for link in section['links'] if path_allowed(c['actor'],link['url'])]
    groups=[section for section in groups if section['links']]
    common=[link for link in common if path_allowed(c['actor'],link['url'])]
    return {'systems':[system for system in SYSTEMS if path_allowed(c['actor'],system['url'])],'active_area':key,'active_system':system,'area_name':system['name'] if system else {'admin':'통합 관리','notifications':'공통 알림'}.get(key,'통합 포털'),'nav_groups':groups,'common_links':common}


LEGACY_CONSOLE_PATHS = ('/admin/', '/work/catalog', '/work/sla')


def console_navigation(path, context):
    groups = []
    from .permissions import allowed
    actor=context['actor']
    can_configure=allowed(actor,'console.access')
    rows = [
        ('업무 구성', [('화면 관리','/console/screens',allowed(actor,'workflow.manage')),('워크플로우 관리','/console/workflows',allowed(actor,'workflow.manage')),('결재선 관리','/console/approval-lines',allowed(actor,'workflow.manage')),('엔티티 관리', '/console/entities', allowed(actor,'entity.read')),
                     ('서비스 카탈로그', '/console/catalog', context['is_service_manager'])]),
        ('플랫폼 운영', [('API · 데이터 연계','/console/integrations',allowed(actor,'integration.manage')),('플러그인 관리', '/console/plugins', allowed(actor,'plugin.read'))]),
        ('서비스 기준', [('SLA · 업무 달력', '/console/sla', context['is_service_manager']),('SLM · 적기처리율','/console/slm',context['is_service_manager'])]),
        ('시스템 관리', [('사용자 관리','/console/users',allowed(actor,'users.manage')),
                     ('조직 · 권한 관리', '/console/access', allowed(actor,'iam.manage')),
                     ('역할 관리','/console/access?tab=roles',allowed(actor,'iam.manage')),
                     ('그룹 관리','/console/access?tab=groups',allowed(actor,'iam.manage')),
                     ('보안 관리','/console/security',allowed(actor,'security.manage')),
                     ('공통코드 관리', '/console/codes', allowed(actor,'code.read'))]),
    ]
    canonical = path
    for old, new in [('/admin/entities','/console/entities'),('/admin/plugins','/console/plugins'),
                     ('/admin/access','/console/access'),('/work/catalog','/console/catalog'),('/work/sla','/console/sla')]:
        if path == old or path.startswith(old+'/'):
            canonical = new + path[len(old):]
            break
    for title, links in rows:
        visible = [dict(label=label, url=url, active=canonical==url or canonical.startswith(url+'/'))
                   for label,url,allowed in links if allowed and __import__('desk.menu_access',fromlist=['path_allowed']).path_allowed(actor,url)]
        if visible:
            groups.append({'title':title,'links':visible})
    return groups
