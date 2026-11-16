# 화면·기능 개별 상세 정의

기준: 2026-11-16, main `55affa25b682ab2b758b0c4bf5c935b9f237d575`. 화면/공통 컴포넌트/동적 편집기 65개, 개별 항목 1200개.

버튼·입력·조회 열·상태 출력·공통 상호작용을 소스 기준으로 개별 정의했습니다. 반복 행은 스키마 단위로 정의하며 사용자/업무 데이터의 각 인스턴스를 중복 문서화하지 않습니다. 조건부 항목은 실제 조건이 성립할 때만 표시됩니다. HTML 필수/선택 속성과 서버 검증을 구분합니다. 미구현 사이드바 기능 3개는 제공 기능에 포함하지 않습니다.

Google 문서와 항목 ID를 공통으로 사용합니다. 원본 `{{ }}`는 서버가 채우는 값이며 실제 개인정보가 아닙니다. 정적 소스 대조 결과이며 모든 브라우저·권한 조합의 새 실행 검수를 뜻하지 않습니다.

## 공통 규칙

- API 폼: JSON 직렬화, CSRF, Idempotency-Key, expected_version(해당 폼에 선언된 경우). 실패는 폼 오류에 표시하고 버튼을 복원합니다. VERSION_CONFLICT는 입력 보존 후 새로고침을 안내합니다.
- GET 검색은 저장 동작이 아닙니다. 일반 POST 인증 폼은 Django 인증·CSRF 규칙을 따릅니다.
- 화면 노출 조건은 서버 권한의 대체물이 아닙니다. 실제 API는 조직·업무·행·필드/그룹 권한을 별도 검사합니다.
- 동적 항목의 유형별 표시/숨김은 [동적 상세](UI-JS_PROCESS.md), 엔티티/디자이너 메타데이터는 해당 화면 정의를 따릅니다.
- 좁은 화면 사이드바는 680px 이하에서 토글되며 Escape/배경 클릭/메뉴 선택/너비 이탈 시 닫힙니다. 데스크톱 접기·폭 조절·설정 저장은 미구현입니다.

## 화면·컴포넌트 색인

