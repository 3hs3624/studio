# UI-PURCHASE_ORDERS · 발주 · 입고

진입/사용: /procurement/orders

소스: `desk/templates/desk/purchase-orders.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): purchasing_views.orders [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PURCHASE_ORDERS-E001 · 구매 요청 → | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /procurement/requisitions | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E002 · 발주 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E003 · 공급업체 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E004 · 수량 · 입고 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E005 · 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E006 · 금액 | th / 별도 입력 제약 없음/조회 항목 | if is_buyer | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E007 · {{ o.item.name }} | a / 별도 입력 제약 없음/조회 항목 | for o in items | 링크 이동: /procurement/orders/{{ o.id }} | `desk/templates/desk/purchase-orders.html:1` |
| UI-PURCHASE_ORDERS-E008 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/purchase-orders.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
