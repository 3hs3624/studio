# UI-PORTAL · 통합 포털

진입/사용: /

소스: `desk/templates/desk/portal.html`

연결: `desk/base.html`, `desk/dashboard-tasks.html`, `desk/delivery-overview.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.home [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PORTAL-E001 · ↗ ▦ ⌘ SYSTEM {{ app.icon }} {{ app.name }} {{ app.description }} 서비스 요청 장애 · 승인 SLA 자산 대장 구매 · 계약 재고 소스 변경 빌드 현황 배포 현황 | a / 별도 입력 제약 없음/조회 항목 | for app in systems | 링크 이동: {{ app.url }} | `desk/templates/desk/portal.html:3` |
| UI-PORTAL-E002 · 01 서비스 요청하기 필요한 서비스를 찾아 신청하세요 ↗ | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /catalog | `desk/templates/desk/portal.html:5` |
| UI-PORTAL-E003 · 02 장애 접수하기 IT 이용 중 발생한 문제를 알려주세요 ↗ | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /portal/incidents/new | `desk/templates/desk/portal.html:5` |
| UI-PORTAL-E004 · 03 내 지급 자산 사용 중인 자산과 지급 이력을 확인하세요 ↗ | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /my-assets | `desk/templates/desk/portal.html:5` |
| UI-PORTAL-E005 · 04 구성항목 찾아보기 조회 가능한 구성항목을 확인하세요 ↗ | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /cis | `desk/templates/desk/portal.html:5` |
| UI-PORTAL-E006 · 서비스 승인 대기 {{ pending_approvals }} 건 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /approvals | `desk/templates/desk/portal.html:5` |
| UI-PORTAL-E007 · 읽지 않은 알림 {{ unread_notifications }} 건 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /notifications | `desk/templates/desk/portal.html:5` |
| UI-PORTAL-E008 · 전체 현황 → | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /systems/resource | `desk/templates/desk/portal.html:6` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
