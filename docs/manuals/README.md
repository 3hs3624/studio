# 통합 ITSM 운영·사용 매뉴얼

2026-11-18 기준. 새 서비스요청 프로세스는 로컬 검증 완료, 운영 DB 초기 적재는 신규 초기 비밀번호를 Render 비밀 환경변수로 전달하는 승인 대기입니다.

- [운영자 매뉴얼](operator-manual.md): 접속, 구현 순서, 역할별 구성, 메뉴별 기능 및 활용 예, 개별 UI 항목 색인.
- [사용자 매뉴얼](user-manual.md): 등록부터 만족도·자동 종료까지, 역할별 처리, 모든 업무 메뉴 및 활용 예.
- [구성·초기 적재 명세](../service-request-satisfaction.md).

## Google Docs · ChatGPT/Studio

- [운영자 매뉴얼](https://docs.google.com/document/d/1laXXdJi7KvAicr8rihyfCSmqacTxhH5zPNwOdq6GA3U/edit)
- [사용자 매뉴얼](https://docs.google.com/document/d/13NNpqUN826YF2bspRhX1Eg0zuVwc7yfzvJvztyOlV8g/edit)

Google 문서에는 7단계 실제 화면 예시가 별도 탭에 포함됩니다. 비밀번호는 이 저장소에 포함하지 않습니다.

## 검증

관련 회귀 68개 통과(환경 제외2), 전체 로컬325개 통과(환경 제외16). GitHub SQLite/PostgreSQL/Docker CI 통과. 6개 역할의 브라우저 로그인, 최초 비밀번호 변경, 승인→배정→조치→확인→만족도→자동 종료, 비할당자 입력 차단을 검증했습니다. 만족도1~5 범위 및 재조치 분기는 서버 테스트로 검증했습니다. 모바일390px 등록 화면 가로 넘침 없음.

코드 운영 배포: main 17940c142263beaf43d8cf2bdf0e564de30e8df6, Render dep-dbu8b8etlv9c73blllcg live 확인. 운영 DB 적재 마커와 신규 두 계정은 아직 없음을 확인했습니다. 초기 적재 전에는 기존 v1 템플릿이 계속 표시됩니다.
