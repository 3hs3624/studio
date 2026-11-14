from django.db.models import Q
from .api import endpoint,query,command
from . import services as s, procurement as p
from .models import Supplier,Contract,Stockroom,StockItem,StockBalance,StockMovement,GoodsReceipt,StockAsset

MASTERS={'suppliers':(Supplier,'buy_supplier'),'contracts':(Contract,'buy_contract'),
         'stockrooms':(Stockroom,'stock_room'),'items':(StockItem,'stock_item')}

@endpoint(['GET','POST'])
def master(request,kind):
    model,op=MASTERS[kind]
    if request.method=='POST': return command(request,op)
    p.master_permission(request.actor,kind)
    params=query(request,['limit','cursor','q'])
    qs=model.objects.filter(organization=request.actor.organization)
    if params.get('q'):
        if len(params['q'])>200: s.fail('INVALID_QUERY','검색어는 최대 200자입니다.',400)
        qs=qs.filter(Q(name__icontains=params['q'])|Q(code__icontains=params['q']))
    return s.page(request.actor,qs,params,lambda obj:p.master_data(obj,request.actor),'buy_master:'+kind)

@endpoint(['GET','POST'])
def requisitions(request):
    if request.method=='POST': return command(request,'buy_request')
    params=query(request,['limit','cursor'])
    return s.page(request.actor,p.request_query(request.actor),params,lambda obj:p.requisition_data(obj,request.actor),'purchase_requests')

@endpoint(['GET'])
def requisition(request,id): return p.requisition_data(p.get_request(request.actor,id),request.actor)

@endpoint(['POST'])
def decide(request,id): return command(request,'buy_decide',id)

@endpoint(['POST'])
def cancel_request(request,id): return command(request,'buy_cancel_request',id)

@endpoint(['GET','POST'])
def orders(request):
    if request.method=='POST': return command(request,'buy_order')
    params=query(request,['limit','cursor'])
    return s.page(request.actor,p.order_query(request.actor),params,lambda obj:p.order_data(obj,request.actor),'purchase_orders')

@endpoint(['GET'])
def order(request,id): return p.order_data(p.get_order(request.actor,id),request.actor)

@endpoint(['POST'])
def order_actions(request,id): return command(request,'buy_order_action',id)

@endpoint(['GET','POST'])
def receipts(request,id):
    if request.method=='POST': return command(request,'buy_receipt',id)
    obj=p.get_order(request.actor,id);params=query(request,['limit','cursor'])
    return s.page(request.actor,GoodsReceipt.objects.filter(order=obj).select_related('stockroom'),params,p.receipt_data,'purchase_receipts:'+str(id))

def require_stock_read(pers):
    if not p.stock_manager(pers) and not p.buyer(pers): s.fail('FORBIDDEN','재고 조회 권한이 없습니다.',403)

@endpoint(['GET'])
def balances(request):
    require_stock_read(request.actor);params=query(request,['limit','cursor'])
    qs=StockBalance.objects.filter(organization=request.actor.organization).select_related('stockroom','item')
    return s.page(request.actor,qs,params,p.balance_data,'stock_balances')

@endpoint(['GET'])
def movements(request):
    require_stock_read(request.actor);params=query(request,['limit','cursor'])
    qs=StockMovement.objects.filter(organization=request.actor.organization).select_related('item','source','target','actor','recipient')
    return s.page(request.actor,qs,params,p.movement_data,'stock_movements')

@endpoint(['POST'])
def transfer(request): return command(request,'stock_transfer')

@endpoint(['POST'])
def issue(request): return command(request,'stock_issue')

@endpoint(['GET','POST'])
def asset_contracts(request):
    if request.method=='POST': return command(request,'buy_asset_contract')
    from .assets import full_reader
    from .models import AssetContractLink
    if not full_reader(request.actor): s.fail('FORBIDDEN','자산 계약 조회 권한이 없습니다.',403)
    params=query(request,['limit','cursor'])
    qs=AssetContractLink.objects.filter(organization=request.actor.organization).select_related('asset','contract__supplier')
    return s.page(request.actor,qs,params,lambda obj:{'id':str(obj.id),'asset_no':obj.asset.asset_no,
        'asset_id':str(obj.asset_id),'contract':p.master_data(obj.contract,request.actor),'reason':obj.reason},'asset_contracts')
