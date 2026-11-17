"""Explicitly invoked SR training preset. Reuses identities, pins old runs, audits automation."""
import uuid
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max
from . import services as s,process_engine as engine
from .access_cache import clear
from .models import (Organization,Person,Department,Group,Membership,RoleGrant,RoleDefinition,CustomRoleGrant,ProcessDefinition,ProcessVersion,ProcessBinding,SecurityEvent,CatalogItem,CatalogVersion,CatalogAudience,CommonCodeGroup,CommonCodeItem,TimelinessPolicy,Ticket,ProcessRun,TimelinessTarget)
from .security_policy import change_password
MARKER='SR_DEMO_20261118'
ACCOUNTS={'user1':'요청자','user_auth1':'요청부서 승인자','worker1':'운영자1','worker2':'운영자2','developer1':'개발자','designer1':'디자이너'}
REASON='사용자 요청 초기 구성·시스템 자동 검증(사람의 독립 검토를 대체하지 않음)'

def people_for(org):return {p.user.username:p for p in Person.objects.filter(organization=org,user__username__in=ACCOUNTS).select_related('user')}

def report(org):
    ps=people_for(org);item=CatalogItem.objects.get(organization=org,code='SR_STANDARD_REQUEST');v=item.versions.order_by('-version').first() if hasattr(item,'versions') else CatalogVersion.objects.filter(item=item).order_by('-version').first()
    return {'organization_id':str(org.id),'users':{k:str(p.id) for k,p in ps.items()},'catalog_id':str(item.id),'workflow_version_id':str(v.workflow_version_id),'tickets':[{'id':str(t.id),'number':t.number,'title':t.title,'status':t.status} for t in Ticket.objects.filter(organization=org,service_request__catalog_version=v,title__startswith='[실습]')],'retained':True}

def publish(org,admin,designer,code,name,kind,graph):
    normalized=engine.validate(admin,kind,graph)
    d,created=ProcessDefinition.objects.get_or_create(organization=org,code=code,defaults={'name':name,'kind':kind,'draft':normalized,'draft_author':designer})
    if d.kind!=kind:s.fail('INVALID_DEFINITION','같은 코드의 정의 종류가 다릅니다.',409)
    if not created:
        ProcessDefinition.objects.get_or_create(organization=org,code=d.code+'_B20261118',defaults={'name':d.name+' · 이전 초안 보관','kind':kind,'draft':d.draft,'draft_author':d.draft_author,'active':False})
    n=(d.versions.aggregate(n=Max('version'))['n'] or 0)+1 if hasattr(d,'versions') else (ProcessVersion.objects.filter(definition=d).aggregate(n=Max('version'))['n'] or 0)+1
    v=ProcessVersion.objects.create(organization=org,definition=d,version=n,graph=normalized,digest=engine.digest(normalized),published_by=admin,reviewed_by=admin,reason=REASON)
    d.name=name;d.draft=normalized;d.draft_author=designer;d.published=v;d.active=True;d.row_version+=1;d.save()
    s.record(admin,d,'SR_TEMPLATE_AUTO_PUBLISHED',uuid.uuid4(),after={'version_id':str(v.id),'automatic_validation':True,'template_owner':str(designer.id),'reason':REASON})
    return v

