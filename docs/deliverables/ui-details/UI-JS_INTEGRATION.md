# UI-JS_INTEGRATION · API 동적 입력·매핑 행

진입/사용: 공통/동적 컴포넌트: 

소스: `desk/static/desk/integrations.js`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-JS_INTEGRATION-E001 · 입력 이름 | 입력 / data-key=input.key | 편집기 열림·해당 대상 선택 시 | API 입력 필드 식별자 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E002 · 입력 유형 | 선택 / data-key=input.type | 편집기 열림·해당 대상 선택 시 | text/number/boolean/json / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E003 · 입력 필수 | 체크 / data-key=input.required | 편집기 열림·해당 대상 선택 시 | 실행 시 필수 검사 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E004 · 입력 행 제거 | 버튼 / data-key=input.remove | 편집기 열림·해당 대상 선택 시 | 현재 API 초안에서 행 제거 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E005 · 결과 이름 | 입력 / data-key=mapping.key | 편집기 열림·해당 대상 선택 시 | 중복 이름 거부 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E006 · 응답 경로 | 입력 / data-key=mapping.path | 편집기 열림·해당 대상 선택 시 | 매핑할 원본 경로 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E007 · 변환 방식 | 선택 / data-key=mapping.transform | 편집기 열림·해당 대상 선택 시 | COPY/STRING/NUMBER/BOOLEAN/TRIM/UPPER/LOWER/DATE / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E008 · 결과 필수 | 체크 / data-key=mapping.required | 편집기 열림·해당 대상 선택 시 | 필수 경로 누락 시 매핑 실패 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |
| UI-JS_INTEGRATION-E009 · 결과 행 제거 | 버튼 / data-key=mapping.remove | 편집기 열림·해당 대상 선택 시 | 현재 매핑 행만 제거 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/integrations.js:3` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
