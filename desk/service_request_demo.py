"""서비스요청 표준 프로세스 초기 구성(역할별 사용자·화면 템플릿·워크플로우·기준정보·예시 요청).

- 기존 계정은 재사용하며 비밀번호를 바꾸지 않는다. 없는 계정만 만든다.
- 화면 템플릿은 디자이너가 작성하고 개발자가 독립 검토한 뒤 디자이너가 게시한다.
  결재선·워크플로우는 개발자가 작성하고 시스템 관리자가 독립 검토한 뒤 개발자가 게시한다.
  모두 운영 콘솔과 같은 업무 명령(flow_save/review/publish)을 사용하며 감사 이력에 남는다.
- 기존 SR_STANDARD 화면·결재선·워크플로우·카탈로그에 새 게시 버전을 추가한다. 이전 게시 버전과
  진행 중인 요청은 그대로 두고, 이전 초안은 *_B20261118 정의로 보관한다.
- 업무 달력·적기처리 기준·장애 SLA가 없을 때만 초기값을 만든다.
- SR_DEMO_20261118 마커가 있으면 다시 실행해도 아무것도 바꾸지 않는다.
"""
import time
import uuid
from django.contrib.auth import get_user_model
from django.db import transaction
from . import services as s
from .access_cache import clear
from .models import (Organization, Person, Department, Group, Membership, RoleGrant, RoleDefinition, CustomRoleGrant,
                     ProcessDefinition, ProcessVersion, ProcessBinding, SecurityEvent, CatalogItem, CatalogVersion,
                     CommonCodeGroup, CommonCodeItem, TimelinessPolicy, Ticket, ProcessRun, TimelinessTarget,
                     BusinessCalendar, SLAPolicy, RoleMenuPolicy)
from .security_policy import change_password

MARKER = 'SR_DEMO_20261118'
ACCOUNTS = {'user1': '요청자', 'user_auth1': '요청부서 승인자', 'worker1': '운영자1', 'worker2': '운영자2',
            'developer1': '개발자', 'designer1': '디자이너'}
DEPARTMENT_OF = {'user1': 'SR_REQUEST_DEPT', 'user_auth1': 'SR_REQUEST_DEPT', 'worker1': 'SR_OPERATIONS_DEPT',
                 'worker2': 'SR_OPERATIONS_DEPT', 'developer1': 'SR_DEV_DEPT', 'designer1': 'SR_DEV_DEPT'}
DEPARTMENTS = [('SR_REQUEST_DEPT', '요청부서'), ('SR_OPERATIONS_DEPT', '서비스 운영부서'), ('SR_DEV_DEPT', '개발부서')]
CATEGORIES = [('ACCOUNT', '계정'), ('ACCESS', '권한'), ('SOFTWARE', '소프트웨어'), ('DEVICE', '장비'), ('OTHER', '기타')]
# 장애 우선순위별 초기 권장값(업무분): 응답, 해결. 조직 합의 후 SLA 화면에서 새 버전으로 조정한다.
INCIDENT_SLA = [(1, 30, 240), (2, 60, 540), (3, 240, 1620), (4, 540, 2700), (5, 1080, 5400)]
FIXED_HOLIDAYS = ['01-01', '03-01', '05-05', '06-06', '08-15', '10-03', '10-09', '12-25']
REASON = '사용자 요청에 따른 서비스요청 표준 프로세스 초기 구성'
CATALOG_NAME = '서비스요청 · 승인부터 만족도까지'


def people_for(org):
    return {p.user.username: p for p in Person.objects.filter(organization=org, user__username__in=ACCOUNTS).select_related('user')}


