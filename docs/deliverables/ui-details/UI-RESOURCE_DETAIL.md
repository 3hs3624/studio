# UI-RESOURCE_DETAIL · 구성항목 상세

진입/사용: /cis, /cis/<uuid:id>

소스: `desk/templates/desk/resource-detail.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.inventory [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-RESOURCE_DETAIL-E001 · ← 목록으로 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동:  /cis /assets  | `desk/templates/desk/resource-detail.html:2` |
| UI-RESOURCE_DETAIL-E002 · 번호 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.ci_no }} {{ item.asset_no }} | `desk/templates/desk/resource-detail.html:4` |
| UI-RESOURCE_DETAIL-E003 · 유형 모델 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.type }} {{ item.model\|default:'—' }} | `desk/templates/desk/resource-detail.html:4` |
| UI-RESOURCE_DETAIL-E004 · 상태 위치 | dt / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ item.status }} {{ item.location\|default:'—' }} | `desk/templates/desk/resource-detail.html:4` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
