# UI-ENTITIES · 엔티티 관리

진입/사용: /admin/entities, /admin/entities/<uuid:id>, /console/entities, /console/entities/<uuid:id>

소스: `desk/templates/desk/entities.html`

연결: `desk/configuration-impact.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.entity_management [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-ENTITIES-F01

UI-ENTITIES-F01 · entity-save · POST(JSON) /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정

항목: UI-ENTITIES-E014, UI-ENTITIES-E015, UI-ENTITIES-E016, UI-ENTITIES-E017, UI-ENTITIES-E018, UI-ENTITIES-E019, UI-ENTITIES-E020, UI-ENTITIES-E021, UI-ENTITIES-E022, UI-ENTITIES-E023, UI-ENTITIES-E024, UI-ENTITIES-E025, UI-ENTITIES-E026, UI-ENTITIES-E027, UI-ENTITIES-E028, UI-ENTITIES-E029, UI-ENTITIES-E030, UI-ENTITIES-E031, UI-ENTITIES-E032

### UI-ENTITIES-F02

UI-ENTITIES-F02 · entity-publish · POST(JSON) /api/v1/admin/entities/{{ entity.id }}/publish / 게시 스키마 불변; 기존 레코드 참조 버전 보존; 물리 테이블 DDL 아님

항목: UI-ENTITIES-E050, UI-ENTITIES-E051, UI-ENTITIES-E052

### UI-ENTITIES-F03

UI-ENTITIES-F03 · entity-record · POST(JSON) /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장.

항목: UI-ENTITIES-E057, UI-ENTITIES-E058, UI-ENTITIES-E059, UI-ENTITIES-E060, UI-ENTITIES-E061, UI-ENTITIES-E062, UI-ENTITIES-E063

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ENTITIES-E001 · 새 엔티티 | a / 별도 입력 제약 없음/조회 항목 | if can_entity_write | 링크 이동: {{ entity_base }}?new=1 | `desk/templates/desk/entities.html:4` |
| UI-ENTITIES-E002 · 코드 | th / 별도 입력 제약 없음/조회 항목 | if not show_editor | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:7` |
| UI-ENTITIES-E003 · 이름 | th / 별도 입력 제약 없음/조회 항목 | if not show_editor | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:7` |
| UI-ENTITIES-E004 · 업무 필드 수 | th / 별도 입력 제약 없음/조회 항목 | if not show_editor | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:7` |
| UI-ENTITIES-E005 · 구성 버전 | th / 별도 입력 제약 없음/조회 항목 | if not show_editor | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:7` |
| UI-ENTITIES-E006 · 시스템 필드 | th / 별도 입력 제약 없음/조회 항목 | if not show_editor | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:7` |
| UI-ENTITIES-E007 · {{ item.code }} | a / 별도 입력 제약 없음/조회 항목 | if not show_editor / for item in entity_list | 링크 이동: {{ entity_base }}/{{ item.id }} | `desk/templates/desk/entities.html:8` |
| UI-ENTITIES-E008 · ← 엔티티 목록 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 링크 이동: {{ entity_base }} | `desk/templates/desk/entities.html:9` |
| UI-ENTITIES-E009 · 시스템 필드 · 자동 제공 8개 (읽기 전용) | summary / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/entities.html:10` |
| UI-ENTITIES-E010 · 필드 코드 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:11` |
| UI-ENTITIES-E011 · 이름 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:11` |
| UI-ENTITIES-E012 · 유형 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:11` |
| UI-ENTITIES-E013 · 관리 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:11` |
| UI-ENTITIES-E014 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:14` |
| UI-ENTITIES-E015 · 엔티티 코드 | text / name=code; required; readonly; maxlength=40; pattern=[A-Za-z][A-Za-z0-9_]{0,39}; value={{ entity.code }} / readonly는 entity일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:15` |
| UI-ENTITIES-E016 · 이름 | text / name=name; required; maxlength=200; value={{ entity.name }} | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:15` |
| UI-ENTITIES-E017 · 필드 코드 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E018 · 표시 이름 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E019 · 유형 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E020 · 필수 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E021 · 길이 · 정밀도 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E022 · 선택지 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E023 · 참조 대상 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E024 · 관계 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E025 · 순서 · 제거 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:17` |
| UI-ENTITIES-E026 · 필드 추가 | button / id=add-entity-field; type=button | else (앞 분기 제외) / if entity | 클라이언트 조작: 필드 추가 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:18` |
| UI-ENTITIES-E027 · 중간 엔티티 설정 | summary / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:19` |
| UI-ENTITIES-E028 · 중간 엔티티로 사용 | checkbox / name=junction_enabled; type=checkbox; checked / checked는 entity.draft_junction일 때 적용 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:20` |
| UI-ENTITIES-E029 · 왼쪽 참조 필드 코드 | text / name=junction_left; maxlength=40; value={{ entity.draft_junction.left_field }} | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:20` |
| UI-ENTITIES-E030 · 오른쪽 참조 필드 코드 | text / name=junction_right; maxlength=40; value={{ entity.draft_junction.right_field }} | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:20` |
| UI-ENTITIES-E031 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:22` |
| UI-ENTITIES-E032 · 초안 저장 | submit / type=submit | else (앞 분기 제외) | 폼 제출: entity-save → /api/v1/admin/entities / /api/v1/admin/entities / 고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정 | `desk/templates/desk/entities.html:22` |
| UI-ENTITIES-E033 · 필드 코드 | text / data-field=key; required; maxlength=40; pattern=[a-z][a-z0-9_]{0,39}; aria-label=필드 코드 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:25` |
| UI-ENTITIES-E034 · 표시 이름 | text / data-field=label; required; maxlength=100; aria-label=표시 이름 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:26` |
| UI-ENTITIES-E035 · 필드 유형 | select / data-field=type; aria-label=필드 유형 | else (앞 분기 제외) / if entity / 선택값: {{ type.key }}={{ type.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:27` |
| UI-ENTITIES-E036 · 필수 입력 | checkbox / data-field=required; type=checkbox; aria-label=필수 입력 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E037 · 문자 길이 | number / data-field=max_length; type=number; min=1; max=65535 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E038 · 전체 자릿수 | number / data-field=precision; type=number; min=1; max=38 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E039 · 소수 자릿수 | number / data-field=scale; type=number; min=0; max=18 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E040 · 설명 | text / data-field=description; maxlength=500 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E041 · 기본값 · JSON | text / data-field=default; placeholder=예: "값", 0, false | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E042 · 자동 기본값 | select / data-field=default_function | else (앞 분기 제외) / if entity / 선택값: =없음; CURRENT_TIMESTAMP=현재 일시; CURRENT_DATE=현재 날짜; UUID=UUID 생성 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:28` |
| UI-ENTITIES-E043 · 공통코드 그룹 | select / data-field=code_group_id; aria-label=공통코드 그룹 | else (앞 분기 제외) / if entity / 선택값: =직접 선택지 입력; {{ group.id }}={{ group.code }} · {{ group.name }} (중지) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:29` |
| UI-ENTITIES-E044 · 선택지 · 쉼표 구분 | text / data-field=options; aria-label=선택지 · 쉼표 구분 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:29` |
| UI-ENTITIES-E045 · 참조 대상 | select / data-field=target_entity_id; aria-label=참조 대상 | else (앞 분기 제외) / if entity / 선택값: =대상 선택; {{ target.id }}={{ target.code }} · {{ target.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:30` |
| UI-ENTITIES-E046 · 연결 관계 | select / data-field=relationship; aria-label=연결 관계 | else (앞 분기 제외) / if entity / 선택값: {{ relation.key }}={{ relation.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/entities.html:31` |
| UI-ENTITIES-E047 · 위로 이동 | button / type=button; aria-label=위로 이동 | else (앞 분기 제외) / if entity | 클라이언트 조작: 위로 이동 | `desk/templates/desk/entities.html:32` |
| UI-ENTITIES-E048 · 아래로 이동 | button / type=button; aria-label=아래로 이동 | else (앞 분기 제외) / if entity | 클라이언트 조작: 아래로 이동 | `desk/templates/desk/entities.html:32` |
| UI-ENTITIES-E049 · 제거 | button / type=button | else (앞 분기 제외) / if entity | 클라이언트 조작: 제거 | `desk/templates/desk/entities.html:32` |
| UI-ENTITIES-E050 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities/{{ entity.id }}/publish / 게시 스키마 불변; 기존 레코드 참조 버전 보존; 물리 테이블 DDL 아님 | `desk/templates/desk/entities.html:35` |
| UI-ENTITIES-E051 · 게시 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if entity | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities/{{ entity.id }}/publish / 게시 스키마 불변; 기존 레코드 참조 버전 보존; 물리 테이블 DDL 아님 | `desk/templates/desk/entities.html:35` |
| UI-ENTITIES-E052 · 저장된 초안 게시 | submit / type=submit | else (앞 분기 제외) / if entity | 폼 제출: entity-publish → /api/v1/admin/entities/{{ entity.id }}/publish / /api/v1/admin/entities/{{ entity.id }}/publish / 게시 스키마 불변; 기존 레코드 참조 버전 보존; 물리 테이블 DDL 아님 | `desk/templates/desk/entities.html:35` |
| UI-ENTITIES-E053 · 버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:36` |
| UI-ENTITIES-E054 · 이름 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:36` |
| UI-ENTITIES-E055 · 게시 사유 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:36` |
| UI-ENTITIES-E056 · 게시 시각 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:36` |
| UI-ENTITIES-E057 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:39` |
| UI-ENTITIES-E058 · {{ field.label }} * | select / data-key={{ field.key }}; data-entity-value; required / required는 field.required일 때 적용 | else (앞 분기 제외) / if entity / if schema / for field in schema_fields / if field.type == 'choice' or field.type == 'code' / 선택값: =선택; {{ value.value }}={{ value.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:41` |
| UI-ENTITIES-E059 · {{ field.label }} * | select / data-key={{ field.key }}; data-entity-value; required / required는 field.required일 때 적용 | else (앞 분기 제외) / if entity / if schema / for field in schema_fields / elif field.type == 'boolean' (앞 분기 제외) / 선택값: =선택; true=예; false=아니오 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:42` |
| UI-ENTITIES-E060 · {{ field.label }} * | select / data-key={{ field.key }}; data-entity-value; required; multiple / required는 field.multiple %}multiple size="4"{% endif %} {% if field.required일 때 적용 | else (앞 분기 제외) / if entity / if schema / for field in schema_fields / elif field.type == 'reference' (앞 분기 제외) / 선택값: =대상 선택; {{ record.id }}={{ record.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:43` |
| UI-ENTITIES-E061 · {{ field.label }} * | textarea / data-key={{ field.key }}; data-entity-value; required; maxlength={{ field.max_length\|default:4000 }} / required는 field.required일 때 적용 | else (앞 분기 제외) / if entity / if schema / for field in schema_fields / elif field.type == 'textarea' or field.type == 'json' or field.type == 'entityset' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:44` |
| UI-ENTITIES-E062 · {{ field.label }} * |  number {{ field.type }} text  / data-key={{ field.key }}; data-entity-value; type= number {{ field.type }} text ; required; maxlength={{ field.max_length\|default:4000 }}; min=-9007199254740991; max=9007199254740991; step=1; value={{ field.initial_value }} / required는 field.type == 'integer' or field.type == 'number' %}number{% elif field.type == 'date' or field.type == 'time' or field.type == 'month' or field.type == 'email' or field.type == 'url' %}{{ field.type }}{% else %}text{% endif %}" {% if field.type == 'integer' %}step="1" min="-9007199254740991" max="9007199254740991"{% endif %} maxlength="{{ field.max_length\|default:4000 }}" {% if field.required일 때 적용 | else (앞 분기 제외) / if entity / if schema / for field in schema_fields / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:45` |
| UI-ENTITIES-E063 · 데이터 등록 | submit / type=submit | else (앞 분기 제외) / if entity / if schema | 폼 제출: entity-record → /api/v1/admin/entities/{{ entity.id }}/records / /api/v1/admin/entities/{{ entity.id }}/records / 게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장. | `desk/templates/desk/entities.html:46` |
| UI-ENTITIES-E064 · 식별자 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:47` |
| UI-ENTITIES-E065 · 정의 버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:47` |
| UI-ENTITIES-E066 · 값 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:47` |
| UI-ENTITIES-E067 · 생성자 · 수정자 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:47` |
| UI-ENTITIES-E068 · 데이터 버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:47` |
| UI-ENTITIES-E069 · 연결 관계 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/entities.html:47` |
| UI-ENTITIES-E070 · 연결 보기 | summary / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if entity / if schema / for record in records | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/entities.html:47` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
