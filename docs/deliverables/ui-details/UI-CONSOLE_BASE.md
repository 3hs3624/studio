# UI-CONSOLE_BASE · 운영 콘솔 공통 셸

진입/사용: /console

소스: `desk/templates/desk/console-base.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.context [code.write, delivery.read, entity.write, iam.manage, plugin.configure, plugin.execute, security.manage, users.manage]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CONSOLE_BASE-E001 · 운영 콘솔 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console | `desk/templates/desk/console-base.html:4` |
| UI-CONSOLE_BASE-E002 · 콘솔 홈 › | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console | `desk/templates/desk/console-base.html:6` |
| UI-CONSOLE_BASE-E003 · {{ link.label }} › | a / 별도 입력 제약 없음/조회 항목 | for group in console_groups / for link in group.links | 링크 이동: {{ link.url }} | `desk/templates/desk/console-base.html:7` |
| UI-CONSOLE_BASE-E004 · 운영 콘솔 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console | `desk/templates/desk/console-base.html:11` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
