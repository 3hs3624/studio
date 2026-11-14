# 구매·계약·입고·창고 재고

기준일: 2026-11-04. PRC-01/02, INV-01, CTR-01의 일부 구현입니다. 재고 실사·조정 승인·납품 반품·회계 처리는 아직 포함하지 않습니다.

## 제공 업무와 화면

- /procurement/requisitions: 구매 요청 작성·지정 승인자 결정. 요청에는 품목 1개·수량·통화·단가 한도를 고정합니다.
- /procurement/orders: 승인된 요청에서 발주 초안 작성→확정→부분/완전 입고. 발주당 품목 1개로 시작합니다.
- /inventory: 창고·품목 등록, 창고별 잔량, 창고 간 이동, 소모품 출고
- /inventory/movements: 입고·출고·반납·이동·폐기의 불변 수불 이력
- /contracts: 공급업체·계약 등록, 유효기간·확정 발주 합계·잔여 한도, 자산 계약 연결

발주 확정은 시스템 기록이며 실제 공급업체에 메일·주문을 전송하지 않습니다. 입고·인수·폐기는 담당자가 실물 작업 후 기록합니다.

## 역할

| 역할 | 권한 |
|---|---|
| PROCUREMENT_MANAGER(구매 관리자) | 공급업체·계약 등록, 구매 승인(지정자만), 발주 생성·확정·취소, 구매 금액·계약 한도 조회 |
| SERVICE_MANAGER(서비스 관리자) | 본인 구매 요청 작성·조회·취소, 본인 요청의 발주 진행 조회. 다른 요청과 발주 금액에 자동 접근하지 않음 |
| STOCK_MANAGER(재고 관리자) | 창고·품목 등록, 발주 입고, 잔량·수불 조회, 창고 이동·소모품 출고 |
| ASSET_MANAGER(자산 관리자) | 자산 계약 연결. 창고 관리 장비 입고·이동·지급·반납·폐기는 STOCK_MANAGER도 필요 |

구매 관리자도 창고 업무 권한을 자동으로 갖지 않습니다. 구매 금액·계약 금액·메모·공급업체 연락처는 구매 관리자에 한정하며 재고 담당자의 발주 조회에서는 금액을 제외합니다. 자산 관리자는 계약 코드·공급업체·기간 등의 연결용 정보만 봅니다. 일반 직원은 구매/재고 원장에 접근할 수 없습니다.

기존 사용자에게 신규 역할을 자동 부여하지 않습니다. 신규 합성 데모에는 buyer(구매), stockadmin(재고+자산+조회)을 추가하고 manager에는 데모 연결 흐름을 위해 재고 권한도 부여합니다. 데모의 넓은 역할 구성이 운영 기본 정책은 아닙니다.

## 구매 승인·발주·계약 규칙

구매 요청은 서비스 또는 구매 관리자가 생성하고, 본인 이외의 활성 구매 관리자를 지정 승인자로 선택합니다. 지정 승인자만 승인/반려하며 반려 사유가 필요합니다. PENDING→APPROVED/REJECTED로 결정하고 신청자는 PENDING/APPROVED를 취소할 수 있습니다. 본인의 처리 중인 서비스 요청을 참조할 수 있지만 서비스 요청을 자동 완료하지는 않습니다.

APPROVED 요청에서만 발주 초안을 만들며 수량·통화는 승인 값과 동일하고 단가는 승인 한도 이하여야 합니다. 요청당 취소되지 않은 발주는 1개입니다. 초안 생성 시 구매 요청은 ORDERED로 바뀝니다. 발주를 취소하면 요청을 APPROVED로 되돌려 다시 발주할 수 있습니다. 초안/확정 후 입고가 없는 발주만 취소할 수 있습니다. 입고가 있으면 단순 취소를 거부합니다.

발주 상태: DRAFT→ORDERED→PART_RECEIVED→RECEIVED. 계약은 선택 사항이며 연결했다면 공급업체·통화가 일치해야 합니다. 계약 기간은 한국시간 기준 날짜로 확정 시 검증합니다. 이미 확정한 발주의 실제 입고는 계약 종료 후에도 기록할 수 있습니다.

