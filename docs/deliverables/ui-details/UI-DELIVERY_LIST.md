# UI-DELIVERY_LIST · {{ delivery_title }}

진입/사용: /resources/changes, /resources/changes/<uuid:id>, /resources/deployments, /resources/deployments/<uuid:id>

소스: `desk/templates/desk/delivery-list.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): delivery_views.listing [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-DELIVERY_LIST-F01

UI-DELIVERY_LIST-F01 · 폼 · get 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-DELIVERY_LIST-E013, UI-DELIVERY_LIST-E014, UI-DELIVERY_LIST-E015, UI-DELIVERY_LIST-E016

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-DELIVERY_LIST-E001 · IT자원 현황 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /systems/resource | `desk/templates/desk/delivery-list.html:1` |
| UI-DELIVERY_LIST-E002 · 제공자 · 원문 식별자 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.provider }} · {{ delivery_item.external_id }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E003 · 상태 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.status_label }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E004 · 저장소 · 브랜치 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item / if delivery_kind == 'SOURCE' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.repository }} · {{ delivery_item.branch }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E005 · 커밋 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item / if delivery_kind == 'SOURCE' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.revision\|default:'—' }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E006 · 빌드 결과 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item / if delivery_kind == 'SOURCE' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.build_label }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E007 · 서비스 · 버전 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.service }} · {{ delivery_item.version }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E008 · 대상 환경 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.environment }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E009 · 외부 계정 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.external_actor\|default:'—' }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E010 · 발생 시각 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.occurred_at }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E011 · 수신 시각 | dt / 별도 입력 제약 없음/조회 항목 | if delivery_item | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ delivery_item.received_at }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E012 · 원문에서 확인 ↗ | a / 별도 입력 제약 없음/조회 항목 | if delivery_item | 링크 이동: {{ delivery_item.external_url }} | `desk/templates/desk/delivery-list.html:2` |
| UI-DELIVERY_LIST-E013 · 제목·저장소·서비스 검색 | text / name=q; maxlength=150; value={{ q }} | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E014 · 상태 | select / name=status | else (앞 분기 제외) / 선택값: =전체; {{ value }}={{ label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E015 · build_status | hidden / name=build_status; type=hidden; value={{ selected_build }} | else (앞 분기 제외) / if selected_build | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E016 · 조회 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 폼 제출: submit → 현재 URL 조회 조건 / 현재 URL 조회 조건 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E017 · 제목 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E018 · 저장소 · 브랜치 서비스 · 버전 · 환경 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E019 · 상태 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E020 · 외부 계정 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E021 · 발생 시각 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E022 · {{ item.title }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for item in delivery_records | 링크 이동: {{ item.detail_url }} | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E023 · 이전 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if delivery_page.has_previous | 링크 이동: ?{{ delivery_filters }}&page={{ delivery_page.previous_page_number }} | `desk/templates/desk/delivery-list.html:3` |
| UI-DELIVERY_LIST-E024 · 다음 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if delivery_page.has_next | 링크 이동: ?{{ delivery_filters }}&page={{ delivery_page.next_page_number }} | `desk/templates/desk/delivery-list.html:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
