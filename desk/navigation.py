"""Three application areas sharing identity and organization boundaries."""
SYSTEMS = [
    {'key':'service','name':'IT서비스','code':'ITSM','url':'/systems/service','description':'요청부터 승인, 장애 해결과 서비스 품질까지','icon':'01'},
    {'key':'asset','name':'IT자산','code':'ITAM','url':'/systems/asset','description':'구매부터 입고, 지급과 반납, 폐기까지','icon':'02'},
    {'key':'resource','name':'IT자원','code':'ITRM','url':'/systems/resource','description':'구성항목과 서비스에 연결된 운영 자원','icon':'03'},
]


def navigation(path, c):
    key = 'portal'
    if path.startswith(('/systems/service','/portal/','/work/','/catalog','/approvals')): key='service'
    elif path.startswith(('/systems/asset','/assets','/my-assets','/procurement','/inventory','/contracts')): key='asset'
    elif path.startswith(('/systems/resource','/cis')): key='resource'
    elif path.startswith('/admin/'): key='admin'
    elif path.startswith('/notifications'): key='notifications'
    groups=[]
    def group(title, rows):
        links=[{'label':label,'url':url,'active':path==url or (url not in ['/systems/service','/systems/asset','/systems/resource'] and path.startswith(url+'/'))} for label,url,visible in rows if visible]
        if links: groups.append({'title':title,'links':links})
    if key=='service':
        group('서비스 이용', [('서비스 현황','/systems/service',True),('서비스 카탈로그','/catalog',True),('내 서비스 요청','/portal/requests',True),('내 장애 요청','/portal/incidents',True),('서비스 승인함','/approvals',True)])
        group('서비스 운영',[('장애 처리','/work/incidents',c['can_work']),('서비스 요청 처리','/work/requests',c['can_work'])])
        group('서비스 설정',[('카탈로그 관리','/work/catalog',c['is_service_manager']),('SLA · 업무 달력','/work/sla',c['is_service_manager'])])
    elif key=='asset':
        group('자산 관리',[('자산 현황','/systems/asset',True),('자산 대장','/assets',True),('내 지급 자산','/my-assets',True)])
        group('구매 · 계약',[('구매 요청 · 승인','/procurement/requisitions',c['can_purchase_request']),('발주 · 입고','/procurement/orders',c['can_stock_read']),('공급업체 · 계약','/contracts',c['can_contract_read'])])
        group('재고 관리',[('창고 · 재고','/inventory',c['can_stock_read']),('재고 이동 이력','/inventory/movements',c['can_stock_read'])])
    elif key=='resource':
        group('구성 관리',[('자원 현황','/systems/resource',True),('구성항목 대장','/cis',True)])
    else:
        group('나의 업무',[('내 서비스 요청','/portal/requests',True),('서비스 승인함','/approvals',True),('내 지급 자산','/my-assets',True)])
    all_links=[link for section in groups for link in section['links']]
    active=[link for link in all_links if link['active']]
    if active:
        longest=max(len(link['url']) for link in active)
        for link in active: link['active']=len(link['url'])==longest
    common=[{'label':'알림함','url':'/notifications','active':key=='notifications'}]
    if c['is_admin']: common.append({'label':'조직 · 권한 관리','url':'/admin/access','active':key=='admin'})
    system=next((s for s in SYSTEMS if s['key']==key),None)
    return {'systems':SYSTEMS,'active_area':key,'active_system':system,'area_name':system['name'] if system else {'admin':'통합 관리','notifications':'공통 알림'}.get(key,'통합 포털'),'nav_groups':groups,'common_links':common}
