# UI-SYSTEM_HOME · 시스템별 업무 현황

진입/사용: /systems/asset, /systems/resource, /systems/service

소스: `desk/templates/desk/system-home.html`

연결: `desk/base.html`, `desk/dashboard-tasks.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.system_home [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-SYSTEM_HOME-E001 · {{ primary_label }} ＋ | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ primary_url }} | `desk/templates/desk/system-home.html:2` |
| UI-SYSTEM_HOME-E002 · {{ metric.label }} {{ metric.value }} 건 ↗ | a / 별도 입력 제약 없음/조회 항목 | for metric in metrics | 링크 이동: {{ metric.url }} | `desk/templates/desk/system-home.html:3` |
| UI-SYSTEM_HOME-E003 · 번호 · 이름 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/system-home.html:5` |
| UI-SYSTEM_HOME-E004 · 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/system-home.html:5` |
| UI-SYSTEM_HOME-E005 · 상세 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/system-home.html:5` |
| UI-SYSTEM_HOME-E006 · {{ item.title }} | a / 별도 입력 제약 없음/조회 항목 | for item in recent_items | 링크 이동: {{ item.url }} | `desk/templates/desk/system-home.html:5` |
| UI-SYSTEM_HOME-E007 · {{ item.title }} 상세 보기 | a / aria-label={{ item.title }} 상세 보기 | for item in recent_items | 링크 이동: {{ item.url }} | `desk/templates/desk/system-home.html:5` |
| UI-SYSTEM_HOME-E008 · {{ primary_label }} | a / 별도 입력 제약 없음/조회 항목 | empty (앞 분기 제외) | 링크 이동: {{ primary_url }} | `desk/templates/desk/system-home.html:5` |
| UI-SYSTEM_HOME-E009 · {{ link.label }} → | a / 별도 입력 제약 없음/조회 항목 | for group in nav_groups / for link in group.links / if link.url != system.url | 링크 이동: {{ link.url }} | `desk/templates/desk/system-home.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
