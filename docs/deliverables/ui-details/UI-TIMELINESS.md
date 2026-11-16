# UI-TIMELINESS · SLM · 적기처리율

진입/사용: /console/slm, /console/slm/reports/<uuid:report_id>/csv

소스: `desk/templates/desk/timeliness.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): timeliness_views.manage [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-TIMELINESS-F01

UI-TIMELINESS-F01 · 폼 · get 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-TIMELINESS-E002, UI-TIMELINESS-E003, UI-TIMELINESS-E004, UI-TIMELINESS-E005

### UI-TIMELINESS-F02

UI-TIMELINESS-F02 · kpi-report · POST(JSON) /api/v1/timeliness/report / 기간과 모집단으로 확정 보고서 산출 후 CSV 다운로드.

항목: UI-TIMELINESS-E006, UI-TIMELINESS-E007, UI-TIMELINESS-E008, UI-TIMELINESS-E009

### UI-TIMELINESS-F03

UI-TIMELINESS-F03 · kpi-policy · POST(JSON) /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각.

항목: UI-TIMELINESS-E017, UI-TIMELINESS-E018, UI-TIMELINESS-E019, UI-TIMELINESS-E020, UI-TIMELINESS-E021, UI-TIMELINESS-E022, UI-TIMELINESS-E023

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-TIMELINESS-E001 · SLA·업무 달력 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/sla | `desk/templates/desk/timeliness.html:1` |
| UI-TIMELINESS-E002 · 시작일 | date / name=from; type=date; required; value={{ kpi_from }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E003 · 종료일 | date / name=to; type=date; required; value={{ kpi_to }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E004 · 집계 모집단 | select / name=cohort | 해당 화면/공통 영역 표시 시 / 선택값: COMPLETION=기간 내 완료 건; DUE=기간 내 기한 도래 건 · 미완료 포함 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 현재 URL 조회 조건 | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E005 · 자동 산출 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit → 현재 URL 조회 조건 / 현재 URL 조회 조건 | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E006 · starts_on | hidden / name=starts_on; type=hidden; value={{ kpi_from }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/report / 기간과 모집단으로 확정 보고서 산출 후 CSV 다운로드. | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E007 · ends_on | hidden / name=ends_on; type=hidden; value={{ kpi_to }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/report / 기간과 모집단으로 확정 보고서 산출 후 CSV 다운로드. | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E008 · cohort | hidden / name=cohort; type=hidden; value={{ kpi_cohort }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/report / 기간과 모집단으로 확정 보고서 산출 후 CSV 다운로드. | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E009 · 현재 조건으로 결과 확정·CSV 내려받기 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: kpi-report → /api/v1/timeliness/report / /api/v1/timeliness/report / 기간과 모집단으로 확정 보고서 산출 후 CSV 다운로드. | `desk/templates/desk/timeliness.html:2` |
| UI-TIMELINESS-E010 · 요청 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E011 · 기준·정책 버전 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E012 · 접수 시각 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E013 · 처리 기한 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E014 · 실제 완료 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E015 · 결과 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E016 · {{ row.number }} | a / 별도 입력 제약 없음/조회 항목 | for row in kpi_rows | 링크 이동: /console/slm/agreements/{{ row.ticket_id }} | `desk/templates/desk/timeliness.html:3` |
| UI-TIMELINESS-E017 · ticket_type | hidden / name=ticket_type; type=hidden; value={{ entry.kind }} | for entry in kpi_policies | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E018 · 정책명 | text / name=name; required; maxlength=200; value={{ entry.current.name }} | for entry in kpi_policies | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E019 · 적기 기준 | select / name=basis | for entry in kpi_policies / 선택값: {{ key }}={{ label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E020 · SLA 목표 처리 시간 · 분 | number / name=target_minutes; type=number; required; min=1; max=525600; value={{ entry.current.target_minutes\|default:1440 }} | for entry in kpi_policies | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E021 · 업무 달력 | select / name=calendar_id | for entry in kpi_policies / 선택값: =경과 시간 · 24시간 기준; {{ calendar.id }}={{ calendar.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E022 · 협의·변경 사유 | text / name=reason; required; maxlength=500 | for entry in kpi_policies | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E023 · 새 정책 게시 | submit / 별도 입력 제약 없음/조회 항목 | for entry in kpi_policies | 폼 제출: kpi-policy → /api/v1/timeliness/policy / /api/v1/timeliness/policy / 적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각. | `desk/templates/desk/timeliness.html:4` |
| UI-TIMELINESS-E024 · {{ report.starts_on }} ~ {{ report.ends_on }} · {{ report.cohort }} · {{ report.created_at }} · CSV | a / 별도 입력 제약 없음/조회 항목 | for report in kpi_reports | 링크 이동: /console/slm/reports/{{ report.id }}/csv | `desk/templates/desk/timeliness.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
