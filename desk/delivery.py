"""Read-only delivery reporting and validated ingestion of provider observations."""
from urllib.parse import urlsplit
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from . import services as s
from .models import DeliveryRecord, DeliveryImport, Organization
from .permissions import allowed, require

STATUS = {'OPEN':'검토 대기','APPROVED':'검토 승인','MERGED':'병합 완료','CLOSED':'종료','COMMITTED':'커밋',
 'QUEUED':'실행 대기','AWAITING_APPROVAL':'배포 승인 대기','RUNNING':'실행 중','SUCCESS':'성공','FAILED':'실패','CANCELLED':'취소','NONE':'결과 없음'}
SOURCE_STATES = ['OPEN','APPROVED','MERGED','CLOSED','COMMITTED']
DEPLOYMENT_STATES = ['QUEUED','AWAITING_APPROVAL','RUNNING','SUCCESS','FAILED','CANCELLED']


def query(actor,kind):
    require(actor,'delivery.read')
    return DeliveryRecord.objects.filter(organization=actor.organization,kind=kind).order_by('-occurred_at','-id')


def decorate(record):
    record.status_label=STATUS.get(record.status,record.status)
    record.build_label=STATUS.get(record.build_status,record.build_status)
    record.detail_url='/resources/'+('changes/' if record.kind=='SOURCE' else 'deployments/')+str(record.id)
    return record


def overview(actor):
    visible=allowed(actor,'delivery.read')
    result={'delivery_allowed':visible,'delivery_changes':[],'delivery_deployments':[],'delivery_providers':[], 'delivery_metrics':[]}
    if not visible:return result
    changes=query(actor,'SOURCE');deployments=query(actor,'DEPLOYMENT')
    result.update(delivery_changes=[decorate(x) for x in changes[:6]],delivery_deployments=[decorate(x) for x in deployments[:6]],
      delivery_metrics=[dict(label=label,value=qs.count(),url=url) for label,qs,url in [
       ('검토 대기 PR',changes.filter(status='OPEN'),'/resources/changes?status=OPEN'),
       ('빌드 실패',changes.filter(build_status='FAILED'),'/resources/changes?build_status=FAILED'),
       ('배포 승인 대기',deployments.filter(status='AWAITING_APPROVAL'),'/resources/deployments?status=AWAITING_APPROVAL'),
       ('배포 실패',deployments.filter(status='FAILED'),'/resources/deployments?status=FAILED')]])
    for provider,label in [('github','GitHub'),('jenkins','Jenkins')]:
        latest=DeliveryImport.objects.filter(organization=actor.organization,provider=provider).order_by('-created_at','-id').first()
        result['delivery_providers'].append(dict(label=label,last=latest))
    return result


def ingest(actor,provider,payload,request_id):
    require(actor,'delivery.manage')
    if not actor.active or not actor.user.is_active or not actor.organization.active:s.fail('FORBIDDEN','비활성 계정입니다.',403)
    if provider not in ('github','jenkins'):s.fail('INVALID_PROVIDER','지원하지 않는 제공자입니다.')
    if not isinstance(payload,list) or len(payload)>500:s.fail('INVALID_INPUT','수신 목록은 최대 500건입니다.')
    fields=['external_id','title','repository','branch','revision','service','version','environment','status','build_status','external_actor','external_url','occurred_at']
    required=['external_id','title','status','external_url','occurred_at']+(['repository','branch'] if provider=='github' else ['service','version','environment'])
    cleaned=[];seen=set()
    for item in payload:
        if not isinstance(item,dict):s.fail('INVALID_INPUT','수신 항목을 확인하십시오.')
        s.check_fields(item,fields,required)
        value={key:s.text(item,key,DeliveryRecord._meta.get_field(key).max_length,required=key in required) for key in fields if key not in ('occurred_at','build_status')}
        if value['external_id'] in seen:s.fail('INVALID_INPUT','동일 제공자 식별자가 중복되었습니다.')
        seen.add(value['external_id'])
        states=SOURCE_STATES if provider=='github' else DEPLOYMENT_STATES
        build=item.get('build_status','NONE')
        if value['status'] not in states or build not in ('NONE','QUEUED','RUNNING','SUCCESS','FAILED'):s.fail('INVALID_STATUS','지원하지 않는 상태입니다.')
        try:
            url=urlsplit(value['external_url'])
            valid=url.scheme=='https' and url.hostname and not url.username and not url.password and not url.fragment and not url.query
            if provider=='github':valid=valid and url.hostname=='github.com' and url.path.startswith('/'+value['repository']+'/')
            timestamp=parse_datetime(item['occurred_at']) if isinstance(item['occurred_at'],str) else None
        except (ValueError,TypeError):valid=False;timestamp=None
        if not valid or not timestamp or timezone.is_naive(timestamp) or timestamp>timezone.now()+timezone.timedelta(minutes=5):s.fail('INVALID_INPUT','HTTPS 원문 주소와 시간대가 포함된 발생 시각을 확인하십시오.')
        value.update(kind='SOURCE' if provider=='github' else 'DEPLOYMENT',build_status=build,occurred_at=timestamp)
        cleaned.append(value)
    with transaction.atomic():
        Organization.objects.select_for_update().get(pk=actor.organization_id)
        accepted=0
        for value in cleaned:
            external_id=value.pop('external_id')
            existing=DeliveryRecord.objects.filter(organization=actor.organization,provider=provider,external_id=external_id).first()
            if existing and existing.occurred_at>value['occurred_at']:continue
            DeliveryRecord.objects.update_or_create(organization=actor.organization,provider=provider,external_id=external_id,defaults={**value,'received_at':timezone.now()})
            accepted+=1
        event=DeliveryImport.objects.create(organization=actor.organization,provider=provider,imported_by=actor,record_count=accepted)
        s.record(actor,event,'DELIVERY_IMPORTED',request_id,after={'provider':provider,'accepted':accepted})
    return accepted
