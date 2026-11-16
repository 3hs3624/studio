# UI-INTEGRATIONS · API · 데이터 연계 관리

진입/사용: /console/integrations, /console/integrations/<uuid:id>

소스: `desk/templates/desk/integrations.html`

연결: 

뷰·권한 참조(동시 필수 권한 목록 아님): integration_views.manage [integration.manage]

## 기능/폼 계약

### UI-INTEGRATIONS-F01

UI-INTEGRATIONS-F01 · save · POST(JSON) /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리.

항목: UI-INTEGRATIONS-E012, UI-INTEGRATIONS-E013, UI-INTEGRATIONS-E014, UI-INTEGRATIONS-E015, UI-INTEGRATIONS-E016, UI-INTEGRATIONS-E017, UI-INTEGRATIONS-E018, UI-INTEGRATIONS-E019, UI-INTEGRATIONS-E020, UI-INTEGRATIONS-E021, UI-INTEGRATIONS-E022, UI-INTEGRATIONS-E023, UI-INTEGRATIONS-E024, UI-INTEGRATIONS-E025, UI-INTEGRATIONS-E026, UI-INTEGRATIONS-E027, UI-INTEGRATIONS-E028, UI-INTEGRATIONS-E029, UI-INTEGRATIONS-E030, UI-INTEGRATIONS-E031, UI-INTEGRATIONS-E032, UI-INTEGRATIONS-E033, UI-INTEGRATIONS-E034, UI-INTEGRATIONS-E035, UI-INTEGRATIONS-E036, UI-INTEGRATIONS-E037, UI-INTEGRATIONS-E038

### UI-INTEGRATIONS-F02

UI-INTEGRATIONS-F02 · publish · POST(JSON) /api/v1/integrations/publish/{{ integration.id }} / 현재 API 초안 검증 후 불변 게시 버전 생성.

항목: UI-INTEGRATIONS-E045, UI-INTEGRATIONS-E046

### UI-INTEGRATIONS-F03

UI-INTEGRATIONS-F03 · invoke · POST(JSON) /api/v1/integrations/invoke/{{ integration.published_id }} / 게시 API 호출. 쓰기 API는 확인 및 멱등성 규칙 적용; 결과/작업 상태 표시.

항목: UI-INTEGRATIONS-E047, UI-INTEGRATIONS-E048, UI-INTEGRATIONS-E049, UI-INTEGRATIONS-E050

### UI-INTEGRATIONS-F04

UI-INTEGRATIONS-F04 · client · POST(JSON) /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용.

항목: UI-INTEGRATIONS-E051, UI-INTEGRATIONS-E052, UI-INTEGRATIONS-E053, UI-INTEGRATIONS-E054, UI-INTEGRATIONS-E055, UI-INTEGRATIONS-E056

### UI-INTEGRATIONS-F05

UI-INTEGRATIONS-F05 · client-stop · POST(JSON) /api/v1/integrations/client-stop/{{ client.id }} / 선택 외부 호출 클라이언트 중지; 사유 검사.

항목: UI-INTEGRATIONS-E057, UI-INTEGRATIONS-E058

### UI-INTEGRATIONS-F06

UI-INTEGRATIONS-F06 · credential · POST(JSON) /api/v1/integrations/credential / 인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함.

항목: UI-INTEGRATIONS-E065, UI-INTEGRATIONS-E066, UI-INTEGRATIONS-E067, UI-INTEGRATIONS-E068, UI-INTEGRATIONS-E069

### UI-INTEGRATIONS-F07

UI-INTEGRATIONS-F07 · network · POST(JSON) /api/v1/integrations/network / HTTPS 호스트·허용 사설 CIDR 정책 검증 후 저장.

