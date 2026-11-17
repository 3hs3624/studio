"""IT 서비스 요청(개발·운영) 템플릿 구성.

기존 서비스요청 표준 구성(SR_STANDARD)을 변경하지 않고, 역할별 사용자·화면 템플릿·결재선·
워크플로우·카탈로그·기준정보·예시 요청을 일반 업무 명령으로 만든다.

- 화면은 디자이너가 초안을 저장하고 개발자가 독립 검토한 뒤 디자이너가 게시한다.
- 결재선·워크플로우는 개발자가 작성하고 시스템 관리자가 독립 검토한 뒤 개발자가 게시한다.
- 카탈로그·업무 달력·적기처리 기준은 서비스 관리자가 게시한다.
- 예시 요청은 요청자가 카탈로그로 신청하고 실제 담당자가 단계를 처리한다.

이미 같은 사용자 ID가 있으면 재사용하며 비밀번호를 바꾸지 않는다. 같은 코드의 구성이 있으면
덮어쓰지 않고 중단한다. 완료 마커가 있으면 다시 실행해도 아무것도 바꾸지 않는다.
"""
import time
import uuid
from django.contrib.auth import get_user_model
from django.db import transaction
from . import services as s
from .access_cache import clear
from .models import (BusinessCalendar, CatalogItem, CatalogVersion, CommonCodeGroup, CommonCodeItem,
                     CustomRoleGrant, Department, Group, Membership, Organization, Person, ProcessDefinition,
                     ProcessRun, RoleDefinition, RoleGrant, RoleMenuPolicy, SecurityEvent, TimelinessPolicy)
from .security_policy import change_password

MARKER = 'SR_TEMPLATE_PROVISIONED'
SAMPLE_MARKER = 'SR_TEMPLATE_SAMPLES_CREATED'
SCREEN_CODE = 'SR_TEMPLATE_SCREEN'
APPROVAL_CODE = 'SR_SERVICE_APPROVAL'
WORKFLOW_CODE = 'SR_SERVICE_FLOW'
CATALOG_CODE = 'SR_SERVICE_REQUEST'
DESIGNER_ROLE = 'SR_SCREEN_DESIGNER'

# username, 표시 이름, 역할 설명, 부서 코드
ACCOUNTS = [
    ('user1', '요청자', '요청자', 'SR_REQUEST_DEPT'),
    ('user_auth1', '요청부서 승인자', '요청부서 승인자', 'SR_REQUEST_DEPT'),
    ('worker1', '운영자1', '운영자1', 'SR_OPERATIONS_DEPT'),
    ('worker2', '운영자2', '운영자2', 'SR_OPERATIONS_DEPT'),
    ('developer1', '개발자', '개발자', 'SR_DEV_DEPT'),
    ('designer1', '디자이너', '디자이너', 'SR_DEV_DEPT'),
]
USERNAMES = [row[0] for row in ACCOUNTS]
DEPARTMENTS = [
    ('SR_REQUEST_DEPT', '요청부서', '서비스를 요청하고 요청부서장이 승인하는 현업 부서'),
    ('SR_OPERATIONS_DEPT', '서비스 운영부서', '서비스요청 접수·조치·운영 반영 담당'),
    ('SR_DEV_DEPT', '개발부서', '프로그램 개발과 화면 디자인 담당'),
]
REQUEST_TYPES = ['기능 개선', '신규 개발', '데이터 추출·변경', '계정·권한', '오류 문의', '기타']
TARGET_SYSTEMS = ['그룹웨어', 'ERP', '고객관리(CRM)', '홈페이지', 'ITSM', '기타']
URGENCIES = ['긴급', '높음', '보통', '낮음']
CODE_GROUPS = [
    ('SR_REQUEST_TYPE', '서비스요청 유형', '서비스요청 신청서의 요청 유형 선택지', REQUEST_TYPES),
    ('SR_TARGET_SYSTEM', '서비스요청 대상 시스템', '서비스요청 신청서의 대상 시스템 선택지', TARGET_SYSTEMS),
    ('SR_URGENCY', '서비스요청 긴급도', '서비스요청 신청서의 긴급도 선택지', URGENCIES),
]
# 장애 우선순위별 초기 권장값(업무분). 조직 합의 후 SLA 화면에서 새 버전으로 조정한다.
INCIDENT_SLA = [(1, 30, 240), (2, 60, 540), (3, 240, 1620), (4, 540, 2700), (5, 1080, 5400)]
REASON = '사용자 요청에 따른 IT 서비스 요청 템플릿 초기 구성'


