# UI-SECURITY_POLICIES · 보안정책 목록/상세

진입/사용: /console/security, /console/security/<str:category>

소스: `desk/templates/desk/security-policies.html`

연결: `desk/console-tabs.html`

뷰·권한 참조(동시 필수 권한 목록 아님): identity_views.security_policies [security.manage]

## 기능/폼 계약

### UI-SECURITY_POLICIES-F01

UI-SECURITY_POLICIES-F01 · security-policy · POST(JSON) /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사.

항목: UI-SECURITY_POLICIES-E009, UI-SECURITY_POLICIES-E010, UI-SECURITY_POLICIES-E011, UI-SECURITY_POLICIES-E012, UI-SECURITY_POLICIES-E013, UI-SECURITY_POLICIES-E014, UI-SECURITY_POLICIES-E015, UI-SECURITY_POLICIES-E016, UI-SECURITY_POLICIES-E017, UI-SECURITY_POLICIES-E018, UI-SECURITY_POLICIES-E019

## 항목별 상세

| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |
|---|---|---|---|---|
| UI-SECURITY_POLICIES-E001 · 정책 목록 | a / 별도 입력 제약 없음/조회 항목 | 해당 화면/공통 영역 표시 시 | 링크 이동: /console/security | `desk/templates/desk/security-policies.html:1` |
| UI-SECURITY_POLICIES-E002 · 정책 | th / 별도 입력 제약 없음/조회 항목 | if not category | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:2` |
| UI-SECURITY_POLICIES-E003 · 적용 상태 | th / 별도 입력 제약 없음/조회 항목 | if not category | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:2` |
| UI-SECURITY_POLICIES-E004 · 설정 버전 | th / 별도 입력 제약 없음/조회 항목 | if not category | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:2` |
| UI-SECURITY_POLICIES-E005 · 변경자 | th / 별도 입력 제약 없음/조회 항목 | if not category | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:2` |
| UI-SECURITY_POLICIES-E006 · 적용일 | th / 별도 입력 제약 없음/조회 항목 | if not category | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:2` |
| UI-SECURITY_POLICIES-E007 · {{ item.label }} | a / 별도 입력 제약 없음/조회 항목 | if not category / for item in policy_list | 링크 이동: /console/security/{{ item.key }} | `desk/templates/desk/security-policies.html:2` |
| UI-SECURITY_POLICIES-E008 · 민감 작업 재인증·내 MFA 설정 | a / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'settings' | 링크 이동: /account/security | `desk/templates/desk/security-policies.html:4` |
| UI-SECURITY_POLICIES-E009 · 입력 항목 | div / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'settings' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:5` |
| UI-SECURITY_POLICIES-E010 · 설정 항목 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'settings' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:5` |
| UI-SECURITY_POLICIES-E011 · 값 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'settings' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:5` |
| UI-SECURITY_POLICIES-E012 · 허용 범위 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'settings' | 조회/상태 표시; 이 항목 자체는 저장하지 않음 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:5` |
| UI-SECURITY_POLICIES-E013 · {{ field.label }} | checkbox / type=checkbox; disabled; checked; aria-label={{ field.label }} / disabled는 field.key == 'mask_contacts'일 때 적용; checked는 field.value일 때 적용 | else (앞 분기 제외) / if active_tab == 'settings' / for field in policy_fields / if field.kind == 'boolean' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:5` |
| UI-SECURITY_POLICIES-E014 · {{ field.label }} |  number text  / type= number text ; required; maxlength=2000; min={{ field.minimum }}; max={{ field.maximum }}; step=1; value={{ field.value }}; aria-label={{ field.label }} | else (앞 분기 제외) / if active_tab == 'settings' / for field in policy_fields / else (앞 분기 제외) | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:5` |
| UI-SECURITY_POLICIES-E015 · 변경 사유 | text / name=reason; required; maxlength=500 | else (앞 분기 제외) / if active_tab == 'settings' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:6` |
| UI-SECURITY_POLICIES-E016 · 조직의 로그인·세션에 미치는 영향을 확인했으며 즉시 적용합니다. | checkbox / name=apply_confirmed; type=checkbox | else (앞 분기 제외) / if active_tab == 'settings' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:6` |
| UI-SECURITY_POLICIES-E017 · 사전 검증·영향 확인 | submit / type=submit | else (앞 분기 제외) / if active_tab == 'settings' | 보안정책 적용 전 미리보기; 결과만 표시하며 저장하지 않음 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:6` |
| UI-SECURITY_POLICIES-E018 · 정책 적용 | submit / type=submit | else (앞 분기 제외) / if active_tab == 'settings' | 폼 제출: security-policy → /api/v1/management/policies/{{ category }} / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:6` |
| UI-SECURITY_POLICIES-E019 · data-policy-output | pre / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / if active_tab == 'settings' | 입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행 / /api/v1/management/policies/{{ category }} / 정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사. | `desk/templates/desk/security-policies.html:6` |
| UI-SECURITY_POLICIES-E020 · 일시 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'checks' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:9` |
| UI-SECURITY_POLICIES-E021 · 사용자 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'checks' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:9` |
| UI-SECURITY_POLICIES-E022 · 이벤트 | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'checks' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:9` |
| UI-SECURITY_POLICIES-E023 · 추적 ID | th / 별도 입력 제약 없음/조회 항목 | else (앞 분기 제외) / elif active_tab == 'checks' (앞 분기 제외) | 조회/상태 표시; 이 항목 자체는 저장하지 않음 | `desk/templates/desk/security-policies.html:9` |

## 확인 기준

정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.
예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.
공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.
