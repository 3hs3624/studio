# UI-JS_PROCESS · 프로세스 동적 항목·노드·권한 편집

진입/사용: 공통/동적 컴포넌트: 

소스: `desk/static/desk/process-editor.js`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): 포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용

## 기능/폼 계약

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-JS_PROCESS-E001 · 그룹 표시·입력 | 선택 / data-key=groupMode | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 groupMode 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:35` |
| UI-JS_PROCESS-E002 · 그룹 조회 역할 | 선택 / data-key=groupReadRoles | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 groupReadRoles 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:35` |
| UI-JS_PROCESS-E003 · 그룹 입력 역할 | 선택 / data-key=groupWriteRoles | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 groupWriteRoles 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:35` |
| UI-JS_PROCESS-E004 · 표시·입력 | 선택 / data-key=fieldMode | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 fieldMode 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:38` |
| UI-JS_PROCESS-E005 · 이 태스크에서 필수 | 체크 / data-key=fieldRequired | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 fieldRequired 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:39` |
| UI-JS_PROCESS-E006 · 조회 역할 · 미선택은 제한 없음 | 선택 / data-key=fieldReadRoles | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 fieldReadRoles 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:39` |
| UI-JS_PROCESS-E007 · 입력 역할 · 미선택은 제한 없음 | 선택 / data-key=fieldWriteRoles | WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우 | 선택 노드/그룹/필드의 fieldWriteRoles 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:39` |
| UI-JS_PROCESS-E008 · 식별자 | 입력 / data-key=key | 편집기 열림·해당 대상 선택 시 | 선택 노드/그룹/필드의 key 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:71` |
| UI-JS_PROCESS-E009 · 이름 | 입력 / data-key=label | 편집기 열림·해당 대상 선택 시 | 선택 노드/그룹/필드의 label 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:71` |
| UI-JS_PROCESS-E010 · 노드 유형 | 선택 / data-key=type | 편집기 열림·해당 대상 선택 시 | 선택 노드/그룹/필드의 type 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:72` |
| UI-JS_PROCESS-E011 · 복수 담당자 처리 | 선택 / data-key=mode | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 mode 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:73` |
| UI-JS_PROCESS-E012 · 게시 API 버전 | 선택 / data-key=api_version_id | WORKFLOW에서 노드 유형 API일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 api_version_id 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:76` |
| UI-JS_PROCESS-E013 · 하위·이관 프로세스 또는 독립 결재 버전 | 선택 / data-key=version_id | WORKFLOW에서 노드 유형 APPROVAL,SUBPROCESS,TRANSFER일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 version_id 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:77` |
| UI-JS_PROCESS-E014 · 하위 작업 수 | 입력 / data-key=count | WORKFLOW에서 노드 유형 SUBPROCESS일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 count 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:77` |
| UI-JS_PROCESS-E015 · 하위 작업 수를 정하는 숫자 항목 | 입력 / data-key=count_field | WORKFLOW에서 노드 유형 SUBPROCESS일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 count_field 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:77` |
| UI-JS_PROCESS-E016 · 하위 입력 매핑 · 하위항목=상위항목 | 입력 / data-key=input_mapping | WORKFLOW에서 노드 유형 SUBPROCESS,TRANSFER,API일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 input_mapping 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:78` |
| UI-JS_PROCESS-E017 · 하위 결과 매핑 · 상위항목=하위항목 | 입력 / data-key=output_mapping | WORKFLOW에서 노드 유형 SUBPROCESS,API일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 output_mapping 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:78` |
| UI-JS_PROCESS-E018 · 이 태스크의 결재선 버전 | 선택 / data-key=approval_version_id | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 approval_version_id 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:79` |
| UI-JS_PROCESS-E019 · 결재 시점 | 선택 / data-key=approval_timing | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. 결재선 버전을 선택한 경우만 표시. | 선택 노드/그룹/필드의 approval_timing 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:79` |
| UI-JS_PROCESS-E020 · 별도 화면 버전 · 비우면 공통 화면 | 선택 / data-key=screen_version_id | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 screen_version_id 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:80` |
| UI-JS_PROCESS-E021 · 조건 데이터 항목 | 입력 / data-key=conditionField | WORKFLOW에서 노드 유형 CONDITION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 conditionField 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:81` |
| UI-JS_PROCESS-E022 · 조건 연산자 | 선택 / data-key=conditionOp | WORKFLOW에서 노드 유형 CONDITION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 conditionOp 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:81` |
| UI-JS_PROCESS-E023 · 비교 값 · 목록은 쉼표 / 논리는 true·false | 입력 / data-key=conditionValue | WORKFLOW에서 노드 유형 CONDITION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 conditionValue 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:81` |
| UI-JS_PROCESS-E024 · 대기 시간 · 초 | 입력 / data-key=wait_seconds | WORKFLOW에서 노드 유형 WAIT일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 wait_seconds 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:82` |
| UI-JS_PROCESS-E025 · 데이터 동작 | 선택 / data-key=action | WORKFLOW에서 노드 유형 ACTION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 선택 노드/그룹/필드의 action 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:82` |
| UI-JS_PROCESS-E026 · 설정할 데이터 항목 | 입력 / data-key=field | WORKFLOW에서 노드 유형 ACTION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. ACTION 동작 SET_FIELD일 때만 표시. | 선택 노드/그룹/필드의 field 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:82` |
| UI-JS_PROCESS-E027 · 설정 값 | 입력 / data-key=value | WORKFLOW에서 노드 유형 ACTION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. ACTION 동작 SET_FIELD일 때만 표시. | 선택 노드/그룹/필드의 value 설정 갱신; 초안 저장 시 그래프 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js:82` |
| UI-JS_PROCESS-E028 · 다음 노드 | 선택 / data-key=next | WORKFLOW에서 노드 유형 TASK,START,JOIN,APPROVAL,WAIT,SUBPROCESS,API,ACTION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 존재하는 단계 이름으로 선택 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E029 · 반려 시 노드 | 선택 / data-key=reject | WORKFLOW에서 노드 유형 TASK,APPROVAL일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 미지정 시 반려 종료 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E030 · 조건 참 경로 | 선택 / data-key=true | WORKFLOW에서 노드 유형 CONDITION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | CONDITION 노드 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E031 · 조건 거짓 경로 | 선택 / data-key=false | WORKFLOW에서 노드 유형 CONDITION일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | CONDITION 노드 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E032 · 병렬 시작 노드 | 입력 / data-key=branches | WORKFLOW에서 노드 유형 PARALLEL일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 쉼표 구분, 연결 대상 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E033 · 병렬 합류 노드 | 선택 / data-key=join | WORKFLOW에서 노드 유형 PARALLEL일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | PARALLEL의 합류 대상 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E034 · 담당자 선택 방식 | 선택 / data-key=selectorKind | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | USER/ROLE/GROUP/DEPARTMENT/STARTER/FIELD_USER / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E035 · 담당자 대상 | 다중선택 / data-key=selectorIds | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. | 방식에 맞는 조직 내 대상; FIELD_USER는 사용자형 데이터 필드 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E036 · 하위 부서 포함 | 체크 / data-key=selectorChildren | WORKFLOW에서 노드 유형 TASK일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용. 담당자 방식 DEPARTMENT일 때만 표시. | DEPARTMENT에서만 표시 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E037 · 항목 식별자 | 입력 / data-key=field.key | 편집기 열림·해당 대상 선택 시 | 고유 키 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E038 · 항목 표시 이름 | 입력 / data-key=field.label | 편집기 열림·해당 대상 선택 시 | 필수 표시 이름 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E039 · 항목 유형 | 선택 / data-key=field.type | 편집기 열림·해당 대상 선택 시 | 화면 논리 유형18개 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E040 · 항목 필수 | 체크 / data-key=field.required | 편집기 열림·해당 대상 선택 시 | 서버 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E041 · 담당자 선택 그룹 | 선택 / data-key=field.group_id | 편집기 열림·해당 대상 선택 시 | 사용자형 필드만 적용 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E042 · 항목 조회 전용 | 체크 / data-key=field.readonly | 편집기 열림·해당 대상 선택 시 | 화면 전체 조회 전용 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E043 · 항목 제거 | 버튼 / data-key=field.remove | 편집기 열림·해당 대상 선택 시 | 현재 항목표에서 제거 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E044 · 단계 삭제 | 버튼 / data-key=node.remove | 편집기 열림·해당 대상 선택 시 | 단계 제거; 남은 참조는 게시 전 검증 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E045 · 단계 목록 선택 | 버튼 / data-key=node.pick | 편집기 열림·해당 대상 선택 시 | 선택한 단계만 편집 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E046 · 흐름도 상자 | 클릭/드래그 / data-key=node.svg | 편집기 열림·해당 대상 선택 시 | 단계 선택·좌표 이동; Enter/Space 선택 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |
| UI-JS_PROCESS-E047 · 필드 규칙 갱신 | 버튼 / data-key=rules.refresh | 편집기 열림·해당 대상 선택 시 | 공통 화면·데이터 항목을 기준으로 규칙 다시 표시 / 클라이언트 편집 상태 → 초안 저장 시 서버 검증 | `desk/static/desk/process-editor.js` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
