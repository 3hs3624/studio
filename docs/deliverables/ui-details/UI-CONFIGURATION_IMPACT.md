# UI-CONFIGURATION_IMPACT · 초안 변경 영향도

진입/사용: /admin/entities, /admin/entities/<uuid:id>, /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/entities, /console/entities/<uuid:id>, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new

소스: `desk/templates/desk/configuration-impact.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CONFIGURATION_IMPACT-E001 · 저장된 초안의 변경 영향도 | summary / 별도 입력 제약 없음/조회 항목 | if configuration_impact | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/configuration-impact.html:1` |
| UI-CONFIGURATION_IMPACT-E002 · 항목 | th / 별도 입력 제약 없음/조회 항목 | if configuration_impact | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/configuration-impact.html:1` |
| UI-CONFIGURATION_IMPACT-E003 · 변경 | th / 별도 입력 제약 없음/조회 항목 | if configuration_impact | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/configuration-impact.html:1` |
| UI-CONFIGURATION_IMPACT-E004 · 검토 | th / 별도 입력 제약 없음/조회 항목 | if configuration_impact | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/configuration-impact.html:1` |
| UI-CONFIGURATION_IMPACT-E005 · 확인 내용 | th / 별도 입력 제약 없음/조회 항목 | if configuration_impact | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/configuration-impact.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
