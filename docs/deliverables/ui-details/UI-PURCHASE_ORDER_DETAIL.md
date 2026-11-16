# UI-PURCHASE_ORDER_DETAIL · 발주 상세

진입/사용: /procurement/orders, /procurement/orders/<uuid:id>

소스: `desk/templates/desk/purchase-order-detail.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): purchasing_views.order [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-PURCHASE_ORDER_DETAIL-F01

UI-PURCHASE_ORDER_DETAIL-F01 · purchase-order-action · POST(JSON) /api/v1/procurement/orders/{{ order.id }}/actions / 발주 상태에 허용된 동작만 실행; 이미 입고한 수량 등 제약 유지.

항목: UI-PURCHASE_ORDER_DETAIL-E004, UI-PURCHASE_ORDER_DETAIL-E005, UI-PURCHASE_ORDER_DETAIL-E006, UI-PURCHASE_ORDER_DETAIL-E007

### UI-PURCHASE_ORDER_DETAIL-F02

UI-PURCHASE_ORDER_DETAIL-F02 · purchase-receipt · POST(JSON) /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지.

항목: UI-PURCHASE_ORDER_DETAIL-E008, UI-PURCHASE_ORDER_DETAIL-E009, UI-PURCHASE_ORDER_DETAIL-E010, UI-PURCHASE_ORDER_DETAIL-E011, UI-PURCHASE_ORDER_DETAIL-E012, UI-PURCHASE_ORDER_DETAIL-E013, UI-PURCHASE_ORDER_DETAIL-E014

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PURCHASE_ORDER_DETAIL-E001 · ← 발주 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /procurement/orders | `desk/templates/desk/purchase-order-detail.html:1` |
| UI-PURCHASE_ORDER_DETAIL-E002 · 발주 / 입고 / 잔량 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ order.quantity }} / {{ order.received_quantity }} / {{ order.remaining_quantity }} | `desk/templates/desk/purchase-order-detail.html:1` |
| UI-PURCHASE_ORDER_DETAIL-E003 · 단가 · 합계 | dt / 별도 입력 제약 없음/조회 항목 | if is_buyer | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ order.currency }} {{ order.unit_price }} · {{ order.total }} | `desk/templates/desk/purchase-order-detail.html:1` |
| UI-PURCHASE_ORDER_DETAIL-E004 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if order.can_release or order.can_cancel | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/orders/{{ order.id }}/actions / 발주 상태에 허용된 동작만 실행; 이미 입고한 수량 등 제약 유지. | `desk/templates/desk/purchase-order-detail.html:2` |
| UI-PURCHASE_ORDER_DETAIL-E005 · 동작 | select / name=action; id=order-action | if order.can_release or order.can_cancel / 선택값: RELEASE=발주 확정; CANCEL=발주 취소 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/actions / 발주 상태에 허용된 동작만 실행; 이미 입고한 수량 등 제약 유지. | `desk/templates/desk/purchase-order-detail.html:2` |
| UI-PURCHASE_ORDER_DETAIL-E006 · 사유 | textarea / name=reason; id=order-action-reason; required; maxlength=10000 | if order.can_release or order.can_cancel | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/actions / 발주 상태에 허용된 동작만 실행; 이미 입고한 수량 등 제약 유지. | `desk/templates/desk/purchase-order-detail.html:2` |
| UI-PURCHASE_ORDER_DETAIL-E007 · 발주 처리 | submit / 별도 입력 제약 없음/조회 항목 | if order.can_release or order.can_cancel | 폼 제출: purchase-order-action → /api/v1/procurement/orders/{{ order.id }}/actions / /api/v1/procurement/orders/{{ order.id }}/actions / 발주 상태에 허용된 동작만 실행; 이미 입고한 수량 등 제약 유지. | `desk/templates/desk/purchase-order-detail.html:2` |
| UI-PURCHASE_ORDER_DETAIL-E008 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if order.can_receive / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:3` |
| UI-PURCHASE_ORDER_DETAIL-E009 · 입고 창고 | select / name=stockroom_id; id=receipt-room; required | if order.can_receive / else (앞 분기 제외) / 선택값: =창고 선택; {{ room.id }}={{ room.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:3` |
| UI-PURCHASE_ORDER_DETAIL-E010 · 이번 입고 수량 | number / name=quantity; id=receipt-quantity; type=number; required; min=1; max={{ order.remaining_quantity }} | if order.can_receive / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:3` |
| UI-PURCHASE_ORDER_DETAIL-E011 · 입고 참조번호 | text / name=reference; id=receipt-reference; required; maxlength=80 | if order.can_receive / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:3` |
| UI-PURCHASE_ORDER_DETAIL-E012 · 개별 장비 · 한 줄에 자산번호,일련번호 | textarea / name=serials; id=receipt-serials; required; placeholder=PC-101,SERIAL-101 | if order.can_receive / else (앞 분기 제외) / if order.item.tracking == 'SERIALIZED' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:4` |
| UI-PURCHASE_ORDER_DETAIL-E013 · 입고 사유 | textarea / name=reason; id=receipt-reason; required; maxlength=10000 | if order.can_receive / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:4` |
| UI-PURCHASE_ORDER_DETAIL-E014 · 입고 확정 | submit / 별도 입력 제약 없음/조회 항목 | if order.can_receive / else (앞 분기 제외) | 폼 제출: purchase-receipt → /api/v1/procurement/orders/{{ order.id }}/receipts / /api/v1/procurement/orders/{{ order.id }}/receipts / 입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지. | `desk/templates/desk/purchase-order-detail.html:4` |
| UI-PURCHASE_ORDER_DETAIL-E015 · {{ a.asset_no }} → | a / 별도 입력 제약 없음/조회 항목 | for r in receipts / for a in r.assets | 링크 이동: /assets/{{ a.id }} | `desk/templates/desk/purchase-order-detail.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