| 화면 ID | 이름 | 개별 항목 | 진입/사용 |
|---|---|---:|---|
| [UI-ACCESS_DEPARTMENTS](UI-ACCESS_DEPARTMENTS.md) | 부서 선택 목록 | 1 | /console/access |
| [UI-ACCESS_PEOPLE](UI-ACCESS_PEOPLE.md) | 사용자·그룹 선택 목록 | 1 | /console/access |
| [UI-ACCESS](UI-ACCESS.md) | 조직 · 권한 관리 | 30 | /admin/access |
| [UI-ACCOUNT_SECURITY](UI-ACCOUNT_SECURITY.md) | 내 계정 보안 | 22 | /account/security |
| [UI-ACTIVATE_ACCOUNT](UI-ACTIVATE_ACCOUNT.md) | 초대 계정 비밀번호 설정 | 5 | /activate/<str:uid>/ |
| [UI-ASSET_DETAIL](UI-ASSET_DETAIL.md) | 자산 상세 | 26 | /assets/<uuid:id> |
| [UI-ASSET_LIST](UI-ASSET_LIST.md) | IT 자산 | 11 | /assets |
| [UI-ASSET_NEW](UI-ASSET_NEW.md) | 자산 등록 | 11 | /assets/new |
| [UI-BASE](UI-BASE.md) | 공통 셸·상단·사이드바·내 정보 | 20 | /, /account/security, /activate/<str:uid>/, /approvals, /assets, /assets/<uuid:id>, /assets/new, /catalog, /catalog/items/<uuid:id>, /cis, /cis/<uuid:id>, /contracts, /inventory, /inventory/movements, /login/mfa/, /my-assets, /notifications, /portal/incidents, /portal/incidents/<uuid:id>, /portal/incidents/new, /portal/requests, /portal/requests/<uuid:id>, /processes, /processes/<uuid:id>, /procurement/orders, /procurement/orders/<uuid:id>, /procurement/requisitions, /procurement/requisitions/<uuid:id>, /resources/changes, /resources/changes/<uuid:id>, /resources/deployments, /resources/deployments/<uuid:id>, /systems/asset, /systems/resource, /systems/service, /work/incidents, /work/incidents/<uuid:id>, /work/requests |
| [UI-CATALOG_DETAIL](UI-CATALOG_DETAIL.md) | 서비스 신청 | 8 | /catalog/items/<uuid:id> |
| [UI-CATALOG_MANAGE](UI-CATALOG_MANAGE.md) | 카탈로그 관리 | 24 | /console/catalog, /work/catalog |
| [UI-CATALOG](UI-CATALOG.md) | 필요한 서비스를 신청하십시오. | 4 | /catalog |
| [UI-CODES](UI-CODES.md) | 공통코드 관리 | 41 | /console/codes, /console/codes/<uuid:id> |
| [UI-CONFIGURATION_IMPACT](UI-CONFIGURATION_IMPACT.md) | 초안 변경 영향도 | 5 | /admin/entities, /admin/entities/<uuid:id>, /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/entities, /console/entities/<uuid:id>, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new |
| [UI-CONSOLE_BASE](UI-CONSOLE_BASE.md) | 운영 콘솔 공통 셸 | 4 | /console |
| [UI-CONSOLE_HOME](UI-CONSOLE_HOME.md) | 운영 콘솔 | 1 | /console |
| [UI-CONSOLE_TABS](UI-CONSOLE_TABS.md) | 공통 상세 탭 | 1 | /admin/access, /admin/plugins, /console/access, /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/plugins, /console/plugins/<str:plugin_id>, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/security, /console/security/<str:category>, /console/users, /console/users/<str:id>, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new |
| [UI-CONTRACTS](UI-CONTRACTS.md) | 공급업체 · 계약 | 25 | /contracts |
| [UI-DASHBOARD_TASKS](UI-DASHBOARD_TASKS.md) | 내가 할 일 공통 영역 | 6 | /, /systems/asset, /systems/resource, /systems/service |
| [UI-DELIVERY_HOME](UI-DELIVERY_HOME.md) | IT자원 업무 홈 | 0 | /systems/asset, /systems/resource, /systems/service |
| [UI-DELIVERY_LIST](UI-DELIVERY_LIST.md) | {{ delivery_title }} | 24 | /resources/changes, /resources/changes/<uuid:id>, /resources/deployments, /resources/deployments/<uuid:id> |
| [UI-DELIVERY_OVERVIEW](UI-DELIVERY_OVERVIEW.md) | IT자원 요약 현황 | 17 | /, /systems/asset, /systems/resource, /systems/service |
| [UI-DETAIL](UI-DETAIL.md) | 장애 상세 | 23 | /portal/incidents/<uuid:id>, /work/incidents/<uuid:id> |
| [UI-ENTITIES](UI-ENTITIES.md) | 엔티티 관리 | 70 | /admin/entities, /admin/entities/<uuid:id>, /console/entities, /console/entities/<uuid:id> |
| [UI-GROUPS](UI-GROUPS.md) | 그룹 관리 | 18 | /console/groups, /console/groups/<str:id> |
| [UI-INTEGRATIONS](UI-INTEGRATIONS.md) | API · 데이터 연계 관리 | 73 | /console/integrations, /console/integrations/<uuid:id> |
| [UI-INVENTORY](UI-INVENTORY.md) | 창고 · 재고 | 33 | /inventory |
| [UI-LIST](UI-LIST.md) | 장애 목록 | 11 | /portal/incidents, /work/incidents |
| [UI-MFA_LOGIN](UI-MFA_LOGIN.md) | 추가 인증 | 3 | /login/mfa/ |
| [UI-MY_ASSETS](UI-MY_ASSETS.md) | 내 지급 자산 | 7 | /my-assets |
| [UI-NEW](UI-NEW.md) | 장애 등록 | 9 | /portal/incidents/new |
| [UI-NOTIFICATIONS](UI-NOTIFICATIONS.md) | 알림함 | 4 | /notifications |
| [UI-ORGANIZATION_ACCESS](UI-ORGANIZATION_ACCESS.md) | 조직 · 권한 관리 | 38 | /console/access |
| [UI-PLUGINS](UI-PLUGINS.md) | 플러그인 목록/상세 | 45 | /admin/plugins, /console/plugins, /console/plugins/<str:plugin_id> |
| [UI-PORTAL](UI-PORTAL.md) | 통합 포털 | 8 | / |
| [UI-PROCESS_CREATE](UI-PROCESS_CREATE.md) | 화면/워크플로우/결재선 생성 | 9 | /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new |
| [UI-PROCESS_FIELD](UI-PROCESS_FIELD.md) | 태스크 동적 입력 필드 | 3 | 공통/동적 컴포넌트: UI-PROCESS_FIELDS |
| [UI-PROCESS_FIELDS](UI-PROCESS_FIELDS.md) | 프로세스 항목표 | 1 | /processes, /processes/<uuid:id> |
| [UI-PROCESS_INBOX](UI-PROCESS_INBOX.md) | 워크플로우 업무·결재 목록/상세 | 38 | /processes, /processes/<uuid:id> |
| [UI-PROCESS_LIST](UI-PROCESS_LIST.md) | 화면/워크플로우/결재선 목록 | 16 | /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new |
| [UI-PROCESS_MANAGE](UI-PROCESS_MANAGE.md) | 화면/워크플로우/결재선 상세 | 48 | /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new |
| [UI-PURCHASE_ORDER_DETAIL](UI-PURCHASE_ORDER_DETAIL.md) | 발주 상세 | 15 | /procurement/orders, /procurement/orders/<uuid:id> |
| [UI-PURCHASE_ORDERS](UI-PURCHASE_ORDERS.md) | 발주 · 입고 | 8 | /procurement/orders |
| [UI-PURCHASE_REQUEST_DETAIL](UI-PURCHASE_REQUEST_DETAIL.md) | 구매요청 상세 | 17 | /procurement/requisitions, /procurement/requisitions/<uuid:id> |
| [UI-PURCHASE_REQUESTS](UI-PURCHASE_REQUESTS.md) | 구매 요청 · 승인 | 17 | /procurement/requisitions |
| [UI-REQUEST_ASSETS](UI-REQUEST_ASSETS.md) | 서비스요청 자산 연결 | 6 | /portal/requests/<uuid:id> |
| [UI-REQUEST_DETAIL](UI-REQUEST_DETAIL.md) | 서비스요청 상세 | 28 | /portal/requests/<uuid:id> |
| [UI-REQUEST_LIST](UI-REQUEST_LIST.md) | 승인함 서비스 요청 처리 전체 서비스 요청 내 서비스 요청 | 9 | /approvals, /portal/requests, /work/requests |
| [UI-RESOURCE_DETAIL](UI-RESOURCE_DETAIL.md) | 구성항목 상세 | 4 | /cis, /cis/<uuid:id> |
| [UI-RESOURCES](UI-RESOURCES.md) | 구성항목 · CI IT 자산 | 8 | /cis, /cis/<uuid:id> |
| [UI-ROLES](UI-ROLES.md) | 역할 관리 | 23 | /console/roles, /console/roles/<str:id> |
| [UI-SCREEN_DESIGNER](UI-SCREEN_DESIGNER.md) | 화면 디자이너·필드 속성·미리보기 | 48 | /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new |
| [UI-SECURITY_POLICIES](UI-SECURITY_POLICIES.md) | 보안정책 목록/상세 | 23 | /console/security, /console/security/<str:category> |
| [UI-SLA_CARD](UI-SLA_CARD.md) | SLA 현황 카드 | 2 | /portal/incidents/<uuid:id>, /work/incidents/<uuid:id> |
| [UI-SLA_SETTINGS](UI-SLA_SETTINGS.md) | SLA · 업무 달력 | 27 | /console/sla, /work/sla |
| [UI-STOCK_MOVEMENTS](UI-STOCK_MOVEMENTS.md) | 입출고 · 이동 이력 | 7 | /inventory/movements |
| [UI-SYSTEM_HOME](UI-SYSTEM_HOME.md) | 시스템별 업무 현황 | 9 | /systems/asset, /systems/resource, /systems/service |
| [UI-TIMELINESS_AGREEMENT](UI-TIMELINESS_AGREEMENT.md) | KPI 기준일·기한 조정 | 6 | /console/slm/agreements/<uuid:id> |
| [UI-TIMELINESS](UI-TIMELINESS.md) | SLM · 적기처리율 | 24 | /console/slm, /console/slm/reports/<uuid:report_id>/csv |
| [UI-USERS](UI-USERS.md) | 사용자 관리 | 60 | /console/users, /console/users/<str:id> |
| [UI-LOGIN](UI-LOGIN.md) | 로그인 | 5 | /login/ |
| [UI-JS_PROCESS](UI-JS_PROCESS.md) | 프로세스 동적 항목·노드·권한 편집 | 47 | 공통/동적 컴포넌트:  |
| [UI-JS_INTEGRATION](UI-JS_INTEGRATION.md) | API 동적 입력·매핑 행 | 9 | 공통/동적 컴포넌트:  |
| [UI-JS_DESIGNER](UI-JS_DESIGNER.md) | 디자이너 동적 캔버스 조작 | 29 | 공통/동적 컴포넌트:  |
| [UI-JS_SHELL](UI-JS_SHELL.md) | 공통 조작·키보드·반응형 | 25 | 공통/동적 컴포넌트:  |
