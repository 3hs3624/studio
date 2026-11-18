# 통합 ITSM 운영·사용 매뉴얼

2026-11-18 통합본 기준. 만족도 프로세스에 개발 분기·독립 검토 게시·서비스 기준값을 합친 최종 구성은 로컬 검증 완료, 운영 DB 초기 적재는 main 병합·배포 후 신규 초기 비밀번호를 Render 비밀 환경변수로 전달해 실행합니다.

- [운영자 매뉴얼](operator-manual.md): 접속, 구현 순서, 역할별 구성, 메뉴별 기능 및 활용 예, 개별 UI 항목 색인.
- [사용자 매뉴얼](user-manual.md): 등록부터 만족도·자동 종료까지, 역할별 처리, 모든 업무 메뉴 및 활용 예.
- [구성·초기 적재 명세](../service-request-satisfaction.md).

## Google Docs(최종 통합본)

- [운영자 매뉴얼 — 최종 통합본](https://docs.google.com/document/d/1UY9TAhEw128EnmgNXfa1eE_ekmzVBTsQuNe495ZyHfs/edit)
- [사용자 매뉴얼 — 최종 통합본](https://docs.google.com/document/d/1adeCznNi2kdR29D_TePzv0t4TqFHOyYcvq5km6uMtzA/edit)

이 저장소의 operator-manual.md·user-manual.md에서 변환한 문서이며, 끝부분에 최종 구성의 화면 예시가 들어 있습니다. 이전에 만든 Google 문서(만족도 7단계판, 개발·운영판)는 이 통합본으로 대체됩니다. 비밀번호는 이 저장소에 포함하지 않습니다.

## 검증

통합본(2026-11-18): 개발 분기·독립 검토 게시·단계별 예시·서비스 기준값을 합친 구성을 기존 운영 구조와 같은 로컬 PostgreSQL 16 DB에 업그레이드 적용해 확인했습니다(재실행 시 변경 없음). 서비스요청 초기 구성 테스트 9개를 통과했습니다.

이전 기록: 관련 회귀 68개 통과(환경 제외2), 전체 로컬325개 통과(환경 제외16). GitHub SQLite/PostgreSQL/Docker CI 통과. 6개 역할의 브라우저 로그인, 최초 비밀번호 변경, 승인→배정→조치→확인→만족도→자동 종료, 비할당자 입력 차단을 검증했습니다. 만족도1~5 범위 및 재조치 분기는 서버 테스트로 검증했습니다. 모바일390px 등록 화면 가로 넘침 없음.

코드 운영 배포: main 17940c142263beaf43d8cf2bdf0e564de30e8df6, Render dep-dbu8b8etlv9c73blllcg live 확인. 운영 DB 적재 마커와 신규 두 계정은 아직 없음을 확인했습니다. 초기 적재 전에는 기존 v1 템플릿이 계속 표시됩니다.
