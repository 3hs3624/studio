# UI-ACCOUNT_SECURITY · 내 계정 보안

진입/사용: /account/security

소스: `desk/templates/desk/account-security.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): account_views.account_security [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-ACCOUNT_SECURITY-F01

UI-ACCOUNT_SECURITY-F01 · 폼 · post 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-ACCOUNT_SECURITY-E004, UI-ACCOUNT_SECURITY-E005, UI-ACCOUNT_SECURITY-E006, UI-ACCOUNT_SECURITY-E007, UI-ACCOUNT_SECURITY-E008, UI-ACCOUNT_SECURITY-E009

### UI-ACCOUNT_SECURITY-F02

UI-ACCOUNT_SECURITY-F02 · 폼 · post 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-ACCOUNT_SECURITY-E010, UI-ACCOUNT_SECURITY-E011, UI-ACCOUNT_SECURITY-E012, UI-ACCOUNT_SECURITY-E013

### UI-ACCOUNT_SECURITY-F03

UI-ACCOUNT_SECURITY-F03 · 폼 · post 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-ACCOUNT_SECURITY-E015, UI-ACCOUNT_SECURITY-E016, UI-ACCOUNT_SECURITY-E017, UI-ACCOUNT_SECURITY-E018

### UI-ACCOUNT_SECURITY-F04

UI-ACCOUNT_SECURITY-F04 · 폼 · post 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-ACCOUNT_SECURITY-E019, UI-ACCOUNT_SECURITY-E020, UI-ACCOUNT_SECURITY-E021, UI-ACCOUNT_SECURITY-E022

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ACCOUNT_SECURITY-E001 · 포털 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: / | `desk/templates/desk/account-security.html:1` |
| UI-ACCOUNT_SECURITY-E002 · 입력 항목 | p / 별도 입력 제약 없음/조회 항목 | if error | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/account-security.html:2` |
| UI-ACCOUNT_SECURITY-E003 · 입력 항목 | p / 별도 입력 제약 없음/조회 항목 | if notice | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/account-security.html:2` |
| UI-ACCOUNT_SECURITY-E004 · action | hidden / name=action; type=hidden; value=password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:4` |
| UI-ACCOUNT_SECURITY-E005 · 현재 비밀번호 | password / name=current_password; type=password; required; autocomplete=current-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:4` |
| UI-ACCOUNT_SECURITY-E006 · 새 비밀번호 | password / name=new_password; type=password; required; autocomplete=new-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:4` |
| UI-ACCOUNT_SECURITY-E007 · 새 비밀번호 확인 | password / name=confirm_password; type=password; required; autocomplete=new-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:4` |
| UI-ACCOUNT_SECURITY-E008 · MFA 인증번호 또는 복구 코드 | text / name=otp; required; autocomplete=one-time-code | if mfa_enabled | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:4` |
| UI-ACCOUNT_SECURITY-E009 · 비밀번호 변경 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL POST / 현재 URL POST | `desk/templates/desk/account-security.html:4` |
| UI-ACCOUNT_SECURITY-E010 · action | hidden / name=action; type=hidden; value=reauth | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:5` |
| UI-ACCOUNT_SECURITY-E011 · 현재 비밀번호 | password / name=current_password; type=password; required; autocomplete=current-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:5` |
| UI-ACCOUNT_SECURITY-E012 · MFA 인증번호 또는 복구 코드 | text / name=otp; required; autocomplete=one-time-code | if mfa_enabled | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:5` |
| UI-ACCOUNT_SECURITY-E013 · 재인증 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL POST / 현재 URL POST | `desk/templates/desk/account-security.html:5` |
| UI-ACCOUNT_SECURITY-E014 · 인증 앱에서 열기 | a / 별도 입력 제약 없음/조회 항목 | if not mfa_enabled | 링크 이동: {{ provisioning_uri }} | `desk/templates/desk/account-security.html:7` |
| UI-ACCOUNT_SECURITY-E015 · action | hidden / name=action; type=hidden; value=mfa_enroll | if not mfa_enabled | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:7` |
| UI-ACCOUNT_SECURITY-E016 · 현재 비밀번호 | password / name=current_password; type=password; required; autocomplete=current-password | if not mfa_enabled | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:7` |
| UI-ACCOUNT_SECURITY-E017 · 인증번호 | text / name=otp; required; pattern=[0-9]{6}; autocomplete=one-time-code | if not mfa_enabled | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:7` |
| UI-ACCOUNT_SECURITY-E018 · MFA 등록 | submit / 별도 입력 제약 없음/조회 항목 | if not mfa_enabled | 폼 제출: submit → 현재 URL POST / 현재 URL POST | `desk/templates/desk/account-security.html:7` |
| UI-ACCOUNT_SECURITY-E019 · action | hidden / name=action; type=hidden; value=mfa_disable | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:8` |
| UI-ACCOUNT_SECURITY-E020 · 현재 비밀번호 | password / name=current_password; type=password; required | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:8` |
| UI-ACCOUNT_SECURITY-E021 · 인증번호 또는 복구 코드 | text / name=otp; required; autocomplete=one-time-code | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/account-security.html:8` |
| UI-ACCOUNT_SECURITY-E022 · MFA 해제 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 폼 제출: submit → 현재 URL POST / 현재 URL POST | `desk/templates/desk/account-security.html:8` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
