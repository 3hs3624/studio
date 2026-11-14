from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .views import context
from . import services as s,procurement as p
from .models import (Supplier,Contract,Stockroom,StockItem,PurchaseRequisition,PurchaseOrder,StockBalance,
                     StockMovement,StockAsset,Person,RoleGrant,Asset)

def render_page(request,template,build):
    try:
        c=context(request);build(c,c['actor']);return render(request,'desk/'+template,c)
    except s.BusinessError as exc: return HttpResponse(exc.message,status=exc.status)

@login_required
def requisitions(request):
    def build(c,actor):
        c.update(s.page(actor,p.request_query(actor),request.GET.dict(),lambda r:p.requisition_data(r,actor),'purchase_requests'))
        if c['can_purchase_request']:
            from .catalog import request_query
            from .permissions import people_with
            c.update(stock_items=StockItem.objects.filter(organization=c['org']),
                source_requests=request_query(actor,'queue').filter(status='IN_PROGRESS'),
                approvers=people_with(c['org'],'procurement.manage').exclude(id=actor.id))
    return render_page(request,'purchase-requests.html',build)

@login_required
def requisition(request,id):
    def build(c,actor):
        r=p.get_request(actor,id);c['purchase_request']=p.requisition_data(r,actor)
        c['can_cancel_request']=r.requester_id==actor.id and r.status in ['PENDING','APPROVED']
        if c['is_buyer']:
            c.update(suppliers=Supplier.objects.filter(organization=c['org']),contracts=Contract.objects.filter(organization=c['org']))
    return render_page(request,'purchase-request-detail.html',build)

@login_required
def orders(request):
    return render_page(request,'purchase-orders.html',lambda c,actor:c.update(s.page(actor,p.order_query(actor),request.GET.dict(),lambda o:p.order_data(o,actor),'purchase_orders')))

@login_required
def order(request,id):
    def build(c,actor):
        obj=p.get_order(actor,id);c['order']=p.order_data(obj,actor)
        c.update(receipts=[p.receipt_data(r) for r in obj.goodsreceipt_set.select_related('stockroom').order_by('-created_at')])
        if c['is_stock_manager']: c['stockrooms']=Stockroom.objects.filter(organization=c['org'])
    return render_page(request,'purchase-order-detail.html',build)

@login_required
def inventory(request):
    def build(c,actor):
        if not c['can_stock_read']: s.fail('FORBIDDEN','재고 조회 권한이 필요합니다.',403)
        balances=StockBalance.objects.filter(organization=c['org']).select_related('item','stockroom')
        c.update(s.page(actor,balances,request.GET.dict(),p.balance_data,'stock_balances'))
        c['balances_all']=list(balances)
        c['balance_versions']={str(b.item_id)+':'+str(b.stockroom_id):b.row_version for b in c['balances_all']}
        c.update(stockrooms=Stockroom.objects.filter(organization=c['org']),
                 people=Person.objects.filter(organization=c['org'],active=True,user__is_active=True))
        if c['is_stock_manager']:
            from .catalog import request_query
            from .permissions import people_with
            c['source_requests']=request_query(actor,'queue').filter(status='IN_PROGRESS')
            c['bulk_balances']=[b for b in c['balances_all'] if b.item.tracking=='BULK' and b.quantity>0]
            c['stock_assets']=StockAsset.objects.filter(organization=c['org'],stockroom__isnull=False,asset__status='STOCK').select_related('asset','item')
    return render_page(request,'inventory.html',build)

@login_required
def movements(request):
    def build(c,actor):
        if not c['can_stock_read']: s.fail('FORBIDDEN','재고 조회 권한이 필요합니다.',403)
        qs=StockMovement.objects.filter(organization=c['org']).select_related('item','source','target','actor','recipient')
        c.update(s.page(actor,qs,request.GET.dict(),p.movement_data,'stock_movements'))
    return render_page(request,'stock-movements.html',build)

@login_required
def contracts(request):
    def build(c,actor):
        if not c['can_contract_read']: s.fail('FORBIDDEN','계약 조회 권한이 필요합니다.',403)
        qs=Contract.objects.filter(organization=c['org']).select_related('supplier')
        c.update(s.page(actor,qs,request.GET.dict(),lambda r:p.master_data(r,actor),'buy_master:contracts'))
        c['suppliers']=Supplier.objects.filter(organization=c['org'])
        if c['is_asset_manager']: c['assets']=Asset.objects.filter(organization=c['org']).order_by('asset_no')
        c['contracts_all']=qs
    return render_page(request,'contracts.html',build)
