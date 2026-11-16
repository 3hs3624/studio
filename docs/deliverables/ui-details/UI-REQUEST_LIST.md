# UI-REQUEST_LIST · 승인함 서비스 요청 처리 전체 서비스 요청 내 서비스 요청

진입/사용: /approvals, /portal/requests, /work/requests

소스: `desk/templates/desk/request-list.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.request_listing [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-REQUEST_LIST-F01

UI-REQUEST_LIST-F01 · 폼 · 원본 참조 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-REQUEST_LIST-E002, UI-REQUEST_LIST-E003

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-REQUEST_LIST-E001 · + 서비스 신청 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /catalog | `desk/templates/desk/request-list.html:2` |
| UI-REQUEST_LIST-E002 · 상태 | select / name=status; id=request-status | 해당 화면/공통 영역 표시 시 / 선택값: =전체; {{ state }}={{ state\|state_label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E003 · 적용 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit →  | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E004 · 서비스 요청 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E005 · 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E006 · 담당자 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E007 · 접수일 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E008 · {{ t.title }} | a / 별도 입력 제약 없음/조회 항목 | for t in items | 링크 이동: /portal/requests/{{ t.id }} | `desk/templates/desk/request-list.html:3` |
| UI-REQUEST_LIST-E009 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?status={{ selected_status\|urlencode }}&cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/request-list.html:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
