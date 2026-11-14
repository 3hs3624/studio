"""Purchasing and warehouse transactions; no external supplier communication."""
import re
import uuid
from datetime import date
from decimal import Decimal
from django.db.models import Q, Sum
from django.utils import timezone
from . import services as s
from .models import (Supplier, Contract, Stockroom, StockItem, StockBalance, PurchaseRequisition,
    PurchaseDecision, PurchaseOrder, GoodsReceipt, StockAsset, StockMovement, AssetContractLink,
    Person, RoleGrant, Asset)

CURRENCIES=['KRW','USD','EUR']
MAX_MONEY=Decimal('99999999999999.99')

def has(p,role): return role in s.roles(p)
def buyer(p): return has(p,'PROCUREMENT_MANAGER')
def stock_manager(p): return has(p,'STOCK_MANAGER')
def require(p,role):
    if not has(p,role): s.fail('FORBIDDEN','해당 구매·재고 업무 권한이 필요합니다.',403)

def quantity(raw,maximum=1_000_000):
    if type(raw) is not int or not 1<=raw<=maximum: s.fail('INVALID_QUANTITY','수량은 허용 범위의 양의 정수여야 합니다.')
    return raw

def currency(raw):
    if raw not in CURRENCIES: s.fail('INVALID_CURRENCY','지원 통화는 KRW, USD, EUR입니다.')
    return raw

def money(raw,unit):
    if not isinstance(raw,str) or not re.fullmatch(r'\d{1,14}(\.\d{1,2})?',raw):
        s.fail('INVALID_MONEY','금액은 소수 둘째 자리 이내의 양수 문자열이어야 합니다.')
    value=Decimal(raw)
    if value<=0 or value>MAX_MONEY or (unit=='KRW' and value!=value.to_integral_value()):
        s.fail('INVALID_MONEY','금액 범위와 통화별 소수 자릿수를 확인하십시오.')
    return value.quantize(Decimal('.01'))

def day(raw):
    try:
        if not isinstance(raw,str) or date.fromisoformat(raw).isoformat()!=raw: raise ValueError()
        return date.fromisoformat(raw)
    except ValueError: s.fail('INVALID_DATE','날짜는 YYYY-MM-DD 형식이어야 합니다.')

def get(model,p,raw):
    obj=model.objects.filter(organization=p.organization,id=s.identifier(raw)).first()
    if not obj: s.fail('NOT_FOUND','대상을 찾을 수 없습니다.',404)
    return obj

def request_query(p):
    qs=PurchaseRequisition.objects.filter(organization=p.organization).select_related('item','requester','approver')
    return qs if buyer(p) else qs.filter(requester=p)

def get_request(p,ident):
    obj=request_query(p).filter(id=ident).first()
    if not obj: s.fail('NOT_FOUND','구매 요청을 찾을 수 없습니다.',404)
    return obj

def order_query(p):
    qs=PurchaseOrder.objects.filter(organization=p.organization).select_related('requisition__item','requisition__requester','supplier','contract')
    return qs if buyer(p) or stock_manager(p) else qs.filter(requisition__requester=p)

def get_order(p,ident):
    obj=order_query(p).filter(id=ident).first()
    if not obj: s.fail('NOT_FOUND','발주를 찾을 수 없습니다.',404)
    return obj

def master_data(obj,p):
    result={'id':str(obj.id),'code':obj.code,'name':obj.name}
    if isinstance(obj,Supplier):
        if buyer(p): result['contact']=obj.contact
    elif isinstance(obj,Contract):
        result.update(supplier_id=str(obj.supplier_id),supplier=obj.supplier.name,starts_on=obj.starts_on.isoformat(),ends_on=obj.ends_on.isoformat())
        if buyer(p):
            committed=PurchaseOrder.objects.filter(contract=obj,status__in=['ORDERED','PART_RECEIVED','RECEIVED']).aggregate(total=Sum('total'))['total'] or Decimal(0)
            result.update(currency=obj.currency,amount=str(obj.amount),committed=str(committed),remaining=str(obj.amount-committed),notes=obj.notes)
    elif isinstance(obj,Stockroom): result['location']=obj.location
    elif isinstance(obj,StockItem): result.update(tracking=obj.tracking,manufacturer=obj.manufacturer,model=obj.model)
    return result