def report(org):
    ps = people_for(org)
    item = CatalogItem.objects.get(organization=org, code='SR_STANDARD_REQUEST')
    v = CatalogVersion.objects.filter(item=item).order_by('-version').first()
    tickets = Ticket.objects.filter(organization=org, service_request__catalog_version=v, title__startswith='[실습]').order_by('created_at', 'id')
    return {'organization_id': str(org.id), 'users': {k: str(p.id) for k, p in ps.items()}, 'catalog_id': str(item.id),
            'workflow_version_id': str(v.workflow_version_id),
            'tickets': [{'id': str(t.id), 'number': t.number, 'title': t.title, 'status': t.status,
                         'stage': current_stage(t)} for t in tickets], 'retained': True}


def current_stage(ticket):
    run = ProcessRun.objects.filter(ticket=ticket).first()
    task = run.tasks.filter(status='OPEN').first() if run else None
    return task.node_key.split('__')[0] if task else (run.status if run else '')


def _authorized(person):
    """Provisioning has no browser session; mark the fresh re-authentication explicitly."""
    person._recent_auth = time.time()
    return person


def run_command(person, operation, data, target=None):
    result, _ = s.execute(_authorized(person), operation, data, uuid.uuid4().hex, uuid.uuid4(), target)
    return result


def publish(org, author, reviewer, code, name, kind, graph):
    """작성자 초안 저장 → 다른 검토자 독립 검토 → 작성자 게시. 기존 정의면 새 버전을 추가한다."""
    d = ProcessDefinition.objects.filter(organization=org, code=code).first()
    if d and d.kind != kind:
        s.fail('INVALID_DEFINITION', '같은 코드의 정의 종류가 다릅니다.', 409)
    if d:
        ProcessDefinition.objects.get_or_create(organization=org, code=d.code + '_B20261118', defaults={
            'name': d.name + ' · 이전 초안 보관', 'kind': kind, 'draft': d.draft, 'draft_author': d.draft_author, 'active': False})
    saved = run_command(author, 'flow_save', dict(kind=kind, code=code, name=name, graph=graph, active=True,
                        expected_version=d.row_version if d else 0, reason=REASON), str(d.id) if d else None)
    if saved['validation_errors']:
        s.fail('INVALID_TEMPLATE', name + ' 검증 오류: ' + '; '.join(saved['validation_errors']))
    reviewed = run_command(reviewer, 'flow_review', dict(expected_version=saved['version'], reason='초기 구성 독립 검토: ' + name), saved['id'])
    run_command(author, 'flow_publish', dict(expected_version=reviewed['version'], reason=REASON), saved['id'])
    return ProcessDefinition.objects.get(id=saved['id']).published


def f(key, label, type='text', required=False, **kw):
    return dict(key=key, label=label, type=type, required=required, **kw)


def build_fields(intake_group, dev_group=None):
    return [
        f('title', '요청 제목', required=True, max_length=180), f('description', '요청 내용', required=True, max_length=2000),
        f('category', '요청 구분', required=True), f('service_system', '대상 시스템', required=True),
        f('request_priority', '요청 우선순위', type='number', required=True, minimum=1, maximum=3),
        f('requested_due', '희망 완료일'), f('request_contact', '요청 연락처'),
        f('assignee', '조치 담당자', 'person', group_id=str(intake_group.id)), f('receipt_note', '접수·배정 의견'),
        f('planned_finish', '처리 예정일시', 'datetime'),
        f('dev_required', '개발 필요 여부', 'boolean', description='예: 개발자 개발 후 담당자 조치 / 아니오: 담당자가 바로 조치'),
        f('dev_content', '개발 내용', 'textarea', max_length=4000), f('dev_artifacts', '변경 프로그램·산출물', 'textarea', max_length=4000),
        f('dev_done', '개발 완료일', 'date'),
        f('resolution', '조치 내용'), f('root_cause', '원인·참고 사항'), f('action_started', '조치 시작일시', 'datetime'),
        f('action_finished', '조치 완료일시', 'datetime'), f('work_minutes', '작업 시간(분)', 'integer', minimum=0, maximum=100000),
        f('confirmed', '조치 결과 정상 확인', 'boolean'), f('feedback', '결과 확인·재조치 의견'),
        f('satisfaction', '만족도(1~5점)', 'integer', minimum=1, maximum=5), f('survey_comment', '만족도 의견'),
    ]


