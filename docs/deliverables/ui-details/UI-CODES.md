# UI-CODES · 공통코드 관리

진입/사용: /console/codes, /console/codes/<uuid:id>

소스: `desk/templates/desk/codes.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): views.common_code_management [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-CODES-F01

UI-CODES-F01 · code-group · POST(JSON) /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사.

항목: UI-CODES-E007, UI-CODES-E008, UI-CODES-E009, UI-CODES-E010, UI-CODES-E011, UI-CODES-E012, UI-CODES-E013

### UI-CODES-F02

UI-CODES-F02 · code-items · POST(JSON) /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사.

항목: UI-CODES-E014, UI-CODES-E015, UI-CODES-E016, UI-CODES-E017, UI-CODES-E018, UI-CODES-E019, UI-CODES-E020, UI-CODES-E021, UI-CODES-E022, UI-CODES-E023, UI-CODES-E024, UI-CODES-E025, UI-CODES-E026, UI-CODES-E027, UI-CODES-E028

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-CODES-E001 · 코드 그룹 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/codes | `desk/templates/desk/codes.html:4` |
| UI-CODES-E002 · 그룹 코드 | th / 별도 입력 제약 없음/조회 항목 | if not code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:5` |
| UI-CODES-E003 · 이름 | th / 별도 입력 제약 없음/조회 항목 | if not code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:5` |
| UI-CODES-E004 · 사용 여부 | th / 별도 입력 제약 없음/조회 항목 | if not code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:5` |
| UI-CODES-E005 · 관리 범위 | th / 별도 입력 제약 없음/조회 항목 | if not code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:5` |
| UI-CODES-E006 · {{ item.code }} | a / 별도 입력 제약 없음/조회 항목 | if not code_group / for item in code_groups | 링크 이동: /console/codes/{{ item.id }} | `desk/templates/desk/codes.html:5` |
| UI-CODES-E007 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E008 · 그룹 코드 | text / name=code; required; readonly; maxlength=40; pattern=[A-Z][A-Z0-9_]{0,39}; value={{ code_group.code }} / readonly는 code_group일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E009 · 이름 | text / name=name; required; maxlength=100; value={{ code_group.name }} | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E010 · 설명 | text / name=description; maxlength=500; value={{ code_group.description }} | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E011 · 사용 | checkbox / name=active; type=checkbox; checked / checked는 not code_group or code_group.active일 때 적용 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E012 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E013 · 그룹 저장 그룹 생성 | submit / type=submit | else (앞 분기 제외) | 폼 제출: code-group → /api/v1/admin/code-groups /{{ code_group.id }}  / /api/v1/admin/code-groups /{{ code_group.id }}  / 조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사. | `desk/templates/desk/codes.html:8` |
| UI-CODES-E014 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E015 · 코드 | th / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E016 · 표시 이름 | th / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E017 · 설명 | th / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E018 · 순서 | th / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E019 · 사용 | th / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E020 · 행 | th / 별도 입력 제약 없음/조회 항목 | if code_group / if not code_group.locked | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E021 · 코드 | text / required; readonly; value={{ item.code }}; aria-label=코드 | if code_group / if not code_group.locked / for item in code_data.items | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E022 · 표시 이름 | text / required; maxlength=100; value={{ item.label }}; aria-label=표시 이름 | if code_group / if not code_group.locked / for item in code_data.items | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E023 · 설명 | text / maxlength=500; value={{ item.description }}; aria-label=설명 | if code_group / if not code_group.locked / for item in code_data.items | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E024 · 정렬 순서 | number / type=number; required; min=0; max=99999; step=1; value={{ item.sort_order }}; aria-label=정렬 순서 | if code_group / if not code_group.locked / for item in code_data.items | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E025 · 사용 여부 | checkbox / type=checkbox; checked; aria-label=사용 여부 / checked는 item.active일 때 적용 | if code_group / if not code_group.locked / for item in code_data.items | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E026 · 코드 추가 | button / id=add-common-code; type=button | if code_group / if not code_group.locked | 클라이언트 조작: 코드 추가 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E027 · 변경 사유 | text / name=reason; required; maxlength=500 | if code_group / if not code_group.locked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E028 · 코드 저장 | submit / type=submit | if code_group / if not code_group.locked | 폼 제출: code-items → /api/v1/admin/code-groups/{{ code_group.id }}/items / /api/v1/admin/code-groups/{{ code_group.id }}/items / 행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사. | `desk/templates/desk/codes.html:10` |
| UI-CODES-E029 · 코드 | text / required; maxlength=40; pattern=[A-Z][A-Z0-9_]{0,39}; aria-label=코드 | if code_group / if not code_group.locked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/codes.html:11` |
| UI-CODES-E030 · 표시 이름 | text / required; maxlength=100; aria-label=표시 이름 | if code_group / if not code_group.locked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/codes.html:11` |
| UI-CODES-E031 · 설명 | text / maxlength=500; aria-label=설명 | if code_group / if not code_group.locked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/codes.html:11` |
| UI-CODES-E032 · 정렬 순서 | number / type=number; required; min=0; max=99999; step=1; value=0; aria-label=정렬 순서 | if code_group / if not code_group.locked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/codes.html:11` |
| UI-CODES-E033 · 사용 여부 | checkbox / type=checkbox; checked; aria-label=사용 여부 | if code_group / if not code_group.locked | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/codes.html:11` |
| UI-CODES-E034 · 취소 | button / type=button | if code_group / if not code_group.locked | 클라이언트 조작: 취소 | `desk/templates/desk/codes.html:11` |
| UI-CODES-E035 · 코드 | th / 별도 입력 제약 없음/조회 항목 | if code_group / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:12` |
| UI-CODES-E036 · 표시 이름 | th / 별도 입력 제약 없음/조회 항목 | if code_group / else (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:12` |
| UI-CODES-E037 · {{ item.code }} · {{ item.name }} | a / 별도 입력 제약 없음/조회 항목 | if code_group / for item in code_usage | 링크 이동: /console/entities/{{ item.id }} | `desk/templates/desk/codes.html:13` |
| UI-CODES-E038 · 일시 | th / 별도 입력 제약 없음/조회 항목 | if code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:14` |
| UI-CODES-E039 · 변경자 | th / 별도 입력 제약 없음/조회 항목 | if code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:14` |
| UI-CODES-E040 · 구성 버전 | th / 별도 입력 제약 없음/조회 항목 | if code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:14` |
| UI-CODES-E041 · 변경 사유 | th / 별도 입력 제약 없음/조회 항목 | if code_group | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/codes.html:14` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