def requisition_data(r,p):
    return {'id':str(r.id),'item':{'id':str(r.item_id),'name':r.item.name},'quantity':r.quantity,
        'currency':r.currency,'max_unit_price':str(r.max_unit_price),'max_total':str(r.max_unit_price*r.quantity),
        'requester':s.person_data(r.requester),'approver':s.person_data(r.approver),'reason':r.reason,
        'source_request_id':str(r.source_request_id) if r.source_request_id else None,'status':r.status,'version':r.row_version,
        'created_at':r.created_at.isoformat(),'can_decide':buyer(p) and r.approver_id==p.id and r.status=='PENDING' and r.requester_id!=p.id,
        'can_order':buyer(p) and r.status=='APPROVED'}

def order_data(o,p):
    result={'id':str(o.id),'number':o.number,'requisition_id':str(o.requisition_id),'supplier':o.supplier.name,
        'item':{'id':str(o.requisition.item_id),'name':o.requisition.item.name,'tracking':o.requisition.item.tracking},
        'quantity':o.quantity,'received_quantity':o.received_quantity,'remaining_quantity':o.quantity-o.received_quantity,
        'status':o.status,'version':o.row_version,'created_at':o.created_at.isoformat(),
        'contract_code':o.contract.code if o.contract else None,'can_release':buyer(p) and o.status=='DRAFT',
        'can_cancel':buyer(p) and o.status in ['DRAFT','ORDERED'] and o.received_quantity==0,
        'can_receive':stock_manager(p) and o.status in ['ORDERED','PART_RECEIVED']}
    if buyer(p): result.update(currency=o.currency,unit_price=str(o.unit_price),total=str(o.total))
    return result

def balance_data(b):
    return {'id':str(b.id),'stockroom_id':str(b.stockroom_id),'stockroom':b.stockroom.name,'item_id':str(b.item_id),
        'item':b.item.name,'tracking':b.item.tracking,'quantity':b.quantity,'version':b.row_version}

def movement_data(m):
    return {'id':str(m.id),'item':m.item.name,'quantity':m.quantity,'kind':m.kind,
        'source':m.source.name if m.source_id else None,'target':m.target.name if m.target_id else None,
        'actor':m.actor.display_name,'recipient':m.recipient.display_name if m.recipient_id else None,
        'destination':m.destination,'reason':m.reason,'asset_ids':m.asset_ids,
        'created_at':m.created_at.isoformat()}

def receipt_data(r):
    return {'id':str(r.id),'order_id':str(r.order_id),'reference':r.reference,'quantity':r.quantity,
            'stockroom':r.stockroom.name,'created_at':r.created_at.isoformat(),
            'assets':[{'id':str(x.asset_id),'asset_no':x.asset.asset_no} for x in r.stockasset_set.select_related('asset')]}

def master_permission(p,kind):
    roles=s.roles(p)
    allowed={'suppliers':{'PROCUREMENT_MANAGER','STOCK_MANAGER'},'contracts':{'PROCUREMENT_MANAGER','ASSET_MANAGER'},
        'stockrooms':{'STOCK_MANAGER','PROCUREMENT_MANAGER','ASSET_MANAGER'},
        'items':{'STOCK_MANAGER','PROCUREMENT_MANAGER','SERVICE_MANAGER','ASSET_MANAGER'}}[kind]
    if not roles&allowed: s.fail('FORBIDDEN','기준정보 조회 권한이 없습니다.',403)

