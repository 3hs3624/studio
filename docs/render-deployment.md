# 외부 임시 접속 — Render Blueprint

기준일: 2026-11-06. Django를 실행할 별도 서버를 수동 준비하는 대신 Render가 Docker 웹 서비스·PostgreSQL·HTTPS 주소·비밀값을 생성하도록 구성했습니다. 실제 SSO는 보류하고 로컬 임시 계정을 사용합니다.

## 배포 시작

[외부 임시 서버·DB 자동 구성 시작](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2F3hs3624%2Fstudio%2Ftree%2Ffeature%2Fincident-workflow)

Render 계정 로그인 후 생성할 웹/DB가 모두 Free인지 검토하고 배포를 승인합니다. 별도 SSH 서버·도메인·수동 DB 연결값 입력은 필요하지 않습니다. 계정 로그인·리소스 생성 승인은 사용자 본인 계정에서 수행해야 하며, 현재 도구에 Render 계정/API 키가 연결되지 않아 이 단계는 대행할 수 없습니다. 구성 작성·로컬/CI 검증과 실제 Render 배포 성공은 별개입니다.

원문/고객 자료를 이 임시 사이트에 적재하지 않습니다. 무료 인스턴스는 검증용이며 운영 출시용이 아닙니다. 무료 웹 서비스는 유휴 시 정지/재시작될 수 있고 무료 PostgreSQL은 생성 후 30일 만료됩니다. 기존 무료 DB 할당·계정 상태에 따라 생성이 거부될 수도 있습니다. 유료 전환/결제는 자동으로 진행하지 않습니다.

## 자동 구성

- render.yaml: Free 웹·Free PostgreSQL 16, Singapore 동일 지역, DB 외부 IP 접속 차단, 자동 소스 배포 off
- Render의 생성 호스트만 ALLOWED_HOSTS와 CSRF origin에 추가, HTTPS 프록시 신뢰·Secure 쿠키 적용
- DATABASE_URL을 해석하되 PostgreSQL/TLS만 허용하고 접속 값은 로그에 출력하지 않음
- WhiteNoise가 정적파일 제공; Caddy 컨테이너/별도 정적 호스팅 없이 기존 Django UI 유지
- 최초 기동에서 마이그레이션·역할별 임시 계정 발급, 재기동에서 기존 비밀번호 유지
- Render가 SECRET_KEY와 계정별 비밀번호 5개를 서로 다른 비밀 환경변수로 생성

## 접속 방법

배포가 성공하면 Render Dashboard의 웹 서비스 URL 뒤 `/login/`에 접속합니다. 정확한 URL은 Render가 실제 생성한 결과를 확인해야 하며 임의로 `studio-itsm-preview.onrender.com`이라고 보장하지 않습니다.

| 아이디 | 역할 | Render Environment에서 확인할 비밀값 |
|---|---|---|
| temp-admin | 조직 관리 | STUDIO_LOCAL_TEMP_ADMIN_PASSWORD |
| temp-manager | 서비스 처리 | STUDIO_LOCAL_TEMP_MANAGER_PASSWORD |
| temp-employee | 요청자 | STUDIO_LOCAL_TEMP_EMPLOYEE_PASSWORD |
| temp-assets | 자산/재고 | STUDIO_LOCAL_TEMP_ASSETS_PASSWORD |
| temp-buyer | 구매 | STUDIO_LOCAL_TEMP_BUYER_PASSWORD |

비밀번호는 Render의 소유자 전용 환경변수 화면에서 확인합니다. 기존 개발환경 접속정보 JSON의 비밀번호와 다릅니다. 소스·로그·공개 페이지·URL에 비밀번호를 표시하지 않습니다. 임시 파일시스템이 초기화되어도 DB 계정은 그대로 유지합니다. 비밀 환경변수 값을 바꾸는 것만으로 기존 DB 사용자 비밀번호를 자동 초기화하지 않으므로 변경 시 명시적 계정 관리 절차를 사용해야 합니다.

## 검증/다음 단계

구성 스키마·설정 파싱, 비밀환경 계정 최초 생성/재기동·누락값 거부, 기본 로컬 계정 모드, 기존 Docker/HTTPS 경로 회귀를 검증합니다. 실제 Render에서는 계정 승인 후 생성 결과·기동 로그·5개 계정 로그인·CSS·세션 회수·DB 보존·재기동을 추가 확인해야 합니다. Render 고유 환경 검증 전에는 외부 배포 완료로 표기하지 않습니다.

계약 운영용 배포에는 조직 소유 호스팅 계정·보존/백업/복원·부하/보안·운영지원·접근제한을 확정해야 합니다. 유료 플랜/운영 인프라 변경은 별도 승인 없이 수행하지 않습니다.

## 확인한 공식 문서

- https://render.com/docs/deploy-django
- https://render.com/docs/blueprint-spec
- https://render.com/docs/deploy-to-render
- https://render.com/docs/free
