# UI-SLA_SETTINGS · SLA · 업무 달력

진입/사용: /console/sla, /work/sla

소스: `desk/templates/desk/sla-settings.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): views.sla_settings [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-SLA_SETTINGS-F01

UI-SLA_SETTINGS-F01 · sla-policy · POST(JSON) /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장.

항목: UI-SLA_SETTINGS-E001, UI-SLA_SETTINGS-E002, UI-SLA_SETTINGS-E003, UI-SLA_SETTINGS-E004, UI-SLA_SETTINGS-E005, UI-SLA_SETTINGS-E006, UI-SLA_SETTINGS-E007, UI-SLA_SETTINGS-E008, UI-SLA_SETTINGS-E009

### UI-SLA_SETTINGS-F02

UI-SLA_SETTINGS-F02 · sla-calendar · POST(JSON) /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장.

항목: UI-SLA_SETTINGS-E010, UI-SLA_SETTINGS-E011, UI-SLA_SETTINGS-E012, UI-SLA_SETTINGS-E013, UI-SLA_SETTINGS-E014, UI-SLA_SETTINGS-E015, UI-SLA_SETTINGS-E016, UI-SLA_SETTINGS-E017, UI-SLA_SETTINGS-E018, UI-SLA_SETTINGS-E019, UI-SLA_SETTINGS-E020, UI-SLA_SETTINGS-E021, UI-SLA_SETTINGS-E022, UI-SLA_SETTINGS-E023

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-SLA_SETTINGS-E001 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:3` |
| UI-SLA_SETTINGS-E002 · 정책 이름 | text / name=name; id=policy-name; required; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:4` |
| UI-SLA_SETTINGS-E003 · 우선순위 | select / name=priority; id=priority | 해당 화면/공통 영역 표시 시 / 선택값: 1=P1; 2=P2; 3=P3; 4=P4; 5=P5 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:5` |
| UI-SLA_SETTINGS-E004 · 업무 달력 | select / name=calendar_id; id=calendar; required | 해당 화면/공통 영역 표시 시 / 선택값: =달력 선택; {{ c.id }}={{ c.name }} · {{ c.timezone }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:5` |
| UI-SLA_SETTINGS-E005 · 응답 목표 · 업무분 | number / name=response_minutes; id=response-minutes; type=number; required; min=1; max=10080; value=30 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:6` |
| UI-SLA_SETTINGS-E006 · 해결 목표 · 업무분 | number / name=resolution_minutes; id=resolution-minutes; type=number; required; min=1; max=10080; value=240 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:6` |
| UI-SLA_SETTINGS-E007 · 임박 알림 기준 · 사용률 % | number / name=warning_percent; id=warning-percent; type=number; required; min=1; max=99; value=80 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:7` |
| UI-SLA_SETTINGS-E008 · 대기 중 해결 시간 정지 | checkbox / name=pause_on_pending; type=checkbox; checked | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:8` |
| UI-SLA_SETTINGS-E009 · 새 정책 게시 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: sla-policy → /api/v1/sla/policies / /api/v1/sla/policies / 우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장. | `desk/templates/desk/sla-settings.html:8` |
| UI-SLA_SETTINGS-E010 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:9` |
| UI-SLA_SETTINGS-E011 · 달력 이름 | text / name=name; id=calendar-name; required; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:10` |
| UI-SLA_SETTINGS-E012 · 시간대 | text / name=timezone; id=calendar-timezone; required; maxlength=80; value=Asia/Seoul | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:11` |
| UI-SLA_SETTINGS-E013 · 월 | checkbox / name=weekdays; type=checkbox; checked; value=0 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E014 · 화 | checkbox / name=weekdays; type=checkbox; checked; value=1 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E015 · 수 | checkbox / name=weekdays; type=checkbox; checked; value=2 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E016 · 목 | checkbox / name=weekdays; type=checkbox; checked; value=3 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E017 · 금 | checkbox / name=weekdays; type=checkbox; checked; value=4 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E018 · 토 | checkbox / name=weekdays; type=checkbox; value=5 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E019 · 일 | checkbox / name=weekdays; type=checkbox; value=6 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:12` |
| UI-SLA_SETTINGS-E020 · 업무 시작 | time / name=starts_at; id=starts-at; type=time; required; value=09:00 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:13` |
| UI-SLA_SETTINGS-E021 · 업무 종료 | time / name=ends_at; id=ends-at; type=time; required; value=18:00 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:13` |
| UI-SLA_SETTINGS-E022 · 휴일 · 한 줄에 YYYY-MM-DD | textarea / name=holidays; id=holidays; placeholder=2026-12-25 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:14` |
| UI-SLA_SETTINGS-E023 · 새 달력 게시 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: sla-calendar → /api/v1/sla/calendars / /api/v1/sla/calendars / 시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장. | `desk/templates/desk/sla-settings.html:14` |
| UI-SLA_SETTINGS-E024 · 정책 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/sla-settings.html:15` |
| UI-SLA_SETTINGS-E025 · 우선순위 · 버전 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/sla-settings.html:15` |
| UI-SLA_SETTINGS-E026 · 응답 / 해결 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/sla-settings.html:15` |
| UI-SLA_SETTINGS-E027 · 달력 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/sla-settings.html:15` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
