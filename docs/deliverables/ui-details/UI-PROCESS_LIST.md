# UI-PROCESS_LIST · 화면/워크플로우/결재선 목록

진입/사용: /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new

소스: `desk/templates/desk/process-list.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): process_views.manage [workflow.manage]

## 기능/폼 계약

### UI-PROCESS_LIST-F01

UI-PROCESS_LIST-F01 · 폼 · get 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-PROCESS_LIST-E002, UI-PROCESS_LIST-E003, UI-PROCESS_LIST-E004, UI-PROCESS_LIST-E005

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PROCESS_LIST-E001 · 새 정의 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ process_base }}/new | `desk/templates/desk/process-list.html:2` |
| UI-PROCESS_LIST-E002 · 이름·코드 검색 | text / name=q; maxlength=100; value={{ search }}; placeholder=정의 이름 또는 코드 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/process-list.html:3` |
| UI-PROCESS_LIST-E003 · 사용 상태 | select / name=state | 해당 화면/공통 영역 표시 시 / 선택값: all=전체; active=사용; inactive=중지 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/process-list.html:3` |
| UI-PROCESS_LIST-E004 · 검색 | submit / type=submit | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL 조회 조건 / 현재 URL 조회 조건 | `desk/templates/desk/process-list.html:3` |
| UI-PROCESS_LIST-E005 · 초기화 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ process_base }} / 현재 URL 조회 조건 | `desk/templates/desk/process-list.html:3` |
| UI-PROCESS_LIST-E006 · 정의 이름 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E007 · 코드 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E008 · 사용 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E009 · 게시 버전 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E010 · 초안 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E011 · 초안 작성자 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E012 · 상세 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E013 · {{ definition.name }} | a / 별도 입력 제약 없음/조회 항목 | for definition in definition_page | 링크 이동: {{ process_base }}/{{ definition.id }} | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E014 · 열기 → | a / 별도 입력 제약 없음/조회 항목 | for definition in definition_page | 링크 이동: {{ process_base }}/{{ definition.id }} | `desk/templates/desk/process-list.html:4` |
| UI-PROCESS_LIST-E015 · ← 이전 | a / 별도 입력 제약 없음/조회 항목 | if definition_page.has_other_pages / if definition_page.has_previous | 링크 이동: ?{{ list_query }}&page={{ definition_page.previous_page_number }} | `desk/templates/desk/process-list.html:5` |
| UI-PROCESS_LIST-E016 · 다음 → | a / 별도 입력 제약 없음/조회 항목 | if definition_page.has_other_pages / if definition_page.has_next | 링크 이동: ?{{ list_query }}&page={{ definition_page.next_page_number }} | `desk/templates/desk/process-list.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
