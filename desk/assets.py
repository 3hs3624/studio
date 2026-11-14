"""Asset ownership lifecycle; all commands run inside services.execute's transaction."""
from django.db.models import Q
from django.utils import timezone
from . import services as s
from .models import Asset, AssetCustody, AssetHistory, Person, TicketResource

def manager(p):
    return 'ASSET_MANAGER' in s.roles(p)

def full_reader(p):
    return s.has_permission(p,'asset.read') or manager(p)

def require_manager(p):
    if not manager(p):
        s.fail('FORBIDDEN','자산 관리자 권한이 필요합니다.',403)

def query(p):
    qs=Asset.objects.filter(organization=p.organization).select_related('custodian','stock_record')
    from .data_access import restrict
    return restrict(p,'assets',qs if full_reader(p) else qs.filter(Q(portal_visible=True)|Q(custodian=p)),'custodian')

def get_asset(p,ident,lock=False):
    qs=Asset.objects.filter(organization=p.organization)
    if lock:
        qs=qs.select_for_update()
    obj=qs.filter(id=ident).first()
    if not obj or not query(p).filter(id=ident).exists():
        s.fail('NOT_FOUND','자산을 찾을 수 없습니다.',404)
    return obj

def actions(a):
    if a.status=='RETIRED':
        return []
    return {'UNVERIFIED':['VERIFY','MOVE'],'STOCK':['ISSUE','MOVE','RETIRE'],'IN_USE':['RETURN','MOVE']}[a.status]

def data(a,p=None):
    detail=bool(p and (full_reader(p) or a.custodian_id==p.id))
    result={'id':str(a.id),'asset_no':a.asset_no,'name':a.name,'model':a.model,'location':a.location,
            'status':a.status,'version':a.row_version}
    if detail:
        result.update(manufacturer=a.manufacturer,serial_number=a.serial_number,
            custodian=s.person_data(a.custodian) if a.custodian else None)
    if p and manager(p):
        result.update(portal_visible=a.portal_visible,allowed_actions=actions(a),can_update=a.status!='RETIRED')
        from .models import StockAsset
        try: row=a.stock_record
        except StockAsset.DoesNotExist: row=None
        if row:
            result['warehouse_managed']=True
            if 'STOCK_MANAGER' not in s.roles(p):
                result['allowed_actions']=[x for x in result['allowed_actions'] if x not in ['ISSUE','RETURN','RETIRE']]
            if row.stockroom_id:
                result['allowed_actions']=[x for x in result['allowed_actions'] if x!='MOVE']
    return result

def snapshot(a):
    return {'id':str(a.id),'asset_no':a.asset_no,'name':a.name,'manufacturer':a.manufacturer,'model':a.model,
        'serial_number':a.serial_number,'location':a.location,'status':a.status,
        'custodian':s.person_data(a.custodian) if a.custodian else None,'portal_visible':a.portal_visible,'version':a.row_version}

def history_query(p,ident=None,personal=False):
    qs=AssetHistory.objects.filter(organization=p.organization).select_related('asset','actor','custody','request')
    if ident:
        qs=qs.filter(asset_id=ident)
    if personal or not full_reader(p):
        qs=qs.filter(custody__person=p,kind__in=['ISSUE','RETURN'])
    return qs

def history_data(h,p,personal=False):
    result={'id':str(h.id),'asset_id':str(h.asset_id),'asset_no':h.after_data['asset_no'],
            'asset_name':h.after_data['name'],'kind':h.kind,'created_at':h.created_at.isoformat()}
    if full_reader(p) and not personal:
        result.update(actor=s.person_data(h.actor),reason=h.reason,before=h.before_data,after=h.after_data)
    if h.request_id:
        from .catalog import request_query
        if request_query(p).filter(id=h.request_id).exists():
            result['request']={'id':str(h.request_id),'number':h.request.number,'title':h.request.title}
    return result

def authorize(p,op,target):
    require_manager(p)
    if op!='asset_create':
        obj=get_asset(p,target,True)
        from .data_access import can_write
        if not can_write(p,'assets',obj,'custodian'):s.fail('FORBIDDEN','이 자산의 변경 범위를 벗어났습니다.',403)

