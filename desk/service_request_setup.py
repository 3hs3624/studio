"""User-authorized, idempotent baseline built from normal workflow definitions.
Initial versions are deployment presets with automatic validation, not a claim of
human independent review. Subsequent UI edits use the regular review/publish gate.
"""
import uuid
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import (Organization,Person,Department,Group,Membership,RoleGrant,ProcessDefinition,ProcessVersion,ProcessBinding,SecurityEvent,CatalogItem)
from . import process_engine as engine,services as s,catalog
from .security_policy import change_password
from .access_cache import clear

USERNAMES=['user1','user_auth1','worker1','worker2','worker3']
MARKER='SR_STANDARD_PROVISIONED'

def configure(organization_id,passwords,force_change=True):
    with transaction.atomic():
        org=Organization.objects.select_for_update().get(id=organization_id)
        actor=Person.objects.filter(organization=org,rolegrant__role='ORG_ADMIN',active=True,user__is_active=True).order_by('created_at').first()
        if not actor:s.fail('NO_ADMIN','조직의 시스템 관리자 계정이 필요합니다.')
        marker=SecurityEvent.objects.filter(organization=org,action=MARKER).first()
        if marker:return {'retained':True,'organization_id':str(org.id)}
        if get_user_model().objects.filter(username__in=USERNAMES).exists():s.fail('EXISTING_ACCOUNTS','동일 사용자 ID가 존재하여 초기 구성을 중단했습니다. 기존 비밀번호는 변경하지 않았습니다.',409)
        if set(passwords)!=set(USERNAMES) or len(set(passwords.values()))!=5:s.fail('INVALID_PASSWORDS','다섯 계정의 서로 다른 초기 비밀번호가 필요합니다.')
        if ProcessDefinition.objects.filter(organization=org,code__in=['SR_STANDARD_SCREEN','SR_STANDARD_APPROVAL','SR_STANDARD']).exists() or CatalogItem.objects.filter(organization=org,code='SR_STANDARD_REQUEST').exists():s.fail('EXISTING_DEFINITION','동일 코드의 구성이 존재합니다. 덮어쓰지 않습니다.',409)
        if ProcessBinding.objects.filter(organization=org,menu_key='service-request').exists():s.fail('EXISTING_BINDING','기존 서비스요청 메뉴 연결이 존재합니다. 덮어쓰지 않습니다.',409)
        request_dept,_=Department.objects.get_or_create(organization=org,code='SR_REQUEST_DEPT',defaults={'name':'요청부서'})
        ops_dept,_=Department.objects.get_or_create(organization=org,code='SR_OPERATIONS_DEPT',defaults={'name':'서비스 운영부서'})
        group=Group.objects.create(organization=org,code='SR_INTAKE',name='서비스요청 접수그룹',description='접수·담당자 배정 및 선택된 담당자의 서비스요청 조치')
        audience=Group.objects.create(organization=org,code='SR_REQUESTERS',name='서비스요청 신청대상',description='서비스요청 초기 프로세스 신청 가능 사용자')
        people={}
        for name,label in [('user1','요청자'),('user_auth1','요청부서 승인자'),('worker1','운영자1'),('worker2','운영자2'),('worker3','운영자3')]:
            user=get_user_model().objects.create_user(username=name,password=None)
            person=Person.objects.create(organization=org,user=user,display_name=label,department=ops_dept if name.startswith('worker') else request_dept)
            change_password(person,passwords[name],force=force_change);people[name]=person
            if name.startswith('worker'):
                RoleGrant.objects.create(organization=org,person=person,role='AGENT');Membership.objects.create(organization=org,person=person,group=group)
        Membership.objects.create(organization=org,person=people['user1'],group=audience)
        clear()
        reason='사용자 요청에 따른 초기 구성 · 자동 검증(수동 독립 검토 아님)'
        def publish(code,name,kind,graph):
            normalized=engine.validate(actor,kind,graph)
            definition=ProcessDefinition.objects.create(organization=org,code=code,name=name,kind=kind,draft=normalized,draft_author=actor)
            version=ProcessVersion.objects.create(organization=org,definition=definition,version=1,graph=normalized,digest=engine.digest(normalized),published_by=actor,reviewed_by=actor,reason=reason)
            definition.published=version;definition.save(update_fields=['published']);s.record(actor,definition,'PROCESS_PRESET_PUBLISHED',uuid.uuid4(),after={'version_id':str(version.id),'automatic_validation':True,'reason':reason});return version
        fields=[dict(key='title',label='요청 제목',type='text',required=True),dict(key='description',label='요청 내용',type='text',required=True),dict(key='assignee',label='조치 담당자',type='person',required=False,group_id=str(group.id)),dict(key='receipt_note',label='접수 의견',type='text',required=False),dict(key='resolution',label='조치 내용',type='text',required=False),dict(key='confirmed',label='조치 결과 확인',type='boolean',required=False),dict(key='feedback',label='사용자 확인 의견',type='text',required=False)]
        screen=publish('SR_STANDARD_SCREEN','서비스요청 공통 화면','SCREEN',dict(fields=fields,read_only=[],columns=2))
        approval=publish('SR_STANDARD_APPROVAL','요청부서 결재선','APPROVAL',dict(stages=[dict(key='department_approve',label='요청부서 결재자 승인',selector=dict(kind='USER',ids=[str(people['user_auth1'].id)]),mode='ALL')]))
        def modes(read,edit=()):return {f['key']:'EDIT' if f['key'] in edit else 'READ' if f['key'] in read else 'HIDDEN' for f in fields}
        nodes=[dict(key='register',label='서비스 요청 등록',type='START',next='department_approve'),dict(key='department_approve',label='요청부서 결재자 승인',type='APPROVAL',version_id=str(approval.id),field_modes=modes(['title','description']),next='receive'),dict(key='receive',label='접수 및 담당자 배정',type='TASK',selector=dict(kind='GROUP',ids=[str(group.id)]),mode='ANY',field_modes=modes(['title','description'],['assignee','receipt_note']),required_fields=['assignee'],next='action'),dict(key='action',label='조치',type='TASK',selector=dict(kind='FIELD_USER',ids=['assignee']),mode='ANY',field_modes=modes(['title','description','assignee','receipt_note'],['resolution']),required_fields=['resolution'],next='confirm'),dict(key='confirm',label='사용자 확인',type='TASK',selector=dict(kind='STARTER',ids=[]),mode='ANY',field_modes=modes(['title','description','resolution'],['confirmed','feedback']),required_fields=['confirmed'],next='confirmation_result'),dict(key='confirmation_result',label='사용자 확인 결과',type='CONDITION',condition=dict(field='confirmed',op='eq',value=True),true='close',false='action'),dict(key='close',label='종료',type='END')]
        workflow=publish('SR_STANDARD','서비스요청 표준 프로세스','WORKFLOW',dict(start='register',catalog_only=True,fields=fields,nodes=nodes,screen_version_id=str(screen.id),close_on_complete=True,ticket_assignee_field='assignee'))
        ProcessBinding.objects.create(organization=org,menu_key='service-request',version=workflow,updated_by=actor,reason=reason)
        # This initial catalogue publication is trusted provisioning. No service
        # management role is added to the system administrator as a side effect.
        from .models import CatalogVersion,CatalogAudience
        item=CatalogItem.objects.create(organization=org,code='SR_STANDARD_REQUEST')
        entry=CatalogVersion.objects.create(organization=org,item=item,version=1,name='서비스 요청',description='등록 → 요청부서 승인 → 접수·담당자 배정 → 조치 → 사용자 확인 → 종료',fulfillment_group=group,approval_required=False,approver=None,public_to_org=False,available=True,fields=[f for f in fields if f['key'] in ('title','description')],workflow_version=workflow)
        CatalogAudience.objects.create(organization=org,catalog_version=entry,group=audience)
        SecurityEvent.objects.create(organization=org,person=actor,action=MARKER,request_id=uuid.uuid4())
        s.record(actor,entry,'SERVICE_REQUEST_PRESET_CONFIGURED',uuid.uuid4(),after={'workflow_id':str(workflow.definition_id),'screen_id':str(screen.definition_id),'catalog_id':str(item.id),'intake_group_id':str(group.id),'user_ids':{k:str(v.id) for k,v in people.items()}})
        return dict(retained=False,workflow_id=str(workflow.definition_id),workflow_version_id=str(workflow.id),catalog_id=str(item.id),group_id=str(group.id),people={name:str(person.id) for name,person in people.items()})


