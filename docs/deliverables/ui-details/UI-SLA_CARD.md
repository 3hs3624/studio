# UI-SLA_CARD · SLA 현황 카드

진입/사용: /portal/incidents/<uuid:id>, /work/incidents/<uuid:id>

소스: `desk/templates/desk/sla-card.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-SLA_CARD-E001 · 응답 목표 시간 사용률 | progress / max=100; value={{ ticket.sla.response.percent }}; aria-label=응답 목표 시간 사용률 | if ticket.sla | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 출력값: value={{ ticket.sla.response.percent }}; max=100 | `desk/templates/desk/sla-card.html:4` |
| UI-SLA_CARD-E002 · 해결 목표 시간 사용률 | progress / max=100; value={{ ticket.sla.resolution.percent }}; aria-label=해결 목표 시간 사용률 | if ticket.sla | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 출력값: value={{ ticket.sla.resolution.percent }}; max=100 | `desk/templates/desk/sla-card.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