def authorize(p,op,target):
    if op in ['buy_supplier','buy_contract','buy_order','buy_order_action']: require(p,'PROCUREMENT_MANAGER')
    elif op in ['stock_room','stock_item','stock_transfer','stock_issue','buy_receipt']: require(p,'STOCK_MANAGER')
    elif op=='buy_request':
        if not s.roles(p)&{'PROCUREMENT_MANAGER','SERVICE_MANAGER'}: s.fail('FORBIDDEN','구매 요청 권한이 없습니다.',403)
    elif op=='buy_decide': require(p,'PROCUREMENT_MANAGER')
    elif op=='buy_asset_contract':
        from .assets import require_manager
        require_manager(p)
    if op in ['buy_decide','buy_cancel_request']: get_request(p,target)
    if op in ['buy_order_action','buy_receipt']:
        order=get_order(p,target)
        if op=='buy_receipt' and order.requisition.item.tracking=='SERIALIZED': require(p,'ASSET_MANAGER')

def replay(p,op,payload,result):
    if op=='stock_transfer' and payload.get('asset_ids'): require(p,'ASSET_MANAGER')
    if op=='stock_issue' and payload.get('service_request_id'):
        from .catalog import get_request as get_service_request
        get_service_request(p,s.identifier(payload['service_request_id']))
    if op in ['buy_order','buy_order_action']:
        current=get_order(p,s.identifier(result['id']))
        for field in ['can_release','can_cancel','can_receive']: result[field]=order_data(current,p)[field]
    return result

def mutate(p,op,data,request_id,target):
    if op in ['buy_supplier','buy_contract','stock_room','stock_item']:
        return create_master(p,op,data,request_id)
    if op=='buy_request': return create_request(p,data,request_id)
    if op in ['buy_decide','buy_cancel_request']: return decide_request(p,op,data,request_id,target)
    if op=='buy_order': return create_order(p,data,request_id)
    if op=='buy_order_action': return order_action(p,data,request_id,target)
    if op=='buy_receipt': return receive(p,data,request_id,target)
    if op in ['stock_transfer','stock_issue']: return stock_action(p,op,data,request_id)
    if op=='buy_asset_contract':
        from .assets import get_asset
        s.check_fields(data,['asset_id','contract_id','reason'],['asset_id','contract_id','reason'])
        asset=get_asset(p,s.identifier(data['asset_id']),True);contract=get(Contract,p,data['contract_id'])
        link=AssetContractLink.objects.create(organization=p.organization,asset=asset,contract=contract,actor=p,reason=s.text(data,'reason'))
        s.record(p,link,'ASSET_CONTRACT_LINKED',request_id,after={'asset_id':str(asset.id),'contract_id':str(contract.id)})
        return {'id':str(link.id),'asset_id':str(asset.id),'contract':master_data(contract,p)},201
    s.fail('INVALID_OPERATION','지원하지 않는 구매·재고 동작입니다.',400)

def create_master(p,op,data,request_id):
    fields={'buy_supplier':['code','name','contact'],'buy_contract':['code','name','supplier_id','starts_on','ends_on','currency','amount','notes'],
            'stock_room':['code','name','location'],'stock_item':['code','name','tracking','manufacturer','model']}[op]
    s.check_fields(data,fields,fields)
    common={'organization':p.organization,'code':s.text(data,'code',80),'name':s.text(data,'name',200)}
    if op=='buy_supplier': obj=Supplier.objects.create(**common,contact=s.text(data,'contact',200,False))
    elif op=='stock_room': obj=Stockroom.objects.create(**common,location=s.text(data,'location',200))
    elif op=='stock_item':
        if data['tracking'] not in ['BULK','SERIALIZED']: s.fail('INVALID_TRACKING','수량 또는 일련번호 추적을 선택하십시오.')
        manufacturer=s.text(data,'manufacturer',200,data['tracking']=='SERIALIZED')
        obj=StockItem.objects.create(**common,tracking=data['tracking'],manufacturer=manufacturer,model=s.text(data,'model',200,False))
    else:
        starts,ends=day(data['starts_on']),day(data['ends_on'])
        if ends<starts: s.fail('INVALID_DATE','계약 종료일을 확인하십시오.')
        unit=currency(data['currency'])
        obj=Contract.objects.create(**common,supplier=get(Supplier,p,data['supplier_id']),starts_on=starts,ends_on=ends,
                currency=unit,amount=money(data['amount'],unit),notes=s.text(data,'notes',10000,False))
    s.record(p,obj,op.upper(),request_id,after={'code':obj.code})
    return master_data(obj,p),201

