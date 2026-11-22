# studio 작업 규칙

통합 IT 관리 솔루션(서비스·자산·구성·변경·구매·계약). IBM Maximo IT의 업무 영역을 참고한 독립 제품이며 IBM 공식·제휴 프로젝트가 아니다. 개요는 `README.md`, 설계는 `docs/`에서 시작한다.

## 0. 공통 원칙 (모든 AI 에이전트·사람 공통)

이 절은 3hs3624 저장소 전체에 같은 문구로 들어간다. 바꿀 때는 모든 저장소에서 함께 바꾼다.

1. **이 파일(AGENTS.md)이 작업 규칙의 원본이다.** Codex 등 AGENTS.md를 읽는 에이전트는 이 파일을, Claude Code는 이 파일을 불러오는 `CLAUDE.md`를 읽는다. 규칙은 이 파일에만 쓰고 `CLAUDE.md`에는 불러오기 한 줄만 둔다.
2. **원본은 GitHub `3hs3624/studio`의 `main`이다.** PC 로컬 폴더, 개인 메모리, 채팅 기록은 근거가 아니다. 작업 시작 시 `main` 최신본에서 출발하고, 끝나면 커밋·푸시해 저장소에 남긴다.
3. **소스·문서·설계 결정·작업 기록은 모두 이 저장소에 둔다.** 다음 작업자가 다른 모델이어도 저장소만 읽고 같은 결과를 이어갈 수 있어야 한다. 결정은 문서(ADR·결정 기록)로, 진행 상황은 작업 기록으로 남긴다.
4. **구글 드라이브(또는 노션)에 함께 올리라고 정한 문서는 계속 함께 올린다.** 저장소가 원본이고 드라이브·노션은 같은 내용의 사본이다.
5. **비밀값은 커밋하지 않는다.** 토큰·비밀번호·`.env`는 저장소 밖에 두고, 필요한 변수 이름만 `.env.example`에 적는다.
6. **완료 보고 전에 아래 "검증" 명령을 실행하고 결과를 남긴다.** 실행하지 못한 검증은 "미검증"으로 적는다.
7. **특정 모델 전용 기능에 결과가 의존하지 않게 한다.** Claude 서브에이전트·훅, Codex 전용 설정 등을 쓰더라도, 같은 결과를 내는 절차를 이 파일이나 `docs/`에 적어 둔다.
8. **도구·버전은 저장소에 고정된 것을 쓴다.** 잠금 파일(`package-lock.json`, `requirements.txt`, `pom.xml` 등)과 `Dockerfile`·`docker-compose.yml`을 기준으로 하며, 바꾸면 이유를 기록한다.

## 1. 기술 기준

- Django 5.2 LTS, 서버 렌더링 UI, Python 3.12 (`docs/adr/001-application-stack.md`).
- 로컬 개발 DB는 SQLite, 운영·동시성 검증은 PostgreSQL 16.
- 의존성: `requirements.txt`. 배포: `Dockerfile`, `render.yaml`, `deploy/`.

## 2. 실행 (로컬 개발)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DEBUG=1                                     # Windows PowerShell: $env:DEBUG=1
python manage.py migrate
python manage.py setup_demo
python manage.py runserver 127.0.0.1:8000
```

자세한 절차와 데모 계정은 `docs/development.md`.

## 3. 검증 (CI `.github/workflows/ci.yml`과 같음)

```bash
DEBUG=1 python manage.py check
DEBUG=1 python manage.py makemigrations --check --dry-run
DEBUG=1 python manage.py test --verbosity 2
```

PostgreSQL 전용 테스트는 CI의 `postgresql` job에서 실행된다. 로컬 SQLite에서는 건너뛰어진다.

## 4. 변경 시 함께 갱신할 문서

- 기능 범위·상태: `docs/maximo-feature-matrix.md`, `docs/first-slice/implementation-status.md`, `docs/roadmap.md`
- 영역별 명세: `docs/assets.md`, `docs/service-requests.md`, `docs/purchasing-inventory.md`, `docs/sla.md` 등 해당 문서
- 화면·운영 절차가 바뀌면 `docs/manuals/`
- 기술 결정은 `docs/adr/`에 새 번호로 추가

## 5. 주의

- IBM 문서 원문·화면 캡처를 옮겨 적지 않는다. 근거는 `docs/ibm-evidence.md`처럼 출처와 자기 말 요약으로만 남긴다.
- 마이그레이션 되돌리기(`migrate desk zero`)는 일회용 테스트 DB에서만 한다.
