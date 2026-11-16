# UI-PURCHASE_REQUEST_DETAIL · 구매요청 상세

진입/사용: /procurement/requisitions, /procurement/requisitions/<uuid:id>

소스: `desk/templates/desk/purchase-request-detail.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): purchasing_views.requisition [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-PURCHASE_REQUEST_DETAIL-F01

UI-PURCHASE_REQUEST_DETAIL-F01 · purchase-decision · POST(JSON) /api/v1/procurement/requisitions/{{ purchase_request.id }}/decision / 구매 승인/반려. 승인자 자격·현재 상태·반려 사유 검사.

항목: UI-PURCHASE_REQUEST_DETAIL-E006, UI-PURCHASE_REQUEST_DETAIL-E007, UI-PURCHASE_REQUEST_DETAIL-E008, UI-PURCHASE_REQUEST_DETAIL-E009

### UI-PURCHASE_REQUEST_DETAIL-F02

UI-PURCHASE_REQUEST_DETAIL-F02 · purchase-order · POST(JSON) /api/v1/procurement/orders / 승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사.

항목: UI-PURCHASE_REQUEST_DETAIL-E010, UI-PURCHASE_REQUEST_DETAIL-E011, UI-PURCHASE_REQUEST_DETAIL-E012, UI-PURCHASE_REQUEST_DETAIL-E013, UI-PURCHASE_REQUEST_DETAIL-E014

### UI-PURCHASE_REQUEST_DETAIL-F03

UI-PURCHASE_REQUEST_DETAIL-F03 · purchase-cancel-request · POST(JSON) /api/v1/procurement/requisitions/{{ purchase_request.id }}/cancel / 신청자의 취소 가능 상태만 허용; 사유와 이력 보존.

항목: UI-PURCHASE_REQUEST_DETAIL-E015, UI-PURCHASE_REQUEST_DETAIL-E016, UI-PURCHASE_REQUEST_DETAIL-E017

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PURCHASE_REQUEST_DETAIL-E001 · ← 구매 요청 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /procurement/requisitions | `desk/templates/desk/purchase-request-detail.html:1` |
| UI-PURCHASE_REQUEST_DETAIL-E002 · 수량 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ purchase_request.quantity }} | `desk/templates/desk/purchase-request-detail.html:1` |
| UI-PURCHASE_REQUEST_DETAIL-E003 · 승인 단가 한도 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ purchase_request.currency }} {{ purchase_request.max_unit_price }} | `desk/templates/desk/purchase-request-detail.html:1` |
| UI-PURCHASE_REQUEST_DETAIL-E004 · 예산 합계 한도 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ purchase_request.currency }} {{ purchase_request.max_total }} | `desk/templates/desk/purchase-request-detail.html:1` |
| UI-PURCHASE_REQUEST_DETAIL-E005 · 사유 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ purchase_request.reason\|linebreaksbr }} | `desk/templates/desk/purchase-request-detail.html:1` |
| UI-PURCHASE_REQUEST_DETAIL-E006 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if purchase_request.can_decide | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/requisitions/{{ purchase_request.id }}/decision / 구매 승인/반려. 승인자 자격·현재 상태·반려 사유 검사. | `desk/templates/desk/purchase-request-detail.html:2` |
| UI-PURCHASE_REQUEST_DETAIL-E007 · 결정 | select / name=decision; id=purchase-decision | if purchase_request.can_decide / 선택값: APPROVE=승인; REJECT=반려 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions/{{ purchase_request.id }}/decision / 구매 승인/반려. 승인자 자격·현재 상태·반려 사유 검사. | `desk/templates/desk/purchase-request-detail.html:2` |
| UI-PURCHASE_REQUEST_DETAIL-E008 · 결정 사유 · 반려 시 필수 | textarea / name=reason; id=purchase-decision-reason; maxlength=10000 | if purchase_request.can_decide | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions/{{ purchase_request.id }}/decision / 구매 승인/반려. 승인자 자격·현재 상태·반려 사유 검사. | `desk/templates/desk/purchase-request-detail.html:2` |
| UI-PURCHASE_REQUEST_DETAIL-E009 · 구매 결정 저장 | submit / 별도 입력 제약 없음/조회 항목 | if purchase_request.can_decide | 폼 제출: purchase-decision → /api/v1/procurement/requisitions/{{ purchase_request.id }}/decision / /api/v1/procurement/requisitions/{{ purchase_request.id }}/decision / 구매 승인/반려. 승인자 자격·현재 상태·반려 사유 검사. | `desk/templates/desk/purchase-request-detail.html:2` |
| UI-PURCHASE_REQUEST_DETAIL-E010 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if purchase_request.can_order | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/orders / 승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사. | `desk/templates/desk/purchase-request-detail.html:3` |
| UI-PURCHASE_REQUEST_DETAIL-E011 · 공급업체 | select / name=supplier_id; id=order-supplier; required | if purchase_request.can_order / 선택값: =공급업체 선택; {{ supplier.id }}={{ supplier.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders / 승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사. | `desk/templates/desk/purchase-request-detail.html:3` |
| UI-PURCHASE_REQUEST_DETAIL-E012 · 계약 · 선택 | select / name=contract_id; id=order-contract | if purchase_request.can_order / 선택값: =계약 없음; {{ contract.id }}={{ contract.code }} · {{ contract.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders / 승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사. | `desk/templates/desk/purchase-request-detail.html:3` |
| UI-PURCHASE_REQUEST_DETAIL-E013 · 발주 단가 · {{ purchase_request.currency }} | number / name=unit_price; id=order-unit-price; type=number; required; min=0.01; max={{ purchase_request.max_unit_price }}; step=0.01 | if purchase_request.can_order | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/orders / 승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사. | `desk/templates/desk/purchase-request-detail.html:3` |
| UI-PURCHASE_REQUEST_DETAIL-E014 · 발주 초안 생성 | submit / 별도 입력 제약 없음/조회 항목 | if purchase_request.can_order | 폼 제출: purchase-order → /api/v1/procurement/orders / /api/v1/procurement/orders / 승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사. | `desk/templates/desk/purchase-request-detail.html:3` |
| UI-PURCHASE_REQUEST_DETAIL-E015 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if can_cancel_request | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/requisitions/{{ purchase_request.id }}/cancel / 신청자의 취소 가능 상태만 허용; 사유와 이력 보존. | `desk/templates/desk/purchase-request-detail.html:4` |
| UI-PURCHASE_REQUEST_DETAIL-E016 · 취소 사유 | textarea / name=reason; id=cancel-reason; required; maxlength=10000 | if can_cancel_request | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions/{{ purchase_request.id }}/cancel / 신청자의 취소 가능 상태만 허용; 사유와 이력 보존. | `desk/templates/desk/purchase-request-detail.html:4` |
| UI-PURCHASE_REQUEST_DETAIL-E017 · 요청 취소 | submit / 별도 입력 제약 없음/조회 항목 | if can_cancel_request | 폼 제출: purchase-cancel-request → /api/v1/procurement/requisitions/{{ purchase_request.id }}/cancel / /api/v1/procurement/requisitions/{{ purchase_request.id }}/cancel / 신청자의 취소 가능 상태만 허용; 사유와 이력 보존. | `desk/templates/desk/purchase-request-detail.html:4` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