def create_request(p,data,request_id):
    fields=['item_id','quantity','currency','max_unit_price','approver_id','reason','source_request_id']
    s.check_fields(data,fields,fields[:-1])
    item=get(StockItem,p,data['item_id']);qty=quantity(data['quantity']);unit=currency(data['currency']);price=money(data['max_unit_price'],unit)
    if price*qty>MAX_MONEY: s.fail('INVALID_MONEY','승인 예산 합계가 허용 범위를 넘었습니다.')
    approver=get(Person,p,data['approver_id'])
    if approver.id==p.id or not approver.active or not approver.user.is_active or not buyer(approver):
        s.fail('INVALID_APPROVER','본인 이외의 활성 구매 관리자를 승인자로 지정하십시오.')
    source=None
    if data.get('source_request_id') is not None:
        from .catalog import get_request,request_staff
        source=get_request(p,s.identifier(data['source_request_id']))
        if source.status!='IN_PROGRESS' or not request_staff(p,source): s.fail('INVALID_SOURCE_REQUEST','처리 중인 서비스 요청만 연결할 수 있습니다.')
    r=PurchaseRequisition.objects.create(organization=p.organization,item=item,quantity=qty,currency=unit,max_unit_price=price,
        requester=p,approver=approver,source_request=source,reason=s.text(data,'reason'))
    s.record(p,r,'PURCHASE_REQUESTED',request_id,after={'quantity':qty,'max_unit_price':str(price),'currency':unit})
    return requisition_data(r,p),201

def decide_request(p,op,data,request_id,target):
    r=get_request(p,target)
    if op=='buy_cancel_request':
        s.check_fields(data,['reason','expected_version'],['reason','expected_version']);s.version(r,data)
        if r.requester_id!=p.id or r.status not in ['PENDING','APPROVED']: s.fail('INVALID_STATE','본인의 대기·승인 요청만 취소할 수 있습니다.',409)
        r.status='CANCELLED';reason=s.text(data,'reason')
    else:
        s.check_fields(data,['decision','reason','expected_version'],['decision','expected_version']);s.version(r,data)
        if r.approver_id!=p.id or r.requester_id==p.id: s.fail('FORBIDDEN','지정 구매 승인자만 결정할 수 있습니다.',403)
        if r.status!='PENDING': s.fail('INVALID_STATE','이미 결정된 구매 요청입니다.',409)
        if data['decision'] not in ['APPROVE','REJECT']: s.fail('INVALID_DECISION','승인·반려를 선택하십시오.')
        reason=s.text(data,'reason',required=data['decision']=='REJECT');r.status='APPROVED' if data['decision']=='APPROVE' else 'REJECTED'
        PurchaseDecision.objects.create(organization=p.organization,requisition=r,actor=p,decision=data['decision'],reason=reason)
    s.bump(r);s.record(p,r,'PURCHASE_REQUEST_DECIDED',request_id,after={'status':r.status,'reason':reason})
    return requisition_data(r,p),200

