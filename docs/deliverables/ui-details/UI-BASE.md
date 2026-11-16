# UI-BASE · 공통 셸·상단·사이드바·내 정보

진입/사용: /, /account/security, /activate/<str:uid>/, /approvals, /assets, /assets/<uuid:id>, /assets/new, /catalog, /catalog/items/<uuid:id>, /cis, /cis/<uuid:id>, /contracts, /inventory, /inventory/movements, /login/mfa/, /my-assets, /notifications, /portal/incidents, /portal/incidents/<uuid:id>, /portal/incidents/new, /portal/requests, /portal/requests/<uuid:id>, /processes, /processes/<uuid:id>, /procurement/orders, /procurement/orders/<uuid:id>, /procurement/requisitions, /procurement/requisitions/<uuid:id>, /resources/changes, /resources/changes/<uuid:id>, /resources/deployments, /resources/deployments/<uuid:id>, /systems/asset, /systems/resource, /systems/service, /work/incidents, /work/incidents/<uuid:id>, /work/requests

소스: `desk/templates/desk/base.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): views.context [code.write, delivery.read, entity.write, iam.manage, plugin.configure, plugin.execute, security.manage, users.manage]

## 기능/폼 계약

### UI-BASE-F01

UI-BASE-F01 · 폼 · post /logout/ / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-BASE-E014

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-BASE-E001 · 본문으로 이동 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: #main | `desk/templates/desk/base.html:5` |
| UI-BASE-E002 · 업무 포털 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: / | `desk/templates/desk/base.html:6` |
| UI-BASE-E003 · ⌂ 통합 홈 ↗ | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 링크 이동: / | `desk/templates/desk/base.html:7` |
| UI-BASE-E004 · {{ link.label }} › | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated / for group in nav_groups / for link in group.links | 링크 이동: {{ link.url }} | `desk/templates/desk/base.html:9` |
| UI-BASE-E005 · {{ link.label }} {{ unread_notifications }} | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated / for link in common_links | 링크 이동: {{ link.url }} | `desk/templates/desk/base.html:10` |
| UI-BASE-E006 · 메뉴 닫기 | button / type=button; aria-label=메뉴 닫기 | 해당 화면/공통 영역 표시 시 | 클라이언트 조작: 메뉴 닫기 | `desk/templates/desk/base.html:12` |
| UI-BASE-E007 · 메뉴 열기 | button / type=button; aria-label=메뉴 열기; aria-controls=primary-navigation; aria-expanded=false | if user.is_authenticated | 클라이언트 조작: 메뉴 열기 | `desk/templates/desk/base.html:13` |
| UI-BASE-E008 · 통합 ITSM | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 링크 이동: / | `desk/templates/desk/base.html:13` |
| UI-BASE-E009 · {{ app.name }} | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated / for app in systems | 링크 이동: {{ app.url }} | `desk/templates/desk/base.html:13` |
| UI-BASE-E010 · 운영 콘솔 새 탭 열기 | a / aria-label=운영 콘솔 새 탭 열기 | if user.is_authenticated / if can_console and not console_mode | 링크 이동: /console | `desk/templates/desk/base.html:13` |
| UI-BASE-E011 · 내 계정 보안 | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 링크 이동: /account/security | `desk/templates/desk/base.html:13` |
| UI-BASE-E012 · 알림 {{ unread_notifications }} | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 링크 이동: /notifications | `desk/templates/desk/base.html:13` |
| UI-BASE-E013 · {{ actor.display_name }} | button / type=button | if user.is_authenticated | 클라이언트 조작: {{ actor.display_name }} | `desk/templates/desk/base.html:13` |
| UI-BASE-E014 · 로그아웃 | submit / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 폼 제출: submit → /logout/ / /logout/ | `desk/templates/desk/base.html:13` |
| UI-BASE-E015 · 입력 항목 | p / 별도 입력 제약 없음/조회 항목 | if password_notice | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/base.html:14` |
| UI-BASE-E016 · 비밀번호 변경 | a / 별도 입력 제약 없음/조회 항목 | if password_notice | 링크 이동: /account/security | `desk/templates/desk/base.html:14` |
| UI-BASE-E017 · 통합 포털 | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 링크 이동: / | `desk/templates/desk/base.html:14` |
| UI-BASE-E018 · 닫기 | button / type=button | if user.is_authenticated | 클라이언트 조작: 닫기 | `desk/templates/desk/base.html:14` |
| UI-BASE-E019 · data-profile-content | div / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/base.html:14` |
| UI-BASE-E020 · 비밀번호 변경·내 계정 보안 | a / 별도 입력 제약 없음/조회 항목 | if user.is_authenticated | 링크 이동: /account/security | `desk/templates/desk/base.html:14` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