def _authorized(person):
    """Provisioning runs without a browser session; mark the fresh re-authentication explicitly."""
    person._recent_auth = time.time()
    return person


def _run(person, operation, data, target=None):
    result, _ = s.execute(_authorized(person), operation, data, uuid.uuid4().hex, uuid.uuid4(), target)
    return result


def screen_fields(ops_group_id):
    """서비스요청 화면 템플릿 항목. 신청서 항목은 카탈로그 양식과 같은 키·유형으로 선언한다."""
    return [
        dict(key='title', label='요청 제목', type='text', required=True, max_length=200),
        dict(key='request_type', label='요청 유형', type='text', required=True, max_length=100),
        dict(key='target_system', label='대상 시스템', type='text', required=True, max_length=100),
        dict(key='urgency', label='긴급도', type='text', required=True, max_length=100),
        dict(key='due_date', label='희망 완료일', type='text', required=False, max_length=10,
             description='YYYY-MM-DD'),
        dict(key='description', label='요청 내용', type='text', required=True, max_length=2000),
        dict(key='expected_effect', label='요청 사유·기대 효과', type='text', required=False, max_length=2000),
        dict(key='dev_required', label='개발 필요 여부', type='boolean', required=False,
             description='예: 개발자 개발 후 운영 반영 / 아니오: 운영자가 바로 조치'),
        dict(key='operator', label='조치 담당 운영자', type='person', required=False, group_id=str(ops_group_id)),
        dict(key='planned_date', label='처리 예정일', type='date', required=False),
        dict(key='intake_note', label='접수 의견', type='textarea', required=False, max_length=4000),
        dict(key='dev_content', label='개발 내용', type='textarea', required=False, max_length=4000),
        dict(key='dev_artifacts', label='변경 프로그램·산출물', type='textarea', required=False, max_length=4000),
        dict(key='dev_done_date', label='개발 완료일', type='date', required=False),
        dict(key='action_content', label='조치·운영 반영 내용', type='textarea', required=False, max_length=4000),
        dict(key='action_date', label='조치 완료일', type='date', required=False),
        dict(key='confirmed', label='조치 결과 확인', type='boolean', required=False,
             description='예: 종료 / 아니오: 운영자 재조치'),
        dict(key='satisfaction', label='만족도(1~5)', type='integer', required=False),
        dict(key='feedback', label='확인 의견', type='textarea', required=False, max_length=4000),
    ]


GROUPS = [
    ('request', '요청 정보', ['title', 'request_type', 'target_system', 'urgency', 'due_date', 'description', 'expected_effect']),
    ('intake', '접수·배정', ['dev_required', 'operator', 'planned_date', 'intake_note']),
    ('development', '개발', ['dev_content', 'dev_artifacts', 'dev_done_date']),
    ('operation', '운영 조치', ['action_content', 'action_date']),
    ('confirmation', '사용자 확인', ['confirmed', 'satisfaction', 'feedback']),
]
WIDE = {'title', 'description', 'expected_effect', 'intake_note', 'dev_content', 'dev_artifacts', 'action_content', 'feedback'}
TALL = {'description': 3, 'expected_effect': 2, 'intake_note': 2, 'dev_content': 3, 'dev_artifacts': 2, 'action_content': 3, 'feedback': 2}


