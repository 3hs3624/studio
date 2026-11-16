# UI-ORGANIZATION_ACCESS · 조직 · 권한 관리

진입/사용: /console/access

소스: `desk/templates/desk/organization-access.html`

연결: `desk/console-tabs.html`, `desk/access-people.html`, `desk/access-departments.html`, `desk/access-departments.html`, `desk/access-people.html`

뷰·권한 참조(동시 필수 권한 목록 아님): organization_views.access [iam.manage]

## 기능/폼 계약

### UI-ORGANIZATION_ACCESS-F01

UI-ORGANIZATION_ACCESS-F01 · org-role-targets · POST(JSON) /api/v1/management/org-role-targets/{{ selected_role.key }} / 역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택.

항목: UI-ORGANIZATION_ACCESS-E004, UI-ORGANIZATION_ACCESS-E005, UI-ORGANIZATION_ACCESS-E006, UI-ORGANIZATION_ACCESS-E007, UI-ORGANIZATION_ACCESS-E008

### UI-ORGANIZATION_ACCESS-F02

UI-ORGANIZATION_ACCESS-F02 · org-menus · POST(JSON) /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사

항목: UI-ORGANIZATION_ACCESS-E009, UI-ORGANIZATION_ACCESS-E010, UI-ORGANIZATION_ACCESS-E011, UI-ORGANIZATION_ACCESS-E012, UI-ORGANIZATION_ACCESS-E013, UI-ORGANIZATION_ACCESS-E014, UI-ORGANIZATION_ACCESS-E015, UI-ORGANIZATION_ACCESS-E016, UI-ORGANIZATION_ACCESS-E017, UI-ORGANIZATION_ACCESS-E018

### UI-ORGANIZATION_ACCESS-F03

UI-ORGANIZATION_ACCESS-F03 · org-group-targets · POST(JSON) /api/v1/management/org-group-targets/{{ selected_group.id }} / 그룹에 사용자·부서를 배정. 그룹 중첩 배정 아님.

항목: UI-ORGANIZATION_ACCESS-E022, UI-ORGANIZATION_ACCESS-E023, UI-ORGANIZATION_ACCESS-E024, UI-ORGANIZATION_ACCESS-E025

### UI-ORGANIZATION_ACCESS-F04

UI-ORGANIZATION_ACCESS-F04 · org-department · POST(JSON) /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지.

항목: UI-ORGANIZATION_ACCESS-E028, UI-ORGANIZATION_ACCESS-E029, UI-ORGANIZATION_ACCESS-E030, UI-ORGANIZATION_ACCESS-E031, UI-ORGANIZATION_ACCESS-E032, UI-ORGANIZATION_ACCESS-E033, UI-ORGANIZATION_ACCESS-E034, UI-ORGANIZATION_ACCESS-E035

### UI-ORGANIZATION_ACCESS-F05

UI-ORGANIZATION_ACCESS-F05 · org-delete · POST(JSON) /api/v1/management/org-department-delete/{{ selected_department.id }} / 부서 삭제. 하위 부서·소속 사용자·배정 참조를 검사.

