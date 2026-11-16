# UI-CONSOLE_TABS · 공통 상세 탭

진입/사용: /admin/access, /admin/plugins, /console/access, /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/plugins, /console/plugins/<str:plugin_id>, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/security, /console/security/<str:category>, /console/users, /console/users/<str:id>, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new

소스: `desk/templates/desk/console-tabs.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CONSOLE_TABS-E001 · {{ tab.label }} | a / 별도 입력 제약 없음/조회 항목 | for tab in tabs | 링크 이동: {{ tab.url }} | `desk/templates/desk/console-tabs.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
