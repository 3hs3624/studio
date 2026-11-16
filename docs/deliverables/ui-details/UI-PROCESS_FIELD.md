# UI-PROCESS_FIELD · 태스크 동적 입력 필드

진입/사용: 공통/동적 컴포넌트: UI-PROCESS_FIELDS

소스: `desk/templates/desk/process-field.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PROCESS_FIELD-E001 · {{ field.label }} * | select / data-process-input={{ field.key }}; required / required는 field.required일 때 적용 | elif field.type == 'person' (앞 분기 제외) / 선택값: =담당자 선택; {{ option.id }}={{ option.name }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/process-field.html:1` |
| UI-PROCESS_FIELD-E002 · {{ field.label }} * | select / data-process-input={{ field.key }}; required / required는 field.required일 때 적용 | elif field.type == 'boolean' (앞 분기 제외) / 선택값: =선택; true=예; false=아니오 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/process-field.html:1` |
| UI-PROCESS_FIELD-E003 · {{ field.label }} * | textarea / data-process-input={{ field.key }}; required; maxlength={{ field.max_length\|default:65535 }} / required는 field.required일 때 적용 | elif field.type == 'textarea' or field.type == 'json' or field.type == 'entityset' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/process-field.html:1` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
