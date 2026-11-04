# IBM 공식 근거와 차이점 — v0.2

확인일: 2026-11-04. 비교 기준은 **Maximo IT 9.1 릴리스 기능**과 **Maximo IT CD 문서**입니다. 최신 버전 전체를 확정한 것이 아니며 CD 문서의 모든 동작이 9.1에도 같다고 단정하지 않습니다. 에디션·계약·기본/옵션 포함 여부는 미확인입니다.

## 근거 목록

| 근거 | 공식 문서·절 | 확인 수준 | 자체 설계와의 차이 |
|---|---|---|---|
| E01 | [What's new in Maximo IT Version 9.1](https://www.ibm.com/docs/en/max-it/cd.0.0_cd?topic=it-whats-new-in-maximo-v91), New and enhanced applications | 본문 확인, 9.1 명시 | AI·협업·IT/OT·토폴로지·관리자 승인이 있으며 초기 41개 후보에 누락 또는 상세 부족 |
| E02 | [Service level agreements](https://www.ibm.com/docs/en/max-it/cd?topic=overview-service-level-agreements), 적용 방식·계산 값 | 본문 확인, CD | 응답·해결·연락 약정, 자동/수동 적용·에스컬레이션 확인. 휴일·정지·재개방 계산의 구체 규칙은 별도 확인 필요 |
| E03 | [Procure licenses](https://www.ibm.com/docs/en/max-it/cd?topic=tasks-procure-licenses), PR·PO·Generating costs | 본문 확인, CD | 라이선스에서 구매 요청·주문·비용 생성 확인. 전체 물류·재고·회계 지원 근거로 확장하지 않음 |
| E04 | [Change Management Overview](https://www.ibm.com/docs/en/max-it/cd?topic=changes-change-management-overview), 기능 목록 | 본문 확인, CD | 영향 평가·작업·승인·일정 충돌·blackout 확인. IBM의 standard/express/advanced와 자체 표준/일반/긴급은 동일 분류가 아님 |
| E05 | [Service Catalog overview](https://www.ibm.com/docs/en/max-it/cd?topic=catalog-service-overview), capabilities | 본문 확인, CD | 서비스 정의·탐색·제공 자격·승인·상태 추적 확인. 자체 양식·버전 구현은 독립 설계 |
| E06 | [Configuration management processes](https://www.ibm.com/docs/en/max-it/cd?topic=items-configuration-management-processes) | 검색 색인 본문만 확인; 직접 열기 403 | 승인 구성 갱신·실제/승인 구성 감사가 색인에 나타남. 원문 재확인 전 검증 완료 불가 |
| E07 | [IBM Maximo IT 9.1 release](https://www.ibm.com/support/pages/ibm-maximo-application-suite-ibm-maximo-it-91), Abstract·Content | 본문 확인 | 9.1의 Manage add-on 관계 확인. 자체 제품이 MAS·Java·OpenShift를 사용해야 한다는 의미는 아님 |

## 9.1 누락 기능 보강

E01의 기능 설명을 근거로 다음 후보를 추가합니다. 아래 인수 기준은 IBM 동작의 복제가 아니라 자체 제품의 목표입니다.

| ID | 후보 기능 | 자체 인수 기준 | 구현 위치 |
|---|---|---|---|
| AI-01 | 담당자·유사 티켓·해결책 추천 | 허용된 데이터만 참조, 제안 근거·사용자 채택 기록, 자동 상태 변경 금지 | 5단계 이후 확장 |
| AI-02 | 셀프서비스 가상 상담 연동 | 사용자 인증·권한 유지, 상담에서 요청으로 전환, 전송 데이터·보존 정책 명시 | 5단계 이후 확장 |
| COL-01 | Teams/Slack ChatOps·협업 | 연결 사용자 권한으로 티켓 조회·갱신, 중복 이벤트·연결 해제 처리 | 5단계 이후 확장 |
| SEC-01 | IT/OT 탐색·취약점 경보 연동 | 출처·자산 매핑·중복 경보·변경 조치 추적, 미매핑 항목 격리 | 5단계 이후 확장 |

서비스 토폴로지는 CFG-02/04, Manager Approvals는 ITSM-04/05와 PLT-04에 연결합니다. 독립 기능으로 중복 집계하지 않습니다.

## 추적 규칙

기능 대응표의 근거 표시는 일부 기능 영역의 존재 확인입니다. 하나의 복합 요구사항에 근거가 있어도 인수 기준 전체가 IBM과 같다는 뜻은 아닙니다. 원문 미확인·수집 도구·라이선스 계산·전체 구매 물류는 추가 검증 대상입니다. 모든 자체 기능의 구현 상태는 미구현입니다.
