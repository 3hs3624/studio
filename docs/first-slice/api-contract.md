# 첫 구현 API 계약 — v0.1

기준 경로 /api/v1. JSON/UTF-8. 조직은 검증된 세션의 활성 조직에서 결정하며 body의 organization_id·requested_by·author_id·priority·status를 신뢰하거나 허용하지 않습니다. 첫 구현은 Django 로컬 비밀번호 인증·세션입니다. 로그인은 /login/, 로그아웃은 POST /logout/이며 SSO는 후속입니다. [ADR-001](../adr/001-application-stack.md)을 참조하십시오.

## 공통 규약

- 인증된 웹 세션, HttpOnly·Secure 쿠키. 쿠키 인증 쓰기에는 CSRF 토큰·Origin 검증을 적용합니다.
- 조회 권한 없는 단일 리소스는 404, 존재를 알아도 되는 리소스의 금지 동작은 403입니다.
- 오류: {"error":{"code":"VERSION_CONFLICT","message":"최신 내용을 다시 확인하십시오.","fields":{},"request_id":"uuid"}}. 원문 stack·내부 기록을 노출하지 않습니다.
- 400 형식/알 수 없는 필드, 401 미인증, 403 금지, 404 비공개·없음, 409 버전/상태/멱등키 충돌, 422 필드·업무 검증 실패, 429 제한. 오류에도 request_id 제공.
- 모든 생성·명령은 Idempotency-Key(1~128자) 필수. 동일 조직·사용자·operation·key에서 같은 본문은 업무 결과 스냅샷 재생, 다른 본문은 409. 최소 24시간 보장. 권한은 재생 시에도 다시 검사하며 내부 필드·연결 대상·allowed_actions는 현재 권한으로 제한합니다. 구현 차이는 [개발 안내](../development.md)를 참조하십시오.
- 갱신·전이·접근 관리 명령은 expected_version 양의 정수 필수. 서버 현재 버전과 다르면 409. 생성은 version=1.
- 목록은 limit 기본 25·최대 100, opaque cursor. 응답 {"items":[],"next_cursor":null}. 응답 시각은 UTC RFC3339.
- unknown field는 거부하고 문자열은 공백만 입력을 거부합니다. 응답은 역할별 allowlist 직렬화합니다.

## 엔드포인트

| 메서드·경로 | 입력 | 성공 | 권한 |
|---|---|---|---|
| GET /me | 없음 | 200 사용자·활성 조직·권한 목록 | 인증 |
| GET /incidents | scope=mine/queue, status, priority, group_id, assignee=me, limit,cursor | 200 IncidentSummary 목록 | mine=본인; queue=허용 그룹, 관리자는 조직 범위 |
| POST /incidents | title,description,impact,urgency,resources? | 201 IncidentDetail, Location 헤더 | 활성 직원; requested_by=세션 사용자 |
| GET /incidents/{id} | 없음 | 200 IncidentDetail | 본인 또는 담당 범위 |
| POST /incidents/{id}/assign | group_id,assignee_id,expected_version | 200 IncidentDetail | NEW는 triage 관리자; 이후 담당자는 그룹 내, 관리자는 조직 내 |
| POST /incidents/{id}/transitions | action,reason?,resolution?,expected_version | 200 IncidentDetail | 화면 명세의 상태·역할 조건 |
| GET /incidents/{id}/comments | limit,cursor | 200 Comment 목록 | 직원 PUBLIC만, 담당 범위 INTERNAL 포함 |
| POST /incidents/{id}/comments | body,visibility,expected_version | 201 Comment, ticket_version | 직원 PUBLIC만; 담당 범위 INTERNAL 허용 |
| GET /incidents/{id}/activity | limit,cursor | 200 허용 활동 목록 | 직원에는 공개 활동만 |
| POST /incidents/{id}/resources | resource_type,resource_id,expected_version | 200 IncidentDetail | 연결 권한과 대상 조회 권한 모두 |
| DELETE /incidents/{id}/resources/{link_id} | expected_version query | 204 | 담당 범위; 멱등키 필수 |
| GET /assets | q,limit,cursor | 200 자산 목록 | 직원은 portal_visible만; 담당자는 자산 조회 권한 |
| GET /assets/{id} | 없음 | 200 자산 상세 | 위와 동일 |
| GET /cis | q,limit,cursor | 200 CI 목록 | 직원은 portal_visible만; 담당자는 CI 조회 권한 |
| GET /cis/{id} | 없음 | 200 CI 상세 | 위와 동일 |
| GET /admin/access | limit,cursor | 200 조직 내 사용자·역할 요약 | 조직 관리자 |
| GET /admin/groups | limit,cursor | 200 조직 내 그룹 목록 | 조직 관리자 |
| PUT /admin/groups/{id}/members/{person_id} | active,expected_version | 200 group_version | 조직 관리자; 열린 배정 소속 해제 차단 |
| PUT /admin/persons/{id}/roles | roles[],expected_version | 200 person_version | 조직 관리자; 마지막 관리자·자기 권한 제거 차단 |

