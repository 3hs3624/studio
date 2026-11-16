# UI-DELIVERY_OVERVIEW · IT자원 요약 현황

진입/사용: /, /systems/asset, /systems/resource, /systems/service

소스: `desk/templates/desk/delivery-overview.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-DELIVERY_OVERVIEW-E001 · {{ metric.label }} {{ metric.value }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for metric in delivery_metrics | 링크 이동: {{ metric.url }} | `desk/templates/desk/delivery-overview.html:3` |
| UI-DELIVERY_OVERVIEW-E002 · 전체 보기 → | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 링크 이동: /resources/changes | `desk/templates/desk/delivery-overview.html:6` |
| UI-DELIVERY_OVERVIEW-E003 · 저장소 · 브랜치 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E004 · 변경 제목 · PR/커밋 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E005 · 변경 계정 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E006 · 검토 상태 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E007 · 빌드 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E008 · 변경일 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E009 · {{ item.title }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for item in delivery_changes | 링크 이동: {{ item.detail_url }} | `desk/templates/desk/delivery-overview.html:7` |
| UI-DELIVERY_OVERVIEW-E010 · 전체 보기 → | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 링크 이동: /resources/deployments | `desk/templates/desk/delivery-overview.html:8` |
| UI-DELIVERY_OVERVIEW-E011 · 서비스 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:9` |
| UI-DELIVERY_OVERVIEW-E012 · 배포 버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:9` |
| UI-DELIVERY_OVERVIEW-E013 · 대상 환경 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:9` |
| UI-DELIVERY_OVERVIEW-E014 · 승인·실행 상태 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:9` |
| UI-DELIVERY_OVERVIEW-E015 · 배포 계정 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:9` |
| UI-DELIVERY_OVERVIEW-E016 · 배포일 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/delivery-overview.html:9` |
| UI-DELIVERY_OVERVIEW-E017 · {{ item.service }} | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / for item in delivery_deployments | 링크 이동: {{ item.detail_url }} | `desk/templates/desk/delivery-overview.html:9` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