def create_order(p,data,request_id):
    s.check_fields(data,['requisition_id','supplier_id','contract_id','unit_price','expected_version'],['requisition_id','supplier_id','contract_id','unit_price','expected_version'])
    r=get_request(p,s.identifier(data['requisition_id']));s.version(r,data)
    if r.status!='APPROVED': s.fail('INVALID_STATE','승인된 구매 요청에서만 발주할 수 있습니다.',409)
    supplier=get(Supplier,p,data['supplier_id']);contract=get(Contract,p,data['contract_id']) if data['contract_id'] is not None else None
    if contract and (contract.supplier_id!=supplier.id or contract.currency!=r.currency): s.fail('INVALID_CONTRACT','공급업체·통화가 계약과 일치해야 합니다.')
    price=money(data['unit_price'],r.currency)
    if price>r.max_unit_price: s.fail('APPROVED_BUDGET_EXCEEDED','승인된 단가 한도를 초과할 수 없습니다.')
    order=PurchaseOrder.objects.create(organization=p.organization,requisition=r,supplier=supplier,contract=contract,
        number='PO-'+uuid.uuid4().hex.upper(),quantity=r.quantity,currency=r.currency,unit_price=price,total=price*r.quantity)
    r.status='ORDERED';s.bump(r)
    s.record(p,order,'PURCHASE_ORDER_DRAFTED',request_id,after={'total':str(order.total),'currency':order.currency})
    return order_data(order,p),201

def order_action(p,data,request_id,target):
    s.check_fields(data,['action','reason','expected_version'],['action','reason','expected_version'])
    order=get_order(p,target);s.version(order,data);reason=s.text(data,'reason')
    if data['action']=='RELEASE':
        if order.status!='DRAFT': s.fail('INVALID_STATE','초안 발주만 확정할 수 있습니다.',409)
        if order.contract_id:
            contract=order.contract;today=timezone.localdate()
            if not contract.starts_on<=today<=contract.ends_on: s.fail('CONTRACT_EXPIRED','계약 유효기간 안에서 발주를 확정하십시오.')
            used=PurchaseOrder.objects.filter(contract=contract,status__in=['ORDERED','PART_RECEIVED','RECEIVED']).aggregate(total=Sum('total'))['total'] or Decimal(0)
            if used+order.total>contract.amount: s.fail('CONTRACT_BUDGET_EXCEEDED','계약 금액 한도를 초과합니다.',409)
        order.status='ORDERED'
    elif data['action']=='CANCEL':
        if order.status not in ['DRAFT','ORDERED'] or order.received_quantity: s.fail('INVALID_STATE','입고가 없는 초안·확정 발주만 취소할 수 있습니다.',409)
        order.status='CANCELLED';r=order.requisition;r.status='APPROVED';s.bump(r)
    else: s.fail('INVALID_ACTION','발주 확정 또는 취소를 선택하십시오.')
    s.bump(order);s.record(p,order,'PURCHASE_ORDER_'+data['action'],request_id,after={'status':order.status,'reason':reason})
    return order_data(order,p),200

def change_balance(p,room,item,delta):
    b=StockBalance.objects.select_for_update().filter(stockroom=room,item=item,organization=p.organization).first()
    if not b:
        if delta<0: s.fail('INSUFFICIENT_STOCK','출고할 재고가 부족합니다.',409)
        b=StockBalance.objects.create(organization=p.organization,stockroom=room,item=item)
    if b.quantity+delta<0: s.fail('INSUFFICIENT_STOCK','출고할 재고가 부족합니다.',409)
    b.quantity+=delta;s.bump(b);return b

def movement(p,item,kind,qty,reason,source=None,target=None,**extra):
    return StockMovement.objects.create(organization=p.organization,item=item,kind=kind,quantity=qty,reason=reason,actor=p,source=source,target=target,**extra)

