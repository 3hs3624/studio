# IT자원 소스·배포 현황

IT자원은 GitHub 소스 형상관리와 Jenkins 빌드·배포 관리입니다. 구성항목(CMDB)은 ITSM의 `/cis`에 유지하며 기존 데이터와 장애 요청 참조를 보존합니다.

## 화면

- 통합 초기화면 `/`: IT자원 최근 소스 변경 6건·배포 6건 및 네 가지 요약 지표.
- `/systems/resource`: IT자원 현황.
- `/resources/changes`: 소스 변경 목록·검색·상태 필터·25건 페이지·상세.
- `/resources/deployments`: 배포 목록·검색·상태 필터·25건 페이지·상세.
- 지표 클릭은 해당 조건의 목록으로 이동합니다. 상세에서 HTTPS 원문을 새 탭으로 엽니다.

지표는 수신한 각 PR/배포의 최신 상태를 집계합니다. 빌드 실패는 소스 변경에 연결된 최근 빌드 실패 상태이며 Jenkins 전체 빌드의 누적 실패 수가 아닙니다.
검토 대기 PR은 `OPEN`, 배포 승인 대기는 `AWAITING_APPROVAL`, 배포 실패는 `FAILED`입니다.
모든 집계·목록·상세는 현재 조직과 `delivery.read` 권한을 검사합니다. 조회 권한이 없으면 지표·목록을 공개하지 않습니다.
기본 시스템 관리자·개발자·솔루션 운영자는 읽기와 수신 권한을 가집니다. 사용자 정의 역할에도 두 권한을 배정할 수 있습니다.
자산·구성 조회 역할은 CI 권한을 유지하며 소스 열람 권한을 자동으로 받지 않습니다.

## 연계 상태의 의미

현재 구현은 **현황 조회와 검증된 스냅샷 수신**입니다. GitHub API 자동 수집, Jenkins API 자동 수집, 웹훅, 빌드 실행, 승인·배포 실행은 아직 구현하지 않았습니다.
제공자별 수신 이력이 없으면 `연계 미설정`을 표시하며, 가져온 후에는 `수동 수신` 및 수신 시각을 표시합니다. 데이터가 있다고 자동 연계 중으로 표시하지 않습니다.
원문의 비공개 저장소·Jenkins 접근 권한은 각 외부 시스템에서도 별도로 요구됩니다.
ITSM 변경 요청과의 연결 추적, 소스→빌드→배포 간 관계 연결, 연계 설정 UI와 자동 수집은 후속 범위입니다.
실제 연계 자격 증명이 없어도 화면을 사용할 수 있지만, 가져온 데이터가 없으면 빈 목록입니다. 임의 데모 데이터를 운영 DB에 생성하지 않습니다.

## 수동 수신

신뢰할 수 있는 연계 어댑터가 내보낸 JSON 배열을 개발자/운영자가 아래 명령으로 가져옵니다. 조직 UUID와 같은 조직의 활성 사용자 ID를 명시해야 합니다.
환경변수에 실제 운영 DB를 연결한 상태에서 실행하면 해당 DB에 반영되므로 대상 환경을 확인하십시오.

```bash
python manage.py import_delivery_snapshot --organization ORGANIZATION_UUID --actor OPERATOR_LOGIN --provider github --file github-observations.json
python manage.py import_delivery_snapshot --organization ORGANIZATION_UUID --actor OPERATOR_LOGIN --provider jenkins --file jenkins-observations.json
```

로컬 AP·DB Docker에서는 `initialize` 컨테이너의 마이그레이션 계정으로 실행합니다. JSON 파일을 stdin에서 임시 파일로 전달하고, 같은 `initialize` 서비스에서 위 명령을 실행하는 별도 운영 절차가 필요합니다. web 런타임 DB 계정에는 신규 테이블 DDL 권한을 부여하지 않습니다.

공통 필수 값: `external_id`, `title`, `status`, `external_url`, `occurred_at`.
GitHub 추가 필수 값: `repository`, `branch`. Jenkins 추가 필수 값: `service`, `version`, `environment`.
선택 값: `revision`, `build_status`, `external_actor` 및 다른 제공자의 선택 열. 발생 시각은 ISO8601 시간대를 포함해야 합니다.
외부 계정에는 이름·연락처 대신 제공자 로그인 식별자만 전달합니다. 비밀번호·토큰·개인키·로그 본문을 수신 파일에 넣지 마십시오.
원문 URL은 HTTPS이며 사용자정보·쿼리·fragment를 허용하지 않습니다. GitHub는 지정 저장소의 github.com 경로만 허용합니다. URL을 서버에서 요청하지 않습니다.

GitHub 예시(테스트 전용):

```json
[{"external_id":"example/app#12","title":"로그인 개선","repository":"example/app","branch":"feature/login","revision":"abc123","status":"OPEN","build_status":"FAILED","external_actor":"developer-account","external_url":"https://github.com/example/app/pull/12","occurred_at":"2026-11-13T09:00:00+09:00"}]
```

Jenkins 예시(테스트 전용):

```json
[{"external_id":"deploy-app/21","title":"앱 운영 배포","service":"앱 서비스","version":"v1.2","environment":"운영","status":"AWAITING_APPROVAL","external_actor":"release-account","external_url":"https://ci.example.test/job/deploy-app/21/","occurred_at":"2026-11-13T09:00:00+09:00"}]
```

제공자·조직·외부 식별자 조합으로 갱신하고 오래된 발생 시각의 관찰은 무시합니다. 한 파일의 중복 식별자와 유효하지 않은 항목은 전체 수신을 거부합니다. 최대 500건/2MiB, 수신 이력·감사 이력은 보존합니다.

## 배포·로컬 적용

동일 소스와 마이그레이션 0015를 온라인과 로컬 Docker에서 사용합니다. 기존 계정·업무 데이터·CI 참조를 삭제하지 않습니다.
온라인 배포는 노트북 소스를 자동으로 바꾸지 않습니다. 로컬은 기존 설정/계정/볼륨을 보존하여 최신 소스를 교체하고 다음을 실행합니다.

```powershell
$env:PYTHONUTF8 = "1"
python deploy/local_split/control.py backup
# 최신 소스 교체 후
python deploy/local_split/control.py up
python deploy/local_split/control.py verify
```