def verify_configuration(organization_id,passwords):
    """Exercise the live configuration in a rolled-back transaction; no test tickets remain."""
    from .models import CatalogVersion,ProcessRun,Ticket,TimelinessTarget
    from .services import BusinessError
    with transaction.atomic():
        people={name:Person.objects.get(organization_id=organization_id,user__username=name) for name in USERNAMES}
        if any(not people[name].user.check_password(passwords[name]) for name in USERNAMES):s.fail('LOGIN_VERIFICATION_FAILED','초기 계정 인증 검증에 실패했습니다.')
        version=CatalogVersion.objects.get(organization_id=organization_id,item__code='SR_STANDARD_REQUEST',version=1)
        created,_=s.execute(people['user1'],'req_create',{'catalog_version_id':str(version.id),'values':{'title':'[자동 검증] 서비스요청','description':'초기 구성 검증 · 트랜잭션 롤백'}},uuid.uuid4().hex,uuid.uuid4())
        run=ProcessRun.objects.get(ticket_id=created['id'])
        def act(name,key,values=None,decision='COMPLETE'):
            run.refresh_from_db();task=run.tasks.get(status='OPEN')
            if task.node_key!=key:s.fail('WRONG_STAGE','서비스요청 단계 연결이 일치하지 않습니다.')
            result,_=s.execute(people[name],'flow_act',dict(task_id=str(task.id),expected_version=run.row_version,decision=decision,values=values or {},reason='초기 구성 자동 검증'),uuid.uuid4().hex,uuid.uuid4(),run.id)
            return result
        approval=run.tasks.get(status='OPEN')
        if approval.person_ids!=[str(people['user_auth1'].id)]:s.fail('WRONG_APPROVER','요청부서 승인자 할당이 일치하지 않습니다.')
        act('user_auth1',approval.node_key,decision='APPROVE')
        task=run.tasks.get(status='OPEN')
        if set(task.person_ids)!={str(people[n].id) for n in ('worker1','worker2','worker3')}:s.fail('WRONG_GROUP','접수그룹 할당이 일치하지 않습니다.')
        act('worker1','receive',{'assignee':str(people['worker2'].id),'receipt_note':'운영자2 배정'})
        run.refresh_from_db()
        if run.tasks.get(status='OPEN').person_ids!=[str(people['worker2'].id)]:s.fail('WRONG_ASSIGNEE','조치 담당자 할당이 일치하지 않습니다.')
        act('worker2','action',{'resolution':'조치 완료'})
        run.refresh_from_db()
        if run.tasks.get(status='OPEN').person_ids!=[str(people['user1'].id)]:s.fail('WRONG_REQUESTER','신청자 확인 할당이 일치하지 않습니다.')
        act('user1','confirm',{'confirmed':False,'feedback':'재조치 확인'})
        act('worker2','action',{'resolution':'재조치 완료'})
        act('user1','confirm',{'confirmed':True,'feedback':'정상 확인'})
        run.refresh_from_db();ticket=Ticket.objects.get(id=run.ticket_id)
        if run.status!='COMPLETED' or ticket.status!='CLOSED' or ticket.assignee_id!=people['worker2'].id or not TimelinessTarget.objects.get(ticket=ticket).completed_at:s.fail('INCOMPLETE_FLOW','서비스요청 종료·담당자·완료시각 검증에 실패했습니다.')
        transaction.set_rollback(True)
    return {'verified':True,'accounts':5,'stages':'register>approve>receive>action>confirm>close','rework_verified':True,'test_data_retained':False}
