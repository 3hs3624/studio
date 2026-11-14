# 로컬 AP·DB 분리 Docker 구성

기존 Render 서비스와 Neon DB를 유지한 채 **새 로컬 설치**를 구성합니다.
Render/Neon의 운영 데이터나 계정을 자동 복제하지 않으며, 기존 서비스 설정도 변경하지 않습니다.

## 구성

| 프로젝트 | 컨테이너 | 역할 |
|---|---|---|
| itsm-local-db | database | PostgreSQL 16, 영속 데이터 볼륨 |
| itsm-local-ap | initialize | 스키마 마이그레이션 및 최초 계정 생성 후 종료 |
| itsm-local-ap | web | 사용자 포털·운영 콘솔·API, Gunicorn |
| itsm-local-ap | proxy | HTTPS 종료, 웹 요청 전달, 로컬 CA |

AP와 DB는 서로 다른 Compose 프로젝트입니다. 기본 구성은 **한 PC에서 AP와 DB 컨테이너를 분리**하며, 물리 서버 두 대를 자동 설치하지는 않습니다.
DB 프로젝트가 만드는 전용 Docker 네트워크에 AP가 연결됩니다.
DB와 web은 호스트 포트를 공개하지 않으며, proxy만 127.0.0.1의 18080/18443 포트를 사용합니다.

## 준비

- Docker Desktop 또는 Docker Engine + Compose v2.24 이상
- Python 3.10 이상 (Windows에서는 아래 python3 대신 python 사용)
- 소스 저장 공간 외에 Docker 이미지·DB를 위한 여유 디스크 최소 4GB 권장
- 저장소의 feature/incident-workflow 브랜치

저장소 최상위 폴더에서 실행합니다.

```bash
git clone --branch feature/incident-workflow https://github.com/3hs3624/studio.git
cd studio
python3 deploy/local_split/control.py configure
python3 deploy/local_split/control.py check-config
python3 deploy/local_split/control.py up
python3 deploy/local_split/control.py verify
```

이미 소스를 내려받으셨다면 clone을 반복하지 말고 해당 브랜치의 최신 소스를 사용하십시오.
configure는 기존 .env.ap/.env.db가 있으면 **덮어쓰지 않습니다**.
이전에 시험 구성한 파일이 남아 있다면 기존 파일·DB 볼륨을 보존하고, 새 빈 소스 폴더와 다른 --name으로 검증하십시오.
다른 스택을 동시에 실행할 때는 --http-port와 --https-port도 다르게 지정해야 합니다.

## 접속 및 계정

**https://localhost:18443/login/**

up이 내보낸 deploy/local_split/local-root.crt를 해당 PC의 신뢰할 루트 인증서로 등록하십시오.
직접 만든 로컬 스택의 인증서인지 확인하고 등록하며, 브라우저의 인증서 검증을 끄지 마십시오.
Windows는 현재 사용자 인증서 관리자의 신뢰할 수 있는 루트 인증 기관, macOS는 키체인 접근의 신뢰 설정을 사용합니다.
verify는 이 CA를 명시적으로 신뢰하므로 OS 인증서 등록 전에도 HTTPS 검증을 수행할 수 있습니다.

최초 관리자 계정은 **temp-admin**입니다.
자동 생성된 비밀번호는 **deploy/local_split/access/accounts.json**에서 확인하십시오.
나머지 temp-manager, temp-employee, temp-assets, temp-buyer도 이 파일에 각각 다른 비밀번호로 기록됩니다.
운영 콘솔은 시스템 관리자·개발자·운영자 역할만 접근할 수 있으며, 최초 계정 중에는 temp-admin만 해당합니다.
새 로컬 설치이므로 Render 로그인 비밀번호와 같지 않습니다.

.env.ap, .env.db, access/accounts.json, backups는 비공개 파일입니다.
POSIX에서는 설정/계정 파일을 0600으로 생성합니다. Windows에서는 사용자 폴더의 NTFS 접근 권한도 확인하십시오.
설정 파일이나 계정 파일이 손실된 상태에서 configure를 다시 실행하면 기존 DB 비밀번호와 맞지 않으므로, 원래 파일을 복구해야 합니다.

## 관리

