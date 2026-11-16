# UI-ACCESS · 조직 · 권한 관리

진입/사용: /admin/access

소스: `desk/templates/desk/access.html`

연결: `desk/console-tabs.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.admin_access [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-ACCESS-F01

UI-ACCESS-F01 · roles · PUT /api/v1/admin/persons/{{ row.person.id }}/roles / 레거시 직접 역할 체크 목록 저장; 조직/보호 관리자 규칙 유지.

항목: UI-ACCESS-E008, UI-ACCESS-E009, UI-ACCESS-E010, UI-ACCESS-E011

### UI-ACCESS-F02

UI-ACCESS-F02 · membership · PUT /api/v1/admin/groups/{{ row.group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사.

항목: UI-ACCESS-E012, UI-ACCESS-E013, UI-ACCESS-E014, UI-ACCESS-E015

### UI-ACCESS-F03

UI-ACCESS-F03 · account · POST(JSON) /api/v1/admin/persons/{{ row.person.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한.

항목: UI-ACCESS-E016, UI-ACCESS-E017, UI-ACCESS-E018, UI-ACCESS-E019

### UI-ACCESS-F04

UI-ACCESS-F04 · revoke-sessions · POST(JSON) /api/v1/admin/persons/{{ row.person.id }}/revoke-sessions / 선택 사용자의 세션을 회수; 현재 세션 여부와 권한 검사.

항목: UI-ACCESS-E020, UI-ACCESS-E021, UI-ACCESS-E022

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ACCESS-E001 · 사용자 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E002 · 로그인 ID | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E003 · 상태 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E004 · 배정된 역할 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E005 · 관리 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E006 · 역할 관리 | a / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' / for row in people | 링크 이동: ?tab=roles#person-{{ row.person.id }} | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E007 · 계정 관리 | a / 별도 입력 제약 없음/조회 항목 | if active_tab == 'users' / for row in people | 링크 이동: ?tab=accounts#account-{{ row.person.id }} | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E008 · {{ role.name\|role_label }} | checkbox / name=roles; type=checkbox; checked; value={{ role.name }} / checked는 role.checked일 때 적용 | elif active_tab == 'roles' (앞 분기 제외) / for row in people / for role in row.roles | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ row.person.id }}/roles / 레거시 직접 역할 체크 목록 저장; 조직/보호 관리자 규칙 유지. | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E009 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'roles' (앞 분기 제외) / for row in people | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/persons/{{ row.person.id }}/roles / 레거시 직접 역할 체크 목록 저장; 조직/보호 관리자 규칙 유지. | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E010 · 변경 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'roles' (앞 분기 제외) / for row in people | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ row.person.id }}/roles / 레거시 직접 역할 체크 목록 저장; 조직/보호 관리자 규칙 유지. | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E011 · 저장 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'roles' (앞 분기 제외) / for row in people | 폼 제출: roles → /api/v1/admin/persons/{{ row.person.id }}/roles / /api/v1/admin/persons/{{ row.person.id }}/roles / 레거시 직접 역할 체크 목록 저장; 조직/보호 관리자 규칙 유지. | `desk/templates/desk/access.html:3` |
| UI-ACCESS-E012 · 그룹 소속 | checkbox / name=active; type=checkbox; checked / checked는 item.checked일 때 적용 | elif active_tab == 'groups' (앞 분기 제외) / for row in memberships / for item in row.people | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/groups/{{ row.group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/access.html:4` |
| UI-ACCESS-E013 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) / for row in memberships / for item in row.people | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/groups/{{ row.group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/access.html:4` |
| UI-ACCESS-E014 · 변경 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'groups' (앞 분기 제외) / for row in memberships / for item in row.people | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/groups/{{ row.group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/access.html:4` |
| UI-ACCESS-E015 · 저장 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) / for row in memberships / for item in row.people | 폼 제출: membership → /api/v1/admin/groups/{{ row.group.id }}/members/{{ item.person.id }} / /api/v1/admin/groups/{{ row.group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/access.html:4` |
| UI-ACCESS-E016 · active | hidden / name=active; type=hidden; value= false true  | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ row.person.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/access.html:6` |
| UI-ACCESS-E017 · 변경 사유 | text / name=reason; required; maxlength=2000 | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ row.person.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/access.html:6` |
| UI-ACCESS-E018 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/persons/{{ row.person.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/access.html:6` |
| UI-ACCESS-E019 · 계정 중지 재활성화 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 폼 제출: account → /api/v1/admin/persons/{{ row.person.id }}/account / /api/v1/admin/persons/{{ row.person.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/access.html:6` |
| UI-ACCESS-E020 · 회수 사유 | text / name=reason; required; maxlength=2000 | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ row.person.id }}/revoke-sessions / 선택 사용자의 세션을 회수; 현재 세션 여부와 권한 검사. | `desk/templates/desk/access.html:7` |
| UI-ACCESS-E021 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/persons/{{ row.person.id }}/revoke-sessions / 선택 사용자의 세션을 회수; 현재 세션 여부와 권한 검사. | `desk/templates/desk/access.html:7` |
| UI-ACCESS-E022 · 모든 기존 세션 회수 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'accounts' (앞 분기 제외) / for row in people | 폼 제출: revoke-sessions → /api/v1/admin/persons/{{ row.person.id }}/revoke-sessions / /api/v1/admin/persons/{{ row.person.id }}/revoke-sessions / 선택 사용자의 세션을 회수; 현재 세션 여부와 권한 검사. | `desk/templates/desk/access.html:7` |
| UI-ACCESS-E023 · 일시 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E024 · 사용자 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E025 · 동작 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E026 · 추적 ID | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E027 · 일시 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E028 · 변경자 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E029 · 동작 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |
| UI-ACCESS-E030 · 변경 사유 | th / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'history' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/access.html:8` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
