# UI-LIST · 장애 목록

진입/사용: /portal/incidents, /work/incidents

소스: `desk/templates/desk/list.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.listing [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-LIST-F01

UI-LIST-F01 · 폼 · get 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-LIST-E002, UI-LIST-E003

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-LIST-E001 · + 장애 접수 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /portal/incidents/new | `desk/templates/desk/list.html:2` |
| UI-LIST-E002 · 상태 | select / name=status; id=status | 해당 화면/공통 영역 표시 시 / 선택값: =전체; NEW=접수; ASSIGNED=배정; IN_PROGRESS=처리 중; PENDING=대기; RESOLVED=해결; CLOSED=종료 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/list.html:4` |
| UI-LIST-E003 · 적용 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL 조회 조건 / 현재 URL 조회 조건 | `desk/templates/desk/list.html:4` |
| UI-LIST-E004 · 요청 · 제목 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/list.html:5` |
| UI-LIST-E005 · 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/list.html:5` |
| UI-LIST-E006 · 우선순위 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/list.html:5` |
| UI-LIST-E007 · 담당자 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/list.html:5` |
| UI-LIST-E008 · SLA 해결 기한 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/list.html:5` |
| UI-LIST-E009 · 접수일 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/list.html:5` |
| UI-LIST-E010 · {{ t.title }} | a / 별도 입력 제약 없음/조회 항목 | for t in items | 링크 이동:  /work /portal /incidents/{{ t.id }} | `desk/templates/desk/list.html:6` |
| UI-LIST-E011 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?status={{ selected_status\|urlencode }}&cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/list.html:8` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