def screen_graph(ops_group_id):
    fields = screen_fields(ops_group_id)
    layout = dict(mode='sections', groups=[dict(key=key, label=label, fields=[
        dict(key=k, span=2 if k in WIDE else 1, height=TALL.get(k, 1)) for k in keys]) for key, label, keys in GROUPS])
    return dict(fields=fields, read_only=[], columns=2, layout=layout)


def node_modes(fields, read=(), edit=()):
    return {f['key']: 'EDIT' if f['key'] in edit else 'READ' if f['key'] in read else 'HIDDEN' for f in fields}


def group_modes(visible):
    return {key: ('EDIT' if key in visible else 'HIDDEN') for key, _, _ in GROUPS}


def workflow_graph(fields, screen_version_id, approval_version_id, ops_group_id, dev_group_id):
    request = [k for k in GROUPS[0][2]]
    intake = GROUPS[1][2]
    dev = GROUPS[2][2]
    ops = GROUPS[3][2]
    confirm = GROUPS[4][2]
    nodes = [
        dict(key='register', label='서비스 요청 등록', type='START', next='department_approval'),
        dict(key='department_approval', label='요청부서 승인', type='APPROVAL', version_id=str(approval_version_id),
             field_modes=node_modes(fields, request), group_modes=group_modes(['request']), next='intake'),
        dict(key='intake', label='접수·검토 및 담당자 배정', type='TASK', selector=dict(kind='GROUP', ids=[str(ops_group_id)]),
             mode='ANY', field_modes=node_modes(fields, request, intake), group_modes=group_modes(['request', 'intake']),
             required_fields=['dev_required', 'operator'], next='development_check'),
        dict(key='development_check', label='개발 필요 여부', type='CONDITION',
             condition=dict(field='dev_required', op='eq', value=True), true='development', false='operation'),
        dict(key='development', label='개발', type='TASK', selector=dict(kind='GROUP', ids=[str(dev_group_id)]), mode='ANY',
             field_modes=node_modes(fields, request + intake, dev), group_modes=group_modes(['request', 'intake', 'development']),
             required_fields=['dev_content', 'dev_done_date'], next='operation'),
        dict(key='operation', label='운영 조치·반영', type='TASK', selector=dict(kind='FIELD_USER', ids=['operator']), mode='ANY',
             field_modes=node_modes(fields, request + intake + dev, ops),
             group_modes=group_modes(['request', 'intake', 'development', 'operation']),
             required_fields=['action_content', 'action_date'], next='confirmation'),
        dict(key='confirmation', label='요청자 확인', type='TASK', selector=dict(kind='STARTER', ids=[]), mode='ANY',
             field_modes=node_modes(fields, request + intake + dev + ops, confirm),
             group_modes=group_modes([g[0] for g in GROUPS]), required_fields=['confirmed'], next='confirmation_result'),
        dict(key='confirmation_result', label='확인 결과', type='CONDITION',
             condition=dict(field='confirmed', op='eq', value=True), true='close', false='operation'),
        dict(key='close', label='종료', type='END'),
    ]
    return dict(start='register', catalog_only=True, fields=fields, nodes=nodes, screen_version_id=str(screen_version_id),
                close_on_complete=True, ticket_assignee_field='operator')


def catalog_form():
    return [
        dict(key='title', label='요청 제목', type='text', required=True),
        dict(key='request_type', label='요청 유형', type='choice', required=True, options=REQUEST_TYPES),
        dict(key='target_system', label='대상 시스템', type='choice', required=True, options=TARGET_SYSTEMS),
        dict(key='urgency', label='긴급도', type='choice', required=True, options=URGENCIES),
        dict(key='due_date', label='희망 완료일', type='date', required=False),
        dict(key='description', label='요청 내용', type='textarea', required=True),
        dict(key='expected_effect', label='요청 사유·기대 효과', type='textarea', required=False),
    ]