계약 한도는 ORDERED/PART_RECEIVED/RECEIVED 발주 합계로 사용액을 계산합니다. 초안은 포함하지 않고 입고 전 취소는 한도를 해제합니다. 같은 조직 잠금 아래 합계와 신규 확정을 검사하여 동시 확정으로 한도를 초과하지 않도록 합니다. 자산 계약 연결은 참조 관계이며 금액을 추가 차감하지 않습니다.

금액은 문자열로 입력하고 Decimal/DB numeric으로 계산합니다. 통화는 KRW/USD/EUR이며 KRW는 정수, USD/EUR는 소수 둘째 자리까지입니다. 개별 금액·합계는 99999999999999.99 이하입니다. 통화 변환·세금·할인·청구·지급·감가상각·법정 회계는 없습니다. SQLite는 개발용이며 운영은 PostgreSQL을 사용합니다.

공급업체·계약·창고·품목은 이 버전에서 등록 후 불변입니다. 계약 개정·증액·공급업체 비활성화·기준정보 정정은 후속입니다. 계약 만료 알림은 아직 없으며 발주 확정 시 기간 검사만 수행합니다.

## 수량 품목과 일련번호 장비

StockItem은 BULK(수량 품목) 또는 SERIALIZED(일련번호 장비)로 구분하고 정수 EA 수량만 관리합니다. 한 명령의 수량은 1~1000000개이며 개별 장비 입고·이동은 최대 100개입니다. 단위 변환·예약·실사·수량 조정은 없습니다.

입고는 발주 잔량 이하로만 가능합니다. 발주별 입고 참조번호를 고유하게 보존하여 멱등키가 달라도 같은 참조를 이중 기록할 수 없습니다. 발주 버전·누적 입고량·영수 원장·창고 잔량·수불·감사/outbox를 한 트랜잭션에서 기록합니다.

SERIALIZED 입고는 수량과 같은 수의 {asset_no,serial_number}를 받아 새 Asset과 StockAsset을 생성합니다. 품목의 이름·제조사·모델과 창고 위치를 사용하며 자산은 비공개 STOCK 상태로 시작합니다. 연결 계약이 있으면 자산 계약 관계도 자동 생성합니다. 중복 자산번호/일련번호 등 오류가 있으면 해당 입고 전체를 롤백합니다.

수량 품목 출고는 재고 잔량과 현재 버전을 검사하고 수령자·사용 위치·사유를 기록합니다. 장비는 수량 출고 API로 처리할 수 없고 개별 자산 지급을 사용합니다. 재고가 부족하면 음수로 만들지 않고 거부합니다.

창고 간 이동은 출발 잔량 버전과 도착 잔량 버전을 검사합니다(도착 잔량이 아직 없으면 0). 장비는 개별 자산 ID·버전도 지정해야 합니다. 출발 창고의 보관 자산만 이동하며 잔량·StockAsset 창고·Asset 위치·이력을 함께 변경합니다.

## 기존 자산 지급/반납과의 연결

창고 관리 자산은 입고 출처·품목을 보존하는 StockAsset으로 식별합니다. 기존 수동 등록 자산을 임의로 재고에 더하지 않습니다.

- ISSUE: 현재 창고 잔량 -1, StockAsset 창고를 비움, 기존 Custody/사용자와 이력 생성
- RETURN: 반납 창고 필수, 해당 잔량 +1, StockAsset/Asset 위치를 창고 위치로 설정, Custody 반납 완료
- RETIRE: 보관 창고 잔량 -1, 자산 폐기 상태·StockAsset 창고 비움
- 창고 보관 장비의 MOVE: 기존 자산 위치 이동을 거부하고 재고 이동 기능을 사용
- 사용 중 장비의 사용자 위치 이동: 창고 수량에 영향 없음

위 작업은 자산 관리자와 재고 관리자 권한을 모두 요구합니다. 서비스 요청 연결 지급에는 기존 요청 처리 범위 권한도 필요합니다. 반납·출고의 부분 실패로 수량과 자산 상태가 나뉘지 않도록 기존 자산 명령의 트랜잭션에 재고 변경을 포함합니다.

## API

기존 세션·CSRF·Idempotency-Key·오류·limit/cursor 규약을 따릅니다. 생성/명령은 멱등키가 필요합니다.

