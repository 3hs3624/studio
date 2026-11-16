# UI-ROLES · 역할 관리

진입/사용: /console/roles, /console/roles/<str:id>

소스: `desk/templates/desk/roles.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): identity_views.roles [iam.manage]

## 기능/폼 계약

### UI-ROLES-F01

UI-ROLES-F01 · role-save · POST(JSON) /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사.

항목: UI-ROLES-E007, UI-ROLES-E008, UI-ROLES-E009, UI-ROLES-E010, UI-ROLES-E011, UI-ROLES-E012, UI-ROLES-E013, UI-ROLES-E014, UI-ROLES-E015, UI-ROLES-E016, UI-ROLES-E017

### UI-ROLES-F02

UI-ROLES-F02 · role-grant · POST(JSON) /api/v1/management/role-grant/{{ selected_role.id }} / 사용자 직접 역할 배정 변경; 보호 관리자 제한·사유 검사.

항목: UI-ROLES-E018, UI-ROLES-E019, UI-ROLES-E020, UI-ROLES-E021

### UI-ROLES-F03

UI-ROLES-F03 · manage-delete · POST(JSON) /api/v1/management/role-delete/{{ selected_role.id }} / 역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동.

항목: UI-ROLES-E022, UI-ROLES-E023

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ROLES-E001 · 역할 목록 역할 생성 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/roles /new  | `desk/templates/desk/roles.html:1` |
| UI-ROLES-E002 · 코드 | th / 별도 입력 제약 없음/조회 항목 | if not selected_role and not new_role | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/roles.html:2` |
| UI-ROLES-E003 · 이름 | th / 별도 입력 제약 없음/조회 항목 | if not selected_role and not new_role | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/roles.html:2` |
| UI-ROLES-E004 · 구분 | th / 별도 입력 제약 없음/조회 항목 | if not selected_role and not new_role | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/roles.html:2` |
| UI-ROLES-E005 · 상태 | th / 별도 입력 제약 없음/조회 항목 | if not selected_role and not new_role | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/roles.html:2` |
| UI-ROLES-E006 · {{ item.code }} | a / 별도 입력 제약 없음/조회 항목 | if not selected_role and not new_role / for item in role_list | 링크 이동: /console/roles/{{ item.id }} | `desk/templates/desk/roles.html:2` |
| UI-ROLES-E007 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E008 · 코드 | text / name=code; required; readonly; maxlength=40; value={{ selected_role.code }} / readonly는 selected_role일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E009 · 이름 | text / name=name; required; readonly; maxlength=100; value={{ selected_role.name }} / readonly는 system_role일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E010 · 설명 | text / name=description; readonly; maxlength=500; value={{ selected_role.description }} / readonly는 system_role일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E011 · 허용 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E012 · 기능 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E013 · 데이터 범위 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E014 · {{ permission.label }} | checkbox / name=permissions; type=checkbox; disabled; checked; value={{ permission.key }}; aria-label={{ permission.label }} / checked는 permission.checked일 때 적용; disabled는 system_role일 때 적용 | else (앞 분기 제외) / for permission in permissions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:3` |
| UI-ROLES-E015 · 사용 | checkbox / name=active; type=checkbox; checked / checked는 not selected_role or selected_role.active일 때 적용 | else (앞 분기 제외) / if not system_role | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:4` |
| UI-ROLES-E016 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if not system_role | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:4` |
| UI-ROLES-E017 · 역할 저장 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if not system_role | 폼 제출: role-save → /api/v1/management/roles /{{ selected_role.id }}  / /api/v1/management/roles /{{ selected_role.id }}  / 역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사. | `desk/templates/desk/roles.html:4` |
| UI-ROLES-E018 · 사용자 | select / name=person_id | else (앞 분기 제외) / if selected_role / if not system_role / 선택값: {{ member.id }}={{ member.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/role-grant/{{ selected_role.id }} / 사용자 직접 역할 배정 변경; 보호 관리자 제한·사유 검사. | `desk/templates/desk/roles.html:6` |
| UI-ROLES-E019 · 배정(해제하면 회수) | checkbox / name=active; type=checkbox; checked | else (앞 분기 제외) / if selected_role / if not system_role | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/role-grant/{{ selected_role.id }} / 사용자 직접 역할 배정 변경; 보호 관리자 제한·사유 검사. | `desk/templates/desk/roles.html:6` |
| UI-ROLES-E020 · 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if selected_role / if not system_role | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/role-grant/{{ selected_role.id }} / 사용자 직접 역할 배정 변경; 보호 관리자 제한·사유 검사. | `desk/templates/desk/roles.html:6` |
| UI-ROLES-E021 · 배정 저장 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if selected_role / if not system_role | 폼 제출: role-grant → /api/v1/management/role-grant/{{ selected_role.id }} / /api/v1/management/role-grant/{{ selected_role.id }} / 사용자 직접 역할 배정 변경; 보호 관리자 제한·사유 검사. | `desk/templates/desk/roles.html:6` |
| UI-ROLES-E022 · 삭제 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if selected_role / if not system_role | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/role-delete/{{ selected_role.id }} / 역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동. | `desk/templates/desk/roles.html:7` |
| UI-ROLES-E023 · 미사용 역할 삭제 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if selected_role / if not system_role | 폼 제출: manage-delete → /api/v1/management/role-delete/{{ selected_role.id }} / /api/v1/management/role-delete/{{ selected_role.id }} / 역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동. | `desk/templates/desk/roles.html:7` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
