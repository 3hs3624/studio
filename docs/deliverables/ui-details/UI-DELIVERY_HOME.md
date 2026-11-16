# UI-DELIVERY_HOME · IT자원 업무 홈

진입/사용: /systems/asset, /systems/resource, /systems/service

소스: `desk/templates/desk/delivery-home.html`

연결: `desk/base.html`, `desk/delivery-overview.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.system_home [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