@transaction.atomic
def configure(organization_id,passwords,seed=True):
    org=Organization.objects.select_for_update().get(pk=organization_id)
    if SecurityEvent.objects.filter(organization=org,action=MARKER).exists():return report(org)
    admin=Person.objects.filter(organization=org,rolegrant__role='ORG_ADMIN',active=True,user__is_active=True).first()
    if not admin:s.fail('NO_ADMIN','초기 구성 관리자 계정이 필요합니다.')
    rd,_=Department.objects.get_or_create(organization=org,code='SR_REQUEST_DEPT',defaults={'name':'요청부서'})
    od,_=Department.objects.get_or_create(organization=org,code='SR_OPERATIONS_DEPT',defaults={'name':'서비스 운영부서'})
    # Global login names must never accidentally attach another organization's account.
    people={}
    for username,label in ACCOUNTS.items():
        user=get_user_model().objects.filter(username=username).first()
        if user:
            person=Person.objects.filter(user=user,organization=org,active=True).first()
            if not person or not user.is_active:s.fail('ACCOUNT_SCOPE','기존 계정의 조직/활성 상태를 확인하십시오.',409)
        else:
            if not passwords.get(username):s.fail('MISSING_PASSWORD','없는 계정에 대한 서로 다른 초기 비밀번호가 필요합니다.')
            user=get_user_model().objects.create_user(username=username,password=None)
            person=Person.objects.create(organization=org,user=user,display_name=label,department=rd if username in ('user1','user_auth1') else od)
            change_password(person,passwords[username],force=True)
        if not person.department_id:person.department=rd if username in ('user1','user_auth1') else od;person.save(update_fields=['department'])
        people[username]=person
    if people['user1'].department_id!=people['user_auth1'].department_id:s.fail('APPROVER_DEPARTMENT','요청자와 요청부서 승인자의 부서를 확인하십시오.',409)
    for username in ('worker1','worker2'):RoleGrant.objects.get_or_create(organization=org,person=people[username],role='AGENT')
    RoleGrant.objects.get_or_create(organization=org,person=people['developer1'],role='DEVELOPER')
    role,_=RoleDefinition.objects.get_or_create(organization=org,code='SR_DESIGNER',defaults={'name':'서비스요청 디자이너','permissions':['console.access','workflow.manage','entity.read','code.read','service.manage']})
    CustomRoleGrant.objects.get_or_create(organization=org,person=people['designer1'],role=role)
    group,_=Group.objects.get_or_create(organization=org,code='SR_DEMO_INTAKE',defaults={'name':'서비스요청 접수그룹 · 만족도 프로세스','description':'운영자1/2 접수·배정 및 조치'})
    for username in ('worker1','worker2'):Membership.objects.get_or_create(organization=org,person=people[username],group=group)
    audience,_=Group.objects.get_or_create(organization=org,code='SR_REQUESTERS',defaults={'name':'서비스요청 신청대상'})
    Membership.objects.get_or_create(organization=org,person=people['user1'],group=audience)
    clear()
    cg,_=CommonCodeGroup.objects.get_or_create(organization=org,code='SR_DEMO_CATEGORY',defaults={'name':'서비스요청 구분(실습)','description':'카탈로그 선택지의 초기 기준 코드'})
    categories=[('ACCOUNT','계정'),('ACCESS','권한'),('SOFTWARE','소프트웨어'),('DEVICE','장비'),('OTHER','기타')]
    for i,(code,label) in enumerate(categories):CommonCodeItem.objects.get_or_create(organization=org,group=cg,code=code,defaults={'label':label,'sort_order':i+1})
    if not TimelinessPolicy.objects.filter(organization=org,ticket_type='SERVICE_REQUEST').exists():TimelinessPolicy.objects.create(organization=org,ticket_type='SERVICE_REQUEST',version=1,name='서비스요청 기본 적기처리 기준',basis='RECEIPT',target_minutes=1440,published_by=admin,reason=REASON)
    def f(key,label,type='text',required=False,**kw):return dict(key=key,label=label,type=type,required=required,**kw)
    fields=[f('title','요청 제목',required=True,max_length=180),f('description','요청 내용',required=True,max_length=2000),f('category','요청 구분',required=True),f('service_system','대상 시스템',required=True),f('request_priority','요청 우선순위',type='number',required=True,minimum=1,maximum=3),f('requested_due','희망 완료일'),f('request_contact','요청 연락처'),f('assignee','조치 담당자','person',group_id=str(group.id)),f('receipt_note','접수·배정 의견'),f('planned_finish','처리 예정일시','datetime'),f('resolution','조치 내용'),f('root_cause','원인·참고 사항'),f('action_started','조치 시작일시','datetime'),f('action_finished','조치 완료일시','datetime'),f('work_minutes','작업 시간(분)','integer',minimum=0,maximum=100000),f('confirmed','조치 결과 정상 확인','boolean'),f('feedback','결과 확인·재조치 의견'),f('satisfaction','만족도(1~5점)','integer',minimum=1,maximum=5),f('survey_comment','만족도 의견')]
    keys={'request':[x['key'] for x in fields[:7]],'receipt':['assignee','receipt_note','planned_finish'],'work':['resolution','root_cause','action_started','action_finished','work_minutes'],'confirmation':['confirmed','feedback'],'survey':['satisfaction','survey_comment']}
    labels={'request':'요청 기본정보','receipt':'접수 및 배정','work':'담당자 조치','confirmation':'조치결과 확인','survey':'만족도 조사'}
    layout=dict(mode='sections',groups=[dict(key=k,label=labels[k],fields=[dict(key=key,span=2 if key in ('description','resolution','receipt_note','feedback','survey_comment') else 1,height=3 if key in ('description','resolution') else 1) for key in vals]) for k,vals in keys.items()])
    screen=publish(org,admin,people['designer1'],'SR_STANDARD_SCREEN','서비스요청 공통 화면 · 만족도 템플릿','SCREEN',dict(fields=fields,read_only=[],columns=2,layout=layout))
    approval=publish(org,admin,people['designer1'],'SR_STANDARD_APPROVAL','요청부서 결재선','APPROVAL',dict(stages=[dict(key='department_approve',label='요청부서 승인',selector=dict(kind='USER',ids=[str(people['user_auth1'].id)]),mode='ALL')]))
    def node(key,type,next=None,read=(),edit=(),required=(),**kw):
        modes={k:'EDIT' if k in edit else 'READ' if k in read else 'HIDDEN' for k in keys}
        result=dict(key=key,label={'register':'요청 등록','department_approve':'요청부서 승인','receive':'접수 및 담당자 배정','action':'담당자 조치','confirm':'조치결과 확인','confirmation_result':'정상 확인 여부','survey':'만족도 조사','close':'종료'}[key],type=type,**kw)
        if next:result['next']=next
        if type in ('TASK','APPROVAL'):result.update(group_modes=modes,required_fields=list(required))
        return result
    nodes=[node('register','START','department_approve'),node('department_approve','APPROVAL','receive',read=['request'],version_id=str(approval.id)),node('receive','TASK','action',read=['request'],edit=['receipt'],required=['assignee','receipt_note'],selector=dict(kind='GROUP',ids=[str(group.id)]),mode='ANY'),node('action','TASK','confirm',read=['request','receipt'],edit=['work'],required=['resolution'],selector=dict(kind='FIELD_USER',ids=['assignee']),mode='ANY'),node('confirm','TASK','confirmation_result',read=['request','work'],edit=['confirmation'],required=['confirmed'],selector=dict(kind='STARTER',ids=[]),mode='ANY'),node('confirmation_result','CONDITION',condition=dict(field='confirmed',op='eq',value=True),true='survey',false='action'),node('survey','TASK','close',read=['request','work','confirmation'],edit=['survey'],required=['satisfaction'],selector=dict(kind='STARTER',ids=[]),mode='ANY'),node('close','END')]
    workflow=publish(org,admin,people['designer1'],'SR_STANDARD','서비스요청 표준 프로세스 · 만족도','WORKFLOW',dict(start='register',catalog_only=True,fields=fields,nodes=nodes,screen_version_id=str(screen.id),close_on_complete=True,ticket_assignee_field='assignee'))
    binding,_=ProcessBinding.objects.get_or_create(organization=org,menu_key='service-request',defaults={'version':workflow,'updated_by':admin,'reason':REASON});binding.version=workflow;binding.updated_by=admin;binding.reason=REASON;binding.save()
    item,_=CatalogItem.objects.get_or_create(organization=org,code='SR_STANDARD_REQUEST')
    n=(CatalogVersion.objects.filter(item=item).aggregate(n=Max('version'))['n'] or 0)+1
    initial=[dict(key=x['key'],label=x['label'],type='integer' if x['key']=='request_priority' else 'choice' if x['key']=='category' else 'date' if x['key']=='requested_due' else 'textarea' if x['key']=='description' else 'text',required=x['required'],**({'options':[v for _,v in categories]} if x['key']=='category' else {})) for x in fields[:7]]
    entry=CatalogVersion.objects.create(organization=org,item=item,version=n,name='서비스요청 · 승인부터 만족도까지',description='등록 → 부서 승인 → 접수·배정 → 조치 → 확인 → 만족도 조사 → 자동 종료',fields=initial,fulfillment_group=group,approval_required=False,public_to_org=False,available=True,workflow_version=workflow)
    CatalogAudience.objects.create(organization=org,catalog_version=entry,group=audience)
    if seed:
        for i,(title,category,system,desc) in enumerate([('업무 시스템 계정 생성','계정','그룹웨어','신규 입사자용 업무 계정을 신청합니다.'),('공유폴더 접근 권한','권한','파일서버','프로젝트 공유폴더 읽기 권한이 필요합니다.'),('개발 도구 설치','소프트웨어','개발 PC','승인된 개발 도구 설치를 요청합니다.'),('업무 노트북 점검','장비','업무 노트북','화상회의 중 발생하는 장비 문제 점검을 요청합니다.'),('업무 시스템 사용 문의','기타','ERP','월 마감 조회 방법과 오류 확인을 요청합니다.')]):
            s.execute(people['user1'],'req_create',dict(catalog_version_id=str(entry.id),values=dict(title='[실습] '+title,description=desc,category=category,service_system=system,request_priority=2)),uuid.uuid4().hex,uuid.uuid4())
    verify(org)
    SecurityEvent.objects.create(organization=org,person=admin,action=MARKER,request_id=uuid.uuid4())
    s.record(admin,item,'SR_DEMO_READY',uuid.uuid4(),after={'workflow_version_id':str(workflow.id),'screen_version_id':str(screen.id),'automatic_validation':True,'sample_count':5 if seed else 0})
    return {**report(org),'retained':False}

