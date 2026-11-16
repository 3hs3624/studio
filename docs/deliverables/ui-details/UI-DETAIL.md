# UI-DETAIL · 장애 상세

진입/사용: /portal/incidents/<uuid:id>, /work/incidents/<uuid:id>

소스: `desk/templates/desk/detail.html`

연결: `desk/base.html`, `desk/sla-card.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.detail [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-DETAIL-F01

UI-DETAIL-F01 · assign · POST(JSON) /api/v1/incidents/{{ ticket.id }}/assign / 처리 그룹과 담당자 배정; 유효한 그룹 소속 및 상태 검사.

항목: UI-DETAIL-E005, UI-DETAIL-E006, UI-DETAIL-E007

### UI-DETAIL-F02

UI-DETAIL-F02 · transition · POST(JSON) /api/v1/incidents/{{ ticket.id }}/transitions / 장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증.

항목: UI-DETAIL-E008, UI-DETAIL-E009, UI-DETAIL-E010, UI-DETAIL-E011, UI-DETAIL-E012

### UI-DETAIL-F03

UI-DETAIL-F03 · detach · DELETE /api/v1/incidents/{{ ticket.id }}/resources/{{ r.link_id }} / 지정 자원 연결 제거; 대상 업무 권한·행 버전 검사.

항목: UI-DETAIL-E013, UI-DETAIL-E014

### UI-DETAIL-F04

UI-DETAIL-F04 · attach · POST(JSON) /api/v1/incidents/{{ ticket.id }}/resources / 장애/요청에 자원 연결; 자원 유형·조회 권한·조직 검사.

항목: UI-DETAIL-E015, UI-DETAIL-E016, UI-DETAIL-E017

### UI-DETAIL-F05

UI-DETAIL-F05 · comment · POST(JSON) /api/v1/incidents/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음

항목: UI-DETAIL-E019, UI-DETAIL-E020, UI-DETAIL-E021, UI-DETAIL-E022

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-DETAIL-E001 · ← 목록으로 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동:  /work /portal /incidents | `desk/templates/desk/detail.html:2` |
| UI-DETAIL-E002 · 담당 그룹 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.group.name }} | `desk/templates/desk/detail.html:8` |
| UI-DETAIL-E003 · 담당자 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.assignee.display_name\|default:'미배정' }} | `desk/templates/desk/detail.html:8` |
| UI-DETAIL-E004 · 우선순위 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ ticket.priority }} | `desk/templates/desk/detail.html:8` |
| UI-DETAIL-E005 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if 'ASSIGN' in ticket.allowed_actions | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/incidents/{{ ticket.id }}/assign / 처리 그룹과 담당자 배정; 유효한 그룹 소속 및 상태 검사. | `desk/templates/desk/detail.html:9` |
| UI-DETAIL-E006 · 담당자 배정 | select / name=assignment; id=assignment; required | if 'ASSIGN' in ticket.allowed_actions / 선택값: =담당자 선택; {{ a.group_id }}:{{ a.person_id }}={{ a.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/assign / 처리 그룹과 담당자 배정; 유효한 그룹 소속 및 상태 검사. | `desk/templates/desk/detail.html:9` |
| UI-DETAIL-E007 · 배정 저장 | submit / 별도 입력 제약 없음/조회 항목 | if 'ASSIGN' in ticket.allowed_actions | 폼 제출: assign → /api/v1/incidents/{{ ticket.id }}/assign / /api/v1/incidents/{{ ticket.id }}/assign / 처리 그룹과 담당자 배정; 유효한 그룹 소속 및 상태 검사. | `desk/templates/desk/detail.html:9` |
| UI-DETAIL-E008 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if has_transitions | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/incidents/{{ ticket.id }}/transitions / 장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증. | `desk/templates/desk/detail.html:10` |
| UI-DETAIL-E009 · 다음 동작 | select / name=action; id=action; required | if has_transitions / 선택값: =동작 선택; {{ action }}=처리 시작 대기로 전환 처리 재개 해결 완료 해결 확인 · 종료 재개방 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/transitions / 장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증. | `desk/templates/desk/detail.html:10` |
| UI-DETAIL-E010 · 사유 대기·재개방 시 필수 | textarea / name=reason; id=reason; maxlength=10000 | if has_transitions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/transitions / 장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증. | `desk/templates/desk/detail.html:10` |
| UI-DETAIL-E011 · 해결 내용 해결 완료 시 필수 | textarea / name=resolution; id=resolution; maxlength=10000 | if has_transitions | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/transitions / 장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증. | `desk/templates/desk/detail.html:10` |
| UI-DETAIL-E012 · 상태 변경 | submit / 별도 입력 제약 없음/조회 항목 | if has_transitions | 폼 제출: transition → /api/v1/incidents/{{ ticket.id }}/transitions / /api/v1/incidents/{{ ticket.id }}/transitions / 장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증. | `desk/templates/desk/detail.html:10` |
| UI-DETAIL-E013 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | for r in ticket.resources / if internal and ticket.status != 'CLOSED' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/incidents/{{ ticket.id }}/resources/{{ r.link_id }} / 지정 자원 연결 제거; 대상 업무 권한·행 버전 검사. | `desk/templates/desk/detail.html:11` |
| UI-DETAIL-E014 · 연결 해제 | submit / 별도 입력 제약 없음/조회 항목 | for r in ticket.resources / if internal and ticket.status != 'CLOSED' | 폼 제출: detach → /api/v1/incidents/{{ ticket.id }}/resources/{{ r.link_id }} / /api/v1/incidents/{{ ticket.id }}/resources/{{ r.link_id }} / 지정 자원 연결 제거; 대상 업무 권한·행 버전 검사. | `desk/templates/desk/detail.html:11` |
| UI-DETAIL-E015 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if internal and ticket.status != 'CLOSED' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/incidents/{{ ticket.id }}/resources / 장애/요청에 자원 연결; 자원 유형·조회 권한·조직 검사. | `desk/templates/desk/detail.html:12` |
| UI-DETAIL-E016 · 대상 연결 | select / name=resource; id=resource; required | if internal and ticket.status != 'CLOSED' / 선택값: =대상 선택; ASSET:{{ a.id }}=자산 · {{ a.name }}; CI:{{ c.id }}=CI · {{ c.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/resources / 장애/요청에 자원 연결; 자원 유형·조회 권한·조직 검사. | `desk/templates/desk/detail.html:12` |
| UI-DETAIL-E017 · 연결 | submit / 별도 입력 제약 없음/조회 항목 | if internal and ticket.status != 'CLOSED' | 폼 제출: attach → /api/v1/incidents/{{ ticket.id }}/resources / /api/v1/incidents/{{ ticket.id }}/resources / 장애/요청에 자원 연결; 자원 유형·조회 권한·조직 검사. | `desk/templates/desk/detail.html:12` |
| UI-DETAIL-E018 · 대화와 처리 기록 | summary / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/detail.html:12` |
| UI-DETAIL-E019 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/incidents/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/detail.html:13` |
| UI-DETAIL-E020 · 댓글 | textarea / name=body; id=body; required; maxlength=10000 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/detail.html:13` |
| UI-DETAIL-E021 · 댓글 공개 범위 | select / name=visibility; aria-label=댓글 공개 범위 | 해당 화면/공통 영역 표시 시 / 선택값: PUBLIC=공개 · 요청자에게 표시; INTERNAL=내부 · 담당자만 표시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/incidents/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/detail.html:13` |
| UI-DETAIL-E022 · 댓글 등록 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: comment → /api/v1/incidents/{{ ticket.id }}/comments / /api/v1/incidents/{{ ticket.id }}/comments / 공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음 | `desk/templates/desk/detail.html:13` |
| UI-DETAIL-E023 · 상태 이력 | summary / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/detail.html:14` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