GROUP_KEYS = {
    'request': ['title', 'description', 'category', 'service_system', 'request_priority', 'requested_due', 'request_contact'],
    'receipt': ['dev_required', 'assignee', 'receipt_note', 'planned_finish'],
    'development': ['dev_content', 'dev_artifacts', 'dev_done'],
    'work': ['resolution', 'root_cause', 'action_started', 'action_finished', 'work_minutes'],
    'confirmation': ['confirmed', 'feedback'],
    'survey': ['satisfaction', 'survey_comment'],
}
GROUP_LABELS = {'request': '요청 기본정보', 'receipt': '접수 및 배정', 'development': '개발', 'work': '담당자 조치',
                'confirmation': '조치결과 확인', 'survey': '만족도 조사'}
WIDE = {'title', 'description', 'resolution', 'receipt_note', 'feedback', 'survey_comment', 'dev_content', 'dev_artifacts'}
TALL = {'description': 3, 'resolution': 3, 'dev_content': 3, 'dev_artifacts': 2}
NODE_LABELS = {'register': '요청 등록', 'department_approve': '요청부서 승인', 'receive': '접수 및 담당자 배정',
               'development_check': '개발 필요 여부', 'development': '개발', 'action': '담당자 조치',
               'confirm': '조치결과 확인', 'confirmation_result': '정상 확인 여부', 'survey': '만족도 조사', 'close': '종료'}


def screen_graph(fields):
    layout = dict(mode='sections', groups=[dict(key=k, label=GROUP_LABELS[k], fields=[
        dict(key=key, span=2 if key in WIDE else 1, height=TALL.get(key, 1)) for key in vals]) for k, vals in GROUP_KEYS.items()])
    return dict(fields=fields, read_only=[], columns=2, layout=layout)


def workflow_graph(fields, screen, approval, intake_group, dev_group):
    def node(key, type, next=None, read=(), edit=(), required=(), **kw):
        result = dict(key=key, label=NODE_LABELS[key], type=type, **kw)
        if next:
            result['next'] = next
        if type in ('TASK', 'APPROVAL'):
            result.update(group_modes={k: 'EDIT' if k in edit else 'READ' if k in read else 'HIDDEN' for k in GROUP_KEYS},
                          required_fields=list(required))
        return result
    nodes = [
        node('register', 'START', 'department_approve'),
        node('department_approve', 'APPROVAL', 'receive', read=['request'], version_id=str(approval.id)),
        node('receive', 'TASK', 'development_check', read=['request'], edit=['receipt'], required=['dev_required', 'assignee', 'receipt_note'],
             selector=dict(kind='GROUP', ids=[str(intake_group.id)]), mode='ANY'),
        node('development_check', 'CONDITION', condition=dict(field='dev_required', op='eq', value=True), true='development', false='action'),
        node('development', 'TASK', 'action', read=['request', 'receipt'], edit=['development'], required=['dev_content', 'dev_done'],
             selector=dict(kind='GROUP', ids=[str(dev_group.id)]), mode='ANY'),
        node('action', 'TASK', 'confirm', read=['request', 'receipt', 'development'], edit=['work'], required=['resolution'],
             selector=dict(kind='FIELD_USER', ids=['assignee']), mode='ANY'),
        node('confirm', 'TASK', 'confirmation_result', read=['request', 'development', 'work'], edit=['confirmation'], required=['confirmed'],
             selector=dict(kind='STARTER', ids=[]), mode='ANY'),
        node('confirmation_result', 'CONDITION', condition=dict(field='confirmed', op='eq', value=True), true='survey', false='action'),
        node('survey', 'TASK', 'close', read=['request', 'development', 'work', 'confirmation'], edit=['survey'], required=['satisfaction'],
             selector=dict(kind='STARTER', ids=[]), mode='ANY'),
        node('close', 'END'),
    ]
    return dict(start='register', catalog_only=True, fields=fields, nodes=nodes, screen_version_id=str(screen.id),
                close_on_complete=True, ticket_assignee_field='assignee')