def receive(p,data,request_id,target):
    s.check_fields(data,['stockroom_id','reference','quantity','serials','reason','expected_version'],['stockroom_id','reference','quantity','serials','reason','expected_version'])
    order=get_order(p,target);s.version(order,data)
    if order.status not in ['ORDERED','PART_RECEIVED']: s.fail('INVALID_STATE','확정된 미입고 발주만 입고할 수 있습니다.',409)
    qty=quantity(data['quantity']);item=order.requisition.item
    if qty>order.quantity-order.received_quantity: s.fail('OVER_RECEIPT','발주 잔량을 초과할 수 없습니다.',409)
    serials=data['serials']
    if not isinstance(serials,list): s.fail('INVALID_SERIALS','일련번호 목록이 필요합니다.')
    if item.tracking=='SERIALIZED':
        require(p,'ASSET_MANAGER')
        if qty>100 or len(serials)!=qty: s.fail('INVALID_SERIALS','장비 입고는 1~100개이며 개별 자산 정보가 수량과 같아야 합니다.')
        for serial in serials:
            s.check_fields(serial,['asset_no','serial_number'],['asset_no','serial_number'])
            s.text(serial,'asset_no',80);s.text(serial,'serial_number',200)
    elif serials: s.fail('INVALID_SERIALS','수량 품목에는 개별 자산을 지정할 수 없습니다.')
    room=get(Stockroom,p,data['stockroom_id']);reason=s.text(data,'reason')
    receipt=GoodsReceipt.objects.create(organization=p.organization,order=order,stockroom=room,reference=s.text(data,'reference',80),
        quantity=qty,received_by=p,serials=serials,reason=reason)
    for serial in serials:
        from .assets import mutate as create_asset
        result,_=create_asset(p,'asset_create',{'asset_no':serial['asset_no'],'name':item.name,'manufacturer':item.manufacturer,
            'model':item.model,'serial_number':serial['serial_number'],'location':room.location,'portal_visible':False,
            'reason':'발주 입고: '+receipt.reference},request_id,None)
        asset=Asset.objects.get(id=result['id'])
        StockAsset.objects.create(organization=p.organization,asset=asset,item=item,stockroom=room,receipt=receipt)
        if order.contract_id: AssetContractLink.objects.create(organization=p.organization,asset=asset,contract=order.contract,actor=p,reason='발주 입고 계약 연결')
    change_balance(p,room,item,qty)
    movement(p,item,'RECEIPT',qty,reason,target=room,receipt=receipt,asset_ids=[str(x) for x in receipt.stockasset_set.values_list('asset_id',flat=True)])
    order.received_quantity+=qty;order.status='RECEIVED' if order.received_quantity==order.quantity else 'PART_RECEIVED';s.bump(order)
    s.record(p,receipt,'GOODS_RECEIVED',request_id,after={'quantity':qty,'order_id':str(order.id),'order_version':order.row_version})
    return receipt_data(receipt),201

def check_balance_version(p,room,item,expected,allow_empty=False):
    b=StockBalance.objects.filter(organization=p.organization,stockroom=room,item=item).first()
    if not b:
        if allow_empty and type(expected) is int and expected==0: return
        s.fail('STOCK_VERSION_CONFLICT','재고를 다시 조회하십시오.',409)
    s.version(b,{'expected_version':expected})