항목: UI-ORGANIZATION_ACCESS-E037, UI-ORGANIZATION_ACCESS-E038

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ORGANIZATION_ACCESS-E001 · 역할 생성 | a / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' | 링크 이동: /console/roles/new | `desk/templates/desk/organization-access.html:4` |
| UI-ORGANIZATION_ACCESS-E002 · {{ row.name }} | a / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / for row in access_roles | 링크 이동: ?tab={{ active_tab }}&selected={{ row.key }} | `desk/templates/desk/organization-access.html:4` |
| UI-ORGANIZATION_ACCESS-E003 · 역할 기본정보·세부 기능 권한 | a / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / if active_tab == 'roles' / else (앞 분기 제외) | 링크 이동: /console/roles/{{ selected_role.key }} | `desk/templates/desk/organization-access.html:7` |
| UI-ORGANIZATION_ACCESS-E004 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / if active_tab == 'roles' / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-role-targets/{{ selected_role.key }} / 역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택. | `desk/templates/desk/organization-access.html:7` |
| UI-ORGANIZATION_ACCESS-E005 · {{ row.name }} | checkbox / name=group_ids; type=checkbox; checked; value={{ row.id }} / checked는 row.id\|stringformat:'s' in selected_groups일 때 적용 | if active_tab == 'roles' or active_tab == 'menus' / if active_tab == 'roles' / else (앞 분기 제외) / for row in access_groups | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-role-targets/{{ selected_role.key }} / 역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택. | `desk/templates/desk/organization-access.html:8` |
| UI-ORGANIZATION_ACCESS-E006 · 선택 부서의 하위 부서에도 적용 | checkbox / name=include_children; type=checkbox; checked / checked는 include_children일 때 적용 | if active_tab == 'roles' or active_tab == 'menus' / if active_tab == 'roles' / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-role-targets/{{ selected_role.key }} / 역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택. | `desk/templates/desk/organization-access.html:8` |
| UI-ORGANIZATION_ACCESS-E007 · 변경 사유 | text / name=reason; required; maxlength=500 | if active_tab == 'roles' or active_tab == 'menus' / if active_tab == 'roles' / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-role-targets/{{ selected_role.key }} / 역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택. | `desk/templates/desk/organization-access.html:8` |
| UI-ORGANIZATION_ACCESS-E008 · 역할 배정 저장 | submit / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / if active_tab == 'roles' / else (앞 분기 제외) | 폼 제출: org-role-targets → /api/v1/management/org-role-targets/{{ selected_role.key }} / /api/v1/management/org-role-targets/{{ selected_role.key }} / 역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택. | `desk/templates/desk/organization-access.html:8` |
| UI-ORGANIZATION_ACCESS-E009 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E010 · 상단 운영콘솔 버튼 및 콘솔 접근 허용 | checkbox / name=console_button; type=checkbox; checked / checked는 console_button일 때 적용 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E011 · 허용 메뉴 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E012 · 조회 데이터 범위 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E013 · 변경 데이터 범위 | th / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E014 · {{ menu.label }} | checkbox / name=menu_keys; type=checkbox; checked; value={{ menu.key }} / checked는 menu.checked일 때 적용 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) / for menu in menu_options | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E015 · data-scope-menu | select / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) / for menu in menu_options / if menu.scoped / 선택값: {{ value }}={{ label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E016 · data-scope-menu | select / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) / for menu in menu_options / if menu.scoped / 선택값: {{ value }}={{ label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E017 · 변경 사유 | text / name=reason; required; maxlength=500 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E018 · 메뉴·버튼 매핑 저장 | submit / 별도 입력 제약 없음/조회 항목 | if active_tab == 'roles' or active_tab == 'menus' / else (앞 분기 제외) | 폼 제출: org-menus → /api/v1/management/org-menus/{{ selected_role.key }} / /api/v1/management/org-menus/{{ selected_role.key }} / 메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사 | `desk/templates/desk/organization-access.html:9` |
| UI-ORGANIZATION_ACCESS-E019 · 그룹 생성 | a / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) | 링크 이동: /console/groups/new | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E020 · {{ row.name }} | a / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) / for row in access_groups | 링크 이동: ?tab=groups&selected={{ row.id }} | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E021 · 그룹 기본정보·변경 이력 | a / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) / if selected_group | 링크 이동: /console/groups/{{ selected_group.id }} | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E022 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) / if selected_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-group-targets/{{ selected_group.id }} / 그룹에 사용자·부서를 배정. 그룹 중첩 배정 아님. | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E023 · 선택 부서의 하위 부서 사용자도 포함 | checkbox / name=include_children; type=checkbox; checked / checked는 include_children일 때 적용 | elif active_tab == 'groups' (앞 분기 제외) / if selected_group | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-group-targets/{{ selected_group.id }} / 그룹에 사용자·부서를 배정. 그룹 중첩 배정 아님. | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E024 · 변경 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'groups' (앞 분기 제외) / if selected_group | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-group-targets/{{ selected_group.id }} / 그룹에 사용자·부서를 배정. 그룹 중첩 배정 아님. | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E025 · 그룹 구성 저장 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'groups' (앞 분기 제외) / if selected_group | 폼 제출: org-group-targets → /api/v1/management/org-group-targets/{{ selected_group.id }} / /api/v1/management/org-group-targets/{{ selected_group.id }} / 그룹에 사용자·부서를 배정. 그룹 중첩 배정 아님. | `desk/templates/desk/organization-access.html:10` |
| UI-ORGANIZATION_ACCESS-E026 · + 부서 추가 | a / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'departments' (앞 분기 제외) | 링크 이동: ?tab=departments&selected=new | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E027 · {{ row.indent }}📁 {{ row.name }} (중지) | a / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'departments' (앞 분기 제외) / for row in departments | 링크 이동: ?tab=departments&selected={{ row.id }} | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E028 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E029 · 부서 코드 | text / name=code; required; readonly; maxlength=40; value={{ selected_department.code }} / readonly는 selected_department일 때 적용 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E030 · 부서명 | text / name=name; required; maxlength=200; value={{ selected_department.name }} | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E031 · 상위 부서 | select / name=parent_id | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department / 선택값: =최상위; {{ row.id }}={{ row.indent }}{{ row.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E032 · 설명 | text / name=description; maxlength=500; value={{ selected_department.description }} | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E033 · 사용 | checkbox / name=active; type=checkbox; checked / checked는 not selected_department or selected_department.active일 때 적용 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E034 · 변경 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E035 · 부서 저장 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department | 폼 제출: org-department → /api/v1/management/org-department /{{ selected_department.id }}  / /api/v1/management/org-department /{{ selected_department.id }}  / 부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지. | `desk/templates/desk/organization-access.html:11` |
| UI-ORGANIZATION_ACCESS-E036 · {{ member.display_name }} | a / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department / if selected_department / for member in department_people | 링크 이동: /console/users/{{ member.id }} | `desk/templates/desk/organization-access.html:12` |
| UI-ORGANIZATION_ACCESS-E037 · 삭제 사유 | text / name=reason; required; maxlength=500 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department / if selected_department | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/org-department-delete/{{ selected_department.id }} / 부서 삭제. 하위 부서·소속 사용자·배정 참조를 검사. | `desk/templates/desk/organization-access.html:12` |
| UI-ORGANIZATION_ACCESS-E038 · 미사용 부서 삭제 | submit / 별도 입력 제약 없음/조회 항목 | elif active_tab == 'departments' (앞 분기 제외) / if selected_department or new_department / if selected_department | 폼 제출: org-delete → /api/v1/management/org-department-delete/{{ selected_department.id }} / /api/v1/management/org-department-delete/{{ selected_department.id }} / 부서 삭제. 하위 부서·소속 사용자·배정 참조를 검사. | `desk/templates/desk/organization-access.html:12` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