def catalog_fields(fields):
    kinds = {'request_priority': 'integer', 'category': 'choice', 'requested_due': 'date', 'description': 'textarea'}
    return [dict(key=x['key'], label=x['label'], type=kinds.get(x['key'], 'text'), required=x['required'],
                 **({'options': [v for _, v in CATEGORIES]} if x['key'] == 'category' else {})) for x in fields if x['key'] in GROUP_KEYS['request']]


def baseline_service_settings(org, manager, admin):
    """업무 달력·적기처리 기준·장애 SLA·서비스 관리자 콘솔 접근. 이미 있으면 두지 않는다."""
    calendar = BusinessCalendar.objects.filter(organization=org).order_by('-created_at').first()
    if not calendar:
        holidays = [f'{year}-{day}' for year in (2026, 2027) for day in FIXED_HOLIDAYS]
        made = run_command(manager, 'sla_calendar', dict(name='기본 업무 달력(평일 09:00~18:00)', timezone='Asia/Seoul',
                           weekdays=[0, 1, 2, 3, 4], starts_at='09:00', ends_at='18:00', holidays=holidays))
        calendar = BusinessCalendar.objects.get(id=made['id'])
    for priority, response, resolution in INCIDENT_SLA:
        if not SLAPolicy.objects.filter(organization=org, priority=priority).exists():
            run_command(manager, 'sla_policy', dict(name='장애 P%d 기본 SLA' % priority, calendar_id=str(calendar.id), priority=priority,
                        response_minutes=response, resolution_minutes=resolution, warning_percent=80, pause_on_pending=True))
    if not TimelinessPolicy.objects.filter(organization=org, ticket_type='SERVICE_REQUEST').exists():
        run_command(manager, 'kpi_policy', dict(name='서비스요청 기본 처리기한(3영업일)', ticket_type='SERVICE_REQUEST', basis='RECEIPT',
                    target_minutes=3 * 9 * 60, calendar_id=str(calendar.id), expected_version=0, reason=REASON))
    if not RoleMenuPolicy.objects.filter(organization=org, role_key='SERVICE_MANAGER').exists():
        from .menu_access import role_menus
        menus = sorted(role_menus(org, 'SERVICE_MANAGER')[0])
        RoleMenuPolicy.objects.create(organization=org, role_key='SERVICE_MANAGER', menu_keys=menus, console_button=True)
        s.record(admin, org, 'SR_DEMO_SERVICE_MANAGER_CONSOLE', uuid.uuid4(), after={'menu_keys': menus, 'console_button': True, 'reason': REASON})
        clear()


