# UI-JS_SHELL · 공통 조작·키보드·반응형

진입/사용: 공통/동적 컴포넌트: 

소스: `desk/static/desk/app.js / desk/static/desk/carbon-ui.css`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-JS_SHELL-E001 · 모바일 사이드바 열기/닫기 | 버튼 / data-key=mobile.open | 편집기 열림·해당 대상 선택 시 | 680px 이하에서 메뉴 버튼 표시. aria-expanded 갱신; 열면 첫 링크로 포커스 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E002 · 메뉴 배경 클릭 | 버튼 / data-key=mobile.backdrop | 편집기 열림·해당 대상 선택 시 | 배경 클릭 시 메뉴 닫고 버튼 포커스 복원 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E003 · Escape 메뉴 닫기 | 키보드 / data-key=mobile.escape | 편집기 열림·해당 대상 선택 시 | 메뉴 열린 상태에서만 닫기 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E004 · 메뉴 포커스 순환 | Tab/Shift+Tab / data-key=mobile.focus | 편집기 열림·해당 대상 선택 시 | 열린 메뉴 링크 안에서 키보드 순환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E005 · 모바일 너비 이탈 | 반응형 / data-key=mobile.breakpoint | 편집기 열림·해당 대상 선택 시 | 680px 초과로 전환 시 메뉴 닫기 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E006 · 데스크톱 사이드바 접기 | 미구현 / data-key=shell.desktop-collapse | 편집기 열림·해당 대상 선택 시 | 현재 데스크톱용 접기 조작 없음; 모바일 메뉴 토글과 구분 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E007 · 사이드바 폭 드래그 조절 | 미구현 / data-key=shell.width | 편집기 열림·해당 대상 선택 시 | 현재 사용자가 폭을 조절하는 핸들/저장 기능 없음. CSS 반응형 너비만 적용 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E008 · 사이드바 상태 저장 | 미구현 / data-key=shell.persist | 편집기 열림·해당 대상 선택 시 | 접힘·너비를 localStorage/서버에 저장하는 기능 없음 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E009 · 장문 입력 높이 조절 | 드래그 / data-key=textarea.resize | 편집기 열림·해당 대상 선택 시 | textarea의 기본 세로 resize 허용; 데이터 자동 저장은 아님 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E010 · 넓은 표 가로 스크롤 | 스크롤 / data-key=table.scroll | 편집기 열림·해당 대상 선택 시 | table-wrap 내부에서 가로 이동; 화면 전체 너비 확장 방지 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E011 · 미저장 변경 경고 | 브라우저 이동 / data-key=form.unsaved | 편집기 열림·해당 대상 선택 시 | data-track-changes 폼 수정 후 이동 시 확인; 저장 성공 후 경고 해제 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E012 · 중복 제출 방지 | 상태 / data-key=form.pending | 편집기 열림·해당 대상 선택 시 | 처리 중 제출 버튼 비활성; 실패 시 오류 표시 및 버튼 복원 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js / desk/static/desk/carbon-ui.css` |
| UI-JS_SHELL-E013 · 본인 정보: 이름 | 조회 / data-key=profile.name | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E014 · 본인 정보: 로그인 ID | 조회 / data-key=profile.username | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E015 · 본인 정보: 부서 | 조회 / data-key=profile.department | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E016 · 본인 정보: 이메일 | 조회 / data-key=profile.email | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E017 · 본인 정보: 연락처 | 조회 / data-key=profile.phone | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E018 · 본인 정보: 적용 역할·배정 경로 | 조회 / data-key=profile.roles | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E019 · 본인 정보: 소속 그룹·배정 경로 | 조회 / data-key=profile.groups | 편집기 열림·해당 대상 선택 시 | 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js:442` |
| UI-JS_SHELL-E020 · 본인 정보 모달 열기 | 상호작용 / data-key=profile.open | 편집기 열림·해당 대상 선택 시 | 비동기 조회 중 불러오는 중 표시; 응답 성공 시 내용 교체 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js` |
| UI-JS_SHELL-E021 · 본인 정보 모달 닫기 | 상호작용 / data-key=profile.close | 편집기 열림·해당 대상 선택 시 | 닫기 버튼·Escape·모달 바깥 클릭으로 닫기 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js` |
| UI-JS_SHELL-E022 · 지급 동작 선택 | 상호작용 / data-key=asset.issue | 편집기 열림·해당 대상 선택 시 | 대상자 필수; 서비스요청 선택 시 요청자 자동 선택 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js` |
| UI-JS_SHELL-E023 · 반납 동작 선택 | 상호작용 / data-key=asset.return | 편집기 열림·해당 대상 선택 시 | 반납 창고 필수; 창고 선택 시 위치 자동 반영 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js` |
| UI-JS_SHELL-E024 · 일련번호 재고 선택 | 상호작용 / data-key=inventory.serial | 편집기 열림·해당 대상 선택 시 | 출발 창고·품목에 맞는 자산만 선택 가능 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js` |
| UI-JS_SHELL-E025 · 엔티티 유형 전환 | 상호작용 / data-key=entity.type | 편집기 열림·해당 대상 선택 시 | 유형에 맞는 선택값·코드·참조·길이/정밀도 컨트롤 활성화 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/app.js` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
