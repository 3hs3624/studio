# UI-PLUGINS · 플러그인 목록/상세

진입/사용: /admin/plugins, /console/plugins, /console/plugins/<str:plugin_id>

소스: `desk/templates/desk/plugins.html`

연결: `desk/console-tabs.html`

뷰·권한 참조(동시 필수 권한 목록 아님): views.plugin_management [뷰/공통 컨텍스트·업무 조회 권한]

## 기능/폼 계약

### UI-PLUGINS-F01

UI-PLUGINS-F01 · plugin-configure · POST(JSON) /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장.

항목: UI-PLUGINS-E017, UI-PLUGINS-E018, UI-PLUGINS-E019, UI-PLUGINS-E020, UI-PLUGINS-E021, UI-PLUGINS-E022, UI-PLUGINS-E023, UI-PLUGINS-E024, UI-PLUGINS-E025, UI-PLUGINS-E026

### UI-PLUGINS-F02

UI-PLUGINS-F02 · plugin-preview · POST(JSON) /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/preview / 플러그인 입력 시험 결과 표시; 실제 번호 발급과 구분.

항목: UI-PLUGINS-E027, UI-PLUGINS-E028, UI-PLUGINS-E029, UI-PLUGINS-E030

### UI-PLUGINS-F03

UI-PLUGINS-F03 · plugin-issue · POST(JSON) /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/issue / 매니페스트 해시·권한·입력을 검증해 업무번호 발급; 결과 재확인 지원.

