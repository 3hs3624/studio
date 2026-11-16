# UI-PROCESS_INBOX · 워크플로우 업무·결재 목록/상세

진입/사용: /processes, /processes/<uuid:id>

소스: `desk/templates/desk/process-inbox.html`

연결: `desk/base.html`, `desk/process-fields.html`, `desk/process-fields.html`, `desk/process-fields.html`, `desk/process-fields.html`

뷰·권한 참조(동시 필수 권한 목록 아님): process_views.inbox [workflow.use]

## 기능/폼 계약

### UI-PROCESS_INBOX-F01

UI-PROCESS_INBOX-F01 · flow-act · POST(JSON) /api/v1/process-runs/act/{{ process_run.id }} / 현재 태스크의 담당자·자격·행 버전·필수값·그룹/필드 권한을 검증해 처리.

항목: UI-PROCESS_INBOX-E004, UI-PROCESS_INBOX-E005, UI-PROCESS_INBOX-E006, UI-PROCESS_INBOX-E007

### UI-PROCESS_INBOX-F02

UI-PROCESS_INBOX-F02 · flow-reassign · POST(JSON) /api/v1/process-runs/reassign/{{ process_run.id }} / 태스크 담당자 재배정; 조직 내 유효 대상·결재 자격 검사.

항목: UI-PROCESS_INBOX-E010, UI-PROCESS_INBOX-E011, UI-PROCESS_INBOX-E012, UI-PROCESS_INBOX-E013

### UI-PROCESS_INBOX-F03

UI-PROCESS_INBOX-F03 · flow-retry_children · POST(JSON) /api/v1/process-runs/retry_children/{{ process_run.id }} / 차단된 하위 실행 보완 재시도; 임의로 완료 상태 조작하지 않음.

항목: UI-PROCESS_INBOX-E014, UI-PROCESS_INBOX-E015, UI-PROCESS_INBOX-E016

### UI-PROCESS_INBOX-F04

UI-PROCESS_INBOX-F04 · flow-resolve_outputs · POST(JSON) /api/v1/process-runs/resolve_outputs/{{ process_run.id }} / 충돌한 하위 결과를 지정 값으로 해소; 사유와 결과 이력 유지.

항목: UI-PROCESS_INBOX-E017, UI-PROCESS_INBOX-E018, UI-PROCESS_INBOX-E019

### UI-PROCESS_INBOX-F05

UI-PROCESS_INBOX-F05 · flow-tick · POST(JSON) /api/v1/process-runs/tick/{{ process_run.id }} / 실행의 대기/자동 진행 평가; 완료 조건 전에는 다음 단계 진행 안 함.

항목: UI-PROCESS_INBOX-E020, UI-PROCESS_INBOX-E021

### UI-PROCESS_INBOX-F06

UI-PROCESS_INBOX-F06 · flow-cancel · POST(JSON) /api/v1/process-runs/cancel/{{ process_run.id }} / 실행 취소 및 관련 태스크 상태 변경; 이력·사유 보존.

항목: UI-PROCESS_INBOX-E022, UI-PROCESS_INBOX-E023, UI-PROCESS_INBOX-E024

### UI-PROCESS_INBOX-F07

UI-PROCESS_INBOX-F07 · flow-start · POST(JSON) /api/v1/process-runs/start / 게시 버전으로 실행 생성; 필수값과 시작 권한을 검사하고 버전 고정.

