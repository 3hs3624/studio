# UI-LOGIN · 로그인

진입/사용: /login/

소스: `desk/templates/registration/login.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

### UI-LOGIN-F01

UI-LOGIN-F01 · 폼 · post 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-LOGIN-E002, UI-LOGIN-E003, UI-LOGIN-E004, UI-LOGIN-E005

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-LOGIN-E001 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if form.errors | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/registration/login.html:3` |
| UI-LOGIN-E002 · next | hidden / name=next; type=hidden; value={{ next }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/registration/login.html:4` |
| UI-LOGIN-E003 · 아이디 | text / name=username; id=id_username; required; autocomplete=username | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/registration/login.html:5` |
| UI-LOGIN-E004 · 비밀번호 | password / name=password; id=id_password; type=password; required; autocomplete=current-password | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL POST | `desk/templates/registration/login.html:6` |
| UI-LOGIN-E005 · 로그인 → | submit / type=submit | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL POST / 현재 URL POST | `desk/templates/registration/login.html:7` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
