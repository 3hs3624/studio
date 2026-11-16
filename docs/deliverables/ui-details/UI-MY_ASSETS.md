# UI-MY_ASSETS · 내 지급 자산

진입/사용: /my-assets

소스: `desk/templates/desk/my-assets.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): asset_views.mine [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-MY_ASSETS-E001 · 자산 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/my-assets.html:2` |
| UI-MY_ASSETS-E002 · 모델 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/my-assets.html:2` |
| UI-MY_ASSETS-E003 · 위치 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/my-assets.html:2` |
| UI-MY_ASSETS-E004 · 상태 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/my-assets.html:2` |
| UI-MY_ASSETS-E005 · {{ a.name }} | a / 별도 입력 제약 없음/조회 항목 | for a in active_assets | 링크 이동: /assets/{{ a.id }} | `desk/templates/desk/my-assets.html:2` |
| UI-MY_ASSETS-E006 · 관련 요청 확인 → | a / 별도 입력 제약 없음/조회 항목 | for h in history_items.items / if h.request | 링크 이동: /portal/requests/{{ h.request.id }} | `desk/templates/desk/my-assets.html:3` |
| UI-MY_ASSETS-E007 · 다음 이력 → | a / 별도 입력 제약 없음/조회 항목 | if history_items.next_cursor | 링크 이동: ?cursor={{ history_items.next_cursor\|urlencode }} | `desk/templates/desk/my-assets.html:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
