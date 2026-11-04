# 도메인 모델 — v0.1

논리 모델이며 SQL 마이그레이션이 아닙니다. 핵심 업무별 식별자와 관계를 먼저 고정합니다.

## 엔터티와 관계

| 영역 | 엔터티 | 주요 관계·제약 |
|---|---|---|
| 조직·접근 | Organization, Department, Person, Identity, Group, Membership, Role, Grant | Person과 로그인 Identity 분리; 퇴사 후 과거 이력 보존 |
| 설정 | SchemaDefinition, FormVersion, WorkflowVersion, RuleVersion | 게시 버전 불변; 인스턴스는 실행 버전 참조 |
| 서비스 | Service, CatalogItem, CatalogVersion, Request | 카탈로그와 운영 서비스 분리; 요청은 신청 당시 버전 참조 |
| 티켓 | Ticket, ServiceRequest, Incident, Problem, Change | 공통 Ticket에 유형별 상세 1:1; 허용 상태는 유형별 정의 |
| 작업 | Task, Assignment, TicketLink, StatusHistory | 담당 그룹·담당자 이력; 관계 유형 검증 |
| 승인 | ApprovalInstance, ApprovalStep, Decision | 결정자·대리·사유·시각 보존; 단계 중복 결정 방지 |
| SLA | SLAPolicyVersion, CalendarVersion, SLAInstance, ClockEvent | 목표별 응답·해결 시계와 정지·재개 이벤트 |
| 자산 | Asset, AssetModel, AssetClass, Location, CustodyHistory | 조직 내 자산번호 고유; 일련번호는 제조사·모델 정책 적용 |
| 구성 | CI, CITypeVersion, CIRelationship, AssetCILink, Baseline | 관계 유형·방향 검증; 자산↔CI는 연결 테이블로 관리 |
| 수집 | SourceSystem, ExternalMapping, Observation, ReconciliationRun, Conflict | 출처+외부 ID 고유; 원본과 승인된 값을 분리 |
| 구매 | PurchaseRequest, PurchaseOrder, OrderLine, Receipt, ReceiptLine, Return | 주문행별 누적 입고·반품 수량 검증 |
| 재고 | Stockroom, Item, InventoryBalance, Reservation, StockMovement | 조직·창고·품목 단위 잔량; 이동 원장과 잔량 정합성 |
| 계약 | Supplier, Contract, ContractLine, Warranty, CostEntry | 자산·서비스·사용권과 근거 계약 연결 |
| 소프트웨어 | SoftwareProduct, ProductAlias, Installation, Entitlement, Allocation, LicenseRuleVersion, ComplianceRun | 설치 사실과 권리 분리; 결과에 계산 입력·규칙 버전 보존 |
| 변경·릴리스 | ChangeAssessment, ChangeWindow, ExecutionTask, Release, ReleaseChange | 변경 승인 버전과 실행·복구 결과 보존 |
| 지식 | Article, ArticleVersion, Review, Audience | 게시본과 편집본 분리; 공개 범위 적용 |
| 공통 | Attachment, Comment, AuditEvent, OutboxEvent, IntegrationJob | 내부 댓글·공개 댓글 구분; 파일 접근은 대상 권한 상속 |

## 공통 필드

업무 레코드에는 id, organization_id, created_at/by, updated_at/by, row_version을 둡니다. 전역 기준정보는 조직 소유 데이터와 구분합니다. 논리 삭제는 대상별 정책으로 적용하고 감사·거래 이력의 연쇄 삭제는 금지합니다. 금액은 통화와 정밀도를 갖고 수량은 단위와 함께 저장합니다.

## 주요 정합성

1. 자산과 CI는 서로 독립적입니다. 하나의 자산에 여러 기술 구성항목이 연결될 수 있으며, 자산 없는 논리 서비스 CI도 가능합니다.
2. 서비스 의존 관계는 Service와 CI 간 명시적 연결로 관리합니다. 순환 관계는 조회 시 방문 집합·최대 깊이로 제어하고 무조건 트리로 취급하지 않습니다.
3. 지급은 자산 상태·보유자 이력·재고 이동을 한 업무 트랜잭션으로 처리합니다. 수량 품목과 개별 식별 자산의 출고를 구분합니다.
4. 재고 이동 원장은 삭제·덮어쓰기 대신 역거래로 정정합니다. 주문 초과 입고 허용 여부는 별도 승인 정책입니다.
5. SLA 이력은 대기 사유와 적용 정책·달력 버전을 포함합니다. 단일 마감 시각만으로 과거 계산을 대체하지 않습니다.
6. 대사 과정에서 원본 수집값이 사용자 승인 값을 곧바로 덮어쓰지 않습니다. 필드별 출처 우선순위와 충돌 검토를 적용합니다.
7. 승인 완료 뒤 중요 금액·대상·위험이 변경되면 재승인 여부를 정책으로 평가합니다.
8. 조직 간 연결은 기본 차단하고 공유 기준정보·허용된 서비스 관계만 명시적으로 예외 처리합니다.

## 이관 설계

외부 키 매핑→원본 보존→중복 후보→검증→시험 이관→건수·관계·금액 대사→전환 순서로 진행합니다. 필수 매핑이 누락된 데이터는 격리하고 임의 보정하지 않습니다. 보존 기간과 삭제·익명화 요구는 별도 결정합니다.
