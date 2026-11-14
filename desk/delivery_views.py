from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from .views import context
from . import delivery,services as s

@login_required
def listing(request,kind,id=None):
    try:
        c=context(request);qs=delivery.query(c['actor'],kind)
        if id:
            item=qs.filter(id=id).first()
            if not item:s.fail('NOT_FOUND','항목을 찾을 수 없습니다.',404)
            c['delivery_item']=delivery.decorate(item)
        status=request.GET.get('status','');text=request.GET.get('q','')[:150];build=request.GET.get('build_status','')
        states=delivery.SOURCE_STATES if kind=='SOURCE' else delivery.DEPLOYMENT_STATES
        if status and status not in states:s.fail('INVALID_FILTER','상태를 확인하십시오.')
        if build and build not in ('NONE','QUEUED','RUNNING','SUCCESS','FAILED'):s.fail('INVALID_FILTER','빌드 상태를 확인하십시오.')
        if status:qs=qs.filter(status=status)
        if build:qs=qs.filter(build_status=build)
        if text:
            from django.db.models import Q
            qs=qs.filter(Q(title__icontains=text)|Q(repository__icontains=text)|Q(service__icontains=text))
        from django.core.paginator import Paginator
        page=Paginator(qs,25).get_page(request.GET.get('page',1))
        from urllib.parse import urlencode
        c.update(delivery_kind=kind,delivery_title='소스 변경 목록' if kind=='SOURCE' else '배포 목록',
            delivery_records=[delivery.decorate(item) for item in page],delivery_page=page,
            delivery_filters=urlencode({'q':text,'status':status,'build_status':build}),q=text,selected_status=status,
            selected_build=build,status_options=[(key,delivery.STATUS[key]) for key in states])
        return render(request,'desk/delivery-list.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)