def _publish_definition(author, reviewer, kind, code, name, graph):
    saved = _run(author, 'flow_save', dict(kind=kind, code=code, name=name, graph=graph, active=True, expected_version=0, reason=REASON))
    if saved['validation_errors']:
        s.fail('INVALID_TEMPLATE', name + ' 검증 오류: ' + '; '.join(saved['validation_errors']))
    reviewed = _run(reviewer, 'flow_review', dict(expected_version=saved['version'], reason='초기 구성 독립 검토: ' + name), saved['id'])
    _run(author, 'flow_publish', dict(expected_version=reviewed['version'], reason=REASON), saved['id'])
    return ProcessDefinition.objects.get(id=saved['id']).published


def _person(org, username):
    return Person.objects.filter(organization=org, user__username=username).select_related('user').first()


def configure(organization_id, passwords=None, force_change=True):
    """Return a summary dict. Raises BusinessError without partial changes on conflicts."""
    passwords = passwords or {}
    with transaction.atomic():
        org = Organization.objects.select_for_update().get(id=organization_id)
        if SecurityEvent.objects.filter(organization=org, action=MARKER).exists():
            return {'retained': True, 'organization_id': str(org.id)}
        admin = Person.objects.filter(organization=org, rolegrant__role='ORG_ADMIN', active=True, user__is_active=True).order_by('created_at').first()
        if not admin:
            s.fail('NO_ADMIN', '조직의 시스템 관리자 계정이 필요합니다.')
        from .permissions import people_with
        manager = people_with(org, 'service.manage').order_by('created_at').first()
        if not manager:
            s.fail('NO_SERVICE_MANAGER', '카탈로그를 게시할 서비스 관리자 계정이 필요합니다.')
        if ProcessDefinition.objects.filter(organization=org, code__in=[SCREEN_CODE, APPROVAL_CODE, WORKFLOW_CODE]).exists() or CatalogItem.objects.filter(organization=org, code=CATALOG_CODE).exists():
            s.fail('EXISTING_DEFINITION', '동일 코드의 화면·워크플로우·카탈로그가 존재합니다. 덮어쓰지 않습니다.', 409)
        user_model = get_user_model()
        foreign = user_model.objects.filter(username__in=USERNAMES).exclude(person__organization=org)
        if foreign.exists():
            s.fail('EXISTING_ACCOUNTS', '다른 조직에 같은 사용자 ID가 있어 구성을 중단했습니다.', 409)
        missing = [name for name in USERNAMES if not _person(org, name)]
        if set(missing) - set(passwords) or len({passwords[n] for n in missing}) != len(missing):
            s.fail('INVALID_PASSWORDS', '새로 만들 계정(' + ', '.join(missing) + ')마다 서로 다른 초기 비밀번호가 필요합니다.')

        departments = {}
        for code, name, description in DEPARTMENTS:
            departments[code], _ = Department.objects.get_or_create(organization=org, code=code, defaults={'name': name, 'description': description})
        people, created = {}, []
        for username, display, _, department in ACCOUNTS:
            person = _person(org, username)
            if not person:
                user = user_model.objects.create_user(username=username, password=None)
                person = Person.objects.create(organization=org, user=user, display_name=display, department=departments[department])
                change_password(person, passwords[username], force=force_change)
                created.append(username)
            elif person.department_id is None:
                person.department = departments[department]
                person.save(update_fields=['department'])
            people[username] = person

        def group(code, name, description, members):
            value, _ = Group.objects.get_or_create(organization=org, code=code, defaults={'name': name, 'description': description})
            for member in members:
                Membership.objects.get_or_create(organization=org, group=value, person=people[member])
            return value
        ops_group = group('SR_OPS', '서비스요청 운영그룹', '서비스요청 접수·검토, 조치·운영 반영 담당 (운영자1·운영자2)', ['worker1', 'worker2'])
        dev_group = group('SR_DEV', '서비스요청 개발그룹', '개발이 필요한 서비스요청의 개발 담당', ['developer1'])
        audience = group('SR_REQUESTERS', '서비스요청 신청대상', '서비스요청 신청 가능 사용자', ['user1'])
        for name in ('worker1', 'worker2', 'developer1'):
            RoleGrant.objects.get_or_create(organization=org, person=people[name], role='AGENT')
        RoleGrant.objects.get_or_create(organization=org, person=people['developer1'], role='DEVELOPER')
        designer_role, _ = RoleDefinition.objects.get_or_create(organization=org, code=DESIGNER_ROLE, defaults={
            'name': '화면 디자이너', 'description': '운영 콘솔의 화면 관리에서 업무 화면 템플릿을 설계·게시',
            'permissions': ['console.access', 'workflow.manage']})
        CustomRoleGrant.objects.get_or_create(organization=org, person=people['designer1'], role=designer_role)
        for code, name, description, labels in CODE_GROUPS:
            code_group, made = CommonCodeGroup.objects.get_or_create(organization=org, code=code, defaults={'name': name, 'description': description})
            if made:
                for index, label in enumerate(labels, 1):
                    CommonCodeItem.objects.create(organization=org, group=code_group, code='%02d' % index, label=label, sort_order=index)
        manager_console = False
        if not RoleMenuPolicy.objects.filter(organization=org, role_key='SERVICE_MANAGER').exists():
            # 서비스 관리자는 기본 메뉴를 유지하고 콘솔의 카탈로그·SLA 설정 화면만 열 수 있게 한다.
            from .menu_access import role_menus
            menus = sorted(role_menus(org, 'SERVICE_MANAGER')[0])
            RoleMenuPolicy.objects.create(organization=org, role_key='SERVICE_MANAGER', menu_keys=menus, console_button=True)
            manager_console = True
        clear()
        s.record(admin, org, 'SR_TEMPLATE_BASELINE_CONFIGURED', uuid.uuid4(), after={
            'created_accounts': created, 'reused_accounts': [n for n in USERNAMES if n not in created],
            'groups': {'ops': str(ops_group.id), 'dev': str(dev_group.id), 'audience': str(audience.id)},
            'designer_role': str(designer_role.id), 'service_manager_console': manager_console, 'code_groups': [c[0] for c in CODE_GROUPS], 'reason': REASON})

        designer, developer = people['designer1'], people['developer1']
        screen = _publish_definition(designer, developer, 'SCREEN', SCREEN_CODE, '서비스요청 화면 템플릿', screen_graph(ops_group.id))
        approval = _publish_definition(developer, admin, 'APPROVAL', APPROVAL_CODE, '서비스요청 요청부서 결재선', dict(stages=[
            dict(key='department_head', label='요청부서 승인자 승인', selector=dict(kind='USER', ids=[str(people['user_auth1'].id)]), mode='ANY')]))
        workflow = _publish_definition(developer, admin, 'WORKFLOW', WORKFLOW_CODE, 'IT 서비스 요청 프로세스(개발·운영)',
                                       workflow_graph(screen.graph['fields'], screen.id, approval.id, ops_group.id, dev_group.id))

        calendar = BusinessCalendar.objects.filter(organization=org).order_by('-created_at').first()
        if not calendar:
            created_calendar = _run(manager, 'sla_calendar', dict(name='기본 업무 달력(평일 09:00~18:00)', timezone='Asia/Seoul',
                weekdays=[0, 1, 2, 3, 4], starts_at='09:00', ends_at='18:00',
                holidays=['2026-01-01', '2026-03-01', '2026-05-05', '2026-06-06', '2026-08-15', '2026-10-03', '2026-10-09', '2026-12-25',
                          '2027-01-01', '2027-03-01', '2027-05-05', '2027-06-06', '2027-08-15', '2027-10-03', '2027-10-09', '2027-12-25']))
            calendar = BusinessCalendar.objects.get(id=created_calendar['id'])
        from .models import SLAPolicy
        for priority, response, resolution in INCIDENT_SLA:
            if not SLAPolicy.objects.filter(organization=org, priority=priority).exists():
                _run(manager, 'sla_policy', dict(name='장애 P%d 기본 SLA' % priority, calendar_id=str(calendar.id), priority=priority,
                     response_minutes=response, resolution_minutes=resolution, warning_percent=80, pause_on_pending=True))
        if not TimelinessPolicy.objects.filter(organization=org, ticket_type='SERVICE_REQUEST').exists():
            _run(manager, 'kpi_policy', dict(name='서비스요청 기본 처리기한(3영업일)', ticket_type='SERVICE_REQUEST', basis='RECEIPT',
                 target_minutes=3 * 9 * 60, calendar_id=str(calendar.id), expected_version=0, reason=REASON))

        entry = _run(manager, 'catalog_publish', dict(code=CATALOG_CODE, name='IT 서비스 요청(개발·운영)',
            description='등록 → 요청부서 승인 → 접수·담당자 배정 → (개발) → 운영 조치·반영 → 요청자 확인 → 종료',
            fulfillment_group_id=str(ops_group.id), approval_required=False, approver_id=None, public_to_org=False,
            audience_group_ids=[str(audience.id)], available=True, fields=catalog_form(), expected_version=0,
            workflow_version_id=str(workflow.id)))
        SecurityEvent.objects.create(organization=org, person=admin, action=MARKER, request_id=uuid.uuid4())
        return dict(retained=False, organization_id=str(org.id), created_accounts=created,
                    reused_accounts=[n for n in USERNAMES if n not in created], screen_version_id=str(screen.id),
                    approval_version_id=str(approval.id), workflow_version_id=str(workflow.id),
                    catalog_version_id=entry['id'], ops_group_id=str(ops_group.id), dev_group_id=str(dev_group.id))


