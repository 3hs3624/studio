# UI-CATALOG_DETAIL · 서비스 신청

진입/사용: /catalog/items/<uuid:id>

소스: `desk/templates/desk/catalog-detail.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.catalog_detail [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-CATALOG_DETAIL-F01

UI-CATALOG_DETAIL-F01 · request-create · POST(JSON) /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성.

항목: UI-CATALOG_DETAIL-E002, UI-CATALOG_DETAIL-E003, UI-CATALOG_DETAIL-E004, UI-CATALOG_DETAIL-E005, UI-CATALOG_DETAIL-E006, UI-CATALOG_DETAIL-E007, UI-CATALOG_DETAIL-E008

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CATALOG_DETAIL-E001 · ← 서비스 카탈로그 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /catalog | `desk/templates/desk/catalog-detail.html:1` |
| UI-CATALOG_DETAIL-E002 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:3` |
| UI-CATALOG_DETAIL-E003 · {{ f.label }} * | textarea / id=field-{{ f.key }}; required; maxlength=4000 / required는 f.required일 때 적용 | for f in form_fields / if f.type == 'textarea' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:5` |
| UI-CATALOG_DETAIL-E004 · {{ f.label }} * | select / id=field-{{ f.key }}; required / required는 f.required일 때 적용 | for f in form_fields / elif f.type == 'choice' (앞 분기 제외) / 선택값: =선택하십시오.; {{ choice }}={{ choice }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:6` |
| UI-CATALOG_DETAIL-E005 · {{ f.label }} * | select / id=field-{{ f.key }}; required / required는 f.required일 때 적용 | for f in form_fields / elif f.type == 'boolean' (앞 분기 제외) / 선택값: =선택하십시오.; true=예; false=아니오 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:7` |
| UI-CATALOG_DETAIL-E006 · {{ f.label }} * |  number date text  / id=field-{{ f.key }}; type= number date text ; required; maxlength=2000; min=-1000000000; max=1000000000; step=1; value={{ f.value }} / required는 f.type == 'integer' %}number{% elif f.type == 'date' %}date{% else %}text{% endif %}" value="{{ f.value }}" {% if f.type == 'integer' %}min="-1000000000" max="1000000000" step="1"{% endif %} maxlength="2000" {% if f.required일 때 적용 | for f in form_fields / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:8` |
| UI-CATALOG_DETAIL-E007 · 취소 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /catalog / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:9` |
| UI-CATALOG_DETAIL-E008 · 서비스 신청 → | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: request-create → /api/v1/requests / /api/v1/requests / 카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성. | `desk/templates/desk/catalog-detail.html:9` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
