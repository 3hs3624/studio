# UI-JS_DESIGNER · 디자이너 동적 캔버스 조작

진입/사용: 공통/동적 컴포넌트: 

소스: `desk/static/desk/screen-designer.js`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-JS_DESIGNER-E001 · 그룹 목록/제목 선택 | 버튼 / data-key=group.choose | 편집기 열림·해당 대상 선택 시 | 추가 버튼과 별개; 선택 그룹과 속성 영역 변경 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E002 · 그룹 탭 선택 | 탭 / data-key=group.tab | 편집기 열림·해당 대상 선택 시 | 탭 표시 모드에서 대상 그룹으로 전환; 드롭 대상 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E003 · 캔버스 필드 선택 | 클릭 / data-key=field.select | 편집기 열림·해당 대상 선택 시 | 선택 표시·빠른 속성 갱신 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E004 · 필드 드래그 이동 | 드래그 / data-key=field.drag | 편집기 열림·해당 대상 선택 시 | 그룹 내 순서 또는 그룹 간 이동; 실행 취소 가능 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E005 · 필드 크기 핸들 | 드래그 / data-key=field.resize | 편집기 열림·해당 대상 선택 시 | 너비1~화면열수, 높이1~5, 48px 단위 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E006 · 우클릭/더블클릭 속성 | 마우스 / data-key=field.context | 편집기 열림·해당 대상 선택 시 | 선택 필드의 상세 속성 열기 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E007 · Ctrl+방향키 | 키보드 / data-key=field.keyboard.move | 편집기 열림·해당 대상 선택 시 | 필드 앞/뒤 이동 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E008 · Shift+방향키 | 키보드 / data-key=field.keyboard.resize | 편집기 열림·해당 대상 선택 시 | 너비/높이 조정 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E009 · Shift+F10 | 키보드 / data-key=field.keyboard.properties | 편집기 열림·해당 대상 선택 시 | 필드 상세 속성 열기 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E010 · 미리보기 그룹 탭 | 탭/키보드 / data-key=preview.tabs | 편집기 열림·해당 대상 선택 시 | 방향키/Home/End 전환; 미리보기 입력값은 저장 안 함 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E011 · Escape로 디자이너 종료 | 키보드 / data-key=dialog.escape | 편집기 열림·해당 대상 선택 시 | 미적용 편집 취소 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/screen-designer.js` |
| UI-JS_DESIGNER-E012 · 문자 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.text | 편집기 열림·해당 대상 선택 시 | 문자 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=text; 분류=문자열 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E013 · 긴 문자 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.textarea | 편집기 열림·해당 대상 선택 시 | 긴 문자 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=textarea; 분류=문자열 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E014 · 정수 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.integer | 편집기 열림·해당 대상 선택 시 | 정수 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=integer; 분류=숫자 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E015 · 실수 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.number | 편집기 열림·해당 대상 선택 시 | 실수 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=number; 분류=숫자 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E016 · 고정소수 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.decimal | 편집기 열림·해당 대상 선택 시 | 고정소수 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=decimal; 분류=숫자 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E017 · 논리값 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.boolean | 편집기 열림·해당 대상 선택 시 | 논리값 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=boolean; 분류=논리 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E018 · 날짜 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.date | 편집기 열림·해당 대상 선택 시 | 날짜 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=date; 분류=날짜·시간 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E019 · 날짜·시간 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.datetime | 편집기 열림·해당 대상 선택 시 | 날짜·시간 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=datetime; 분류=날짜·시간 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E020 · 시간 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.time | 편집기 열림·해당 대상 선택 시 | 시간 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=time; 분류=날짜·시간 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E021 · 연월 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.month | 편집기 열림·해당 대상 선택 시 | 연월 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=month; 분류=날짜·시간 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E022 · 연도 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.year | 편집기 열림·해당 대상 선택 시 | 연도 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=year; 분류=날짜·시간 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E023 · JSON 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.json | 편집기 열림·해당 대상 선택 시 | JSON 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=json; 분류=구조화 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E024 · JSON 목록 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.entityset | 편집기 열림·해당 대상 선택 시 | JSON 목록 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=entityset; 분류=구조화 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E025 · 사용자 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.person | 편집기 열림·해당 대상 선택 시 | 사용자 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=person; 분류=연결 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E026 · UUID 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.uuid | 편집기 열림·해당 대상 선택 시 | UUID 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=uuid; 분류=문자열 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E027 · 이메일 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.email | 편집기 열림·해당 대상 선택 시 | 이메일 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=email; 분류=문자열 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E028 · 전화번호 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.phone | 편집기 열림·해당 대상 선택 시 | 전화번호 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=phone; 분류=문자열 | `desk/data_types.py:12` |
| UI-JS_DESIGNER-E029 · URL 필드 추가 | 아이콘 버튼/드래그 / data-key=palette.url | 편집기 열림·해당 대상 선택 시 | URL 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 / 유형=url; 분류=문자열 | `desk/data_types.py:12` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
