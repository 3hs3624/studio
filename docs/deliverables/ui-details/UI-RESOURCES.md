# UI-RESOURCES · 구성항목 · CI IT 자산

진입/사용: /cis, /cis/<uuid:id>

소스: `desk/templates/desk/resources.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.inventory [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-RESOURCES-F01

UI-RESOURCES-F01 · 폼 · 원본 참조 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-RESOURCES-E001, UI-RESOURCES-E002

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-RESOURCES-E001 · 이름 검색 | text / name=q; id=q; maxlength=200; value={{ q }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E002 · 검색 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit →  | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E003 · 번호 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E004 · 이름 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E005 · 유형 모델 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E006 · 상태 위치 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E007 · {{ item.name }} | a / 별도 입력 제약 없음/조회 항목 | for item in items | 링크 이동:  /cis /assets /{{ item.id }} | `desk/templates/desk/resources.html:1` |
| UI-RESOURCES-E008 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?q={{ q\|urlencode }}&cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/resources.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