SAMPLES = [
    dict(stage='department_approve', values=dict(title='[실습] 신규 입사자 그룹웨어 계정 생성', category='계정', service_system='그룹웨어', request_priority=1,
         requested_due='2026-11-20', description='11월 18일 입사 예정자 2명의 그룹웨어 계정과 메일 계정 생성을 요청합니다.')),
    dict(stage='receive', values=dict(title='[실습] 프로젝트 공유폴더 접근 권한', category='권한', service_system='파일서버', request_priority=2,
         description='차세대 프로젝트 공유폴더 읽기·쓰기 권한이 필요합니다.')),
    dict(stage='development', values=dict(title='[실습] 고객 상담 이력 조회 화면 개발', category='소프트웨어', service_system='고객관리(CRM)', request_priority=2,
         requested_due='2026-12-15', description='고객별 최근 1년 상담 이력을 한 화면에서 조회하고 상담 유형별로 필터링하는 화면을 요청합니다.'),
         receive=dict(dev_required=True, assignee='worker1', receipt_note='화면 신규 개발 필요. 개발 완료 후 운영자1이 운영 반영합니다.')),
    dict(stage='confirm', values=dict(title='[실습] 업무 노트북 화상회의 점검', category='장비', service_system='업무 노트북', request_priority=3,
         description='화상회의 중 마이크가 자주 끊깁니다. 장비 점검을 요청합니다.'),
         receive=dict(dev_required=False, assignee='worker2', receipt_note='장비 점검 건. 운영자2 조치.'),
         action=dict(resolution='오디오 드라이버를 최신 버전으로 업데이트하고 화상회의 시험 통화로 정상 동작을 확인했습니다.', root_cause='구버전 오디오 드라이버', work_minutes=40)),
    dict(stage='close', values=dict(title='[실습] ERP 월 마감 조회 오류', category='기타', service_system='ERP', request_priority=1,
         description='ERP 월 마감 조회 화면에서 기간을 지정하면 오류가 표시됩니다.'),
         receive=dict(dev_required=True, assignee='worker1', receipt_note='조회 프로그램 수정 필요.'),
         development=dict(dev_content='월 마감 조회의 기간 조건 처리 오류를 수정했습니다.', dev_artifacts='closing/MonthlyQuery.java', dev_done='2026-11-17'),
         action=dict(resolution='수정 프로그램을 운영 서버에 반영하고 조회를 확인했습니다.', work_minutes=30),
         confirm=dict(confirmed=True, feedback='정상 조회됩니다.'), survey=dict(satisfaction=5, survey_comment='빠르게 처리해 주셔서 감사합니다.')),
]
ORDER = ['department_approve', 'receive', 'development', 'action', 'confirm', 'survey', 'close']


def advance_sample(people, run, sample):
    def act(who, key, values=None, decision='COMPLETE'):
        run.refresh_from_db()
        task = run.tasks.get(status='OPEN')
        if task.node_key.split('__')[0] != key:
            s.fail('WRONG_STAGE', '예시 요청 단계가 일치하지 않습니다: ' + task.node_key)
        s.execute(people[who], 'flow_act', dict(task_id=str(task.id), expected_version=run.row_version, decision=decision,
                  values=values or {}, reason='예시 데이터 처리'), uuid.uuid4().hex, uuid.uuid4(), run.id)
    target = ORDER.index(sample['stage'])
    if target > 0:
        act('user_auth1', 'department_approve', decision='APPROVE')
    if target > 1:
        act('worker1', 'receive', {**sample['receive'], 'assignee': str(people[sample['receive']['assignee']].id)})
    if target > 2 and sample['receive']['dev_required']:
        act('developer1', 'development', sample['development'])
    if target > 3:
        act(sample['receive']['assignee'], 'action', sample['action'])
    if target > 4:
        act('user1', 'confirm', sample['confirm'])
    if target > 5:
        act('user1', 'survey', sample['survey'])