항목: UI-PLUGINS-E031, UI-PLUGINS-E032, UI-PLUGINS-E033, UI-PLUGINS-E034

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-PLUGINS-E001 · 플러그인 목록 | a / 별도 입력 제약 없음/조회 항목 | if plugin | 링크 이동: /console/plugins | `desk/templates/desk/plugins.html:4` |
| UI-PLUGINS-E002 · 플러그인 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E003 · 분류 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E004 · 설치 버전 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E005 · 사용 상태 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E006 · 설정 버전 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E007 · 호환 상태 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E008 · 최근 성공 실행 | th / 별도 입력 제약 없음/조회 항목 | if not plugin | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E009 · {{ item.manifest.name }} | a / 별도 입력 제약 없음/조회 항목 | if not plugin / for item in plugins | 링크 이동: /console/plugins/{{ item.manifest.plugin_id }} | `desk/templates/desk/plugins.html:6` |
| UI-PLUGINS-E010 · 식별자 | dt / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ plugin.manifest.plugin_id }} | `desk/templates/desk/plugins.html:10` |
| UI-PLUGINS-E011 · 설치 버전 | dt / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ plugin.manifest.version }} | `desk/templates/desk/plugins.html:10` |
| UI-PLUGINS-E012 · 제공 기능 | dt / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ plugin.manifest.capabilities\|join:', ' }} | `desk/templates/desk/plugins.html:10` |
| UI-PLUGINS-E013 · 의존성 | dt / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ plugin.manifest.dependencies\|default:'없음' }} | `desk/templates/desk/plugins.html:10` |
| UI-PLUGINS-E014 · 사용 상태 | dt / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: 사용 중지 | `desk/templates/desk/plugins.html:10` |
| UI-PLUGINS-E015 · 설정 버전 | dt / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / 출력값: {{ plugin.version }} | `desk/templates/desk/plugins.html:10` |
| UI-PLUGINS-E016 · 설정으로 이동 → | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'overview' | 링크 이동: ?tab=settings | `desk/templates/desk/plugins.html:11` |
| UI-PLUGINS-E017 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:14` |
| UI-PLUGINS-E018 · 설정 항목 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:15` |
| UI-PLUGINS-E019 · 값 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:15` |
| UI-PLUGINS-E020 · 식별자 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:15` |
| UI-PLUGINS-E021 · {{ field.label }} | checkbox / type=checkbox; checked; aria-label={{ field.label }} / checked는 field.value일 때 적용 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) / for field in plugin.settings / if field.type == 'boolean' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:15` |
| UI-PLUGINS-E022 · {{ field.label }} | select / aria-label={{ field.label }} | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) / for field in plugin.settings / elif field.type == 'enum' (앞 분기 제외) / 선택값: {{ option.value }}={{ option.label }} | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:16` |
| UI-PLUGINS-E023 · {{ field.label }} |  number text  / type= number text ; required; maxlength={{ field.maxlength }}; min={{ field.minimum }}; max={{ field.maximum }}; step=1; value={{ field.value }}; aria-label={{ field.label }} / required는 field.type == 'integer' %}number{% else %}text{% endif %}" {% if field.type == 'integer' %}min="{{ field.minimum }}" max="{{ field.maximum }}" step="1"{% endif %} {% if field.maxlength %}maxlength="{{ field.maxlength }}"{% endif일 때 적용 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) / for field in plugin.settings / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:17` |
| UI-PLUGINS-E024 · 사용 | checkbox / name=enabled; type=checkbox; checked / checked는 plugin.binding.enabled일 때 적용 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:18` |
| UI-PLUGINS-E025 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:19` |
| UI-PLUGINS-E026 · 설정 저장 | submit / type=submit | else (앞 분기 제외) / elif active_tab == 'settings' (앞 분기 제외) | 폼 제출: plugin-configure → /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/configuration / 등록 매니페스트에 맞는 설정·행 버전 검증 후 저장. | `desk/templates/desk/plugins.html:19` |
| UI-PLUGINS-E027 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/preview / 플러그인 입력 시험 결과 표시; 실제 번호 발급과 구분. | `desk/templates/desk/plugins.html:23` |
| UI-PLUGINS-E028 · {{ field.label }} | textarea / maxlength=4000 | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute / for field in plugin.manifest.input_fields | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/preview / 플러그인 입력 시험 결과 표시; 실제 번호 발급과 구분. | `desk/templates/desk/plugins.html:23` |
| UI-PLUGINS-E029 · 예상 번호 확인 기능 미리보기 | submit / type=submit | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute | 폼 제출: plugin-preview → /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/preview / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/preview / 플러그인 입력 시험 결과 표시; 실제 번호 발급과 구분. | `desk/templates/desk/plugins.html:23` |
| UI-PLUGINS-E030 · data-plugin-output | pre / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/preview / 플러그인 입력 시험 결과 표시; 실제 번호 발급과 구분. | `desk/templates/desk/plugins.html:23` |
| UI-PLUGINS-E031 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute / if 'plugin.issue' in plugin.manifest.capabilities | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/issue / 매니페스트 해시·권한·입력을 검증해 업무번호 발급; 결과 재확인 지원. | `desk/templates/desk/plugins.html:24` |
| UI-PLUGINS-E032 · 실제 발급 | submit / type=submit | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute / if 'plugin.issue' in plugin.manifest.capabilities | 폼 제출: plugin-issue → /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/issue / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/issue / 매니페스트 해시·권한·입력을 검증해 업무번호 발급; 결과 재확인 지원. | `desk/templates/desk/plugins.html:24` |
| UI-PLUGINS-E033 · 새 발급 준비 | button / type=button | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute / if 'plugin.issue' in plugin.manifest.capabilities | 클라이언트 조작: 새 발급 준비 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/issue / 매니페스트 해시·권한·입력을 검증해 업무번호 발급; 결과 재확인 지원. | `desk/templates/desk/plugins.html:24` |
| UI-PLUGINS-E034 · data-plugin-output | pre / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / if plugin.binding.enabled and plugin.compatible and can_plugin_execute / if 'plugin.issue' in plugin.manifest.capabilities | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/admin/plugins/{{ plugin.manifest.plugin_id }}/issue / 매니페스트 해시·권한·입력을 검증해 업무번호 발급; 결과 재확인 지원. | `desk/templates/desk/plugins.html:24` |
| UI-PLUGINS-E035 · 설정으로 이동 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'test' (앞 분기 제외) / else (앞 분기 제외) | 링크 이동: ?tab=settings | `desk/templates/desk/plugins.html:25` |
| UI-PLUGINS-E036 · 일시 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'runs' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:26` |
| UI-PLUGINS-E037 · 실행자 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'runs' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:26` |
| UI-PLUGINS-E038 · 동작 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'runs' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:26` |
| UI-PLUGINS-E039 · 결과 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'runs' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:26` |
| UI-PLUGINS-E040 · 상세 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'runs' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:26` |
| UI-PLUGINS-E041 · 설정 버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'runs' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:26` |
| UI-PLUGINS-E042 · 일시 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'changes' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:27` |
| UI-PLUGINS-E043 · 변경자 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'changes' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:27` |
| UI-PLUGINS-E044 · 설정 버전 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'changes' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:27` |
| UI-PLUGINS-E045 · 변경 사유 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'changes' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/plugins.html:27` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