| 경로 | 메서드·내용 |
|---|---|
| /api/v1/procurement/suppliers | GET/POST code,name,contact |
| /api/v1/procurement/contracts | GET/POST code,name,supplier_id,starts_on,ends_on,currency,amount,notes |
| /api/v1/procurement/requisitions | GET/POST item_id,quantity,currency,max_unit_price,approver_id,reason,source_request_id(선택) |
| /api/v1/procurement/requisitions/{id} | GET 본인/구매 관리자 범위 |
| /api/v1/procurement/requisitions/{id}/decision | POST decision,reason(반려 필수),expected_version |
| /api/v1/procurement/requisitions/{id}/cancel | POST reason,expected_version |
| /api/v1/procurement/orders | GET/POST requisition_id,supplier_id,contract_id(null 가능),unit_price,expected_version(구매 요청 버전) |
| /api/v1/procurement/orders/{id} | GET 역할별 금액 가림 |
| /api/v1/procurement/orders/{id}/actions | POST action=RELEASE/CANCEL,reason,expected_version |
| /api/v1/procurement/orders/{id}/receipts | GET/POST stockroom_id,reference,quantity,serials[],reason,expected_version(발주 버전) |
| /api/v1/inventory/stockrooms | GET/POST code,name,location |
| /api/v1/inventory/items | GET/POST code,name,tracking,manufacturer,model |
| /api/v1/inventory/balances | GET 역할 범위의 창고 잔량·버전 |
| /api/v1/inventory/movements | GET 수불 원장 |
| /api/v1/inventory/transfer | POST item_id,source_id,target_id,quantity,reason,expected_source_version,expected_target_version,asset_ids[],asset_versions{} |
| /api/v1/inventory/issue | POST item_id,source_id,quantity,reason,expected_source_version,person_id,destination,service_request_id/expected_request_version(선택) |
| /api/v1/procurement/asset-contracts | GET/POST asset_id,contract_id,reason |

수량 품목의 이동도 asset_ids=[]/asset_versions={}를 보냅니다. 자산 RETURN 명령에 stockroom_id를 추가했으며 창고 관리 자산에는 필수입니다. 구매 승인 목록은 /procurement/requisitions에서 관리하며 현재 서비스 승인함·개별 알림 전송과는 별도입니다.

## DB·운영·검증

기준정보·결정·입고·수불·자산 계약 연결은 DB에서 수정/삭제를 차단합니다. 구매 요청/발주의 원 수량·단가·당사자·참조와 StockAsset의 품목/입고 출처도 불변입니다. 조직 경계와 비음수 잔량·초과 입고·활성 발주 고유 제약을 사용합니다. 모든 업무 명령은 기존 조직 단위 잠금으로 직렬화하며 외부 네트워크 호출을 하지 않습니다.

현재 설계는 단일 품목 발주, 정수 수량, 조직 단위 쓰기 직렬화로 시작합니다. 큰 창고·품목 목록의 입력 선택기는 후속 최적화 대상이며 운영 부하 목표를 검증하지 않았습니다. 수불 원장과 잔량의 모든 임의 SQL 변경을 교차 행 제약으로 보장하지는 않습니다.

신규 데모는 buyer, stockadmin, manager로 구매 요청→승인→발주→입고→자산 지급을 확인할 수 있습니다. 기존 설치에는 신규 역할을 자동 부여하지 않습니다. 변경된 역할·구매·재고 데이터가 있는 DB의 역방향 마이그레이션은 복원 계획 없이 수행하지 마십시오. 역/정방향 검증은 disposable DB에 한정합니다.

자동 테스트는 승인·통화/단가·계약 기간/한도·부분/중복/초과 입고·이동·출고·장비 원자성·역할/금액 가림·불변 기록을 포함합니다. PostgreSQL에서는 동시 입고·동시 출고·동시 계약 확정 및 장비 지급/창고 이동 경합을 실제 별도 연결로 검증합니다. Chromium에서는 공급업체/계약 작성부터 양 유형 입고·이동·출고·장비 반납과 계약 잔여액을 확인했습니다.

후속 범위: 복수 품목 발주·분할 발주, 납품 반품/입고 정정, 실사·조정 승인, 계약 개정/만료 알림, 지급/청구·회계·환율·세금·반품 회계, 공급업체 실제 연동입니다.
