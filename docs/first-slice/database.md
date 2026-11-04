# 첫 구현 DB 명세 — v0.1

논리 모델을 구현 가능한 관계형 구조로 구체화한 설계이며 실행 마이그레이션은 아직 없습니다. UUID 식별자, UTC 시각, 정수 row_version, 조직 범위 복합 외래키를 사용합니다. DB 제품 선택은 유보합니다.

## 테이블

| 테이블 | 주요 열·자료형 | 제약·인덱스 |
|---|---|---|
| organizations | id uuid PK, name varchar(200), active boolean | 이름 비어있음 금지 |
| persons | id uuid PK, organization_id uuid, display_name varchar(200), active boolean | UNIQUE(organization_id,id) |
| identities | id uuid PK, issuer varchar(500), subject varchar(255), person_id uuid | UNIQUE(issuer,subject), 인증 검증 후 매핑 |
| groups | id uuid PK, organization_id uuid, name varchar(200), active boolean | UNIQUE(organization_id,id), UNIQUE(organization_id,name) |
| memberships | organization_id uuid, group_id uuid, person_id uuid | PK(organization_id,group_id,person_id), 동일 조직 FK |
| role_grants | organization_id uuid, person_id uuid, role varchar(40) | PK(organization_id,person_id,role), 역할 allowlist |
| assets | id uuid PK, organization_id uuid, asset_no varchar(80), name varchar(200), model varchar(200), location varchar(200), portal_visible boolean | UNIQUE(organization_id,id), UNIQUE(organization_id,asset_no) |
| configuration_items | id uuid PK, organization_id uuid, ci_no varchar(80), name varchar(200), type varchar(80), status varchar(40), portal_visible boolean | UNIQUE(organization_id,id), UNIQUE(organization_id,ci_no) |
| tickets | id uuid PK, organization_id uuid, number varchar(40), type varchar(20), title varchar(200), description text, requested_by uuid, status varchar(30), group_id uuid nullable, assignee_id uuid nullable, row_version integer, created_at/updated_at timestamp | UNIQUE(organization_id,id), UNIQUE(organization_id,number), type=INCIDENT |
| incidents | ticket_id uuid PK, organization_id uuid, impact smallint, urgency smallint, priority smallint, pending_reason text nullable, resolution text nullable | (organization_id,ticket_id) FK tickets; impact/urgency 1..3, priority 1..5 |
| ticket_resources | organization_id uuid, ticket_id uuid, asset_id uuid nullable, ci_id uuid nullable | exactly one target nonnull; 대상별 부분 고유 인덱스로 중복 연결 금지 |
| comments | id uuid PK, organization_id uuid, ticket_id uuid, author_id uuid, visibility varchar(10), body text, created_at timestamp | visibility PUBLIC/INTERNAL, body 1..10000字; append-only |
| status_history | id uuid PK, organization_id uuid, ticket_id uuid, from_status/to_status varchar(30), reason text, actor_id uuid, occurred_at timestamp | append-only, 티켓별 시간 인덱스 |
| audit_events | id uuid PK, organization_id uuid, actor_id uuid, action varchar(80), entity_type varchar(80), entity_id uuid, before_data/after_data json, reason text, request_id uuid, occurred_at timestamp | append-only, 조직·대상·시간 인덱스; 민감 값 필터링 |
| outbox_events | id uuid PK, organization_id uuid, event_type varchar(80), entity_id uuid, payload json, created_at timestamp, processed_at timestamp nullable, attempts integer, next_attempt_at timestamp | 미처리 일정 인덱스; 재시도 worker용 |
| idempotency_records | organization_id uuid, actor_id uuid, operation varchar(100), key varchar(128), request_hash varchar(64), response_code integer, response_body json, expires_at timestamp | PK(organization_id,actor_id,operation,key) |

위 표에서 JSON·timestamp는 개념 타입이며 DB에 맞는 물리 타입으로 전환합니다. 한국어 글자수 제한은 서버 기준 Unicode code point로 계산하고 UI와 맞춥니다. ticket_resources의 대상별 부분 고유 인덱스는 DB별 지원 방식으로 구현합니다.

## 외래키와 불변 조건

모든 조직 소유 FK는 (organization_id,id) 조합으로 선언합니다. 관계 테이블도 organization_id를 보유합니다. 요청자·작성자·그룹·담당자·자산·CI는 같은 조직이어야 합니다. assignee_id는 group_id 없이 설정할 수 없습니다. 배정 시 활성 그룹의 활성 멤버인지 트랜잭션 안에서 검증합니다. 소속 해제 시 열린 배정 건을 먼저 재배정하거나 요청을 거부합니다.

ticket.type=INCIDENT와 상세 테이블 1:1은 생성 서비스에서 단일 트랜잭션으로 강제하고 DB 제품 선정 후 제약 트리거 등을 평가합니다. 상태 전이는 서비스에서 현재 상태·역할·row_version을 함께 검증합니다. 우선순위는 고정 매트릭스에서 계산하고 클라이언트 값을 저장하지 않습니다.

## 쓰기 원자성

장애 생성: idempotency 잠금/등록 → ticket·incident → 최초 이력·감사 → outbox → 응답 저장 → commit.

상태 전이: 접근 확인 → version 조건 UPDATE → 상세 수정 → status_history·audit·outbox → commit. 버전 불일치 시 전체 rollback 후 409. 같은 명령 재시도는 저장된 응답을 반환하고 이력·이벤트를 중복 생성하지 않습니다.

그룹·역할 수정에도 감사·row_version과 마지막 관리자 보호가 필요합니다. 표의 설정 테이블에도 created_at/by·updated_at/by·row_version을 추가합니다. 초기 DB 적재는 합성 데이터만 사용하며 운영 인증 우회용 계정을 제공하지 않습니다.

## 조회·삭제·보존

목록 인덱스: tickets(organization_id,requested_by,created_at,id), tickets(organization_id,group_id,status,created_at,id), tickets(organization_id,assignee_id,status,created_at,id). 페이지 정렬은 created_at DESC,id DESC이며 커서에 동일 필터·조직·조회 범위를 결합합니다.

tickets·comments·history·audit의 일반 삭제 API는 제공하지 않습니다. 퇴사자는 비활성화하고 과거 작성자를 유지합니다. 개인정보 삭제·익명화·보존 기간은 운영 출시 전 결정하며 무기한 보존으로 자동 확정하지 않습니다. 워커 처리 이력 정리와 idempotency 만료는 최소 24시간 재시도 보장 후 별도 정책으로 수행합니다.