항목: UI-PROCESS_INBOX-E026, UI-PROCESS_INBOX-E027, UI-PROCESS_INBOX-E028

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PROCESS_INBOX-E001 · 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /processes | `desk/templates/desk/process-inbox.html:1` |
| UI-PROCESS_INBOX-E002 · 연결된 서비스요청 | a / 별도 입력 제약 없음/조회 항목 | if process_run / if process_run.ticket_id | 링크 이동: /portal/requests/{{ process_run.ticket_id }} | `desk/templates/desk/process-inbox.html:2` |
| UI-PROCESS_INBOX-E003 · 상위 프로세스 · {{ run_parent.title }} | a / 별도 입력 제약 없음/조회 항목 | if process_run / if run_parent | 링크 이동: /processes/{{ run_parent.id }} | `desk/templates/desk/process-inbox.html:2` |
| UI-PROCESS_INBOX-E004 · task_id | hidden / name=task_id; type=hidden; value={{ task.id }} | if process_run / for task in run_tasks / if task.can_act | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/act/{{ process_run.id }} / 현재 태스크의 담당자·자격·행 버전·필수값·그룹/필드 권한을 검증해 처리. | `desk/templates/desk/process-inbox.html:4` |
| UI-PROCESS_INBOX-E005 · 처리 결과 | select / name=decision | if process_run / for task in run_tasks / if task.can_act / 선택값: APPROVE=승인; REJECT=반려; COMPLETE=업무 완료 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/act/{{ process_run.id }} / 현재 태스크의 담당자·자격·행 버전·필수값·그룹/필드 권한을 검증해 처리. | `desk/templates/desk/process-inbox.html:4` |
| UI-PROCESS_INBOX-E006 · 처리 사유·의견 | text / name=reason; maxlength=2000 | if process_run / for task in run_tasks / if task.can_act | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/act/{{ process_run.id }} / 현재 태스크의 담당자·자격·행 버전·필수값·그룹/필드 권한을 검증해 처리. | `desk/templates/desk/process-inbox.html:4` |
| UI-PROCESS_INBOX-E007 · 처리·다음 단계 진행 | submit / 별도 입력 제약 없음/조회 항목 | if process_run / for task in run_tasks / if task.can_act | 폼 제출: flow-act → /api/v1/process-runs/act/{{ process_run.id }} / /api/v1/process-runs/act/{{ process_run.id }} / 현재 태스크의 담당자·자격·행 버전·필수값·그룹/필드 권한을 검증해 처리. | `desk/templates/desk/process-inbox.html:4` |
| UI-PROCESS_INBOX-E008 · {{ child.title }} | a / 별도 입력 제약 없음/조회 항목 | if process_run / for task in run_tasks / if task.children / for child in task.children | 링크 이동: /processes/{{ child.id }} | `desk/templates/desk/process-inbox.html:5` |
| UI-PROCESS_INBOX-E009 · 운영자 재할당 | summary / 별도 입력 제약 없음/조회 항목 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / if task.kind == 'TASK' or task.kind == 'APPROVAL' | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E010 · task_id | hidden / name=task_id; type=hidden; value={{ task.id }} | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / if task.kind == 'TASK' or task.kind == 'APPROVAL' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/reassign/{{ process_run.id }} / 태스크 담당자 재배정; 조직 내 유효 대상·결재 자격 검사. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E011 · 담당자 | select / name=person_ids; required; multiple | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / if task.kind == 'TASK' or task.kind == 'APPROVAL' / 선택값: {{ person.id }}={{ person.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/reassign/{{ process_run.id }} / 태스크 담당자 재배정; 조직 내 유효 대상·결재 자격 검사. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E012 · 재할당 사유 | text / name=reason; required; maxlength=2000 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / if task.kind == 'TASK' or task.kind == 'APPROVAL' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/reassign/{{ process_run.id }} / 태스크 담당자 재배정; 조직 내 유효 대상·결재 자격 검사. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E013 · 재할당 | submit / 별도 입력 제약 없음/조회 항목 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / if task.kind == 'TASK' or task.kind == 'APPROVAL' | 폼 제출: flow-reassign → /api/v1/process-runs/reassign/{{ process_run.id }} / /api/v1/process-runs/reassign/{{ process_run.id }} / 태스크 담당자 재배정; 조직 내 유효 대상·결재 자격 검사. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E014 · task_id | hidden / name=task_id; type=hidden; value={{ task.id }} | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / elif task.kind == 'SUBPROCESS' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/retry_children/{{ process_run.id }} / 차단된 하위 실행 보완 재시도; 임의로 완료 상태 조작하지 않음. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E015 · 반려·취소 하위 작업 재실행 사유 | text / name=reason; required; maxlength=2000 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / elif task.kind == 'SUBPROCESS' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/retry_children/{{ process_run.id }} / 차단된 하위 실행 보완 재시도; 임의로 완료 상태 조작하지 않음. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E016 · 실패 하위 작업 재실행 | submit / 별도 입력 제약 없음/조회 항목 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / elif task.kind == 'SUBPROCESS' (앞 분기 제외) | 폼 제출: flow-retry_children → /api/v1/process-runs/retry_children/{{ process_run.id }} / /api/v1/process-runs/retry_children/{{ process_run.id }} / 차단된 하위 실행 보완 재시도; 임의로 완료 상태 조작하지 않음. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E017 · task_id | hidden / name=task_id; type=hidden; value={{ task.id }} | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / elif task.kind == 'SUBPROCESS' (앞 분기 제외) / if process_run.block_reason == 'CHILD_OUTPUT_CONFLICT' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/resolve_outputs/{{ process_run.id }} / 충돌한 하위 결과를 지정 값으로 해소; 사유와 결과 이력 유지. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E018 · 결과 조정 사유 | text / name=reason; required; maxlength=2000 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / elif task.kind == 'SUBPROCESS' (앞 분기 제외) / if process_run.block_reason == 'CHILD_OUTPUT_CONFLICT' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/resolve_outputs/{{ process_run.id }} / 충돌한 하위 결과를 지정 값으로 해소; 사유와 결과 이력 유지. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E019 · 완료된 하위 결과 확정 | submit / 별도 입력 제약 없음/조회 항목 | if process_run / for task in run_tasks / if can_manage_process and task.status == 'OPEN' / elif task.kind == 'SUBPROCESS' (앞 분기 제외) / if process_run.block_reason == 'CHILD_OUTPUT_CONFLICT' | 폼 제출: flow-resolve_outputs → /api/v1/process-runs/resolve_outputs/{{ process_run.id }} / /api/v1/process-runs/resolve_outputs/{{ process_run.id }} / 충돌한 하위 결과를 지정 값으로 해소; 사유와 결과 이력 유지. | `desk/templates/desk/process-inbox.html:6` |
| UI-PROCESS_INBOX-E020 · 대기 만료 처리 사유 | text / name=reason; required; maxlength=2000 | if process_run / if process_run.status == 'ACTIVE' or process_run.status == 'BLOCKED' / if can_manage_process or can_cancel_process / if can_manage_process | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/tick/{{ process_run.id }} / 실행의 대기/자동 진행 평가; 완료 조건 전에는 다음 단계 진행 안 함. | `desk/templates/desk/process-inbox.html:7` |
| UI-PROCESS_INBOX-E021 · 만료된 대기 진행 | submit / 별도 입력 제약 없음/조회 항목 | if process_run / if process_run.status == 'ACTIVE' or process_run.status == 'BLOCKED' / if can_manage_process or can_cancel_process / if can_manage_process | 폼 제출: flow-tick → /api/v1/process-runs/tick/{{ process_run.id }} / /api/v1/process-runs/tick/{{ process_run.id }} / 실행의 대기/자동 진행 평가; 완료 조건 전에는 다음 단계 진행 안 함. | `desk/templates/desk/process-inbox.html:7` |
| UI-PROCESS_INBOX-E022 · 취소 사유 | text / name=reason; required; maxlength=2000 | if process_run / if process_run.status == 'ACTIVE' or process_run.status == 'BLOCKED' / if can_manage_process or can_cancel_process / if can_cancel_process | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/cancel/{{ process_run.id }} / 실행 취소 및 관련 태스크 상태 변경; 이력·사유 보존. | `desk/templates/desk/process-inbox.html:7` |
| UI-PROCESS_INBOX-E023 · 진행 중인 하위 실행도 취소됨을 확인합니다. | checkbox / type=checkbox; required | if process_run / if process_run.status == 'ACTIVE' or process_run.status == 'BLOCKED' / if can_manage_process or can_cancel_process / if can_cancel_process | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/cancel/{{ process_run.id }} / 실행 취소 및 관련 태스크 상태 변경; 이력·사유 보존. | `desk/templates/desk/process-inbox.html:7` |
| UI-PROCESS_INBOX-E024 · 실행 취소 | submit / 별도 입력 제약 없음/조회 항목 | if process_run / if process_run.status == 'ACTIVE' or process_run.status == 'BLOCKED' / if can_manage_process or can_cancel_process / if can_cancel_process | 폼 제출: flow-cancel → /api/v1/process-runs/cancel/{{ process_run.id }} / /api/v1/process-runs/cancel/{{ process_run.id }} / 실행 취소 및 관련 태스크 상태 변경; 이력·사유 보존. | `desk/templates/desk/process-inbox.html:7` |
| UI-PROCESS_INBOX-E025 · {{ process.name }} · v{{ process.published.version }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for process in available_processes | 링크 이동: ?start={{ process.published_id }} | `desk/templates/desk/process-inbox.html:9` |
| UI-PROCESS_INBOX-E026 · version_id | hidden / name=version_id; type=hidden; value={{ start_version.id }} | else (앞 분기 제외) / if start_version | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/start / 게시 버전으로 실행 생성; 필수값과 시작 권한을 검사하고 버전 고정. | `desk/templates/desk/process-inbox.html:9` |
| UI-PROCESS_INBOX-E027 · 업무 제목 | text / name=title; required; maxlength=300 | else (앞 분기 제외) / if start_version | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/process-runs/start / 게시 버전으로 실행 생성; 필수값과 시작 권한을 검사하고 버전 고정. | `desk/templates/desk/process-inbox.html:9` |
| UI-PROCESS_INBOX-E028 · 프로세스 시작 | submit / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if start_version | 폼 제출: flow-start → /api/v1/process-runs/start / /api/v1/process-runs/start / 게시 버전으로 실행 생성; 필수값과 시작 권한을 검사하고 버전 고정. | `desk/templates/desk/process-inbox.html:9` |
| UI-PROCESS_INBOX-E029 · 조회 가능 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 링크 이동: ?scope=all | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E030 · 내 시작 건 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 링크 이동: ?scope=mine | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E031 · 내 처리 대기 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 링크 이동: ?scope=assigned | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E032 · 업무 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E033 · 프로세스·버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E034 · 상태 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E035 · 시작일 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E036 · {{ run.title }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for run in run_page | 링크 이동: /processes/{{ run.id }} | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E037 · 이전 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if run_page.has_previous | 링크 이동: ?scope={{ run_scope }}&page={{ run_page.previous_page_number }} | `desk/templates/desk/process-inbox.html:10` |
| UI-PROCESS_INBOX-E038 · 다음 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if run_page.has_next | 링크 이동: ?scope={{ run_scope }}&page={{ run_page.next_page_number }} | `desk/templates/desk/process-inbox.html:10` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
