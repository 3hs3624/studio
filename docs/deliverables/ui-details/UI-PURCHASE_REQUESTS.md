# UI-PURCHASE_REQUESTS · 구매 요청 · 승인

진입/사용: /procurement/requisitions

소스: `desk/templates/desk/purchase-requests.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): purchasing_views.requisitions [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-PURCHASE_REQUESTS-F01

UI-PURCHASE_REQUESTS-F01 · purchase-request · POST(JSON) /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성.

항목: UI-PURCHASE_REQUESTS-E002, UI-PURCHASE_REQUESTS-E003, UI-PURCHASE_REQUESTS-E004, UI-PURCHASE_REQUESTS-E005, UI-PURCHASE_REQUESTS-E006, UI-PURCHASE_REQUESTS-E007, UI-PURCHASE_REQUESTS-E008, UI-PURCHASE_REQUESTS-E009, UI-PURCHASE_REQUESTS-E010

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PURCHASE_REQUESTS-E001 · 발주 목록 → | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /procurement/orders | `desk/templates/desk/purchase-requests.html:1` |
| UI-PURCHASE_REQUESTS-E002 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if can_purchase_request | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E003 · 품목 | select / name=item_id; id=purchase-item; required | if can_purchase_request / 선택값: =선택하십시오.; {{ item.id }}={{ item.code }} · {{ item.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E004 · 수량 | number / name=quantity; id=purchase-quantity; type=number; required; min=1; max=1000000 | if can_purchase_request | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E005 · 통화 | select / name=currency; id=purchase-currency | if can_purchase_request / 선택값: KRW=KRW; USD=USD; EUR=EUR | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E006 · 승인 요청 단가 한도 | number / name=max_unit_price; id=purchase-price; type=number; required; min=0.01; step=0.01 | if can_purchase_request | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E007 · 구매 승인자 | select / name=approver_id; id=purchase-approver; required | if can_purchase_request / 선택값: =구매 관리자 선택; {{ person.id }}={{ person.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E008 · 관련 서비스 요청 · 선택 | select / name=source_request_id; id=source-service-request | if can_purchase_request / 선택값: =연결 없음; {{ t.id }}={{ t.title }} · {{ t.requested_by.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E009 · 구매 사유 | textarea / name=reason; id=purchase-reason; required; maxlength=10000 | if can_purchase_request | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E010 · 구매 요청 | submit / 별도 입력 제약 없음/조회 항목 | if can_purchase_request | 폼 제출: purchase-request → /api/v1/procurement/requisitions / /api/v1/procurement/requisitions / 품목·수량·승인자·연결 요청 검증 후 구매 요청 생성. | `desk/templates/desk/purchase-requests.html:2` |
| UI-PURCHASE_REQUESTS-E011 · 품목 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-requests.html:3` |
| UI-PURCHASE_REQUESTS-E012 · 수량 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-requests.html:3` |
| UI-PURCHASE_REQUESTS-E013 · 예산 한도 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-requests.html:3` |
| UI-PURCHASE_REQUESTS-E014 · 승인자 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-requests.html:3` |
| UI-PURCHASE_REQUESTS-E015 · 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/purchase-requests.html:3` |
| UI-PURCHASE_REQUESTS-E016 · {{ r.item.name }} | a / 별도 입력 제약 없음/조회 항목 | for r in items / if r.status | 링크 이동: /procurement/requisitions/{{ r.id }} | `desk/templates/desk/purchase-requests.html:3` |
| UI-PURCHASE_REQUESTS-E017 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/purchase-requests.html:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
