# 서비스 카탈로그·요청·승인 구현 명세

기준일: 2026-11-04. ITSM-01/04/05 및 PLT-03/04의 일부 구현입니다. 범용 워크플로 엔진·IBM 전체 기능 동등성을 의미하지 않습니다.

## 사용자 업무

1. 서비스 관리자가 /work/catalog에서 서비스 코드·설명·처리 그룹·승인 기준·신청 양식을 게시합니다.
2. 직원은 /catalog에서 본인에게 공개된 최신 서비스를 선택해 신청합니다.
3. 승인 필요 서비스는 지정 승인자 1명에게 배정되고 /approvals와 알림함에 표시됩니다. 승인 생략 서비스는 바로 처리 대기로 접수됩니다.
4. 승인 후 처리 그룹에서 담당자를 배정하고 처리 시작→처리 완료를 기록합니다.
5. 요청자가 결과를 확인하고 종료합니다. 서비스 관리자도 종료할 수 있습니다.

신청자는 승인 대기·승인 완료 상태에서 사유를 입력하고 취소할 수 있습니다. 처리 시작 후에는 이 버전에서 취소할 수 없습니다. 반려·취소 건은 원본을 수정하지 않고 최신 양식으로 새 요청을 만들며 이전 요청 ID를 연결합니다.

계정 발급을 외부 시스템에서 자동 실행하지는 않습니다. 자산 지급·반납은 [자산 수명주기](assets.md)에서 요청과 연결해 기록할 수 있으며 물리적 인수인계는 담당자가 수행합니다.

## 카탈로그와 신청 양식

- CatalogItem의 코드는 조직 내 고유하며 게시 이력은 CatalogVersion으로 보존합니다. 게시 요청의 expected_version은 신규 0, 기존 코드는 현재 최고 버전입니다. 동시 게시·오래된 게시 화면은 충돌로 반환합니다.
- 각 버전에는 처리 그룹, 승인 필요 여부, 지정 승인자, 조직 전체/특정 그룹 공개, 신규 신청 허용 여부, 입력 항목을 보존합니다. 신청 중단은 같은 코드의 새 버전을 available=false로 게시합니다.
- 공개 범위의 그룹 소속은 AGENT 역할과 무관합니다. 조직 내 일반 직원도 지정 그룹에 소속되면 해당 서비스를 신청할 수 있습니다.
- 최신 버전만 신규 신청에 사용하며 과거 버전 제출은 409로 거부합니다. 공개 범위가 없거나 신청 중단 상태이면 404입니다. 이전에 접수한 본인 요청은 이후 공개 범위가 바뀌어도 조회할 수 있습니다.
- 필드는 최대 20개이며 key(소문자 영문으로 시작하는 영문·숫자·밑줄, 최대 40자), label(100자), type, required와 선택지로 구성합니다. 종류는 text(2000자), textarea(4000자), integer(±10억), choice(최대 30개 선택지·각 100자), date(YYYY-MM-DD), boolean입니다.
- 서버에서 필수·자료형·선택지·알 수 없는 항목을 검증합니다. 정수에 boolean·실수는 허용하지 않으며 필수 boolean에는 false도 유효한 답입니다. 사용자 스크립트·임의 HTML·조건부 필드·파일 업로드는 없습니다.
- 접수된 ServiceRequest의 입력값·양식·승인 기준은 DB에서 수정/삭제를 차단합니다. 새 카탈로그 버전이 기존 요청을 변경하지 않습니다.

## 상태·권한

| 상태 | 다음 동작 | 권한·조건 |
|---|---|---|
| PENDING_APPROVAL | APPROVE→APPROVED 또는 REJECT→REJECTED | 접수 시 지정 승인자만, 반려 사유 필수 |
| PENDING_APPROVAL/APPROVED | CANCEL→CANCELLED | 신청자만, 취소 사유 필수 |
| APPROVED | 담당자 배정·START→IN_PROGRESS | 처리 권한과 해당 그룹의 활성 AGENT 배정 필요 |
| IN_PROGRESS | FULFILL→FULFILLED | 배정된 본인 담당자 또는 서비스 관리자, 처리 내용 필수 |
| FULFILLED | CLOSE→CLOSED | 신청자 또는 서비스 관리자 |
| REJECTED/CANCELLED | 새 요청으로 재신청 | 같은 서비스·본인 원본만, 원본 상태 유지 |

처리 담당자는 승인 완료 이후에만 요청을 조회·처리합니다. 서비스 관리자는 조직 내 감독 조회가 가능하지만 지정 승인자가 아니면 승인·반려할 수 없습니다. 조직 관리자 역할은 업무 조회·승인 권한을 자동으로 주지 않습니다. 지정 승인자는 본인에게 배정된 요청과 과거 결정을 조회할 수 있으나 별도 처리 권한 없이 내부 댓글을 볼 수 없습니다.

자기 승인 대상 신청은 접수부터 거부하며 결정 API에서도 재검증합니다. 승인자가 비활성이면 신규 접수를 거부합니다. 이미 대기 중인 승인자의 교체·대결·다단계 승인·인사 시스템의 직속 상사 자동 선택은 아직 없습니다. 이 경우 신청자가 취소하고 관리자가 새 버전을 게시한 뒤 재신청하는 절차가 필요합니다.

요청 처리 그룹은 접수된 카탈로그 버전에 고정합니다. 그룹 내 활성 AGENT에게 재배정할 수 있으며 그룹 간 이관은 아직 없습니다. 마지막 관리자·열린 배정 보호는 기존과 같고 종료·반려·취소는 열린 배정에서 제외합니다.