@transaction.atomic
def configure(organization_id, passwords, seed=True):
    org = Organization.objects.select_for_update().get(pk=organization_id)
    if SecurityEvent.objects.filter(organization=org, action=MARKER).exists():
        return report(org)
    admin = Person.objects.filter(organization=org, rolegrant__role='ORG_ADMIN', active=True, user__is_active=True).order_by('created_at').first()
    if not admin:
        s.fail('NO_ADMIN', '초기 구성 관리자 계정이 필요합니다.')
    departments = {}
    for code, name in DEPARTMENTS:
        departments[code], _ = Department.objects.get_or_create(organization=org, code=code, defaults={'name': name})
    # Global login names must never accidentally attach another organization's account.
    people = {}
    for username, label in ACCOUNTS.items():
        user = get_user_model().objects.filter(username=username).first()
        if user:
            person = Person.objects.filter(user=user, organization=org, active=True).first()
            if not person or not user.is_active:
                s.fail('ACCOUNT_SCOPE', '기존 계정의 조직/활성 상태를 확인하십시오.', 409)
        else:
            if not passwords.get(username):
                s.fail('MISSING_PASSWORD', '없는 계정에 대한 서로 다른 초기 비밀번호가 필요합니다.')
            user = get_user_model().objects.create_user(username=username, password=None)
            person = Person.objects.create(organization=org, user=user, display_name=label, department=departments[DEPARTMENT_OF[username]])
            change_password(person, passwords[username], force=True)
        if not person.department_id:
            person.department = departments[DEPARTMENT_OF[username]]
            person.save(update_fields=['department'])
        people[username] = person
    if people['user1'].department_id != people['user_auth1'].department_id:
        s.fail('APPROVER_DEPARTMENT', '요청자와 요청부서 승인자의 부서를 확인하십시오.', 409)
    for username in ('worker1', 'worker2', 'developer1'):
        RoleGrant.objects.get_or_create(organization=org, person=people[username], role='AGENT')
    RoleGrant.objects.get_or_create(organization=org, person=people['developer1'], role='DEVELOPER')
    role, _ = RoleDefinition.objects.get_or_create(organization=org, code='SR_DESIGNER', defaults={
        'name': '서비스요청 디자이너', 'permissions': ['console.access', 'workflow.manage', 'entity.read', 'code.read', 'service.manage']})
    CustomRoleGrant.objects.get_or_create(organization=org, person=people['designer1'], role=role)
    group, _ = Group.objects.get_or_create(organization=org, code='SR_DEMO_INTAKE', defaults={'name': '서비스요청 접수그룹 · 만족도 프로세스', 'description': '운영자1/2 접수·배정 및 조치'})
    for username in ('worker1', 'worker2'):
        Membership.objects.get_or_create(organization=org, person=people[username], group=group)
    dev_group, _ = Group.objects.get_or_create(organization=org, code='SR_DEV', defaults={'name': '서비스요청 개발그룹', 'description': '개발이 필요한 서비스요청의 개발 담당'})
    Membership.objects.get_or_create(organization=org, person=people['developer1'], group=dev_group)
    audience, _ = Group.objects.get_or_create(organization=org, code='SR_REQUESTERS', defaults={'name': '서비스요청 신청대상'})
    Membership.objects.get_or_create(organization=org, person=people['user1'], group=audience)
    clear()
    cg, _ = CommonCodeGroup.objects.get_or_create(organization=org, code='SR_DEMO_CATEGORY', defaults={'name': '서비스요청 구분(실습)', 'description': '카탈로그 선택지의 초기 기준 코드'})
    for i, (code, label) in enumerate(CATEGORIES):
        CommonCodeItem.objects.get_or_create(organization=org, group=cg, code=code, defaults={'label': label, 'sort_order': i + 1})
    from .permissions import people_with
    manager = people_with(org, 'service.manage').exclude(id=people['designer1'].id).order_by('created_at').first() or people['designer1']
    baseline_service_settings(org, manager, admin)

    designer, developer = people['designer1'], people['developer1']
    fields = build_fields(group, dev_group)
    screen = publish(org, designer, developer, 'SR_STANDARD_SCREEN', '서비스요청 공통 화면 · 만족도 템플릿', 'SCREEN', screen_graph(fields))
    approval = publish(org, developer, admin, 'SR_STANDARD_APPROVAL', '요청부서 결재선', 'APPROVAL', dict(stages=[
        dict(key='department_approve', label='요청부서 승인', selector=dict(kind='USER', ids=[str(people['user_auth1'].id)]), mode='ALL')]))
    workflow = publish(org, developer, admin, 'SR_STANDARD', '서비스요청 표준 프로세스 · 만족도', 'WORKFLOW',
                       workflow_graph(fields, screen, approval, group, dev_group))
    binding = ProcessBinding.objects.filter(organization=org, menu_key='service-request').first()
    run_command(developer, 'flow_bind', dict(version_id=str(workflow.id), expected_version=binding.row_version if binding else 0, reason=REASON), 'service-request')
    item = CatalogItem.objects.filter(organization=org, code='SR_STANDARD_REQUEST').first()
    latest = CatalogVersion.objects.filter(item=item).order_by('-version').first() if item else None
    entry = run_command(designer, 'catalog_publish', dict(code='SR_STANDARD_REQUEST', name=CATALOG_NAME,
        description='등록 → 부서 승인 → 접수·배정 → (개발) → 조치 → 확인 → 만족도 조사 → 자동 종료',
        fulfillment_group_id=str(group.id), approval_required=False, approver_id=None, public_to_org=False,
        audience_group_ids=[str(audience.id)], available=True, fields=catalog_fields(fields),
        expected_version=latest.version if latest else 0, workflow_version_id=str(workflow.id)))
    verify(org)
    if seed:
        for sample in SAMPLES:
            created = run_command(people['user1'], 'req_create', dict(catalog_version_id=entry['catalog_version_id'], values=sample['values']))
            advance_sample(people, ProcessRun.objects.get(ticket_id=created['id']), sample)
    SecurityEvent.objects.create(organization=org, person=admin, action=MARKER, request_id=uuid.uuid4())
    s.record(admin, CatalogItem.objects.get(organization=org, code='SR_STANDARD_REQUEST'), 'SR_DEMO_READY', uuid.uuid4(), after={
        'workflow_version_id': str(workflow.id), 'screen_version_id': str(screen.id), 'independent_review': True,
        'sample_count': len(SAMPLES) if seed else 0})
    return {**report(org), 'retained': False}


