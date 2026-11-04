# 로컬 실행·검증 안내

## 실행

Python 3.12 환경에서 저장소 루트에서 실행합니다. 아래 명령은 로컬 개발 전용입니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEBUG=1
python manage.py migrate
python manage.py setup_demo
python manage.py runserver 127.0.0.1:8000
```

http://127.0.0.1:8000/login/ 에 접속합니다. setup_demo는 비밀번호를 직접 입력받으며 기존 조직 데이터가 있으면 거부합니다. 합성 계정은 employee(직원), agent(담당자), manager(서비스 관리자), assetadmin(자산 관리자), buyer(구매 담당자), stockadmin(재고·자산 관리자), orgadmin(조직 관리자)입니다. manager는 데모에서 자산·재고 관리자 권한도 가집니다. 모두 사용자가 선택한 로컬 비밀번호를 사용합니다. 공개 기본 비밀번호는 없습니다. 운영 모드에서는 데모 생성을 거부합니다.

직원으로 장애 접수→manager로 서비스 데스크에서 agent에 배정→agent로 처리 시작·해결→employee로 해결 확인·종료 순서로 확인합니다. 조직 관리자는 별도 역할이며 자동으로 다른 사람의 장애 처리 권한을 갖지 않습니다.

## 자동 검증

```bash
DEBUG=1 python manage.py check
DEBUG=1 python manage.py makemigrations --check --dry-run
DEBUG=1 python manage.py test --verbosity 2
DEBUG=1 python manage.py process_outbox
DEBUG=1 python manage.py evaluate_sla
```

현재 테스트는 총 121개이며 SQLite에서는 PostgreSQL 전용 동시성 12개가 건너뛰어집니다. POST 요청에는 세션 인증·CSRF 토큰·Idempotency-Key가 필요합니다. 세부 API는 [계약](first-slice/api-contract.md)에 있습니다.

PostgreSQL 환경은 DEBUG=1, DB_ENGINE=postgresql, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT로 설정합니다. 테스트 DB를 생성할 수 있는 **테스트 전용** 권한이 필요합니다. 운영 계정에는 DB 생성 권한을 부여하지 않습니다. CI에 SQLite·PostgreSQL 16 검증 job을 정의했습니다.

## 운영 전 준비

운영 모드(DEBUG=0)는 SECRET_KEY·DB_ENGINE=postgresql·DB_NAME·DB_USER·실제 ALLOWED_HOSTS를 요구합니다. SECRET_KEY는 충분한 길이의 난수로 비밀 저장소에서 주입하십시오. HTTPS·TLS 프록시 설정·정적 파일 제공·프로세스 관리자·공유 로그인 제한·백업/복원·부하 목표는 환경에 맞게 구성해야 합니다. 신뢰할 프록시가 확정되지 않아 forwarded 헤더를 임의 신뢰하지 않습니다.

마이그레이션 되돌리기는 데이터 삭제를 일으킬 수 있으므로 disposable 테스트 DB에서만 roundtrip 검증합니다. 운영 롤백 수단으로 migrate desk zero를 사용하지 않습니다. 감사·상태 이력·댓글은 DB 트리거로 append-only이며 보존·익명화는 후속 정책입니다.

## 첫 설계와의 구현 차이

- Person과 Django auth_user 1:1을 사용합니다. 별도 외부 Identity·복수 조직·조직 전환은 후속입니다.
- organization_id와 관계의 조직 일치는 SQLite/PostgreSQL DB 트리거로 강제합니다. 초기 설계의 복합 외래키 대신 이 방식을 적용했습니다. Incident는 Ticket PK를 공유하고 조직을 중복 저장하지 않습니다.
- 고정 상태 전이·우선순위 표를 사용합니다. 카탈로그 양식과 1명 지정 승인 흐름을 지원합니다. 범용 조건부 양식·다단계 승인·규칙 엔진은 아직 없습니다. SLA는 [추가 구현 명세](sla.md)의 고정 규칙을 지원합니다.
- 자산 등록·정정·지급·반납·이동·폐기 이력은 [자산 명세](assets.md)를 지원합니다. CI는 아직 조회·장애 연결 수준입니다. 수량 재고는 구매·재고 추가 명세를 참조하십시오. 토폴로지·자동 수집은 후속입니다.
- idempotency 응답은 업무 결과 스냅샷을 유지하면서 **현재 권한에 맞게 내부 필드·자산·allowed_actions를 다시 제한**합니다. 권한 변경 후 byte 단위 동일 응답을 보장하지 않습니다. 키는 자동 삭제하지 않아 24시간 이상 보존되며 정리 정책은 후속입니다.
- outbox는 로컬 sink만 제공합니다. 5회 실패한 건은 중단하며 재처리 관리 UI·외부 전달 어댑터는 없습니다.
- 파일 업로드·외부 알림·이메일 접수·지식·SSO는 미구현입니다. 서비스 카탈로그·요청·승인은 추가 구현 명세를 참조하십시오.
- 검색·접수 폼·자산 선택·관리 화면은 첫 규모를 위한 구현이며 대규모 목록 최적화·접근성 정식 감사·운영 부하·복원 리허설은 아직 수행하지 않았습니다.

## SLA 평가와 알림함

새 데모 데이터에는 평일 09:00~18:00 Asia/Seoul 달력과 P1~P5 정책이 포함됩니다. 기존 DB에는 정책을 자동 소급 생성하지 않으므로 서비스 관리자로 /work/sla에서 게시하십시오. /notifications에서 본인 알림을 확인할 수 있습니다. 매분 evaluate_sla를 실행하도록 환경 스케줄러를 설정해야 하며 runserver 자체에는 타이머가 없습니다. 이메일·메신저 발송은 미구현입니다.

## 카탈로그·서비스 요청·승인

[추가 명세](service-requests.md)를 참조하십시오. 신규 데모 DB에는 노트북 신청 서비스가 포함됩니다. employee가 /catalog에서 신청→manager가 /approvals에서 결정→manager 또는 agent가 /work/requests에서 배정·처리→employee가 결과를 확인·종료합니다. 반려·취소 건은 새 요청으로 재신청합니다. 기존 DB에는 데모 카탈로그가 자동 추가되지 않습니다. 서비스 요청에는 아직 장애용 SLA를 적용하지 않습니다.

개발용 DB를 분리하려면 DEBUG=1 SQLITE_PATH=/절대경로/파일.sqlite3로 각 migrate·setup_demo·runserver 명령을 실행하십시오. 새 서비스 요청이 있는 DB는 이전 INCIDENT 전용 스키마로 단순 롤백하지 마십시오.

## 자산 수명주기

[자산 추가 명세](assets.md)를 참조하십시오. 기존 자산은 UNVERIFIED이며 입고 확인 전에는 지급할 수 없습니다. 기존 사용자에게 ASSET_MANAGER 역할을 자동 부여하지 않습니다. assetadmin은 자산 작업, manager는 서비스 요청에 연결한 지급을 데모에서 확인할 수 있습니다. /my-assets에서 직원 본인의 현재 지급 자산과 과거 지급·반납을 확인합니다.

## 구매·계약·재고

[추가 명세](purchasing-inventory.md)를 참조하십시오. manager가 구매 요청→buyer가 지정 승인·발주 확정→stockadmin이 부분 입고·창고 이동·출고를 수행합니다. 창고 관리 장비의 지급·반납·폐기는 자산·재고 두 역할을 요구하며, 반납 시 창고를 지정해야 합니다. 계약·공급업체 금액·연락처는 구매 역할로 제한합니다. 공급업체 반품·실사 조정·계약 만료 알림은 후속입니다.
