# 사이드바 접기·폭 조절·설정 유지

2026-11-17 구현. 업무 포털과 운영 콘솔 공통 기능입니다. DB 마이그레이션은 없습니다.

| 항목 ID | 조작 | 동작·제한 |
|---|---|---|
| UI-SIDEBAR-E001 | 상단 사이드바 버튼 | 681px 이상에서 접기/펼치기. 접으면 본문을 확장하고 메뉴를 포커스/접근성 탐색에서 제외. 버튼의 aria-expanded와 이름 갱신 |
| UI-SIDEBAR-E002 | 우측 경계 드래그 | 기본 256px, 최소 220px, 최대 min(480px, 화면 너비의 45%). 포인터 캡처로 경계 밖 이동도 처리. Escape·pointercancel·크기 전환은 저장 전 폭으로 복원 |
| UI-SIDEBAR-E003 | 경계에서 방향키 | 좌/우 10px, Shift+좌/우 50px, Home 최소, End 현재 최대. 화면에서 실제 보이는 폭을 기준으로 조절 |
| UI-SIDEBAR-E004 | 경계 두 번 클릭 | 선호 폭 256px로 복원. 좁은 화면에서는 현재 최대 폭 이내로 표시 |
| UI-SIDEBAR-E005 | 브라우저 설정 유지 | studio.sidebar.v1 키에 width·collapsed만 localStorage 저장. 새로고침·화면 이동·포털/콘솔 전환에 적용. 계정 정보·비밀번호·권한은 저장하지 않음 |
| UI-SIDEBAR-E006 | 저장 실패/손상 | 접근 차단·JSON 손상·잘못된 자료형/범위는 기본값 또는 현재 페이지 동작으로 처리. DB/서버에 설정을 저장하지 않으며 다른 브라우저/장치에는 동기화하지 않음 |
| UI-SIDEBAR-E007 | 모바일 전환 | 680px 이하에서는 기존 메뉴 오버레이 사용. 데스크톱 접힘 때문에 모바일 메뉴가 비활성화되지 않음. 데스크톱 복귀 시 선호 상태 복원. 일시적인 화면 폭 제한은 저장된 선호 폭을 덮어쓰지 않음 |
| UI-SIDEBAR-E008 | 같은 브라우저의 다른 탭 | storage 이벤트로 유효한 설정 변경 동기화. 드래그 중에는 외부 변경을 적용하지 않음. 키 삭제 시 기본값 |

기존 UI-JS_SHELL-E006/E007/E008은 위 기능의 개요 정의로 유지합니다. 상세 ID는 각각의 조작·예외를 설명하는 확장 정의이며 이전 화면/항목 전체 집계와 별도로 관리합니다.

## 확인

- 브라우저 17개 시나리오 통과, JavaScript 오류 0건. 포털/콘솔 실제 공통 템플릿을 합성 사용자 컨텍스트로 렌더링했습니다.
- 기존 desk.test_portal·desk.test_render 13개 통과, Django check 및 JS 문법 검사 통과.
- 브라우저 검증: Playwright와 Chromium이 설치된 Python에서 `python deploy/check_sidebar_browser.py` 실행. Django 렌더 Python은 DJANGO_PYTHON(기본 .venv/bin/python), 브라우저는 CHROMIUM_PATH(기본 /usr/bin/chromium), 결과 위치는 SIDEBAR_ARTIFACT_DIR(기본 /tmp/studio-sidebar-check)로 변경 가능.
- 설치형·노트북 Docker에는 최신 소스/이미지를 받아 재시작해야 반영됩니다. 브라우저 설정은 접속 출처별로 별도 저장됩니다.

구현: desk/static/desk/sidebar.js, carbon-ui.css, templates/desk/base.html, sidebar-controls.html. 모바일 메뉴 구현은 기존 app.js를 유지합니다.