첫 접수 때 resources는 [{resource_type:"ASSET" 또는 "CI",resource_id:"uuid"}], 최대 20개이며 각 대상 조회 권한을 검사합니다. 이후 연결·해제는 담당자 전용입니다. 접수 시 그룹은 서버 기본 triage 정책으로 정하되 상태 NEW를 유지하고 담당자는 비워 둡니다. 설정된 triage 그룹이 없으면 422로 거부합니다.

assign은 NEW→ASSIGNED 전이와 이력을 함께 처리하고 이후에는 배정만 바꿉니다. CLOSED에서는 금지합니다. 처음부터 담당자를 필수 지정하며 그룹만 배정하는 경로는 후속입니다.

## 데이터 계약

IncidentSummary: id uuid,number string,title string,status enum,priority P1..P5,group {id,name}|null,assignee {id,name}|null,created_at,updated_at,version integer.

IncidentDetail: Summary + description,impact 1..3,urgency 1..3,requested_by {id,display_name},resolution string|null,resources[],allowed_actions[]. 내부 대기 사유·감사 원문은 직원 응답에서 제외합니다. resources는 티켓 접근과 별도로 현재 대상 조회 권한을 적용합니다. 목록·상세의 필드 정책을 동일하게 유지합니다.

Comment: id,body,visibility,author {id,display_name},created_at. 불변 기록이며 수정·삭제·공개 전환 API 없음.

Asset: id,asset_no,name,model,location. CI: id,ci_no,name,type,status. 계약·비용·일련번호·보안 경보는 첫 조회 계약에서 제외합니다.

## 명령 예시

POST /incidents
Idempotency-Key: demo-create-001

{"title":"업무용 PC 접속 장애","description":"로그인 후 네트워크에 연결되지 않습니다.","impact":3,"urgency":2}

응답: 201, status NEW, priority P4, version 1. number는 서버 발급 식별자입니다.

POST /incidents/{id}/transitions
Idempotency-Key: demo-resolve-001

{"action":"RESOLVE","resolution":"네트워크 설정을 복구하고 연결을 확인했습니다.","expected_version":4}

응답: 200, status RESOLVED, version 5. action은 START/WAIT/RESUME/RESOLVE/CLOSE/REOPEN. WAIT·REOPEN에는 reason, RESOLVE에는 resolution을 요구합니다. 전체 전이표는 [화면 명세](screens.md)를 따릅니다. 예시는 합성 데이터이며 실행된 요청이 아닙니다.

## SLA 확장

티켓 응답의 sla 필드, 달력·정책 게시, 알림 조회·읽음 API는 [SLA 추가 명세](../sla.md)를 따릅니다. 기존 API 경로·상태 전이·인증 규약은 유지합니다.

## 서비스 요청 확장

서비스 카탈로그·요청·승인 API는 [추가 명세](../service-requests.md)를 따릅니다. 기존 장애 API는 INCIDENT만 다루며 SERVICE_REQUEST를 조회·변경하지 않습니다. 알림 응답에는 kind,label,ticket_url을 추가했고 기존 SLA 필드는 유지합니다.

## 자산 수명주기 확장

자산 등록·수정·상태 처리·지급/반납 이력·본인 자산 조회 API와 역할·버전 규칙은 [자산 추가 명세](../assets.md)를 따릅니다. 기존 Asset 조회 경로는 유지하며 상태·버전을 추가하고 민감 필드를 권한별로 제한합니다.
