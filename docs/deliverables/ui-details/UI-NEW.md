# UI-NEW · 장애 등록

진입/사용: /portal/incidents/new

소스: `desk/templates/desk/new.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.new_incident [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-NEW-F01

UI-NEW-F01 · create · POST(JSON) /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동.

항목: UI-NEW-E002, UI-NEW-E003, UI-NEW-E004, UI-NEW-E005, UI-NEW-E006, UI-NEW-E007, UI-NEW-E008, UI-NEW-E009

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-NEW-E001 · ← 요청 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /portal/incidents | `desk/templates/desk/new.html:2` |
| UI-NEW-E002 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:4` |
| UI-NEW-E003 · 제목 * | text / name=title; id=title; required; maxlength=200; placeholder=어떤 문제가 발생했습니까? | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:5` |
| UI-NEW-E004 · 상세 내용 * | textarea / name=description; id=description; required; maxlength=10000; placeholder=발생 시점, 오류 메시지와 업무 영향을 설명해 주십시오. | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:6` |
| UI-NEW-E005 · 영향도 | select / name=impact; id=impact | 해당 화면/공통 영역 표시 시 / 선택값: 3=낮음 · 개인 업무; 2=보통 · 일부 부서; 1=높음 · 조직 전체 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:7` |
| UI-NEW-E006 · 긴급도 | select / name=urgency; id=urgency | 해당 화면/공통 영역 표시 시 / 선택값: 3=낮음 · 우회 가능; 2=보통 · 업무 지연; 1=높음 · 업무 중단 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:7` |
| UI-NEW-E007 · 관련 자산 또는 CI 선택 | select / name=resource; id=resource | 해당 화면/공통 영역 표시 시 / 선택값: =선택하지 않음; ASSET:{{ a.id }}=자산 · {{ a.name }}; CI:{{ c.id }}=CI · {{ c.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:8` |
| UI-NEW-E008 · 취소 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /portal/incidents / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:9` |
| UI-NEW-E009 · 장애 접수 → | submit / type=submit | 해당 화면/공통 영역 표시 시 | 폼 제출: create → /api/v1/incidents / /api/v1/incidents / 장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동. | `desk/templates/desk/new.html:9` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
