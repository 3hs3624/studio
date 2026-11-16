# UI-CONTRACTS · 공급업체 · 계약

진입/사용: /contracts

소스: `desk/templates/desk/contracts.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): purchasing_views.contracts [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-CONTRACTS-F01

UI-CONTRACTS-F01 · supplier · POST(JSON) /api/v1/procurement/suppliers / 공급업체 기준정보 저장; 조직별 식별자/활성 값 검사.

항목: UI-CONTRACTS-E001, UI-CONTRACTS-E002, UI-CONTRACTS-E003, UI-CONTRACTS-E004, UI-CONTRACTS-E005

### UI-CONTRACTS-F02

UI-CONTRACTS-F02 · contract · POST(JSON) /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사.

항목: UI-CONTRACTS-E006, UI-CONTRACTS-E007, UI-CONTRACTS-E008, UI-CONTRACTS-E009, UI-CONTRACTS-E010, UI-CONTRACTS-E011, UI-CONTRACTS-E012, UI-CONTRACTS-E013, UI-CONTRACTS-E014, UI-CONTRACTS-E015

### UI-CONTRACTS-F03

UI-CONTRACTS-F03 · asset-contract · POST(JSON) /api/v1/procurement/asset-contracts / 자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사.

항목: UI-CONTRACTS-E021, UI-CONTRACTS-E022, UI-CONTRACTS-E023, UI-CONTRACTS-E024, UI-CONTRACTS-E025

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CONTRACTS-E001 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_buyer | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/suppliers / 공급업체 기준정보 저장; 조직별 식별자/활성 값 검사. | `desk/templates/desk/contracts.html:2` |
| UI-CONTRACTS-E002 · 공급업체 코드 | text / name=code; id=supplier-code; required; maxlength=80 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/suppliers / 공급업체 기준정보 저장; 조직별 식별자/활성 값 검사. | `desk/templates/desk/contracts.html:2` |
| UI-CONTRACTS-E003 · 공급업체 이름 | text / name=name; id=supplier-name; required; maxlength=200 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/suppliers / 공급업체 기준정보 저장; 조직별 식별자/활성 값 검사. | `desk/templates/desk/contracts.html:2` |
| UI-CONTRACTS-E004 · 업무 연락처 | text / name=contact; id=supplier-contact; maxlength=200 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/suppliers / 공급업체 기준정보 저장; 조직별 식별자/활성 값 검사. | `desk/templates/desk/contracts.html:2` |
| UI-CONTRACTS-E005 · 공급업체 등록 | submit / 별도 입력 제약 없음/조회 항목 | if is_buyer | 폼 제출: supplier → /api/v1/procurement/suppliers / /api/v1/procurement/suppliers / 공급업체 기준정보 저장; 조직별 식별자/활성 값 검사. | `desk/templates/desk/contracts.html:2` |
| UI-CONTRACTS-E006 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_buyer | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E007 · 계약 코드 | text / name=code; id=contract-code; required; maxlength=80 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E008 · 계약 이름 | text / name=name; id=contract-name; required; maxlength=200 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E009 · 계약 공급업체 | select / name=supplier_id; id=contract-supplier; required | if is_buyer / 선택값: =공급업체 선택; {{ v.id }}={{ v.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E010 · 시작일 | date / name=starts_on; id=contract-start; type=date; required | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E011 · 종료일 | date / name=ends_on; id=contract-end; type=date; required | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E012 · 계약 통화 | select / name=currency; id=contract-currency | if is_buyer / 선택값: KRW=KRW; USD=USD; EUR=EUR | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E013 · 계약 금액 한도 | number / name=amount; id=contract-amount; type=number; required; min=0.01; step=0.01 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E014 · 계약 메모 | textarea / name=notes; id=contract-notes; maxlength=10000 | if is_buyer | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E015 · 계약 등록 | submit / 별도 입력 제약 없음/조회 항목 | if is_buyer | 폼 제출: contract → /api/v1/procurement/contracts / /api/v1/procurement/contracts / 계약 기준정보·공급업체·기간 저장; 참조 범위 검사. | `desk/templates/desk/contracts.html:3` |
| UI-CONTRACTS-E016 · 계약 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/contracts.html:4` |
| UI-CONTRACTS-E017 · 공급업체 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/contracts.html:4` |
| UI-CONTRACTS-E018 · 유효기간 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/contracts.html:4` |
| UI-CONTRACTS-E019 · 한도 / 확정 발주 / 잔여 | th / 별도 입력 제약 없음/조회 항목 | if is_buyer | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/contracts.html:4` |
| UI-CONTRACTS-E020 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/contracts.html:4` |
| UI-CONTRACTS-E021 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if is_asset_manager | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/procurement/asset-contracts / 자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사. | `desk/templates/desk/contracts.html:5` |
| UI-CONTRACTS-E022 · 자산 | select / name=asset_id; id=contract-asset; required | if is_asset_manager / 선택값: =자산 선택; {{ a.id }}={{ a.asset_no }} · {{ a.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/asset-contracts / 자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사. | `desk/templates/desk/contracts.html:5` |
| UI-CONTRACTS-E023 · 연결 계약 | select / name=contract_id; id=link-contract; required | if is_asset_manager / 선택값: =계약 선택; {{ c.id }}={{ c.code }} · {{ c.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/asset-contracts / 자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사. | `desk/templates/desk/contracts.html:5` |
| UI-CONTRACTS-E024 · 연결 사유 | textarea / name=reason; id=contract-link-reason; required; maxlength=10000 | if is_asset_manager | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/procurement/asset-contracts / 자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사. | `desk/templates/desk/contracts.html:5` |
| UI-CONTRACTS-E025 · 자산 계약 연결 | submit / 별도 입력 제약 없음/조회 항목 | if is_asset_manager | 폼 제출: asset-contract → /api/v1/procurement/asset-contracts / /api/v1/procurement/asset-contracts / 자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사. | `desk/templates/desk/contracts.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