def verify(org):
    """Real command path, rolled back; retains no verification request/vote/history."""
    with transaction.atomic():
        ps=people_for(org);v=CatalogVersion.objects.filter(organization=org,item__code='SR_STANDARD_REQUEST').order_by('-version').first()
        created,_=s.execute(ps['user1'],'req_create',{'catalog_version_id':str(v.id),'values':dict(title='[자동 검증] 삭제될 요청',description='롤백 검증',category='계정',service_system='검증',request_priority=2)},uuid.uuid4().hex,uuid.uuid4())
        run=ProcessRun.objects.get(ticket_id=created['id'])
        def act(who,key,values=None,decision='COMPLETE'):
            run.refresh_from_db();task=run.tasks.get(status='OPEN')
            if task.node_key!=key:raise AssertionError((task.node_key,key))
            return s.execute(ps[who],'flow_act',dict(task_id=str(task.id),expected_version=run.row_version,decision=decision,values=values or {},reason='사전 구성 롤백 검증'),uuid.uuid4().hex,uuid.uuid4(),run.id)
        act('user_auth1',run.tasks.get(status='OPEN').node_key,decision='APPROVE')
        act('worker1','receive',{'assignee':str(ps['worker2'].id),'receipt_note':'운영자2 배정'})
        act('worker2','action',{'resolution':'조치 완료'})
        act('user1','confirm',{'confirmed':False,'feedback':'재조치 요청'})
        act('worker2','action',{'resolution':'재조치 완료'})
        act('user1','confirm',{'confirmed':True,'feedback':'정상 확인'})
        run.refresh_from_db();assert run.status=='ACTIVE' and run.tasks.get(status='OPEN').node_key=='survey'
        act('user1','survey',{'satisfaction':5,'survey_comment':'만족합니다.'})
        run.refresh_from_db();ticket=Ticket.objects.get(pk=run.ticket_id)
        assert run.status=='COMPLETED' and ticket.status=='CLOSED' and TimelinessTarget.objects.get(ticket=ticket).completed_at
        transaction.set_rollback(True)
    return True