```bash
python3 deploy/local_split/control.py status
python3 deploy/local_split/control.py restart
python3 deploy/local_split/control.py verify
python3 deploy/local_split/control.py backup
python3 deploy/local_split/control.py stop
```

- stop은 AP를 먼저 내리고 DB를 내립니다. DB·인증서 named volume과 설정·계정 파일을 보존합니다.
- up은 DB 상태 확인 후 AP 초기화를 실행합니다. 기존 계정과 비밀번호는 유지합니다.
- AP/DB를 따로 시작하려면 db-up 후 ap-up을 사용합니다.
- backup은 로컬 DB의 PostgreSQL custom-format 덤프를 backups에 0600으로 저장하고 아카이브 목록을 검사합니다. 실제 복원 검증은 별도 빈 DB에서 수행해야 합니다.
- DB 볼륨 이름은 기본 itsm-local-db-data입니다. 데이터가 필요하면 docker compose down -v 또는 docker volume rm으로 삭제하지 마십시오.
- DB 소유자, 마이그레이션 사용자, 웹 실행 사용자 계정을 분리합니다. web 컨테이너에 소유자·마이그레이션 비밀번호를 전달하지 않습니다.
- 소스는 비관리자 UID로 실행하며, 호스트 파일 권한이 0600이어도 이미지 안에서는 애플리케이션 코드를 읽을 수 있도록 빌드합니다.

## 장애 확인

```bash
docker compose --env-file deploy/local_split/.env.ap -f deploy/local_split/ap.compose.yaml logs --tail 80 initialize web proxy
docker compose --env-file deploy/local_split/.env.db -f deploy/local_split/db.compose.yaml logs --tail 80 database
```

로그에는 비밀번호를 추가 출력하지 마십시오. 설정 검사에는 check-config를 사용합니다.
docker compose config 전체 출력은 비밀값을 포함할 수 있으므로 공유하지 마십시오.

- Docker 연결 실패: Docker Desktop/daemon이 실행 중인지 확인합니다.
- 포트 사용 중: 새 설치에서 configure --http-port 18081 --https-port 18444처럼 지정합니다.
- CA 오류: up 후 내보낸 인증서와 현재 스택이 같은지 확인합니다.
- DB 인증 실패: 기존 DB 볼륨과 .env.ap/.env.db가 같은 설치의 파일인지 확인합니다. 파일을 임의 재생성하지 마십시오.
- 기업용 HTTPS 빌드 프록시: configure --build-ca /absolute/path/to/ca-bundle.pem을 사용합니다. CA는 빌드 secret mount로만 전달하며 이미지에 저장하지 않습니다.

## 운영 환경 전환

현재 프로필은 PC 내부 접속용입니다. 외부 접속을 자동으로 열지 않습니다.
나중에 물리 AP 서버와 DB 서버를 분리할 때는 앱 이미지를 재사용하고, 별도 프로필에서 DB 사설 주소·TLS verify-full·서버 인증서·접속 허용 IP·방화벽을 설정합니다.
운영 공개 전에는 공인 HTTPS 인증서, 호스트/CSRF 설정, 비밀키 관리, DB 백업/복원, 첨부파일 영속 저장소 및 모니터링을 갖춰야 합니다.
비동기 워커나 파일 저장소는 실제 해당 기능 구현에 맞춰 추가합니다. 이 구성이 새로운 업무 기능을 구현한 것은 아닙니다.

자동 검증은 .github/workflows/local-docker.yml에 있습니다.
새 설치, HTTPS/CSRF 로그인, 3개 업무 영역, API·정적 파일, 운영콘솔 권한, 런타임 DB 권한, 컨테이너 재생성 후 계정 보존, 재시작 및 백업 아카이브를 확인합니다.

## 기존 설치 업데이트

엔티티 기본 필드·관계 기능 및 기존 데이터 보존 업데이트 절차는 [엔티티 관리 안내](../../docs/entity-relationships.md#로컬-docker-업데이트)를 참고하십시오. 기존 설정·계정 파일과 Docker 볼륨을 유지하며 소스만 업데이트합니다.

조직·권한 탭, 업무번호 생성 플러그인, 공통코드 관리의 사용법은 [운영 콘솔 구성 관리](../../docs/console-configuration.md)를 참고하십시오.
