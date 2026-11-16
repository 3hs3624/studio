# UI-REQUEST_ASSETS · 서비스요청 자산 연결

진입/사용: /portal/requests/<uuid:id>

소스: `desk/templates/desk/request-assets.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

### UI-REQUEST_ASSETS-F01

UI-REQUEST_ASSETS-F01 · request-asset-issue · 원본 참조  / 선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사.

항목: UI-REQUEST_ASSETS-E002, UI-REQUEST_ASSETS-E003, UI-REQUEST_ASSETS-E004, UI-REQUEST_ASSETS-E005, UI-REQUEST_ASSETS-E006

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-REQUEST_ASSETS-E001 · {{ event.name }} | a / 별도 입력 제약 없음/조회 항목 | if ticket.asset_events or can_issue_asset / for event in ticket.asset_events / if event.can_view | 링크 이동: /assets/{{ event.asset_id }} | `desk/templates/desk/request-assets.html:2` |
| UI-REQUEST_ASSETS-E002 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if ticket.asset_events or can_issue_asset / if can_issue_asset | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사. | `desk/templates/desk/request-assets.html:3` |
| UI-REQUEST_ASSETS-E003 · 지급할 자산 | select / name=asset_id; id=request-asset; required | if ticket.asset_events or can_issue_asset / if can_issue_asset / 선택값: =보관 중인 자산 선택; {{ a.id }}={{ a.asset_no }} · {{ a.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사. | `desk/templates/desk/request-assets.html:4` |
| UI-REQUEST_ASSETS-E004 · 지급 후 위치 | text / name=location; id=request-asset-location; required; maxlength=200 | if ticket.asset_events or can_issue_asset / if can_issue_asset | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사. | `desk/templates/desk/request-assets.html:4` |
| UI-REQUEST_ASSETS-E005 · 지급 사유 | textarea / name=reason; id=request-asset-reason; required; maxlength=10000 | if ticket.asset_events or can_issue_asset / if can_issue_asset | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / 선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사. | `desk/templates/desk/request-assets.html:4` |
| UI-REQUEST_ASSETS-E006 · 요청에 연결해 지급 | submit / 별도 입력 제약 없음/조회 항목 | if ticket.asset_events or can_issue_asset / if can_issue_asset | 폼 제출: request-asset-issue →  / 선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사. | `desk/templates/desk/request-assets.html:4` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