SAMPLES = [
    dict(stage='department_approval', values=dict(title='신규 입사자 그룹웨어 계정·결재 권한 등록', request_type='계정·권한',
         target_system='그룹웨어', urgency='높음', due_date='2026-11-20',
         description='11월 18일 입사 예정자 2명의 그룹웨어 계정 생성과 요청부서 결재선 권한 등록을 요청합니다.',
         expected_effect='입사 첫날부터 전자결재와 메일을 사용할 수 있습니다.')),
    dict(stage='intake', values=dict(title='월간 매출 보고서 엑셀 다운로드 기능 개선', request_type='기능 개선',
         target_system='ERP', urgency='보통', due_date='2026-11-30',
         description='ERP 월간 매출 보고서를 엑셀로 내려받을 때 거래처명이 잘립니다. 전체 거래처명을 포함하도록 개선을 요청합니다.',
         expected_effect='보고서 수작업 보정 시간을 줄입니다.')),
    dict(stage='development', values=dict(title='고객 상담 이력 조회 화면 신규 개발', request_type='신규 개발',
         target_system='고객관리(CRM)', urgency='보통', due_date='2026-12-15',
         description='고객별 최근 1년 상담 이력을 한 화면에서 조회하고 상담 유형별로 필터링하는 화면을 요청합니다.',
         expected_effect='상담원이 이전 상담 내용을 빠르게 확인해 응대 시간을 줄입니다.'),
         intake=dict(dev_required=True, operator='worker1', planned_date='2026-12-10', intake_note='화면 신규 개발 필요. 개발 완료 후 운영자1이 운영 반영합니다.')),
    dict(stage='confirmation', values=dict(title='3분기 거래처별 발주 실적 데이터 추출', request_type='데이터 추출·변경',
         target_system='ERP', urgency='낮음', due_date='2026-11-25',
         description='2026년 3분기 거래처별 발주 건수와 금액을 엑셀 파일로 추출해 주십시오.',
         expected_effect='분기 구매 실적 보고 자료로 사용합니다.'),
         intake=dict(dev_required=False, operator='worker2', planned_date='2026-11-21', intake_note='데이터 추출 건. 운영자2가 조치합니다.'),
         operation=dict(action_content='3분기 거래처별 발주 실적을 추출해 요청자 메일로 송부했습니다. (파일: 2026Q3_발주실적.xlsx)', action_date='2026-11-17')),
    dict(stage='close', values=dict(title='홈페이지 공지사항 게시판 첨부파일 다운로드 오류', request_type='오류 문의',
         target_system='홈페이지', urgency='긴급', due_date='2026-11-18',
         description='홈페이지 공지사항 게시판에서 첨부파일 다운로드 시 오류 페이지가 표시됩니다.',
         expected_effect='고객이 공지 첨부 자료를 정상적으로 내려받을 수 있습니다.'),
         intake=dict(dev_required=True, operator='worker1', planned_date='2026-11-18', intake_note='파일 경로 처리 오류로 보임. 개발 수정 후 운영 반영.'),
         development=dict(dev_content='첨부파일 저장 경로의 한글 파일명 인코딩 처리를 수정했습니다.', dev_artifacts='board/download.jsp, FileUtil.java', dev_done_date='2026-11-17'),
         operation=dict(action_content='수정 프로그램을 운영 서버에 반영하고 다운로드를 확인했습니다.', action_date='2026-11-17'),
         confirmation=dict(confirmed=True, satisfaction=5, feedback='정상적으로 내려받아집니다. 감사합니다.')),
]
ORDER = ['department_approval', 'intake', 'development', 'operation', 'confirmation', 'close']


