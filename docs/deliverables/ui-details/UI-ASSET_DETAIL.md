# UI-ASSET_DETAIL · 자산 상세

진입/사용: /assets/<uuid:id>

소스: `desk/templates/desk/asset-detail.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): asset_views.detail [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-ASSET_DETAIL-F01

UI-ASSET_DETAIL-F01 · asset-update · PUT /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사.

항목: UI-ASSET_DETAIL-E011, UI-ASSET_DETAIL-E012, UI-ASSET_DETAIL-E013, UI-ASSET_DETAIL-E014, UI-ASSET_DETAIL-E015, UI-ASSET_DETAIL-E016, UI-ASSET_DETAIL-E017, UI-ASSET_DETAIL-E018

### UI-ASSET_DETAIL-F02

UI-ASSET_DETAIL-F02 · asset-action · POST(JSON) /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사

항목: UI-ASSET_DETAIL-E019, UI-ASSET_DETAIL-E020, UI-ASSET_DETAIL-E021, UI-ASSET_DETAIL-E022, UI-ASSET_DETAIL-E023, UI-ASSET_DETAIL-E024, UI-ASSET_DETAIL-E025, UI-ASSET_DETAIL-E026

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ASSET_DETAIL-E001 · ← 자산 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /assets | `desk/templates/desk/asset-detail.html:1` |
| UI-ASSET_DETAIL-E002 · 자산번호 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.asset_no }} | `desk/templates/desk/asset-detail.html:3` |
| UI-ASSET_DETAIL-E003 · 모델 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.model\|default:'—' }} | `desk/templates/desk/asset-detail.html:3` |
| UI-ASSET_DETAIL-E004 · 위치 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.location }} | `desk/templates/desk/asset-detail.html:3` |
| UI-ASSET_DETAIL-E005 · 제조사 · 일련번호 | dt / 별도 입력 제약 없음/조회 항목 | if private_details | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.manufacturer\|default:'—' }} / {{ item.serial_number\|default:'—' }} | `desk/templates/desk/asset-detail.html:3` |
| UI-ASSET_DETAIL-E006 · 사용자 | dt / 별도 입력 제약 없음/조회 항목 | if private_details | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.custodian.display_name\|default:'미지급' }} | `desk/templates/desk/asset-detail.html:3` |
| UI-ASSET_DETAIL-E007 · 재고 품목 | dt / 별도 입력 제약 없음/조회 항목 | if stock_record | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ stock_record.item.name }} | `desk/templates/desk/asset-detail.html:5` |
| UI-ASSET_DETAIL-E008 · 현재 보관 창고 | dt / 별도 입력 제약 없음/조회 항목 | if stock_record | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ stock_record.stockroom.name\|default:'창고 외부' }} | `desk/templates/desk/asset-detail.html:5` |
| UI-ASSET_DETAIL-E009 · 관련 서비스 요청 → | a / 별도 입력 제약 없음/조회 항목 | for h in history_items.items / if h.request | 링크 이동: /portal/requests/{{ h.request.id }} | `desk/templates/desk/asset-detail.html:5` |
| UI-ASSET_DETAIL-E010 · 다음 이력 → | a / 별도 입력 제약 없음/조회 항목 | if history_items.next_cursor | 링크 이동: ?cursor={{ history_items.next_cursor\|urlencode }} | `desk/templates/desk/asset-detail.html:5` |
| UI-ASSET_DETAIL-E011 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if item.can_update | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E012 · 자산 이름 | text / name=name; id=edit-name; required; maxlength=200; value={{ item.name }} | if item.can_update | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E013 · 모델 | text / name=model; id=edit-model; maxlength=200; value={{ item.model }} | if item.can_update | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E014 · 제조사 | text / name=manufacturer; id=edit-manufacturer; readonly; maxlength=200; value={{ item.manufacturer }} / readonly는 item.status == 'IN_USE'일 때 적용 | if item.can_update | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E015 · 일련번호 | text / name=serial_number; id=edit-serial; readonly; maxlength=200; value={{ item.serial_number }} / readonly는 item.status == 'IN_USE'일 때 적용 | if item.can_update | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E016 · 수정 사유 | textarea / name=reason; id=edit-reason; required; maxlength=10000 | if item.can_update | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E017 · 기본 자산 정보 공개 | checkbox / name=portal_visible; type=checkbox; checked / checked는 item.portal_visible일 때 적용 | if item.can_update | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E018 · 정보 수정 | submit / 별도 입력 제약 없음/조회 항목 | if item.can_update | 폼 제출: asset-update → /api/v1/assets/{{ item.id }} / /api/v1/assets/{{ item.id }} / 자산 정보 수정; 변경 버전·조직·수정 권한 검사. | `desk/templates/desk/asset-detail.html:6` |
| UI-ASSET_DETAIL-E019 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if item.allowed_actions | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:7` |
| UI-ASSET_DETAIL-E020 · 처리 동작 | select / name=action; id=asset-action; required | if item.allowed_actions / 선택값: =동작 선택; {{ action }}={{ action\|asset_label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:7` |
| UI-ASSET_DETAIL-E021 · 수령자 | select / name=person_id; id=asset-person | if item.allowed_actions / 선택값: =수령자 선택; {{ p.id }}={{ p.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:8` |
| UI-ASSET_DETAIL-E022 · 처리 후 위치 | text / name=location; id=action-location; maxlength=200; value={{ item.location }} | if item.allowed_actions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:9` |
| UI-ASSET_DETAIL-E023 · 서비스 요청 연결 · 선택 | select / name=service_request_id; id=asset-request | if item.allowed_actions / 선택값: =별도 요청 연결 없음; {{ t.id }}={{ t.title }} · {{ t.requested_by.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:10` |
| UI-ASSET_DETAIL-E024 · 반납 창고 | select / name=stockroom_id; id=return-stockroom | if item.allowed_actions / if stock_record / 선택값: =창고 선택; {{ room.id }}={{ room.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:11` |
| UI-ASSET_DETAIL-E025 · 처리 사유 | textarea / name=reason; id=action-reason; required; maxlength=10000 | if item.allowed_actions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:11` |
| UI-ASSET_DETAIL-E026 · 자산 처리 | submit / 별도 입력 제약 없음/조회 항목 | if item.allowed_actions | 폼 제출: asset-action → /api/v1/assets/{{ item.id }}/actions / /api/v1/assets/{{ item.id }}/actions / ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사 | `desk/templates/desk/asset-detail.html:11` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