def replay(p,op,payload,result):
    a=get_asset(p,s.identifier(result['id']))
    current=data(a,p)
    result.update(allowed_actions=current.get('allowed_actions',[]),can_update=a.status!='RETIRED')
    if payload.get('service_request_id'):
        from .catalog import get_request
        get_request(p,s.identifier(payload['service_request_id']))
    return result

def related_request(p,raw,person,expected=None):
    if not raw:
        return None
    from .catalog import get_request,request_staff
    t=get_request(p,s.identifier(raw),True)
    if not request_staff(p,t):
        s.fail('FORBIDDEN','연결할 서비스 요청의 처리 권한이 필요합니다.',403)
    if t.status!='IN_PROGRESS' or t.requested_by_id!=person.id:
        s.fail('INVALID_ASSET_REQUEST','처리 중인 서비스 요청과 자산 수령자가 일치해야 합니다.')
    s.version(t,{'expected_version':expected})
    return t

def log(p,a,kind,reason,request_id,before=None,custody=None,ticket=None):
    after=snapshot(a)
    event=AssetHistory.objects.create(organization=p.organization,asset=a,actor=p,kind=kind,reason=reason,
        before_data=before or {},after_data=after,custody=custody,request=ticket)
    s.record(p,a,'ASSET_'+kind,request_id,before or {},after)
    return event

def validate_identity(manufacturer,serial):
    if serial and not manufacturer:
        s.fail('INVALID_SERIAL','일련번호를 입력할 때는 제조사도 입력하십시오.')

