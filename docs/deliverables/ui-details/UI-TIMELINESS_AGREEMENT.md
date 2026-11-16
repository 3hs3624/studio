# UI-TIMELINESS_AGREEMENT · KPI 기준일·기한 조정

진입/사용: /console/slm/agreements/<uuid:id>

소스: `desk/templates/desk/timeliness-agreement.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): timeliness_views.agreement [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-TIMELINESS_AGREEMENT-F01

UI-TIMELINESS_AGREEMENT-F01 · kpi-adjust · POST(JSON) /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / 요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존.

항목: UI-TIMELINESS_AGREEMENT-E002, UI-TIMELINESS_AGREEMENT-E003, UI-TIMELINESS_AGREEMENT-E004, UI-TIMELINESS_AGREEMENT-E005, UI-TIMELINESS_AGREEMENT-E006

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-TIMELINESS_AGREEMENT-E001 · 적기처리율 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/slm | `desk/templates/desk/timeliness-agreement.html:1` |
| UI-TIMELINESS_AGREEMENT-E002 · 합의한 처리 시작 · 시간대 포함 | text / name=agreed_start_at; value={{ kpi_target.agreed_start_at\|date:'c' }}; placeholder=2026-11-13T09:00:00+09:00 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / 요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존. | `desk/templates/desk/timeliness-agreement.html:1` |
| UI-TIMELINESS_AGREEMENT-E003 · 고객 요청 완료 기한 | text / name=requested_due_at; value={{ kpi_target.requested_due_at\|date:'c' }}; placeholder=2026-11-14T18:00:00+09:00 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / 요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존. | `desk/templates/desk/timeliness-agreement.html:1` |
| UI-TIMELINESS_AGREEMENT-E004 · 고객 합의 완료 기한 | text / name=agreed_due_at; value={{ kpi_target.agreed_due_at\|date:'c' }}; placeholder=2026-11-14T18:00:00+09:00 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / 요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존. | `desk/templates/desk/timeliness-agreement.html:1` |
| UI-TIMELINESS_AGREEMENT-E005 · 합의·변경 사유 | text / name=reason; required; maxlength=500 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / 요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존. | `desk/templates/desk/timeliness-agreement.html:1` |
| UI-TIMELINESS_AGREEMENT-E006 · 합의 내용 저장·기한 재계산 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: kpi-adjust → /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / /api/v1/timeliness/adjust/{{ kpi_ticket.id }} / 요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존. | `desk/templates/desk/timeliness-agreement.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
