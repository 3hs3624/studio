# UI-INVENTORY · 창고 · 재고

진입/사용: /inventory

소스: `desk/templates/desk/inventory.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): purchasing_views.inventory [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-INVENTORY-F01

UI-INVENTORY-F01 · stock-transfer · POST(JSON) /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동.

항목: UI-INVENTORY-E007, UI-INVENTORY-E008, UI-INVENTORY-E009, UI-INVENTORY-E010, UI-INVENTORY-E011, UI-INVENTORY-E012, UI-INVENTORY-E013

### UI-INVENTORY-F02

UI-INVENTORY-F02 · stock-issue · POST(JSON) /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고.

항목: UI-INVENTORY-E014, UI-INVENTORY-E015, UI-INVENTORY-E016, UI-INVENTORY-E017, UI-INVENTORY-E018, UI-INVENTORY-E019, UI-INVENTORY-E020, UI-INVENTORY-E021

### UI-INVENTORY-F03

UI-INVENTORY-F03 · stockroom · POST(JSON) /api/v1/inventory/stockrooms / 창고 기준정보와 위치 저장; 조직 범위 검사.

항목: UI-INVENTORY-E022, UI-INVENTORY-E023, UI-INVENTORY-E024, UI-INVENTORY-E025, UI-INVENTORY-E026

### UI-INVENTORY-F04

UI-INVENTORY-F04 · stock-item · POST(JSON) /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사.

항목: UI-INVENTORY-E027, UI-INVENTORY-E028, UI-INVENTORY-E029, UI-INVENTORY-E030, UI-INVENTORY-E031, UI-INVENTORY-E032, UI-INVENTORY-E033

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-INVENTORY-E001 · 수불 이력 → | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /inventory/movements | `desk/templates/desk/inventory.html:1` |
| UI-INVENTORY-E002 · 품목 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/inventory.html:2` |
| UI-INVENTORY-E003 · 창고 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/inventory.html:2` |
| UI-INVENTORY-E004 · 추적 방식 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/inventory.html:2` |
| UI-INVENTORY-E005 · 현재 수량 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/inventory.html:2` |
| UI-INVENTORY-E006 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/inventory.html:2` |
| UI-INVENTORY-E007 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E008 · 출발 재고 | select / name=balance; id=transfer-source; required | if is_stock_manager / 선택값: =품목 · 창고 선택; {{ b.id }}={{ b.item.name }} · {{ b.stockroom.name }} · {{ b.quantity }}개 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E009 · 도착 창고 | select / name=target_id; id=transfer-target; required | if is_stock_manager / 선택값: =창고 선택; {{ room.id }}={{ room.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E010 · 이동 수량 | number / name=quantity; id=transfer-quantity; type=number; required; min=1; max=1000000 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E011 · 이동할 개별 자산 | select / name=asset_ids; id=transfer-assets; multiple | if is_stock_manager / 선택값: {{ row.asset_id }}={{ row.asset.asset_no }} · {{ row.asset.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E012 · 이동 사유 | textarea / name=reason; id=transfer-reason; required; maxlength=10000 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E013 · 재고 이동 | submit / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 폼 제출: stock-transfer → /api/v1/inventory/transfer / /api/v1/inventory/transfer / 출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동. | `desk/templates/desk/inventory.html:3` |
| UI-INVENTORY-E014 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E015 · 출고 재고 | select / name=balance; id=issue-balance; required | if is_stock_manager / 선택값: =수량 품목 선택; {{ b.id }}={{ b.item.name }} · {{ b.stockroom.name }} · {{ b.quantity }}개 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E016 · 출고 수량 | number / name=quantity; id=issue-quantity; type=number; required; min=1; max=1000000 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E017 · 수령자 | select / name=person_id; id=issue-person; required | if is_stock_manager / 선택값: =선택하십시오.; {{ person.id }}={{ person.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E018 · 사용 위치 | text / name=destination; id=issue-destination; required; maxlength=200 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E019 · 관련 서비스 요청 · 선택 | select / name=service_request_id; id=issue-service-request | if is_stock_manager / 선택값: =연결 없음; {{ t.id }}={{ t.title }} · {{ t.requested_by.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E020 · 출고 사유 | textarea / name=reason; id=issue-reason; required; maxlength=10000 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E021 · 소모품 출고 | submit / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 폼 제출: stock-issue → /api/v1/inventory/issue / /api/v1/inventory/issue / 재고 가용 수량·대상자·연결 서비스요청을 검사해 출고. | `desk/templates/desk/inventory.html:4` |
| UI-INVENTORY-E022 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/inventory/stockrooms / 창고 기준정보와 위치 저장; 조직 범위 검사. | `desk/templates/desk/inventory.html:5` |
| UI-INVENTORY-E023 · 창고 코드 | text / name=code; id=room-code; required; maxlength=80 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/stockrooms / 창고 기준정보와 위치 저장; 조직 범위 검사. | `desk/templates/desk/inventory.html:5` |
| UI-INVENTORY-E024 · 창고 이름 | text / name=name; id=room-name; required; maxlength=200 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/stockrooms / 창고 기준정보와 위치 저장; 조직 범위 검사. | `desk/templates/desk/inventory.html:5` |
| UI-INVENTORY-E025 · 창고 위치 | text / name=location; id=room-location; required; maxlength=200 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/stockrooms / 창고 기준정보와 위치 저장; 조직 범위 검사. | `desk/templates/desk/inventory.html:5` |
| UI-INVENTORY-E026 · 창고 등록 | submit / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 폼 제출: stockroom → /api/v1/inventory/stockrooms / /api/v1/inventory/stockrooms / 창고 기준정보와 위치 저장; 조직 범위 검사. | `desk/templates/desk/inventory.html:5` |
| UI-INVENTORY-E027 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |
| UI-INVENTORY-E028 · 품목 코드 | text / name=code; id=item-code; required; maxlength=80 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |
| UI-INVENTORY-E029 · 품목 이름 | text / name=name; id=item-name; required; maxlength=200 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |
| UI-INVENTORY-E030 · 추적 방식 | select / name=tracking; id=item-tracking | if is_stock_manager / 선택값: BULK=수량 품목; SERIALIZED=일련번호 장비 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |
| UI-INVENTORY-E031 · 품목 제조사 · 장비 필수 | text / name=manufacturer; id=item-manufacturer; maxlength=200 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |
| UI-INVENTORY-E032 · 품목 모델 | text / name=model; id=item-model; maxlength=200 | if is_stock_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |
| UI-INVENTORY-E033 · 품목 등록 | submit / 별도 입력 제약 없음/조회 항목 | if is_stock_manager | 폼 제출: stock-item → /api/v1/inventory/items / /api/v1/inventory/items / 재고 품목·추적 방식을 저장; 코드/참조 검사. | `desk/templates/desk/inventory.html:6` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