def mutate(p,op,payload,request_id,target):
    if op=='asset_create':
        allowed=['asset_no','name','manufacturer','model','serial_number','location','portal_visible','reason']
        s.check_fields(payload,allowed,['asset_no','name','model','location','portal_visible','reason'])
        if type(payload['portal_visible']) is not bool:
            s.fail('INVALID_VISIBILITY','공개 여부는 boolean이어야 합니다.')
        manufacturer=s.text(payload,'manufacturer',200,False)
        serial=s.text(payload,'serial_number',200,False)
        validate_identity(manufacturer,serial)
        a=Asset.objects.create(organization=p.organization,asset_no=s.text(payload,'asset_no',80),name=s.text(payload,'name',200),
            manufacturer=manufacturer,model=s.text(payload,'model',200,False),serial_number=serial,
            location=s.text(payload,'location',200),portal_visible=payload['portal_visible'],status='STOCK')
        log(p,a,'REGISTER',s.text(payload,'reason'),request_id)
        return data(a,p),201

    a=get_asset(p,target,True)
    before=snapshot(a)
    if op=='asset_update':
        allowed=['name','manufacturer','model','serial_number','portal_visible','reason','expected_version']
        s.check_fields(payload,allowed,allowed)
        s.version(a,payload)
        if a.status=='RETIRED':
            s.fail('INVALID_STATE','폐기 처리한 자산은 수정할 수 없습니다.',409)
        if type(payload['portal_visible']) is not bool:
            s.fail('INVALID_VISIBILITY','공개 여부는 boolean이어야 합니다.')
        manufacturer=s.text(payload,'manufacturer',200,False)
        serial=s.text(payload,'serial_number',200,False)
        validate_identity(manufacturer,serial)
        if a.status=='IN_USE' and (manufacturer!=a.manufacturer or serial!=a.serial_number):
            s.fail('IDENTITY_LOCKED','제조사·일련번호 정정은 반납 후에 진행하십시오.',409)
        a.name=s.text(payload,'name',200);a.model=s.text(payload,'model',200,False)
        a.manufacturer=manufacturer;a.serial_number=serial;a.portal_visible=payload['portal_visible']
        s.bump(a)
        log(p,a,'UPDATE',s.text(payload,'reason'),request_id,before)
        return data(a,p),200

    s.check_fields(payload,['action','person_id','location','reason','expected_version','service_request_id','expected_request_version','stockroom_id'],
                   ['action','reason','expected_version'])
    s.version(a,payload)
    action=payload['action']
    if not isinstance(action,str) or action not in ['VERIFY','ISSUE','RETURN','MOVE','RETIRE']:
        s.fail('INVALID_ACTION','지원하지 않는 자산 동작입니다.')
    if action not in actions(a):
        s.fail('INVALID_STATE','현재 자산 상태에서 실행할 수 없습니다.',409)
    extra={'ISSUE':['person_id','location','service_request_id','expected_request_version'],
           'RETURN':['location','service_request_id','expected_request_version','stockroom_id'],
           'MOVE':['location'],'VERIFY':['location'],'RETIRE':[]}[action]
    s.check_fields(payload,['action','reason','expected_version']+extra)
    if payload.get('service_request_id') is not None:
        s.identifier(payload['service_request_id'])
    if 'expected_request_version' in payload and not payload.get('service_request_id'):
        s.fail('INVALID_INPUT','서비스 요청 없이 요청 버전을 지정할 수 없습니다.')
    active_custody=AssetCustody.objects.select_for_update().filter(asset=a,returned_at__isnull=True).first()
    if ((a.status=='IN_USE' and (not active_custody or active_custody.person_id!=a.custodian_id))
            or (a.status!='IN_USE' and active_custody)):
        s.fail('INVALID_CUSTODY','자산 상태와 현재 지급 기록이 일치하지 않습니다.',409)
    reason=s.text(payload,'reason')
    custody=None;ticket=None
    if action=='ISSUE':
        person=Person.objects.filter(id=s.identifier(payload.get('person_id')),organization=p.organization,
                                     active=True,user__is_active=True).first()
        if not person:
            s.fail('INVALID_RECIPIENT','같은 조직의 활성 수령자를 선택하십시오.')
        if active_custody:
            s.fail('ASSET_ALREADY_ISSUED','이미 지급된 자산입니다.',409)
        ticket=related_request(p,payload.get('service_request_id'),person,payload.get('expected_request_version'))
        a.location=s.text(payload,'location',200)
        a.status='IN_USE';a.custodian=person
        custody=AssetCustody.objects.create(organization=p.organization,asset=a,person=person,issued_by=p,
            issue_request=ticket,issue_location=a.location,issue_reason=reason)
        if ticket:
            TicketResource.objects.get_or_create(organization=p.organization,ticket=ticket,asset=a)
    elif action=='RETURN':
        custody=active_custody
        if not custody or custody.person_id!=a.custodian_id:
            s.fail('INVALID_CUSTODY','현재 지급 기록을 확인하십시오.',409)
        ticket=related_request(p,payload.get('service_request_id'),custody.person,payload.get('expected_request_version')) if payload.get('service_request_id') else custody.issue_request
        a.location=s.text(payload,'location',200)
        moment=timezone.now()
        if moment<custody.created_at:
            s.fail('INVALID_CUSTODY_TIME','반납 시각은 지급 시각보다 이전일 수 없습니다.',409)
        custody.returned_at=moment;custody.returned_by=p
        custody.return_location=a.location;custody.return_reason=reason
        a.status='STOCK';a.custodian=None
    elif action in ('MOVE','VERIFY'):
        if payload.get('person_id') or payload.get('service_request_id'):
            s.fail('INVALID_INPUT','이 동작에는 수령자·서비스 요청을 지정할 수 없습니다.')
        a.location=s.text(payload,'location',200)
        if action=='VERIFY':
            a.status='STOCK'
    elif action=='RETIRE':
        if payload.get('person_id') or payload.get('service_request_id'):
            s.fail('INVALID_INPUT','이 동작에는 수령자·서비스 요청을 지정할 수 없습니다.')
        a.status='RETIRED'
    from .procurement import synchronize_asset
    synchronize_asset(p,a,action,payload,ticket)
    if action=='RETURN':
        custody.return_location=a.location
        custody.save()
    s.bump(a)
    if payload.get('service_request_id'):
        TicketResource.objects.get_or_create(organization=p.organization,ticket=ticket,asset=a)
        previous_version=ticket.row_version
        s.bump(ticket)
        s.record(p,ticket,'ASSET_'+action+'_LINKED',request_id,{'version':previous_version},
                 {'version':ticket.row_version,'asset_id':str(a.id)})
    log(p,a,action,reason,request_id,before,custody,ticket)
    return data(a,p),200

def request_asset_events(p,t):
    events=AssetHistory.objects.filter(organization=p.organization,request=t,kind__in=['ISSUE','RETURN']).order_by('created_at')
    visible=query(p)
    return [{'asset_id':str(h.asset_id),'asset_no':h.after_data['asset_no'],'name':h.after_data['name'],
             'action':h.kind,'created_at':h.created_at.isoformat(),'can_view':visible.filter(id=h.asset_id).exists()} for h in events]
