# UI-PROCESS_MANAGE · 화면/워크플로우/결재선 상세

진입/사용: /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new

소스: `desk/templates/desk/process-manage.html`

연결: `desk/console-tabs.html`, `desk/configuration-impact.html`, `desk/screen-designer.html`

뷰·권한 참조(동시 필수 권한 목록 아님): process_views.manage [workflow.manage]

## 기능/폼 계약

### UI-PROCESS_MANAGE-F01

UI-PROCESS_MANAGE-F01 · flow-save · POST(JSON) /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행

항목: UI-PROCESS_MANAGE-E004, UI-PROCESS_MANAGE-E005, UI-PROCESS_MANAGE-E006, UI-PROCESS_MANAGE-E007, UI-PROCESS_MANAGE-E008, UI-PROCESS_MANAGE-E009, UI-PROCESS_MANAGE-E010, UI-PROCESS_MANAGE-E011, UI-PROCESS_MANAGE-E012, UI-PROCESS_MANAGE-E013, UI-PROCESS_MANAGE-E014, UI-PROCESS_MANAGE-E015, UI-PROCESS_MANAGE-E016, UI-PROCESS_MANAGE-E017, UI-PROCESS_MANAGE-E018, UI-PROCESS_MANAGE-E019, UI-PROCESS_MANAGE-E020, UI-PROCESS_MANAGE-E021, UI-PROCESS_MANAGE-E022, UI-PROCESS_MANAGE-E023, UI-PROCESS_MANAGE-E024, UI-PROCESS_MANAGE-E025, UI-PROCESS_MANAGE-E026, UI-PROCESS_MANAGE-E027, UI-PROCESS_MANAGE-E028, UI-PROCESS_MANAGE-E029

### UI-PROCESS_MANAGE-F02

UI-PROCESS_MANAGE-F02 · flow-review · POST(JSON) /api/v1/processes/review/{{ process_definition.id }} / 작성자와 다른 검토자, 현재 초안 해시 및 버전 확인 후 독립 검토 기록

항목: UI-PROCESS_MANAGE-E030, UI-PROCESS_MANAGE-E031, UI-PROCESS_MANAGE-E032

### UI-PROCESS_MANAGE-F03

UI-PROCESS_MANAGE-F03 · flow-publish · POST(JSON) /api/v1/processes/publish/{{ process_definition.id }} / 동일 초안의 유효한 독립 검토 확인 후 불변 게시 버전 생성; 진행 중 실행 유지

항목: UI-PROCESS_MANAGE-E033, UI-PROCESS_MANAGE-E034, UI-PROCESS_MANAGE-E035

### UI-PROCESS_MANAGE-F04

UI-PROCESS_MANAGE-F04 · flow-clone · POST(JSON) /api/v1/processes/clone/{{ process_definition.id }} / 이전 게시 버전을 새 초안으로 복제; 기존 게시본 불변.

항목: UI-PROCESS_MANAGE-E040, UI-PROCESS_MANAGE-E041, UI-PROCESS_MANAGE-E042

### UI-PROCESS_MANAGE-F05

UI-PROCESS_MANAGE-F05 · flow-retire · POST(JSON) /api/v1/processes/retire/{{ v.id }} / 게시 버전 신규 실행 퇴역. 이미 진행 중인 실행은 유지.

항목: UI-PROCESS_MANAGE-E043, UI-PROCESS_MANAGE-E044

### UI-PROCESS_MANAGE-F06

UI-PROCESS_MANAGE-F06 · flow-bind · POST(JSON) /api/v1/processes/bind/service-request / 업무 메뉴/카탈로그와 게시 프로세스 버전 연결; 지원 어댑터와 대상 검사.

