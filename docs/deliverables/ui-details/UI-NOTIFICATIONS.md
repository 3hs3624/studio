# UI-NOTIFICATIONS · 알림함

진입/사용: /notifications

소스: `desk/templates/desk/notifications.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.notifications [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-NOTIFICATIONS-F01

UI-NOTIFICATIONS-F01 · notification-read · POST(JSON) /api/v1/notifications/{{ n.id }}/read / 접근 가능한 본인 알림을 읽음 처리.

항목: UI-NOTIFICATIONS-E002, UI-NOTIFICATIONS-E003

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-NOTIFICATIONS-E001 · {{ n.ticket_title }} | a / 별도 입력 제약 없음/조회 항목 | for n in items | 링크 이동: {{ n.ticket_url }} | `desk/templates/desk/notifications.html:3` |
| UI-NOTIFICATIONS-E002 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | for n in items / if not n.read_at | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/notifications/{{ n.id }}/read / 접근 가능한 본인 알림을 읽음 처리. | `desk/templates/desk/notifications.html:3` |
| UI-NOTIFICATIONS-E003 · 확인 | submit / 별도 입력 제약 없음/조회 항목 | for n in items / if not n.read_at | 폼 제출: notification-read → /api/v1/notifications/{{ n.id }}/read / /api/v1/notifications/{{ n.id }}/read / 접근 가능한 본인 알림을 읽음 처리. | `desk/templates/desk/notifications.html:3` |
| UI-NOTIFICATIONS-E004 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/notifications.html:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
