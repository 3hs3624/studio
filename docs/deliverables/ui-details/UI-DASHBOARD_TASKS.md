# UI-DASHBOARD_TASKS · 내가 할 일 공통 영역

진입/사용: /, /systems/asset, /systems/resource, /systems/service

소스: `desk/templates/desk/dashboard-tasks.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-DASHBOARD_TASKS-E001 · {{ tab.label }} | a / 별도 입력 제약 없음/조회 항목 | for tab in todo_tabs | 링크 이동: {{ tab.url }} | `desk/templates/desk/dashboard-tasks.html:1` |
| UI-DASHBOARD_TASKS-E002 · 업무 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/dashboard-tasks.html:1` |
| UI-DASHBOARD_TASKS-E003 · 유형 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/dashboard-tasks.html:1` |
| UI-DASHBOARD_TASKS-E004 · 현재 단계 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/dashboard-tasks.html:1` |
| UI-DASHBOARD_TASKS-E005 · 생성일 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/dashboard-tasks.html:1` |
| UI-DASHBOARD_TASKS-E006 · {{ row.title }} | a / 별도 입력 제약 없음/조회 항목 | for row in todo_rows | 링크 이동: {{ row.url }} | `desk/templates/desk/dashboard-tasks.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