항목: UI-INTEGRATIONS-E070, UI-INTEGRATIONS-E071, UI-INTEGRATIONS-E072, UI-INTEGRATIONS-E073

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-INTEGRATIONS-E001 · 새 API | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/integrations?new=1 | `desk/templates/desk/integrations.html:2` |
| UI-INTEGRATIONS-E002 · 코드 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:3` |
| UI-INTEGRATIONS-E003 · 이름 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:3` |
| UI-INTEGRATIONS-E004 · 방식 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:3` |
| UI-INTEGRATIONS-E005 · 게시 버전 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:3` |
| UI-INTEGRATIONS-E006 · {{ item.code }} | a / 별도 입력 제약 없음/조회 항목 | for item in integrations | 링크 이동: /console/integrations/{{ item.id }} | `desk/templates/desk/integrations.html:3` |
| UI-INTEGRATIONS-E007 · 정의·매핑 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: #definition | `desk/templates/desk/integrations.html:4` |
| UI-INTEGRATIONS-E008 · 버전·호출 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: #try | `desk/templates/desk/integrations.html:4` |
| UI-INTEGRATIONS-E009 · 실행 이력 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: #history | `desk/templates/desk/integrations.html:4` |
| UI-INTEGRATIONS-E010 · 인증정보 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: #credentials | `desk/templates/desk/integrations.html:4` |
| UI-INTEGRATIONS-E011 · 허용 호스트 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: #network | `desk/templates/desk/integrations.html:4` |
| UI-INTEGRATIONS-E012 · API 코드 | text / name=code; required; readonly; value={{ integration.code }} / readonly는 integration일 때 적용 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:6` |
| UI-INTEGRATIONS-E013 · 이름 | text / name=name; required; value={{ integration.name }} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:6` |
| UI-INTEGRATIONS-E014 · 프로토콜 | select / name=protocol | 해당 화면/공통 영역 표시 시 / 선택값: {{ key }}={{ label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:6` |
| UI-INTEGRATIONS-E015 · 실행 계정 | select / name=run_as | 해당 화면/공통 영역 표시 시 / 선택값: {{ person.id }}={{ person.user.username }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:6` |
| UI-INTEGRATIONS-E016 · 사용 | checkbox / name=active; type=checkbox; checked / checked는 not integration or integration.active일 때 적용 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:6` |
| UI-INTEGRATIONS-E017 · 변경 사유 | text / name=reason; required | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:6` |
| UI-INTEGRATIONS-E018 · HTTPS URL | text / name=url; placeholder=https://api.example.com/resources/{id} | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E019 · HTTP 메서드 | select / name=method | 해당 화면/공통 영역 표시 시 / 선택값: GET=GET; POST=POST; PUT=PUT; PATCH=PATCH; DELETE=DELETE | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E020 · 인증정보 | select / name=credential_id | 해당 화면/공통 영역 표시 시 / 선택값: =인증 없음; {{ credential.id }}={{ credential.name }} · {{ credential.auth_type }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E021 · 외부 영향 | select / name=effect | 해당 화면/공통 영역 표시 시 / 선택값: READ=조회; WRITE=변경 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E022 · 시간 제한 · 초 | number / name=timeout; type=number; min=1; max=30; value=15 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E023 · 재시도 · 회 | number / name=retries; type=number; min=0; max=3; value=0 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E024 · 대상 시스템이 Idempotency-Key를 보장함 | checkbox / name=target_idempotency; type=checkbox | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:7` |
| UI-INTEGRATIONS-E025 · 이름 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:8` |
| UI-INTEGRATIONS-E026 · 유형 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:8` |
| UI-INTEGRATIONS-E027 · 필수 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:8` |
| UI-INTEGRATIONS-E028 · 관리 열(화면 제목은 공백) | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:8` |
| UI-INTEGRATIONS-E029 · 입력 항목 추가 | button / type=button | 해당 화면/공통 영역 표시 시 | API 입력 정의 행 추가 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:8` |
| UI-INTEGRATIONS-E030 · 결과 이름 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:9` |
| UI-INTEGRATIONS-E031 · 원본 경로 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:9` |
| UI-INTEGRATIONS-E032 · 변환 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:9` |
| UI-INTEGRATIONS-E033 · 필수 | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:9` |
| UI-INTEGRATIONS-E034 · 관리 열(화면 제목은 공백) | th / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:9` |
| UI-INTEGRATIONS-E035 · 매핑 추가 | button / type=button | 해당 화면/공통 영역 표시 시 | API 응답 매핑 행 추가 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:9` |
| UI-INTEGRATIONS-E036 · 고급 프로토콜·데이터 적재 설정 | summary / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:10` |
| UI-INTEGRATIONS-E037 · 추가 설정 · JSON | textarea / name=advanced | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:10` |
| UI-INTEGRATIONS-E038 · 초안 저장 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: save → /api/v1/integrations/save /{{ integration.id }}  / /api/v1/integrations/save /{{ integration.id }}  / API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리. | `desk/templates/desk/integrations.html:10` |
| UI-INTEGRATIONS-E039 · OpenAPI 3.x / Swagger 2.0 JSON 가져오기 | summary / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음 | `desk/templates/desk/integrations.html:11` |
| UI-INTEGRATIONS-E040 · OpenAPI 문서 | textarea / aria-label=OpenAPI 문서 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/integrations.html:11` |
| UI-INTEGRATIONS-E041 · 작업 읽기 | button / type=button | 해당 화면/공통 영역 표시 시 | OpenAPI 문서 작업 목록 조회; 파싱 오류 표시 | `desk/templates/desk/integrations.html:11` |
| UI-INTEGRATIONS-E042 · 가져올 작업 | select / aria-label=가져올 작업 | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/integrations.html:11` |
| UI-INTEGRATIONS-E043 · 선택 작업을 초안에 반영 | button / type=button | 해당 화면/공통 영역 표시 시 | 선택 작업의 설정을 현재 API 초안에 가져오기; 자동 게시하지 않음 | `desk/templates/desk/integrations.html:11` |
| UI-INTEGRATIONS-E044 · data-spec-message | p / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:11` |
| UI-INTEGRATIONS-E045 · 게시 사유 | text / name=reason; required | if integration | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/publish/{{ integration.id }} / 현재 API 초안 검증 후 불변 게시 버전 생성. | `desk/templates/desk/integrations.html:13` |
| UI-INTEGRATIONS-E046 · 검증 후 새 버전 게시 | submit / 별도 입력 제약 없음/조회 항목 | if integration | 폼 제출: publish → /api/v1/integrations/publish/{{ integration.id }} / /api/v1/integrations/publish/{{ integration.id }} / 현재 API 초안 검증 후 불변 게시 버전 생성. | `desk/templates/desk/integrations.html:13` |
| UI-INTEGRATIONS-E047 · 입력 값 · JSON | textarea / name=inputs | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/invoke/{{ integration.published_id }} / 게시 API 호출. 쓰기 API는 확인 및 멱등성 규칙 적용; 결과/작업 상태 표시. | `desk/templates/desk/integrations.html:14` |
| UI-INTEGRATIONS-E048 · 외부 변경 호출임을 확인합니다. | checkbox / name=confirm_write; type=checkbox | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/invoke/{{ integration.published_id }} / 게시 API 호출. 쓰기 API는 확인 및 멱등성 규칙 적용; 결과/작업 상태 표시. | `desk/templates/desk/integrations.html:14` |
| UI-INTEGRATIONS-E049 · 실행 큐에 등록 | submit / 별도 입력 제약 없음/조회 항목 | if integration / if integration.published | 폼 제출: invoke → /api/v1/integrations/invoke/{{ integration.published_id }} / /api/v1/integrations/invoke/{{ integration.published_id }} / 게시 API 호출. 쓰기 API는 확인 및 멱등성 규칙 적용; 결과/작업 상태 표시. | `desk/templates/desk/integrations.html:14` |
| UI-INTEGRATIONS-E050 · data-integration-result | pre / 별도 입력 제약 없음/조회 항목 | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/invoke/{{ integration.published_id }} / 게시 API 호출. 쓰기 API는 확인 및 멱등성 규칙 적용; 결과/작업 상태 표시. | `desk/templates/desk/integrations.html:14` |
| UI-INTEGRATIONS-E051 · 계정명 | text / name=name; required | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E052 · 인증 | select / name=auth_mode | if integration / if integration.published / 선택값: API_KEY=API_KEY; HMAC_SHA256=HMAC_SHA256 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E053 · 분당 호출 수 | number / name=rate_limit; type=number; min=1; max=1000; value=60 | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E054 · 사유 | text / name=reason; required | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E055 · 호출 계정 발급 | submit / 별도 입력 제약 없음/조회 항목 | if integration / if integration.published | 폼 제출: client → /api/v1/integrations/client/{{ integration.published_id }} / /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E056 · data-integration-result | pre / 별도 입력 제약 없음/조회 항목 | if integration / if integration.published | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/client/{{ integration.published_id }} / 외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E057 · 중지 사유 | text / name=reason; required | if integration / for client in integration_clients / if client.active | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/client-stop/{{ client.id }} / 선택 외부 호출 클라이언트 중지; 사유 검사. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E058 · 계정 중지 | submit / 별도 입력 제약 없음/조회 항목 | if integration / for client in integration_clients / if client.active | 폼 제출: client-stop → /api/v1/integrations/client-stop/{{ client.id }} / /api/v1/integrations/client-stop/{{ client.id }} / 선택 외부 호출 클라이언트 중지; 사유 검사. | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E059 · 시각 | th / 별도 입력 제약 없음/조회 항목 | if integration | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E060 · 상태 | th / 별도 입력 제약 없음/조회 항목 | if integration | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E061 · 시도 | th / 별도 입력 제약 없음/조회 항목 | if integration | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E062 · 결과 | th / 별도 입력 제약 없음/조회 항목 | if integration | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E063 · 결과·이력 보기 | button / type=button | if integration / for job in integration_jobs | API 실행 결과 상세 조회; 조회 실패 안내 표시 | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E064 · data-job-result | pre / 별도 입력 제약 없음/조회 항목 | if integration | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 | `desk/templates/desk/integrations.html:15` |
| UI-INTEGRATIONS-E065 · 이름 | text / name=name; required | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/credential / 인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함. | `desk/templates/desk/integrations.html:16` |
| UI-INTEGRATIONS-E066 · 인증 방식 | select / name=auth_type | 해당 화면/공통 영역 표시 시 / 선택값: {{ key }}={{ label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/credential / 인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함. | `desk/templates/desk/integrations.html:16` |
| UI-INTEGRATIONS-E067 · 변경 사유 | text / name=reason; required | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/credential / 인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함. | `desk/templates/desk/integrations.html:16` |
| UI-INTEGRATIONS-E068 · 인증 항목 · JSON | textarea / name=secret; autocomplete=off | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/credential / 인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함. | `desk/templates/desk/integrations.html:16` |
| UI-INTEGRATIONS-E069 · 인증정보 저장 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: credential → /api/v1/integrations/credential / /api/v1/integrations/credential / 인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함. | `desk/templates/desk/integrations.html:16` |
| UI-INTEGRATIONS-E070 · 호스트 · 한 줄에 하나 | textarea / name=allowed_hosts | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/network / HTTPS 호스트·허용 사설 CIDR 정책 검증 후 저장. | `desk/templates/desk/integrations.html:17` |
| UI-INTEGRATIONS-E071 · 사설망 CIDR · 필요할 때만 | textarea / name=allowed_private_cidrs | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/network / HTTPS 호스트·허용 사설 CIDR 정책 검증 후 저장. | `desk/templates/desk/integrations.html:18` |
| UI-INTEGRATIONS-E072 · 변경 사유 | text / name=reason; required | 해당 화면/공통 영역 표시 시 | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/integrations/network / HTTPS 호스트·허용 사설 CIDR 정책 검증 후 저장. | `desk/templates/desk/integrations.html:19` |
| UI-INTEGRATIONS-E073 · 허용 정책 저장 | submit / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 폼 제출: network → /api/v1/integrations/network / /api/v1/integrations/network / HTTPS 호스트·허용 사설 CIDR 정책 검증 후 저장. | `desk/templates/desk/integrations.html:19` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