항목: UI-PROCESS_MANAGE-E045, UI-PROCESS_MANAGE-E046, UI-PROCESS_MANAGE-E047

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PROCESS_MANAGE-E001 · ← {{ process_title }} 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ process_base }} | `desk/templates/desk/process-manage.html:2` |
| UI-PROCESS_MANAGE-E002 · 새 정의 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ process_base }}/new | `desk/templates/desk/process-manage.html:3` |
| UI-PROCESS_MANAGE-E003 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_definition.validation_errors | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-manage.html:8` |
| UI-PROCESS_MANAGE-E004 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:10` |
| UI-PROCESS_MANAGE-E005 · kind | hidden / name=kind; type=hidden; value={{ process_kind }} | if active_tab == 'design' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:10` |
| UI-PROCESS_MANAGE-E006 · 코드 | text / name=code; required; readonly; maxlength=40; value={{ process_definition.code }} / readonly는 process_definition일 때 적용 | if active_tab == 'design' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:10` |
| UI-PROCESS_MANAGE-E007 · 이름 | text / name=name; required; maxlength=200; value={{ process_definition.name }} | if active_tab == 'design' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:10` |
| UI-PROCESS_MANAGE-E008 · 신규 실행 허용 | checkbox / name=active; type=checkbox; checked / checked는 not process_definition or process_definition.active일 때 적용 | if active_tab == 'design' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:10` |
| UI-PROCESS_MANAGE-E009 · 공통 화면 · 게시 버전 | select / name=common_screen | if active_tab == 'design' / if process_kind == 'WORKFLOW' / 선택값: =직접 데이터 항목 정의; {{ v.id }}={{ v.definition.name }} · v{{ v.version }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:11` |
| UI-PROCESS_MANAGE-E010 · 화면 디자이너 열기 | button / type=button | if active_tab == 'design' / if process_kind != 'APPROVAL' / if process_kind == 'SCREEN' | 클라이언트 조작: 화면 디자이너 열기 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E011 · 항목 추가 | button / type=button | if active_tab == 'design' / if process_kind != 'APPROVAL' | 클라이언트 조작: 항목 추가 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E012 · 항목표·고급 설정 프로세스 데이터 항목 편집 | summary / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E013 · 식별자 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E014 · 표시 이름 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E015 · 유형 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E016 · 필수 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E017 · 담당자 선택 그룹 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E018 · 조회 전용 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' / if process_kind == 'SCREEN' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E019 · 관리 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'APPROVAL' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E020 · 화면 열 수 | select / name=screen_columns | if active_tab == 'design' / if process_kind != 'APPROVAL' / if process_kind == 'SCREEN' / 선택값: 1=1; 2=2; 3=3 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:12` |
| UI-PROCESS_MANAGE-E021 · 결재 단계 추가 노드 추가 | button / type=button | if active_tab == 'design' / if process_kind != 'SCREEN' | 클라이언트 조작: 결재 단계 추가 노드 추가 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E022 · 고급 실행 설정 | summary / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' / if process_kind != 'SCREEN' / if process_kind == 'WORKFLOW' | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E023 · 서비스 카탈로그에서만 신규 실행 | checkbox / name=catalog_only; type=checkbox; checked / checked는 process_draft.catalog_only일 때 적용 | if active_tab == 'design' / if process_kind != 'SCREEN' / if process_kind == 'WORKFLOW' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E024 · 완료 시 연결 서비스요청 종료 | checkbox / name=close_on_complete; type=checkbox; checked / checked는 process_draft.close_on_complete일 때 적용 | if active_tab == 'design' / if process_kind != 'SCREEN' / if process_kind == 'WORKFLOW' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E025 · 서비스요청 담당자 필드 | text / name=ticket_assignee_field; value={{ process_draft.ticket_assignee_field }} | if active_tab == 'design' / if process_kind != 'SCREEN' / if process_kind == 'WORKFLOW' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E026 · 시작 노드 식별자 | text / name=start_node; required; maxlength=40; value={{ process_draft.start\|default:'start' }} | if active_tab == 'design' / if process_kind != 'SCREEN' / if process_kind == 'WORKFLOW' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E027 · 흐름도 새로고침 | button / type=button | if active_tab == 'design' / if process_kind != 'SCREEN' / if process_kind == 'WORKFLOW' | 클라이언트 조작: 흐름도 새로고침 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:13` |
| UI-PROCESS_MANAGE-E028 · 변경 사유 | text / name=reason; required; maxlength=500; placeholder=변경한 내용을 간단히 입력하십시오. | if active_tab == 'design' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:14` |
| UI-PROCESS_MANAGE-E029 · 초안 저장·검증 | submit / 별도 입력 제약 없음/조회 항목 | if active_tab == 'design' | 폼 제출: flow-save → /api/v1/processes/save /{{ process_definition.id }}  / /api/v1/processes/save /{{ process_definition.id }}  / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-manage.html:14` |
| UI-PROCESS_MANAGE-E030 · 검토 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/review/{{ process_definition.id }} / 작성자와 다른 검토자, 현재 초안 해시 및 버전 확인 후 독립 검토 기록 | `desk/templates/desk/process-manage.html:15` |
| UI-PROCESS_MANAGE-E031 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/review/{{ process_definition.id }} / 작성자와 다른 검토자, 현재 초안 해시 및 버전 확인 후 독립 검토 기록 | `desk/templates/desk/process-manage.html:15` |
| UI-PROCESS_MANAGE-E032 · 독립 검토 완료 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 폼 제출: flow-review → /api/v1/processes/review/{{ process_definition.id }} / /api/v1/processes/review/{{ process_definition.id }} / 작성자와 다른 검토자, 현재 초안 해시 및 버전 확인 후 독립 검토 기록 | `desk/templates/desk/process-manage.html:15` |
| UI-PROCESS_MANAGE-E033 · 게시 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/publish/{{ process_definition.id }} / 동일 초안의 유효한 독립 검토 확인 후 불변 게시 버전 생성; 진행 중 실행 유지 | `desk/templates/desk/process-manage.html:15` |
| UI-PROCESS_MANAGE-E034 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/publish/{{ process_definition.id }} / 동일 초안의 유효한 독립 검토 확인 후 불변 게시 버전 생성; 진행 중 실행 유지 | `desk/templates/desk/process-manage.html:15` |
| UI-PROCESS_MANAGE-E035 · 검토된 초안 게시 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 폼 제출: flow-publish → /api/v1/processes/publish/{{ process_definition.id }} / /api/v1/processes/publish/{{ process_definition.id }} / 동일 초안의 유효한 독립 검토 확인 후 불변 게시 버전 생성; 진행 중 실행 유지 | `desk/templates/desk/process-manage.html:15` |
| UI-PROCESS_MANAGE-E036 · 버전 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E037 · 게시자 · 검토자 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E038 · 게시일 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E039 · 복구·중단 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E040 · version_id | hidden / name=version_id; type=hidden; value={{ v.id }} | elif active_tab == 'versions' (앞 분기 제외) / if process_definition / for v in process_versions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/clone/{{ process_definition.id }} / 이전 게시 버전을 새 초안으로 복제; 기존 게시본 불변. | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E041 · 복제 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition / for v in process_versions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/clone/{{ process_definition.id }} / 이전 게시 버전을 새 초안으로 복제; 기존 게시본 불변. | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E042 · 이 버전으로 새 초안 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition / for v in process_versions | 폼 제출: flow-clone → /api/v1/processes/clone/{{ process_definition.id }} / /api/v1/processes/clone/{{ process_definition.id }} / 이전 게시 버전을 새 초안으로 복제; 기존 게시본 불변. | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E043 · 중단 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition / for v in process_versions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/retire/{{ v.id }} / 게시 버전 신규 실행 퇴역. 이미 진행 중인 실행은 유지. | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E044 · 이 버전 신규 실행 중단 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'versions' (앞 분기 제외) / if process_definition / for v in process_versions | 폼 제출: flow-retire → /api/v1/processes/retire/{{ v.id }} / /api/v1/processes/retire/{{ v.id }} / 게시 버전 신규 실행 퇴역. 이미 진행 중인 실행은 유지. | `desk/templates/desk/process-manage.html:17` |
| UI-PROCESS_MANAGE-E045 · 서비스요청 기본 프로세스 | select / name=version_id; required | elif active_tab == 'bindings' (앞 분기 제외) / 선택값: =게시 버전 선택; {{ v.id }}={{ v.definition.name }} · v{{ v.version }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/bind/service-request / 업무 메뉴/카탈로그와 게시 프로세스 버전 연결; 지원 어댑터와 대상 검사. | `desk/templates/desk/process-manage.html:18` |
| UI-PROCESS_MANAGE-E046 · 연결 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'bindings' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/bind/service-request / 업무 메뉴/카탈로그와 게시 프로세스 버전 연결; 지원 어댑터와 대상 검사. | `desk/templates/desk/process-manage.html:18` |
| UI-PROCESS_MANAGE-E047 · 메뉴 연결 저장 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'bindings' (앞 분기 제외) | 폼 제출: flow-bind → /api/v1/processes/bind/service-request / /api/v1/processes/bind/service-request / 업무 메뉴/카탈로그와 게시 프로세스 버전 연결; 지원 어댑터와 대상 검사. | `desk/templates/desk/process-manage.html:18` |
| UI-PROCESS_MANAGE-E048 · {{ run.title }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for run in process_runs | 링크 이동: /processes/{{ run.id }} | `desk/templates/desk/process-manage.html:19` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
