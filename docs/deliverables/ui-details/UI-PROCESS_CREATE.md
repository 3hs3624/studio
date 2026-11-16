# UI-PROCESS_CREATE · 화면/워크플로우/결재선 생성

진입/사용: /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new

소스: `desk/templates/desk/process-create.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): process_views.manage [workflow.manage]

## 기능/폼 계약

### UI-PROCESS_CREATE-F01

UI-PROCESS_CREATE-F01 · flow-save · POST(JSON) /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행

항목: UI-PROCESS_CREATE-E002, UI-PROCESS_CREATE-E003, UI-PROCESS_CREATE-E004, UI-PROCESS_CREATE-E005, UI-PROCESS_CREATE-E006, UI-PROCESS_CREATE-E007, UI-PROCESS_CREATE-E008, UI-PROCESS_CREATE-E009

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PROCESS_CREATE-E001 · ← {{ process_title }} 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ process_base }} | `desk/templates/desk/process-create.html:2` |
| UI-PROCESS_CREATE-E002 · kind | hidden / name=kind; type=hidden; value={{ process_kind }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E003 · reason | hidden / name=reason; type=hidden; value=새 정의 생성 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E004 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E005 · 코드 | text / name=code; required; maxlength=40; pattern=[A-Za-z][A-Za-z0-9_]{0,39} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E006 · 이름 | text / name=name; required; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E007 · 사용 | checkbox / name=active; type=checkbox; checked | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E008 · 취소 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: {{ process_base }} / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |
| UI-PROCESS_CREATE-E009 · 생성 후 설계 시작 | submit / type=submit | 해당 화면/공통 영역 표시 시 | 폼 제출: flow-save → /api/v1/processes/save / /api/v1/processes/save / 그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행 | `desk/templates/desk/process-create.html:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
