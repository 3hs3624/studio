# UI-SCREEN_DESIGNER · 화면 디자이너·필드 속성·미리보기

진입/사용: /console/approval-lines, /console/approval-lines/<uuid:id>, /console/approval-lines/new, /console/screens, /console/screens/<uuid:id>, /console/screens/new, /console/workflows, /console/workflows/<uuid:id>, /console/workflows/new

소스: `desk/templates/desk/screen-designer.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

### UI-SCREEN_DESIGNER-F01

UI-SCREEN_DESIGNER-F01 · 폼 · 원본 참조 현재 화면 / 네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.

항목: UI-SCREEN_DESIGNER-E027, UI-SCREEN_DESIGNER-E028, UI-SCREEN_DESIGNER-E029, UI-SCREEN_DESIGNER-E030, UI-SCREEN_DESIGNER-E031, UI-SCREEN_DESIGNER-E032, UI-SCREEN_DESIGNER-E033, UI-SCREEN_DESIGNER-E034, UI-SCREEN_DESIGNER-E035, UI-SCREEN_DESIGNER-E036, UI-SCREEN_DESIGNER-E037, UI-SCREEN_DESIGNER-E038, UI-SCREEN_DESIGNER-E039, UI-SCREEN_DESIGNER-E040, UI-SCREEN_DESIGNER-E041, UI-SCREEN_DESIGNER-E042, UI-SCREEN_DESIGNER-E043, UI-SCREEN_DESIGNER-E044

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-SCREEN_DESIGNER-E001 · 그룹 표시 | select / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 / 선택값: sections=그룹 나열; tabs=탭 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E002 · 열 수 | select / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 / 선택값: 1=1; 2=2; 3=3 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E003 · 실행 취소 | button / type=button | 해당 화면/공통 영역 표시 시 | 최근 편집 이전 상태로 복원; 실행 취소 이력이 없으면 비활성 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E004 · 다시 실행 | button / type=button | 해당 화면/공통 영역 표시 시 | 실행 취소한 다음 상태 복원; 다시 실행 이력 없으면 비활성 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E005 · 화면 미리보기 | button / type=button | 해당 화면/공통 영역 표시 시 | 편집 중 배치를 별도 미리보기 모달에 표시; 입력값 저장 안 함 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E006 · 취소·닫기 | button / type=button | 해당 화면/공통 영역 표시 시 | 미적용 변경을 버리고 디자이너 닫기 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E007 · 적용하고 닫기 | button / type=button | 해당 화면/공통 영역 표시 시 | 현재 배치를 항목표에 반영하고 닫기; 서버 저장은 별도 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E008 · 초안 저장 | button / type=button | 해당 화면/공통 영역 표시 시 | 사유와 배치를 원래 화면 저장 폼으로 전달해 초안 저장·검증 | `desk/templates/desk/screen-designer.html:2` |
| UI-SCREEN_DESIGNER-E009 · 저장 사유 | text / maxlength=500; placeholder=변경한 내용을 간단히 입력하십시오. | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:3` |
| UI-SCREEN_DESIGNER-E010 · data-designer-status | span / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/screen-designer.html:3` |
| UI-SCREEN_DESIGNER-E011 · data-designer-error | p / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/screen-designer.html:3` |
| UI-SCREEN_DESIGNER-E012 · 필드 검색 | search / type=search; placeholder=문자, 숫자, 날짜… | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:4` |
| UI-SCREEN_DESIGNER-E013 · {{ type.icon }} {{ type.label }} | button / type=button | for type in process_field_types | 선택 그룹에 해당 논리 유형 필드 추가; 드래그 시 놓은 그룹/위치에 추가 | `desk/templates/desk/screen-designer.html:4` |
| UI-SCREEN_DESIGNER-E014 · ＋ 그룹 추가 | button / type=button | 해당 화면/공통 영역 표시 시 | 고유 그룹 키로 새 그룹 추가 후 선택 | `desk/templates/desk/screen-designer.html:4` |
| UI-SCREEN_DESIGNER-E015 · 그룹 이름 | text / maxlength=100 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E016 · 그룹 삭제·필드 이동 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 그룹 삭제; 포함 필드는 남은 그룹으로 이동 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E017 · 표시 이름 | text / data-quick=label; maxlength=100 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E018 · 너비 · 열 | number / data-quick=span; type=number; min=1; max=3 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E019 · 높이 · 단 | number / data-quick=height; type=number; min=1; max=5 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E020 · 필수 입력 | checkbox / data-quick=required; type=checkbox | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E021 · 조회 전용 | checkbox / data-quick=readonly; type=checkbox | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E022 · 유형·상세 속성 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 필드 상세 속성 모달 열기 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E023 · 앞으로 이동 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 필드를 앞 순서로 이동 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E024 · 뒤로 이동 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 필드를 뒤 순서로 이동 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E025 · 필드 복제 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 필드를 새 식별자로 복제 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E026 · 필드 삭제 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 필드 및 배치에서 제거 | `desk/templates/desk/screen-designer.html:6` |
| UI-SCREEN_DESIGNER-E027 · data-property-error | p / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E028 · 식별자 | text / name=key; required; maxlength=40; pattern=[a-z][a-z0-9_]{0,39} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E029 · 표시 이름 | text / name=label; required; maxlength=100 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E030 · 유형 | select / name=type | 해당 화면/공통 영역 표시 시 / 선택값: {{ type.key }}={{ type.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E031 · 배치 그룹 | select / name=group | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E032 · 너비 · 차지할 열 수 | number / name=span; type=number; required; min=1; max=3 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E033 · 높이 · 48px 단위 | number / name=height; type=number; required; min=1; max=5 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E034 · 담당자 선택 범위 | select / name=group_id | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E035 · 최대 문자 수 | number / name=max_length; type=number; min=1; max=65535 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E036 · 전체 자릿수 · DECIMAL | number / name=precision; type=number; min=1; max=38 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E037 · 소수 자릿수 · DECIMAL | number / name=scale; type=number; min=0; max=18 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E038 · 설명 | text / name=description; maxlength=500 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E039 · 기본값 · JSON 표기 | text / name=default; maxlength=4000; placeholder=예: "기본값", 0, false | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E040 · 자동 기본값 | select / name=default_function | 해당 화면/공통 영역 표시 시 / 선택값: =사용 안 함; CURRENT_TIMESTAMP=현재 일시 · 날짜시간형; CURRENT_DATE=현재 날짜 · 날짜형; UUID=UUID 생성 · UUID형 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E041 · 필수 입력 | checkbox / name=required; type=checkbox | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E042 · 조회 전용 | checkbox / name=readonly; type=checkbox | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E043 · 취소 | button / type=button | 해당 화면/공통 영역 표시 시 | 속성 변경 미적용 후 닫기 | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E044 · 속성 적용 | submit / type=submit | 해당 화면/공통 영역 표시 시 | 폼 제출: submit →  | `desk/templates/desk/screen-designer.html:8` |
| UI-SCREEN_DESIGNER-E045 · data-designer-applied | p / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/screen-designer.html:9` |
| UI-SCREEN_DESIGNER-E046 · 데스크톱 | button / type=button | 해당 화면/공통 영역 표시 시 | 미리보기 데스크톱 너비로 전환 | `desk/templates/desk/screen-designer.html:11` |
| UI-SCREEN_DESIGNER-E047 · 모바일 | button / type=button | 해당 화면/공통 영역 표시 시 | 미리보기 모바일 너비로 전환 | `desk/templates/desk/screen-designer.html:11` |
| UI-SCREEN_DESIGNER-E048 · 편집으로 돌아가기 | button / type=button | 해당 화면/공통 영역 표시 시 | 미리보기 종료 후 편집 상태 복귀 | `desk/templates/desk/screen-designer.html:11` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
