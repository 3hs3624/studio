# UI-CATALOG · 필요한 서비스를 신청하십시오.

진입/사용: /catalog

소스: `desk/templates/desk/catalog.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.catalog_listing [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-CATALOG-F01

UI-CATALOG-F01 · 폼 · 원본 참조 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-CATALOG-E001, UI-CATALOG-E002

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CATALOG-E001 · 서비스 검색 | text / name=q; id=catalog-q; maxlength=200; value={{ q }}; placeholder=서비스 이름 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/catalog.html:3` |
| UI-CATALOG-E002 · 검색 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: submit →  | `desk/templates/desk/catalog.html:3` |
| UI-CATALOG-E003 · {{ item.code }} {{ item.name }} {{ item.description\|truncatechars:140 }} 워크플로우 처리 승인 필요 바로 접수 신청하기 → | a / 별도 입력 제약 없음/조회 항목 | for item in items | 링크 이동: /catalog/items/{{ item.id }} | `desk/templates/desk/catalog.html:4` |
| UI-CATALOG-E004 · 다음 페이지 → | a / 별도 입력 제약 없음/조회 항목 | if next_cursor | 링크 이동: ?q={{ q\|urlencode }}&cursor={{ next_cursor\|urlencode }} | `desk/templates/desk/catalog.html:5` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
