# UI-CATALOG_MANAGE · 카탈로그 관리

진입/사용: /console/catalog, /work/catalog

소스: `desk/templates/desk/catalog-manage.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): views.catalog_manage [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-CATALOG_MANAGE-F01

UI-CATALOG_MANAGE-F01 · catalog-publish · POST(JSON) /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시.

항목: UI-CATALOG_MANAGE-E001, UI-CATALOG_MANAGE-E002, UI-CATALOG_MANAGE-E003, UI-CATALOG_MANAGE-E004, UI-CATALOG_MANAGE-E005, UI-CATALOG_MANAGE-E006, UI-CATALOG_MANAGE-E007, UI-CATALOG_MANAGE-E008, UI-CATALOG_MANAGE-E009, UI-CATALOG_MANAGE-E010, UI-CATALOG_MANAGE-E011, UI-CATALOG_MANAGE-E012, UI-CATALOG_MANAGE-E013, UI-CATALOG_MANAGE-E014

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CATALOG_MANAGE-E001 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:4` |
| UI-CATALOG_MANAGE-E002 · 서비스 코드 | text / name=code; id=catalog-code; required; maxlength=40; pattern=[A-Za-z][A-Za-z0-9_-]{0,39}; placeholder=LAPTOP_REQUEST | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:5` |
| UI-CATALOG_MANAGE-E003 · expected_version | hidden / name=expected_version; type=hidden; value=0 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:5` |
| UI-CATALOG_MANAGE-E004 · 서비스 이름 | text / name=name; id=catalog-name; required; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:5` |
| UI-CATALOG_MANAGE-E005 · 적용 워크플로우 | select / name=workflow_version_id | 해당 화면/공통 영역 표시 시 / 선택값: =메뉴 기본값 · {{ workflow_binding.version.definition.name }} v{{ workflow_binding.version.version }} 기존 고정 처리 방식; {{ version.id }}={{ version.definition.name }} · v{{ version.version }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:6` |
| UI-CATALOG_MANAGE-E006 · 서비스 설명 | textarea / name=description; id=catalog-description; required; maxlength=10000 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:6` |
| UI-CATALOG_MANAGE-E007 · 처리 그룹 | select / name=fulfillment_group_id; id=fulfillment-group; required | 해당 화면/공통 영역 표시 시 / 선택값: =그룹 선택; {{ group.id }}={{ group.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:7` |
| UI-CATALOG_MANAGE-E008 · 지정 승인자 | select / name=approver_id; id=approver | 해당 화면/공통 영역 표시 시 / 선택값: =승인자 선택; {{ person.id }}={{ person.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:7` |
| UI-CATALOG_MANAGE-E009 · 승인 필요 | checkbox / name=approval_required; type=checkbox; checked | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:8` |
| UI-CATALOG_MANAGE-E010 · 조직 전체 공개 | checkbox / name=public_to_org; type=checkbox; checked | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:8` |
| UI-CATALOG_MANAGE-E011 · 신규 신청 허용 | checkbox / name=available; type=checkbox; checked | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:8` |
| UI-CATALOG_MANAGE-E012 · 특정 그룹 공개 | select / name=audience_group_ids; id=catalog-audiences; multiple | 해당 화면/공통 영역 표시 시 / 선택값: {{ group.id }}={{ group.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:9` |
| UI-CATALOG_MANAGE-E013 · + 항목 추가 | button / id=add-catalog-field; type=button | 해당 화면/공통 영역 표시 시 | 클라이언트 조작: + 항목 추가 / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:10` |
| UI-CATALOG_MANAGE-E014 · 카탈로그 게시 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: catalog-publish → /api/v1/catalog/versions / /api/v1/catalog/versions / 서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시. | `desk/templates/desk/catalog-manage.html:11` |
| UI-CATALOG_MANAGE-E015 · 항목 식별자 | text / data-field=key; required; maxlength=40; pattern=[a-z][a-z0-9_]{0,39} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/catalog-manage.html:12` |
| UI-CATALOG_MANAGE-E016 · 항목 이름 | text / data-field=label; required; maxlength=100 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/catalog-manage.html:12` |
| UI-CATALOG_MANAGE-E017 · 입력 종류 | select / data-field=type | 해당 화면/공통 영역 표시 시 / 선택값: text=짧은 글; textarea=긴 글; integer=정수; choice=선택; date=날짜; boolean=예 · 아니오 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/catalog-manage.html:12` |
| UI-CATALOG_MANAGE-E018 · 선택지 · 쉼표로 구분 | text / data-field=options; placeholder=노트북, 데스크톱 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/catalog-manage.html:12` |
| UI-CATALOG_MANAGE-E019 · 필수 항목 | checkbox / data-field=required; type=checkbox; checked | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/catalog-manage.html:12` |
| UI-CATALOG_MANAGE-E020 · 항목 제거 | button / type=button | 해당 화면/공통 영역 표시 시 | 클라이언트 조작: 항목 제거 | `desk/templates/desk/catalog-manage.html:12` |
| UI-CATALOG_MANAGE-E021 · 서비스 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/catalog-manage.html:13` |
| UI-CATALOG_MANAGE-E022 · 버전 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/catalog-manage.html:13` |
| UI-CATALOG_MANAGE-E023 · 신청 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/catalog-manage.html:13` |
| UI-CATALOG_MANAGE-E024 · 승인 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/catalog-manage.html:13` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