def stock_action(p,op,data,request_id):
    common=['item_id','source_id','quantity','reason','expected_source_version']
    extra=['target_id','expected_target_version','asset_ids','asset_versions'] if op=='stock_transfer' else ['person_id','destination','service_request_id','expected_request_version']
    s.check_fields(data,common+extra,common+(['target_id','expected_target_version','asset_ids','asset_versions'] if op=='stock_transfer' else ['person_id','destination']))
    item=get(StockItem,p,data['item_id']);source=get(Stockroom,p,data['source_id']);qty=quantity(data['quantity']);reason=s.text(data,'reason')
    check_balance_version(p,source,item,data['expected_source_version'])
    target=None;recipient=None;ticket=None;ids=[]
    if op=='stock_transfer':
        target=get(Stockroom,p,data['target_id'])
        if target.id==source.id: s.fail('INVALID_STOCKROOM','서로 다른 창고를 선택하십시오.')
        check_balance_version(p,target,item,data['expected_target_version'],True)
        if not isinstance(data['asset_ids'],list) or not isinstance(data['asset_versions'],dict): s.fail('INVALID_ASSETS','자산 목록과 버전은 목록·객체 형식이어야 합니다.')
        if item.tracking=='SERIALIZED':
            require(p,'ASSET_MANAGER')
            raw=data['asset_ids'];versions=data['asset_versions']
            if not isinstance(raw,list) or qty>100 or len(raw)!=qty or not isinstance(versions,dict): s.fail('INVALID_ASSETS','이동 수량과 개별 자산·버전 목록을 확인하십시오.')
            ids=[s.identifier(x) for x in raw]
            if len(set(ids))!=len(ids) or set(versions)!=set(str(x) for x in ids): s.fail('INVALID_ASSETS','자산은 중복 없이 버전을 지정하십시오.')
            rows=list(StockAsset.objects.filter(organization=p.organization,asset_id__in=ids,item=item,stockroom=source).select_related('asset'))
            if len(rows)!=qty: s.fail('INVALID_ASSETS','출발 창고의 해당 품목 자산만 이동할 수 있습니다.')
            from .assets import snapshot,log
            for row in rows:
                a=row.asset;s.version(a,{'expected_version':versions[str(a.id)]})
                if a.status!='STOCK' or a.custodian_id or a.custodies.filter(returned_at__isnull=True).exists(): s.fail('INVALID_ASSETS','보관 중인 자산만 이동할 수 있습니다.',409)
                before=snapshot(a);a.location=target.location;s.bump(a);row.stockroom=target;row.save()
                log(p,a,'MOVE',reason,request_id,before)
        elif data['asset_ids'] or data['asset_versions']: s.fail('INVALID_ASSETS','수량 품목에는 개별 자산을 지정하지 마십시오.')
        change_balance(p,source,item,-qty);change_balance(p,target,item,qty)
        record=movement(p,item,'TRANSFER',qty,reason,source=source,target=target,asset_ids=[str(x) for x in ids])
    else:
        if item.tracking!='BULK': s.fail('SERIALIZED_ASSET_REQUIRED','장비 출고는 자산 지급 화면에서 수행하십시오.')
        recipient=get(Person,p,data['person_id'])
        if not recipient.active or not recipient.user.is_active: s.fail('INVALID_RECIPIENT','활성 수령자를 선택하십시오.')
        if data.get('service_request_id') is not None:
            from .assets import related_request
            ticket=related_request(p,data['service_request_id'],recipient,data.get('expected_request_version'))
        change_balance(p,source,item,-qty)
        record=movement(p,item,'ISSUE',qty,reason,source=source,recipient=recipient,request=ticket,destination=s.text(data,'destination',200))
        if ticket: s.bump(ticket)
    s.record(p,record,'STOCK_MOVED',request_id,after={'kind':record.kind,'quantity':qty})
    return movement_data(record),201

def synchronize_asset(p,a,action,payload,ticket):
    row=StockAsset.objects.filter(asset=a,organization=p.organization).select_related('item','stockroom').first()
    if not row:
        if payload.get('stockroom_id'): s.fail('INVALID_STOCKROOM','창고 관리 자산에만 반납 창고를 지정할 수 있습니다.')
        return
    if action=='MOVE' and row.stockroom_id:
        s.fail('WAREHOUSE_TRANSFER_REQUIRED','창고 보관 자산은 재고 이동 화면에서 이동하십시오.',409)
    if action not in ['ISSUE','RETURN','RETIRE']: return
    require(p,'STOCK_MANAGER')
    if action in ['ISSUE','RETIRE']:
        if not row.stockroom_id: s.fail('INVALID_STOCK_STATE','출발 창고 기록을 확인하십시오.',409)
        change_balance(p,row.stockroom,row.item,-1)
        movement(p,row.item,action,1,payload['reason'],source=row.stockroom,asset=a,
            recipient=a.custodian if action=='ISSUE' else None,request=ticket,asset_ids=[str(a.id)],destination=a.location if action=='ISSUE' else '')
        row.stockroom=None
    else:
        if row.stockroom_id: s.fail('INVALID_STOCK_STATE','이미 창고에 보관된 자산입니다.',409)
        room=get(Stockroom,p,payload.get('stockroom_id'));a.location=room.location
        change_balance(p,room,row.item,1)
        movement(p,row.item,'RETURN',1,payload['reason'],target=room,asset=a,request=ticket,asset_ids=[str(a.id)])
        row.stockroom=room
    row.save()
