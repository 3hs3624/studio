# UI-GROUPS · 그룹 관리

진입/사용: /console/groups, /console/groups/<str:id>

소스: `desk/templates/desk/groups.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): identity_views.groups [iam.manage]

## 기능/폼 계약

### UI-GROUPS-F01

UI-GROUPS-F01 · group-save · POST(JSON) /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사.

항목: UI-GROUPS-E007, UI-GROUPS-E008, UI-GROUPS-E009, UI-GROUPS-E010, UI-GROUPS-E011, UI-GROUPS-E012

### UI-GROUPS-F02

UI-GROUPS-F02 · membership · PUT /api/v1/admin/groups/{{ selected_group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사.

항목: UI-GROUPS-E013, UI-GROUPS-E014, UI-GROUPS-E015

### UI-GROUPS-F03

UI-GROUPS-F03 · manage-delete · POST(JSON) /api/v1/management/group-delete/{{ selected_group.id }} / 역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동.

항목: UI-GROUPS-E017, UI-GROUPS-E018

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-GROUPS-E001 · 그룹 목록 그룹 생성 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/groups /new  | `desk/templates/desk/groups.html:1` |
| UI-GROUPS-E002 · 코드 | th / 별도 입력 제약 없음/조회 항목 | if not selected_group and not new_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/groups.html:2` |
| UI-GROUPS-E003 · 그룹 | th / 별도 입력 제약 없음/조회 항목 | if not selected_group and not new_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/groups.html:2` |
| UI-GROUPS-E004 · 상태 | th / 별도 입력 제약 없음/조회 항목 | if not selected_group and not new_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/groups.html:2` |
| UI-GROUPS-E005 · 접수 그룹 | th / 별도 입력 제약 없음/조회 항목 | if not selected_group and not new_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/groups.html:2` |
| UI-GROUPS-E006 · {{ item.code }} | a / 별도 입력 제약 없음/조회 항목 | if not selected_group and not new_group / for item in group_list | 링크 이동: /console/groups/{{ item.id }} | `desk/templates/desk/groups.html:2` |
| UI-GROUPS-E007 · 코드 | text / name=code; required; readonly; maxlength=40; value={{ selected_group.code }} / readonly는 selected_group일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사. | `desk/templates/desk/groups.html:3` |
| UI-GROUPS-E008 · 이름 | text / name=name; required; maxlength=200; value={{ selected_group.name }} | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사. | `desk/templates/desk/groups.html:3` |
| UI-GROUPS-E009 · 설명 | text / name=description; maxlength=500; value={{ selected_group.description }} | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사. | `desk/templates/desk/groups.html:3` |
| UI-GROUPS-E010 · 사용 | checkbox / name=active; type=checkbox; checked / checked는 not selected_group or selected_group.active일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사. | `desk/templates/desk/groups.html:3` |
| UI-GROUPS-E011 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사. | `desk/templates/desk/groups.html:3` |
| UI-GROUPS-E012 · 그룹 저장 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 폼 제출: group-save → /api/v1/management/groups /{{ selected_group.id }}  / /api/v1/management/groups /{{ selected_group.id }}  / 그룹 정의 저장. 조직별 코드 중복·활성 여부 검사. | `desk/templates/desk/groups.html:3` |
| UI-GROUPS-E013 · 소속 | checkbox / name=active; type=checkbox; checked / checked는 item.checked일 때 적용 | else (앞 분기 제외) / if selected_group / for item in members | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/groups/{{ selected_group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/groups.html:4` |
| UI-GROUPS-E014 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if selected_group / for item in members | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/groups/{{ selected_group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/groups.html:4` |
| UI-GROUPS-E015 · 저장 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if selected_group / for item in members | 폼 제출: membership → /api/v1/admin/groups/{{ selected_group.id }}/members/{{ item.person.id }} / /api/v1/admin/groups/{{ selected_group.id }}/members/{{ item.person.id }} / 그룹 소속 활성 상태 변경; 대상·조직·사유 검사. | `desk/templates/desk/groups.html:4` |
| UI-GROUPS-E016 · {{ ticket.number }} · {{ ticket.title }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if selected_group / for ticket in open_tickets | 링크 이동:  /work/incidents/ /work/requests/ {{ ticket.id }} | `desk/templates/desk/groups.html:5` |
| UI-GROUPS-E017 · 삭제 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if selected_group | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/group-delete/{{ selected_group.id }} / 역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동. | `desk/templates/desk/groups.html:6` |
| UI-GROUPS-E018 · 미사용 그룹 삭제 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if selected_group | 폼 제출: manage-delete → /api/v1/management/group-delete/{{ selected_group.id }} / /api/v1/management/group-delete/{{ selected_group.id }} / 역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동. | `desk/templates/desk/groups.html:6` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
