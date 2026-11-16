# UI-REQUEST_DETAIL · 서비스요청 상세

진입/사용: /portal/requests/<uuid:id>

소스: `desk/templates/desk/request-detail.html`

연결: `desk/base.html`, `desk/request-assets.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.request_detail [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-REQUEST_DETAIL-F01

UI-REQUEST_DETAIL-F01 · request-decision · POST(JSON) /api/v1/requests/{{ ticket.id }}/decision / 지정 승인자만 결정; 자기 결재 배제·반려 사유 검증; 상태/버전 충돌 차단

항목: UI-REQUEST_DETAIL-E009, UI-REQUEST_DETAIL-E010, UI-REQUEST_DETAIL-E011, UI-REQUEST_DETAIL-E012

### UI-REQUEST_DETAIL-F02

UI-REQUEST_DETAIL-F02 · request-assign · POST(JSON) /api/v1/requests/{{ ticket.id }}/assign / 허용된 처리 그룹 구성원만 배정; 변경 사유/버전 검사

항목: UI-REQUEST_DETAIL-E015, UI-REQUEST_DETAIL-E016, UI-REQUEST_DETAIL-E017

### UI-REQUEST_DETAIL-F03

UI-REQUEST_DETAIL-F03 · request-action · POST(JSON) /api/v1/requests/{{ ticket.id }}/actions / 허용된 현재 상태의 시작/조치 완료/확인 종료/취소 동작만 실행.

항목: UI-REQUEST_DETAIL-E018, UI-REQUEST_DETAIL-E019, UI-REQUEST_DETAIL-E020, UI-REQUEST_DETAIL-E021

### UI-REQUEST_DETAIL-F04

UI-REQUEST_DETAIL-F04 · comment · POST(JSON) /api/v1/requests/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음

항목: UI-REQUEST_DETAIL-E024, UI-REQUEST_DETAIL-E025, UI-REQUEST_DETAIL-E026, UI-REQUEST_DETAIL-E027

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-REQUEST_DETAIL-E001 · SLA 합의 시각·기한 관리 | a / 별도 입력 제약 없음/조회 항목 | if is_service_manager | 링크 이동: /console/slm/agreements/{{ ticket.id }} | `desk/templates/desk/request-detail.html:2` |
| UI-REQUEST_DETAIL-E002 · ← 서비스 요청 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /portal/requests | `desk/templates/desk/request-detail.html:2` |
| UI-REQUEST_DETAIL-E003 · 업무·결재 진행 화면 → | a / 별도 입력 제약 없음/조회 항목 | if ticket.process_run_id | 링크 이동: /processes/{{ ticket.process_run_id }} | `desk/templates/desk/request-detail.html:3` |
| UI-REQUEST_DETAIL-E004 · {{ answer.label }} | dt / 별도 입력 제약 없음/조회 항목 | for answer in answers | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ answer.value\|linebreaksbr }} | `desk/templates/desk/request-detail.html:3` |
| UI-REQUEST_DETAIL-E005 · 이전 요청 확인 → | a / 별도 입력 제약 없음/조회 항목 | if ticket.resubmission_of | 링크 이동: /portal/requests/{{ ticket.resubmission_of }} | `desk/templates/desk/request-detail.html:3` |
| UI-REQUEST_DETAIL-E006 · 지정 승인자 | dt / 별도 입력 제약 없음/조회 항목 | if ticket.approval | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.approval.approver.display_name }} | `desk/templates/desk/request-detail.html:5` |
| UI-REQUEST_DETAIL-E007 · 승인 상태 | dt / 별도 입력 제약 없음/조회 항목 | if ticket.approval | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: 승인 대기 {{ ticket.approval.status\|state_label }} | `desk/templates/desk/request-detail.html:5` |
| UI-REQUEST_DETAIL-E008 · 결정 사유 | dt / 별도 입력 제약 없음/조회 항목 | if ticket.approval / if ticket.approval.reason | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.approval.reason\|linebreaksbr }} | `desk/templates/desk/request-detail.html:5` |
| UI-REQUEST_DETAIL-E009 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if ticket.approval / if ticket.can_decide | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/requests/{{ ticket.id }}/decision / 지정 승인자만 결정; 자기 결재 배제·반려 사유 검증; 상태/버전 충돌 차단 | `desk/templates/desk/request-detail.html:6` |
| UI-REQUEST_DETAIL-E010 · 승인 결정 | select / name=decision; id=decision | if ticket.approval / if ticket.can_decide / 선택값: APPROVE=승인; REJECT=반려 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/decision / 지정 승인자만 결정; 자기 결재 배제·반려 사유 검증; 상태/버전 충돌 차단 | `desk/templates/desk/request-detail.html:6` |
| UI-REQUEST_DETAIL-E011 · 결정 사유 반려 시 필수 | textarea / name=reason; id=decision-reason; maxlength=10000 | if ticket.approval / if ticket.can_decide | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/decision / 지정 승인자만 결정; 자기 결재 배제·반려 사유 검증; 상태/버전 충돌 차단 | `desk/templates/desk/request-detail.html:6` |
| UI-REQUEST_DETAIL-E012 · 결정 저장 | submit / 별도 입력 제약 없음/조회 항목 | if ticket.approval / if ticket.can_decide | 폼 제출: request-decision → /api/v1/requests/{{ ticket.id }}/decision / /api/v1/requests/{{ ticket.id }}/decision / 지정 승인자만 결정; 자기 결재 배제·반려 사유 검증; 상태/버전 충돌 차단 | `desk/templates/desk/request-detail.html:6` |
| UI-REQUEST_DETAIL-E013 · 처리 그룹 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.group.name }} | `desk/templates/desk/request-detail.html:7` |
| UI-REQUEST_DETAIL-E014 · 담당자 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.assignee.display_name\|default:'미배정' }} | `desk/templates/desk/request-detail.html:7` |
| UI-REQUEST_DETAIL-E015 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if ticket.can_assign | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/requests/{{ ticket.id }}/assign / 허용된 처리 그룹 구성원만 배정; 변경 사유/버전 검사 | `desk/templates/desk/request-detail.html:7` |
| UI-REQUEST_DETAIL-E016 · 담당자 배정 | select / name=assignee_id; id=request-assignee; required | if ticket.can_assign / 선택값: =담당자 선택; {{ person.id }}={{ person.display_name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/assign / 허용된 처리 그룹 구성원만 배정; 변경 사유/버전 검사 | `desk/templates/desk/request-detail.html:7` |
| UI-REQUEST_DETAIL-E017 · 배정 저장 | submit / 별도 입력 제약 없음/조회 항목 | if ticket.can_assign | 폼 제출: request-assign → /api/v1/requests/{{ ticket.id }}/assign / /api/v1/requests/{{ ticket.id }}/assign / 허용된 처리 그룹 구성원만 배정; 변경 사유/버전 검사 | `desk/templates/desk/request-detail.html:7` |
| UI-REQUEST_DETAIL-E018 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if ticket.allowed_actions | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/requests/{{ ticket.id }}/actions / 허용된 현재 상태의 시작/조치 완료/확인 종료/취소 동작만 실행. | `desk/templates/desk/request-detail.html:8` |
| UI-REQUEST_DETAIL-E019 · 다음 동작 | select / name=action; id=request-action; required | if ticket.allowed_actions / 선택값: =선택하십시오.; {{ action }}=처리 시작 처리 완료 확인 · 종료 신청 취소 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/actions / 허용된 현재 상태의 시작/조치 완료/확인 종료/취소 동작만 실행. | `desk/templates/desk/request-detail.html:8` |
| UI-REQUEST_DETAIL-E020 · 처리 내용 · 취소 사유 | textarea / name=reason; id=request-reason; maxlength=10000 | if ticket.allowed_actions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/actions / 허용된 현재 상태의 시작/조치 완료/확인 종료/취소 동작만 실행. | `desk/templates/desk/request-detail.html:8` |
| UI-REQUEST_DETAIL-E021 · 요청 처리 | submit / 별도 입력 제약 없음/조회 항목 | if ticket.allowed_actions | 폼 제출: request-action → /api/v1/requests/{{ ticket.id }}/actions / /api/v1/requests/{{ ticket.id }}/actions / 허용된 현재 상태의 시작/조치 완료/확인 종료/취소 동작만 실행. | `desk/templates/desk/request-detail.html:8` |
| UI-REQUEST_DETAIL-E022 · 다시 신청하기 → | a / 별도 입력 제약 없음/조회 항목 | if ticket.requested_by.id == actor.id\|stringformat:'s' / if ticket.status == 'REJECTED' or ticket.status == 'CANCELLED' | 링크 이동: /catalog/items/{{ ticket.catalog_item_id }}?resubmission_of={{ ticket.id }} | `desk/templates/desk/request-detail.html:9` |
| UI-REQUEST_DETAIL-E023 · 대화 | summary / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/request-detail.html:10` |
| UI-REQUEST_DETAIL-E024 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/requests/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/request-detail.html:10` |
| UI-REQUEST_DETAIL-E025 · 댓글 | textarea / name=body; id=body; required; maxlength=10000 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/request-detail.html:10` |
| UI-REQUEST_DETAIL-E026 · 댓글 공개 범위 | select / name=visibility; aria-label=댓글 공개 범위 | 해당 화면/공통 영역 표시 시 / 선택값: PUBLIC=공개 · 요청자에게 표시; INTERNAL=내부 · 처리 담당자만 표시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/requests/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/request-detail.html:10` |
| UI-REQUEST_DETAIL-E027 · 댓글 등록 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: comment → /api/v1/requests/{{ ticket.id }}/comments / /api/v1/requests/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/request-detail.html:10` |
| UI-REQUEST_DETAIL-E028 · 처리 이력 | summary / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/request-detail.html:11` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
