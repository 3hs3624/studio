# UI-USERS · 사용자 관리

진입/사용: /console/users, /console/users/<str:id>

소스: `desk/templates/desk/users.html`

연결: `desk/console-tabs.html`

뷰·권한 참조(동시 필수 권한 목록 아님): identity_views.users [users.manage]

## 기능/폼 계약

### UI-USERS-F01

UI-USERS-F01 · 폼 · get 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-USERS-E002, UI-USERS-E003, UI-USERS-E004, UI-USERS-E005, UI-USERS-E006, UI-USERS-E007

### UI-USERS-F02

UI-USERS-F02 · user-create · POST(JSON) /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세

항목: UI-USERS-E013, UI-USERS-E014, UI-USERS-E015, UI-USERS-E016, UI-USERS-E017, UI-USERS-E018, UI-USERS-E019, UI-USERS-E020, UI-USERS-E021, UI-USERS-E022, UI-USERS-E023, UI-USERS-E024, UI-USERS-E025, UI-USERS-E026, UI-USERS-E027, UI-USERS-E028, UI-USERS-E029

### UI-USERS-F03

UI-USERS-F03 · user-save · POST(JSON) /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사

항목: UI-USERS-E031, UI-USERS-E032, UI-USERS-E033, UI-USERS-E034, UI-USERS-E035, UI-USERS-E036, UI-USERS-E037, UI-USERS-E038, UI-USERS-E039

### UI-USERS-F04

