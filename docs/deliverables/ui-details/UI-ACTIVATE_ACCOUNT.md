# UI-ACTIVATE_ACCOUNT · 초대 계정 비밀번호 설정

진입/사용: /activate/<str:uid>/

소스: `desk/templates/desk/activate-account.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): account_views.activate_account [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-ACTIVATE_ACCOUNT-F01

UI-ACTIVATE_ACCOUNT-F01 · 폼 · post 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-ACTIVATE_ACCOUNT-E002, UI-ACTIVATE_ACCOUNT-E003, UI-ACTIVATE_ACCOUNT-E004, UI-ACTIVATE_ACCOUNT-E005

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ACTIVATE_ACCOUNT-E001 · 입력 항목 | p / 별도 입력 제약 없음/조회 항목 | if error | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/activate-account.html:1` |
| UI-ACTIVATE_ACCOUNT-E002 · token | hidden / name=token; id=activation-token; type=hidden | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/activate-account.html:1` |
| UI-ACTIVATE_ACCOUNT-E003 · 새 비밀번호 | password / name=new_password; type=password; required; autocomplete=new-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/activate-account.html:1` |
| UI-ACTIVATE_ACCOUNT-E004 · 비밀번호 확인 | password / name=confirm_password; type=password; required; autocomplete=new-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/desk/activate-account.html:1` |
| UI-ACTIVATE_ACCOUNT-E005 · 계정 활성화 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL POST / 현재 URL POST | `desk/templates/desk/activate-account.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