## 데이터·정합성

Ticket 공통 원장을 INCIDENT와 SERVICE_REQUEST로 구분하고 DB에서 유형별 허용 상태를 검증합니다. 장애 API는 INCIDENT만, 서비스 요청 API는 SERVICE_REQUEST만 조회·변경합니다. 두 유형의 상세 모델을 혼용하지 않습니다. 서비스 요청에는 아직 장애용 SLA 정책을 적용하지 않습니다.

CatalogItem·CatalogVersion·CatalogAudience·ServiceRequest·ApprovalDecision은 append-only입니다. RequestApproval은 대기·승인·반려·취소 상태를 가지며 ApprovalDecision은 승인 건당 최대 1개입니다. 모든 조직 참조는 DB 트리거로 검증합니다.

조직→사용자→티켓 순서의 기존 잠금과 row_version·멱등키를 재사용합니다. 결정·취소·처리·이력·감사·알림·outbox를 한 트랜잭션에 기록합니다. 같은 키 재시도는 중복 신청·결정을 만들지 않습니다. 서로 다른 키의 동시 승인/반려·승인/취소는 같은 버전에서 1건만 성공합니다. 재생 응답도 현재 조회·처리 권한을 검증합니다.

스키마 변경 시 SQLite 테이블 재생성으로 기존 트리거가 사라지지 않도록 마이그레이션 전후에 보호 트리거를 제거·재설치합니다. 기존 데이터가 있는 운영 DB의 역방향 변경은 복원 계획 없이 수행하지 마십시오. 특히 새 서비스 요청을 만든 후에는 이전 INCIDENT 전용 제약으로 단순 롤백할 수 없습니다.

## 알림

기존 알림함에 승인 요청, 승인 결과, 처리 대기, 처리 완료, 요청 취소를 추가했습니다. 승인 요청은 지정 승인자, 결정은 신청자, 처리 대기는 현재 처리 권한이 있는 그룹 담당자·서비스 관리자, 처리 완료는 신청자에게 전달합니다. 승인 대기 중 취소는 기존 승인자에게 전달합니다.

SLA 알림은 기존 alert 참조를 유지하고 서비스 요청 알림은 immutable AuditEvent를 참조합니다. (수신자, 이벤트)별로 중복 생성하지 않으며 현재 티켓 접근 범위를 다시 검사합니다. 알림 제목에는 신청 상세값을 포함하지 않습니다. 읽음 API·SLA 알림 경로는 유지합니다. 이메일·메신저 발송은 없습니다.

## API

기존 세션·CSRF·Idempotency-Key·오류 규약과 limit/cursor 페이지 규약을 따릅니다.

| 메서드·경로 | 입력·응답 |
|---|---|
| GET /api/v1/catalog/items | q,limit,cursor → 본인에게 공개된 최신 서비스 목록 |
| GET /api/v1/catalog/items/{item_id} | 최신 신청 양식 |
| GET/POST /api/v1/catalog/versions | 서비스 관리자만. POST: code,name,description,fulfillment_group_id,approval_required,approver_id(null 가능),public_to_org,audience_group_ids[],available,fields[],expected_version → 201 게시 버전 |
| GET/POST /api/v1/requests | GET scope=mine/queue,status,limit,cursor. POST catalog_version_id,values{},resubmission_of(선택) → 201 요청, Location |
| GET /api/v1/requests/{id} | 본인·지정 승인자·허용 처리 범위의 상세 |
| POST /api/v1/requests/{id}/decision | decision=APPROVE/REJECT,reason(반려 필수),expected_version |
| POST /api/v1/requests/{id}/assign | assignee_id,expected_version |
| POST /api/v1/requests/{id}/actions | action=START/FULFILL/CLOSE/CANCEL,reason(완료·취소 필수),expected_version |
| GET/POST /api/v1/requests/{id}/comments | GET 공개 범위 필터, POST body,visibility,expected_version |
| GET /api/v1/approvals | 본인 승인 대기 목록 |

상세 응답은 fields/values와 카탈로그 버전, 승인 상태·사유, 이전 요청 ID, 허용 동작을 포함합니다. 서버 상태를 클라이언트에서 직접 지정할 수 없습니다. 서비스 요청 댓글도 공개/내부를 분리합니다.

## 실행·검증

새 setup_demo에는 manager 승인자를 사용하는 노트북 신청이 포함됩니다. 기존 DB는 마이그레이션 후 서비스 관리자로 카탈로그를 직접 게시하십시오. local SQLite 파일을 격리하려면 DEBUG=1에서 SQLITE_PATH를 지정할 수 있습니다.

자동 테스트는 공개 범위·자기 승인·지정 승인자·버전 보존·반려·재신청·취소·역할 분리·자료형 검증·내부 댓글·알림·원자적 롤백·DB 보호를 포함합니다. PostgreSQL 전용 테스트는 승인/반려 및 승인/취소의 실제 동시 처리를 검증합니다.

Chromium에서는 항목 빌더로 카탈로그 게시→직원 신청→반려→입력값을 보존한 새 요청→승인→배정→처리 완료→요청자 종료, 내부 댓글 격리·알림 링크·모바일 화면을 확인했습니다.

후속 범위: 다단계·조건부·대리 승인, 직속 상사 자동 배정, 신청 후 수정·재승인, SLA의 서비스 요청 적용, 파일, 자동 프로비저닝, 구매와의 연동입니다. 자산 지급·반납의 부분 연결은 자산 추가 명세를 따릅니다.