UI-USERS-F04 · account · POST(JSON) /api/v1/admin/persons/{{ selected_user.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한.

항목: UI-USERS-E042, UI-USERS-E043, UI-USERS-E044

### UI-USERS-F05

UI-USERS-F05 · user-reset · POST(JSON) /api/v1/management/user-reset/{{ selected_user.id }} / 비밀번호 정책을 검증해 임시 비밀번호 설정 및 변경 강제; 비밀값을 문서/로그에 기록하지 않음

항목: UI-USERS-E045, UI-USERS-E046, UI-USERS-E047

### UI-USERS-F06

UI-USERS-F06 · user-action · POST(JSON) /api/v1/management/user-unlock/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용.

항목: UI-USERS-E048, UI-USERS-E049

### UI-USERS-F07

UI-USERS-F07 · user-action · POST(JSON) /api/v1/management/user-mfa-reset/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용.

항목: UI-USERS-E050, UI-USERS-E051

### UI-USERS-F08

UI-USERS-F08 · user-invite · POST(JSON) /api/v1/management/user-invite/{{ selected_user.id }} / 초대 링크를 결과 영역에 표시; 개인정보/비밀번호를 복제하지 않음.

항목: UI-USERS-E052, UI-USERS-E053, UI-USERS-E054

### UI-USERS-F09

UI-USERS-F09 · user-action · POST(JSON) /api/v1/management/user-erase/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용.

항목: UI-USERS-E055, UI-USERS-E056, UI-USERS-E057

### UI-USERS-F10

UI-USERS-F10 · user-session · POST(JSON) /api/v1/management/user-session/{{ selected_user.id }} / 선택 세션 회수; 조직 경계·소유자/관리 권한 검사.

항목: UI-USERS-E058, UI-USERS-E059, UI-USERS-E060

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-USERS-E001 · 사용자 목록 사용자 생성 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/users /new  | `desk/templates/desk/users.html:2` |
| UI-USERS-E002 · 로그인 ID·이름 검색 | text / name=q; value={{ q }} | if not selected_user and not new_user | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/users.html:3` |
| UI-USERS-E003 · 상태 | select / name=status | if not selected_user and not new_user / 선택값: =전체; active=활성; inactive=중지 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/users.html:3` |
| UI-USERS-E004 · 부서 | select / name=department | if not selected_user and not new_user / 선택값: =전체; {{ department.id }}={{ department.indent }}{{ department.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/users.html:3` |
| UI-USERS-E005 · 그룹 | select / name=group | if not selected_user and not new_user / 선택값: =전체; {{ group.id }}={{ group.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/users.html:3` |
| UI-USERS-E006 · 역할 | select / name=role | if not selected_user and not new_user / 선택값: =전체; {{ role.code }}={{ role.name\|role_label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/users.html:3` |
| UI-USERS-E007 · 조회 | submit / 별도 입력 제약 없음/조회 항목 | if not selected_user and not new_user | 폼 제출: submit → 현재 URL 조회 조건 / 현재 URL 조회 조건 | `desk/templates/desk/users.html:3` |
| UI-USERS-E008 · 이름 | th / 별도 입력 제약 없음/조회 항목 | if not selected_user and not new_user | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/users.html:3` |
| UI-USERS-E009 · 로그인 ID | th / 별도 입력 제약 없음/조회 항목 | if not selected_user and not new_user | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/users.html:3` |
| UI-USERS-E010 · 상태 | th / 별도 입력 제약 없음/조회 항목 | if not selected_user and not new_user | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/users.html:3` |
| UI-USERS-E011 · 사용 종료일 | th / 별도 입력 제약 없음/조회 항목 | if not selected_user and not new_user | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/users.html:3` |
| UI-USERS-E012 · {{ member.display_name }} | a / 별도 입력 제약 없음/조회 항목 | if not selected_user and not new_user / for member in people | 링크 이동: /console/users/{{ member.id }} | `desk/templates/desk/users.html:3` |
| UI-USERS-E013 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | elif new_user (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E014 · 로그인 ID | text / name=username; required; maxlength=150; autocomplete=off | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E015 · 이름 | text / name=full_name; required; maxlength=200 | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E016 · 부서 | select / name=department_id | elif new_user (앞 분기 제외) / 선택값: =미지정; {{ department.id }}={{ department.indent }}{{ department.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E017 · 이메일 | email / name=email; type=email; maxlength=254 | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E018 · 연락처 | text / name=phone; maxlength=40 | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E019 · 사번 | text / name=employee_id; maxlength=80 | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E020 · 초기 비밀번호(초대 방식이 아닐 때) | password / name=password; type=password; autocomplete=new-password | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E021 · 초대 방식 | checkbox / name=invite; type=checkbox; checked | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E022 · 생성 사유 | text / name=reason; required; maxlength=500 | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:4` |
| UI-USERS-E023 · 기존 사용자 | select / 별도 입력 제약 없음/조회 항목 | elif new_user (앞 분기 제외) / 선택값: =선택; {{ member.id }}={{ member.display_name }} · {{ member.user.username }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E024 · 복제할 부서 | select / 별도 입력 제약 없음/조회 항목 | elif new_user (앞 분기 제외) / 선택값: =선택; {{ department.id }}={{ department.indent }}{{ department.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E025 · 사용자 할당 조회 | button / type=button | elif new_user (앞 분기 제외) | 선택 사용자/부서 할당을 조회하고 복제할 역할·그룹 선택 목록과 토큰 갱신 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E026 · 부서 할당 조회 | button / type=button | elif new_user (앞 분기 제외) | 선택 사용자/부서 할당을 조회하고 복제할 역할·그룹 선택 목록과 토큰 갱신 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E027 · allocation_token | hidden / name=allocation_token; type=hidden | elif new_user (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E028 · data-copy-error | div / 별도 입력 제약 없음/조회 항목 | elif new_user (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E029 · 사용자 생성 | submit / 별도 입력 제약 없음/조회 항목 | elif new_user (앞 분기 제외) | 폼 제출: user-create → /api/v1/management/users / /api/v1/management/users / 초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세 | `desk/templates/desk/users.html:5` |
| UI-USERS-E030 · 개인정보 조회·편집(재인증 및 접근 이력 기록) | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'profile' / if not reveal | 링크 이동: ?tab=profile&reveal=1 | `desk/templates/desk/users.html:7` |
| UI-USERS-E031 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'profile' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E032 · 이름 | text / name=full_name; required; maxlength=200; value={{ profile.full_name }} | else (앞 분기 제외) / if active_tab == 'profile' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E033 · 이메일 | email / name=email; type=email; maxlength=254; value={{ profile.email }} | else (앞 분기 제외) / if active_tab == 'profile' / if reveal | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E034 · 연락처 | text / name=phone; maxlength=40; value={{ profile.phone }} | else (앞 분기 제외) / if active_tab == 'profile' / if reveal | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E035 · 사번 | text / name=employee_id; maxlength=80; value={{ profile.employee_id }} | else (앞 분기 제외) / if active_tab == 'profile' / if reveal | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E036 · 부서 | select / name=department_id | else (앞 분기 제외) / if active_tab == 'profile' / 선택값: =미지정; {{ department.id }}={{ department.indent }}{{ department.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E037 · 사용 종료일 | date / name=expires_on; type=date; value={{ selected_user.expires_on\|date:'Y-m-d' }} | else (앞 분기 제외) / if active_tab == 'profile' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E038 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if active_tab == 'profile' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E039 · 사용자 정보 저장 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'profile' | 폼 제출: user-save → /api/v1/management/users/{{ selected_user.id }} / /api/v1/management/users/{{ selected_user.id }} / 개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사 | `desk/templates/desk/users.html:8` |
| UI-USERS-E040 · 역할 배정 관리 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'roles' (앞 분기 제외) | 링크 이동: /console/access?tab=roles | `desk/templates/desk/users.html:9` |
| UI-USERS-E041 · 그룹 구성 관리 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'roles' (앞 분기 제외) | 링크 이동: /console/access?tab=groups | `desk/templates/desk/users.html:9` |
| UI-USERS-E042 · active | hidden / name=active; type=hidden; value= false true  | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ selected_user.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/users.html:11` |
| UI-USERS-E043 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/persons/{{ selected_user.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/users.html:11` |
| UI-USERS-E044 · 계정 중지 계정 재활성화 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 폼 제출: account → /api/v1/admin/persons/{{ selected_user.id }}/account / /api/v1/admin/persons/{{ selected_user.id }}/account / 계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한. | `desk/templates/desk/users.html:11` |
| UI-USERS-E045 · 새 임시 비밀번호 | password / name=password; type=password; required; autocomplete=new-password | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-reset/{{ selected_user.id }} / 비밀번호 정책을 검증해 임시 비밀번호 설정 및 변경 강제; 비밀값을 문서/로그에 기록하지 않음 | `desk/templates/desk/users.html:12` |
| UI-USERS-E046 · 초기화 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-reset/{{ selected_user.id }} / 비밀번호 정책을 검증해 임시 비밀번호 설정 및 변경 강제; 비밀값을 문서/로그에 기록하지 않음 | `desk/templates/desk/users.html:12` |
| UI-USERS-E047 · 비밀번호 초기화·변경 강제 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 폼 제출: user-reset → /api/v1/management/user-reset/{{ selected_user.id }} / /api/v1/management/user-reset/{{ selected_user.id }} / 비밀번호 정책을 검증해 임시 비밀번호 설정 및 변경 강제; 비밀값을 문서/로그에 기록하지 않음 | `desk/templates/desk/users.html:12` |
| UI-USERS-E048 · 잠금 해제 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-unlock/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:13` |
| UI-USERS-E049 · 잠금 해제 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 폼 제출: user-action → /api/v1/management/user-unlock/{{ selected_user.id }} / /api/v1/management/user-unlock/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:13` |
| UI-USERS-E050 · MFA 초기화 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-mfa-reset/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:14` |
| UI-USERS-E051 · MFA 초기화 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) | 폼 제출: user-action → /api/v1/management/user-mfa-reset/{{ selected_user.id }} / /api/v1/management/user-mfa-reset/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:14` |
| UI-USERS-E052 · 초대 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) / if not selected_user.user.has_usable_password | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-invite/{{ selected_user.id }} / 초대 링크를 결과 영역에 표시; 개인정보/비밀번호를 복제하지 않음. | `desk/templates/desk/users.html:15` |
| UI-USERS-E053 · 초대 링크 발급 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) / if not selected_user.user.has_usable_password | 폼 제출: user-invite → /api/v1/management/user-invite/{{ selected_user.id }} / /api/v1/management/user-invite/{{ selected_user.id }} / 초대 링크를 결과 영역에 표시; 개인정보/비밀번호를 복제하지 않음. | `desk/templates/desk/users.html:15` |
| UI-USERS-E054 · data-invitation-output | pre / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) / if not selected_user.user.has_usable_password | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-invite/{{ selected_user.id }} / 초대 링크를 결과 영역에 표시; 개인정보/비밀번호를 복제하지 않음. | `desk/templates/desk/users.html:15` |
| UI-USERS-E055 · 개인정보 파기 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) / if not selected_user.active | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-erase/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:16` |
| UI-USERS-E056 · 복원할 수 없으며 업무 참조 ID와 감사 이력은 유지됨을 확인합니다. | checkbox / type=checkbox; required | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) / if not selected_user.active | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-erase/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:16` |
| UI-USERS-E057 · 개인정보 파기 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'security' (앞 분기 제외) / if not selected_user.active | 폼 제출: user-action → /api/v1/management/user-erase/{{ selected_user.id }} / /api/v1/management/user-erase/{{ selected_user.id }} / 잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용. | `desk/templates/desk/users.html:16` |
| UI-USERS-E058 · session_id | hidden / name=session_id; type=hidden; value={{ session.id }} | else (앞 분기 제외) / elif active_tab == 'sessions' (앞 분기 제외) / for session in user_sessions / if not session.revoked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-session/{{ selected_user.id }} / 선택 세션 회수; 조직 경계·소유자/관리 권한 검사. | `desk/templates/desk/users.html:17` |
| UI-USERS-E059 · 회수 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'sessions' (앞 분기 제외) / for session in user_sessions / if not session.revoked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/user-session/{{ selected_user.id }} / 선택 세션 회수; 조직 경계·소유자/관리 권한 검사. | `desk/templates/desk/users.html:17` |
| UI-USERS-E060 · 세션 회수 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'sessions' (앞 분기 제외) / for session in user_sessions / if not session.revoked | 폼 제출: user-session → /api/v1/management/user-session/{{ selected_user.id }} / /api/v1/management/user-session/{{ selected_user.id }} / 선택 세션 회수; 조직 경계·소유자/관리 권한 검사. | `desk/templates/desk/users.html:17` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