def create_samples(organization_id):
    """요청자가 카탈로그로 5건을 신청하고, 각 건을 지정 단계까지 실제 담당자가 처리한다."""
    with transaction.atomic():
        org = Organization.objects.select_for_update().get(id=organization_id)
        if SecurityEvent.objects.filter(organization=org, action=SAMPLE_MARKER).exists():
            return {'retained': True}
        if not SecurityEvent.objects.filter(organization=org, action=MARKER).exists():
            s.fail('NOT_CONFIGURED', '템플릿 구성을 먼저 완료하십시오.')
        people = {name: _person(org, name) for name in USERNAMES}
        version = CatalogVersion.objects.filter(organization=org, item__code=CATALOG_CODE).order_by('-version').first()
        numbers = []
        for sample in SAMPLES:
            created = _run(people['user1'], 'req_create', dict(catalog_version_id=str(version.id), values=sample['values']))
            run = ProcessRun.objects.get(ticket_id=created['id'])

            def act(username, key, values=None, decision='COMPLETE'):
                run.refresh_from_db()
                task = run.tasks.get(status='OPEN')
                if task.node_key.split('__')[0] != key:
                    s.fail('WRONG_STAGE', '예시 요청 단계가 일치하지 않습니다: ' + task.node_key)
                _run(people[username], 'flow_act', dict(task_id=str(task.id), expected_version=run.row_version, decision=decision,
                     values=values or {}, reason='예시 데이터 처리'), run.id)
            target = ORDER.index(sample['stage'])
            if target > 0:
                act('user_auth1', 'department_approval', decision='APPROVE')
            if target > 1:
                intake = dict(sample['intake'])
                intake['operator'] = str(people[intake['operator']].id)
                act('worker1', 'intake', intake)
            if target > 2 and sample['intake']['dev_required']:
                act('developer1', 'development', sample['development'])
            if target > 3:
                act(sample['intake']['operator'], 'operation', sample['operation'])
            if target > 4:
                act('user1', 'confirmation', sample['confirmation'])
            run.refresh_from_db()
            numbers.append(dict(title=sample['values']['title'], stage=sample['stage'], status=run.ticket.status, run_id=str(run.id)))
        SecurityEvent.objects.create(organization=org, person=people['user1'], action=SAMPLE_MARKER, request_id=uuid.uuid4())
        return {'retained': False, 'samples': numbers}