def verify(org):
    """Real command path, rolled back; retains no verification request/vote/history."""
    with transaction.atomic():
        ps = people_for(org)
        v = CatalogVersion.objects.filter(organization=org, item__code='SR_STANDARD_REQUEST').order_by('-version').first()
        created, _ = s.execute(ps['user1'], 'req_create', {'catalog_version_id': str(v.id), 'values': dict(
            title='[자동 검증] 삭제될 요청', description='롤백 검증', category='계정', service_system='검증', request_priority=2)}, uuid.uuid4().hex, uuid.uuid4())
        run = ProcessRun.objects.get(ticket_id=created['id'])

        def act(who, key, values=None, decision='COMPLETE'):
            run.refresh_from_db()
            task = run.tasks.get(status='OPEN')
            if task.node_key.split('__')[0] != key:
                raise AssertionError((task.node_key, key))
            return s.execute(ps[who], 'flow_act', dict(task_id=str(task.id), expected_version=run.row_version, decision=decision,
                             values=values or {}, reason='사전 구성 롤백 검증'), uuid.uuid4().hex, uuid.uuid4(), run.id)
        act('user_auth1', 'department_approve', decision='APPROVE')
        act('worker1', 'receive', {'dev_required': True, 'assignee': str(ps['worker2'].id), 'receipt_note': '개발 후 운영자2 조치'})
        act('developer1', 'development', {'dev_content': '개발 완료', 'dev_done': '2026-11-18'})
        act('worker2', 'action', {'resolution': '조치 완료'})
        act('user1', 'confirm', {'confirmed': False, 'feedback': '재조치 요청'})
        act('worker2', 'action', {'resolution': '재조치 완료'})
        act('user1', 'confirm', {'confirmed': True, 'feedback': '정상 확인'})
        run.refresh_from_db()
        assert run.status == 'ACTIVE' and run.tasks.get(status='OPEN').node_key == 'survey'
        act('user1', 'survey', {'satisfaction': 5, 'survey_comment': '만족합니다.'})
        run.refresh_from_db()
        ticket = Ticket.objects.get(pk=run.ticket_id)
        assert run.status == 'COMPLETED' and ticket.status == 'CLOSED' and ticket.assignee_id == ps['worker2'].id
        assert TimelinessTarget.objects.get(ticket=ticket).completed_at
        transaction.set_rollback(True)
    return True
