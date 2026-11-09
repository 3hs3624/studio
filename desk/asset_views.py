from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from . import assets, services as s
from .models import Asset, Person, ASSET_STATUSES
from .views import context

def candidates(p):
    from .catalog import request_query
    return request_query(p,'queue').filter(status='IN_PROGRESS').select_related('requested_by')

@login_required
def listing(request):
    try:
        c=context(request);p=c['actor']
        qs=assets.query(p)
        params=request.GET.dict()
        q=params.get('q','')[:200];state=params.get('status','')
        if state:
            if state not in ASSET_STATUSES:
                s.fail('INVALID_STATUS','자산 상태를 확인하십시오.',400)
            qs=qs.filter(status=state)
        if q:
            qs=qs.filter(Q(name__icontains=q)|Q(asset_no__icontains=q))
        c.update(s.page(p,qs,params,lambda a:assets.data(a,p),'Asset'))
        c.update(q=q,selected_status=state,states=ASSET_STATUSES,total=qs.count())
        return render(request,'desk/asset-list.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def new(request):
    try:
        c=context(request);assets.require_manager(c['actor'])
        return render(request,'desk/asset-new.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def detail(request,id):
    try:
        c=context(request);p=c['actor'];a=assets.get_asset(p,id)
        c.update(item=assets.data(a,p),private_details=assets.full_reader(p) or a.custodian_id==p.id)
        history=assets.history_query(p,id)
        c['history_items']=s.page(p,history,request.GET.dict(),lambda h:assets.history_data(h,p),'asset_history:'+str(id))
        if assets.manager(p):
            c.update(people=Person.objects.filter(organization=p.organization,active=True,user__is_active=True).order_by('profile__full_name'),
                     requests=candidates(p))
        from .models import StockAsset,Stockroom,AssetContractLink
        row=StockAsset.objects.filter(asset=a).select_related('stockroom','item').first()
        if row and assets.full_reader(p):
            c.update(stock_record=row,stockrooms=Stockroom.objects.filter(organization=p.organization))
        if assets.full_reader(p):
            c['contract_links']=AssetContractLink.objects.filter(asset=a).select_related('contract__supplier')
        return render(request,'desk/asset-detail.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)

@login_required
def mine(request):
    try:
        c=context(request);p=c['actor']
        qs=assets.history_query(p,personal=True)
        c.update(active_assets=[assets.data(a,p) for a in Asset.objects.filter(organization=p.organization,custodian=p)],
            history_items=s.page(p,qs,request.GET.dict(),lambda h:assets.history_data(h,p,True),'my_asset_history'))
        return render(request,'desk/my-assets.html',c)
    except s.BusinessError as exc:
        return HttpResponse(exc.message,status=exc.status)
