# UI-ASSET_NEW · 자산 등록

진입/사용: /assets/new

소스: `desk/templates/desk/asset-new.html`

연결: `desk/base.html`

뷰·권한 참조(동시 필수 권한 목록 아님): asset_views.new [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-ASSET_NEW-F01

UI-ASSET_NEW-F01 · asset-create · POST(JSON) /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동.

항목: UI-ASSET_NEW-E002, UI-ASSET_NEW-E003, UI-ASSET_NEW-E004, UI-ASSET_NEW-E005, UI-ASSET_NEW-E006, UI-ASSET_NEW-E007, UI-ASSET_NEW-E008, UI-ASSET_NEW-E009, UI-ASSET_NEW-E010, UI-ASSET_NEW-E011

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-ASSET_NEW-E001 · ← 자산 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /assets | `desk/templates/desk/asset-new.html:1` |
| UI-ASSET_NEW-E002 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:3` |
| UI-ASSET_NEW-E003 · 자산번호 | text / name=asset_no; id=asset-no; required; maxlength=80 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:4` |
| UI-ASSET_NEW-E004 · 자산 이름 | text / name=name; id=asset-name; required; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:4` |
| UI-ASSET_NEW-E005 · 제조사 | text / name=manufacturer; id=manufacturer; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:5` |
| UI-ASSET_NEW-E006 · 모델 | text / name=model; id=asset-model; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:5` |
| UI-ASSET_NEW-E007 · 일련번호 | text / name=serial_number; id=serial-number; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:6` |
| UI-ASSET_NEW-E008 · 보관 위치 | text / name=location; id=asset-location; required; maxlength=200 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:6` |
| UI-ASSET_NEW-E009 · 등록 사유 | textarea / name=reason; id=registration-reason; required; maxlength=10000 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:7` |
| UI-ASSET_NEW-E010 · 조직 직원에게 기본 자산 정보 공개 | checkbox / name=portal_visible; type=checkbox | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:8` |
| UI-ASSET_NEW-E011 · 자산 등록 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: asset-create → /api/v1/assets / /api/v1/assets / 자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동. | `desk/templates/desk/asset-new.html:9` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
