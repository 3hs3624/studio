# 통합 ITSM 사용자 매뉴얼

> 운영 적용 상태: 코드와 로컬 검증은 완료했으며 신규 계정·템플릿·실습 요청 5건의 운영 DB 초기 적재는 비밀번호 전달 승인 대기입니다. 기존 운영 계정과 진행 요청은 유지됩니다.

2026-11-18 · 서비스요청 등록부터 만족도 조사·자동 종료까지의 구현 기준. 요청자·요청부서 승인자·접수 운영자·배정 담당자가 실제 업무를 처리하는 방법입니다. 나머지 포털 메뉴는 해당 권한이 있을 때 사용합니다. 화면을 설계·게시하는 방법은 운영자 매뉴얼을 참조합니다.

화면 예시는 로컬 검증 환경입니다. 배포 조직의 버전 번호·요청 번호·입력 데이터는 다를 수 있습니다.

## 1. 접속과 첫 로그인

https://studio-itsm-preview-2zzi.onrender.com/login/ 에서 아이디·비밀번호로 로그인합니다. 요청자는 user1, 요청부서 승인자는 user_auth1, 접수·조치 운영자는 worker1/worker2입니다. 기존 계정은 기존 비밀번호를 사용합니다. 신규 계정 초기 비밀번호는 별도 비공개 접속정보로 받으며 첫 로그인에서 현재 비밀번호·새 비밀번호·확인값으로 변경합니다. 비밀번호를 모르면 반복 시도하지 말고 관리자에게 초기화를 요청합니다.

활용 예: user1으로 로그인해 통합 홈을 보고 서비스 카탈로그로 이동합니다. 잠금 안내가 나오면 잠금 시간 또는 관리자 해제를 확인합니다. 개발자/디자이너 계정으로 일반 요청자의 처리 가능 여부를 대신 확인하지 않습니다.

## 2. 통합 홈·시스템 이동·내가 할 일

통합 홈은 IT서비스·IT자산·IT자원으로 이동하는 카드와 자주 찾는 업무, 내가 할 일, 내 승인·알림을 제공합니다. 메뉴는 역할에 따라 표시됩니다. 내가 할 일의 ‘나’는 본인 할당, ‘부서’는 현재 부서 담당자의 대기 건(하위 부서 제외), ‘전체’는 기존 조회 권한 안의 건입니다. 전체를 눌러도 조직 전체 권한이 생기지 않습니다. 총건수와 최근10건을 표시하며 연결 SR/태스크의 중복은 제외합니다.

활용 예: worker1은 ‘나’에서 접수 태스크를 열고, ‘부서’에서 같은 운영부서의 대기 업무를 확인합니다. user1의 ‘전체’에 다른 사람의 비공개 요청이 나타나지 않는 것이 정상입니다. 부서가 미지정이면 안내와 빈 결과를 볼 수 있습니다.

## 3. 상단 메뉴·사이드바·본인 정보

상단 시스템 전환은 같은 로그인 안에서 업무 영역을 바꿉니다. 본인 이름은 이름·ID·부서·연락처·역할·그룹과 배정 출처를 보여 주는 모달을 엽니다. 닫기·Escape·모달 바깥 클릭으로 닫습니다. 내 계정 보안은 비밀번호/MFA/세션, 알림은 업무 알림, 로그아웃은 현재 인증을 종료합니다.

데스크톱 상단 메뉴 버튼으로 사이드바를 접고 펼칩니다. 경계를 드래그하면 기본256px에서220~480px 및 화면 너비 제한 안으로 조절됩니다. 경계에 키보드 포커스를 두고 좌우10px·Shift50px·Home/End를 사용하거나 두 번 클릭해 기본 폭으로 돌아갑니다. 드래그 중 Escape는 변경을 취소합니다. 상태는 같은 브라우저에서 유지되며 다른 장치에는 복사되지 않습니다. 모바일 메뉴는 별도 열기·배경/Escape 닫기를 사용합니다.

활용 예: 요청 목록 표가 좁으면 메뉴를 접거나 표 안에서 가로 스크롤합니다. 브라우저 저장이 차단돼도 현재 화면에서는 조작할 수 있습니다.

## 4. 서비스 카탈로그: 서비스 선택·신청

IT서비스 → 서비스 카탈로그에서 서비스 이름을 검색합니다. 신청 가능한 카드만 보이며 카드의 승인/워크플로우 안내를 확인하고 선택합니다. ‘서비스요청 · 승인부터 만족도까지’를 열면 공통 화면의 요청 기본정보 그룹이 표시됩니다.

입력은 요청 제목, 요청 내용, 요청 구분(계정/권한/소프트웨어/장비/기타), 대상 시스템, 요청 우선순위1~3, 희망 완료일, 요청 연락처입니다. 앞의5개는 필수입니다. 요청 제목은 실제 목록 제목으로 사용합니다. 희망 완료일은 요청자의 희망이며 운영자가 합의한 처리 기한이나 SLA 변경을 자동 승인하는 값이 아닙니다. 신청 시 처리용 배정·조치·만족도 필드는 나타나지 않습니다. 취소는 목록으로 이동하고 ‘서비스 신청 →’은 저장·프로세스 시작입니다.

활용 예: 제목 ‘공유폴더 접근 권한’, 내용 ‘프로젝트 A 폴더 읽기 권한’, 구분 ‘권한’, 시스템 ‘파일서버’, 우선순위2를 입력합니다. 업무 필요성과 대상 범위를 구체적으로 적습니다. 비밀번호·주민번호·인증 키를 내용에 넣지 않습니다. 저장 후 요청부서 승인 단계가 시작됩니다.

## 5. 내 서비스 요청: 목록·검색·상세

내 서비스 요청에서 제목/번호·상태 등 제공된 조회 조건을 사용하고 행을 선택합니다. 상세는 신청 당시 양식의 답변·상태·승인/담당 정보·연결 자산·대화·처리 이력을 보여 줍니다. 적용 워크플로우의 ‘업무·결재 진행 화면 →’을 누르면 해당 실행으로 이동합니다. 대화와 이력은 우측 영역에서 접고 펼칠 수 있습니다.

워크플로우 연결 건은 상세의 레거시 직접 처리로 우회하지 않습니다. 반려/취소 상태의 본인 건은 ‘다시 신청하기’로 최신 양식의 새 요청을 만들 수 있고 이전 요청 링크를 보존합니다. 새 게시 버전이 생겨도 진행 중인 건의 단계와 화면은 자동으로 바뀌지 않습니다.

활용 예: ‘[실습] 공유폴더 접근 권한’을 열어 요청자·현재 단계·담당 그룹을 확인합니다. 반려되었으면 결정 사유를 보완해 재신청하며 기존 반려 건의 내용을 몰래 수정해 진행시키지 않습니다.

## 6. 서비스 승인함: 요청부서 승인자

user_auth1은 서비스 승인함 또는 내가 할 일에서 본인 승인 대기 건을 엽니다. 연결 워크플로우 업무·결재 화면에서 요청정보를 읽고 승인 결정(APPROVE/REJECT)과 사유를 제출합니다. 승인 단계는 업무 필드 입력 단계가 아니므로 요청 내용·담당자·만족도를 변경하지 않습니다. 자기 신청을 자기 결재하거나 다른 사람의 결재를 수행할 수 없습니다.

활용 예: 업무 필요성과 대상 시스템을 확인한 후 승인하면 접수그룹으로 이동합니다. 신청 근거가 부족하면 반려 사유에 ‘권한 대상 폴더와 사용 기간을 기재해 재신청’처럼 구체적으로 씁니다. 작성 화면이 조회 전용이라고 해서 오류가 아닙니다.

## 7. 워크플로우 업무·결재: 목록과 공통 처리

목록의 조회 가능/내 시작 건/내 처리 대기와 페이지 이동을 사용합니다. 실행을 열면 프로세스 이름·게시 버전·연결 SR·태스크 상태·담당자·그룹별 데이터·실행 이력이 나옵니다. 현재 열린 태스크이며 본인에게 할당된 경우만 입력/결정 폼과 ‘처리·다음 단계 진행’ 버튼이 제공됩니다. 종료/완료 단계는 조회 전용입니다. 같은 화면이어도 단계별로 보이는 그룹과 필드가 다릅니다.

필수표시 항목과 처리 사유를 작성해 버튼을 누릅니다. 저장 전 변경 사항은 서버에 반영되지 않습니다. 중복 제출 중 버튼은 잠기며, 다른 사람이 먼저 처리하면 버전 충돌/완료 안내가 나올 수 있습니다. 새로고침 전에 입력을 복사해 둡니다. 관리자용 재할당·취소·대기 진행 버튼은 일반 처리자가 사용하지 않습니다.

활용 예: worker1이 접수 태스크를 완료한 뒤 같은 화면을 다시 보내지 않습니다. 화면의 다음 열린 태스크와 담당자가 worker2로 바뀌었는지 확인합니다.

## 8. 접수 및 담당자 배정: worker1·worker2

서비스요청 접수그룹의 두 운영자 모두 같은 접수 태스크를 볼 수 있습니다. ANY 처리이므로 한 명이 완료하면 나머지 사람의 접수 처리는 종료됩니다. 요청정보는 조회하고 접수 및 배정 그룹에서 조치 담당자·접수/배정 의견·선택적 처리 예정일시를 입력합니다. 담당자와 접수 의견은 필수입니다. 담당자는 전용 그룹의 활성 worker1/worker2 중 선택합니다.

활용 예: worker1이 담당자 worker2, 의견 ‘파일서버 권한 검토 후 조치’, 처리 예정일시를 입력해 제출합니다. 다음 조치 태스크는 worker2 한 명에게만 할당됩니다. 접수그룹에 있다고 다른 사람의 조치를 대신 제출할 수 있는 것은 아닙니다.

## 9. 담당자 조치: 배정된 운영자

배정된 운영자는 나의 할 일 또는 업무·결재에서 조치 태스크를 엽니다. 요청/접수 정보는 읽고 담당자 조치 그룹의 조치 내용·원인/참고·조치 시작/완료일시·작업 시간(분)을 입력합니다. 조치 내용은 필수이며 작업 시간은 정수0~100000입니다. 날짜시간은 시간대를 포함한 ISO 형식으로 입력합니다(예: 2026-11-18T10:30:00+09:00). 입력 후 ‘처리·다음 단계 진행’을 누르면 요청자 확인으로 이동합니다.

활용 예: worker2가 조치 내용 ‘프로젝트 A 폴더 읽기 권한 추가 및 접속 확인’, 작업 시간20을 입력합니다. 완료 후 결과 확인은 worker2가 대신 수행하지 않습니다. 비할당 worker1에게는 조치 제출 폼이 보이지 않습니다.

## 10. 조치결과 확인: 요청자

user1에게 확인 태스크가 할당됩니다. 요청과 조치 내용을 읽고 ‘조치 결과 정상 확인’에서 예/아니오, 결과 확인·재조치 의견을 입력합니다. 확인값은 필수입니다. 예는 만족도 조사로, 아니오는 기존 배정 담당자의 조치로 돌아갑니다. 이 단계만 완료해서는 요청이 자동 종료되지 않습니다.

활용 예: 공유폴더 접속이 되면 예와 ‘정상 접속 확인’을 입력합니다. 여전히 권한이 없으면 아니오와 재현 상황을 적어 제출합니다. 단순히 댓글로 ‘완료’라고 쓰는 것은 태스크 완료가 아닙니다.

## 11. 만족도 조사와 자동 종료

정상 확인 후 user1에게 만족도 조사 태스크가 생깁니다. 만족도 정수1~5점은 필수, 의견은 선택입니다. ‘처리·다음 단계 진행’으로 제출하면 다음 종료 노드가 자동 실행되어 SR과 워크플로우가 종료됩니다. 별도 종료 버튼은 필요 없습니다. 낮은 점수도 유효한 조사 제출이므로 종료됩니다.

활용 예: 5점과 ‘안내가 명확했습니다’를 입력해 제출합니다. 0·6·소수점은 허용되지 않습니다. 점수 범위 오류가 나면 유효한 값으로 바꿉니다. 실패 시 기존 태스크는 열린 상태로 유지됩니다. 완료 후 입력 폼이 사라지고 종료 상태·처리 이력·KPI 완료 근거를 확인합니다.

## 12. 대화·처리 이력·연결 자산

댓글 입력과 공개 범위를 선택해 등록합니다. 공개는 요청자에게, 내부는 허용된 처리 담당자에게 보입니다. 요청자는 내부 범위를 임의 선택할 수 없습니다. 처리 이력은 상태·작성자·시각·사유를 읽는 영역입니다. 연결 자산은 요청과 관련된 지급/참조 정보를 조회하고 허용된 운영자는 자산 지급·계약/요청 연결 업무로 이동할 수 있습니다.

활용 예: 추가 자료가 필요하면 공개 댓글로 요청합니다. 운영자끼리의 분석 메모는 내부 댓글로 구분합니다. 댓글 등록 후에도 승인/배정/확인은 해당 태스크의 처리 버튼으로 따로 완료해야 합니다.

## 13. IT서비스 현황·서비스 요청 처리

현황은 조회 범위의 요청/장애 수와 최근 업무, 내가 할 일을 보여 줍니다. 운영자에게는 서비스 요청 처리/장애 처리 메뉴가 추가됩니다. 처리 목록은 검색·필터·상세·담당 정보를 확인하는 곳이며 연결된 SR의 단계 입력은 업무·결재 화면에서 수행합니다. 요청 목록이 비었을 때는 검색 조건, 공개 대상, 로그인 계정·부서·그룹·역할을 확인합니다.

활용 예: 운영자가 ‘전체’를 눌렀는데 다른 조직 요청이 보이지 않는 것은 정상입니다. 서비스 카탈로그가 비어 있으면 현재 user1이 신청대상 그룹에 속하는지 관리자에게 확인을 요청합니다.

## 14. 내 장애 요청: 등록·조회·처리 협조

장애 등록은 제목·설명·영향도·긴급도와 허용 자원 참조를 작성합니다. 목록에서 검색/상태 조건을 사용하고 상세에서 배정·상태·해결 내용·공개 대화·이력·자원·SLA를 확인합니다. 역할과 현재 상태에 따라 해결 확인/재개방/취소 등 허용 전이만 제공됩니다. 운영자는 처리 그룹/담당자 배정과 상태 전이·해결 내용을 작성합니다.

활용 예: ‘VPN 접속 오류’를 장애로 등록하고 발생 시각·재현 조건을 남깁니다. 단순 소프트웨어 설치 요청은 장애 대신 서비스 카탈로그를 사용합니다. ‘대기’로 인한 SLA 정지 여부는 화면의 정책 안내를 확인합니다.

## 15. 구성항목 대장

구성항목 대장에서 제공된 검색/필터·목록·상세를 사용해 시스템/구성항목과 연결된 자산·업무를 조회합니다. 공개/소유/역할 범위에 따라 결과가 달라집니다. 화면에 없는 타 조직 항목의 URL을 직접 입력해 조회하지 않습니다.

활용 예: 장애 대상 시스템을 찾고 같은 이름의 개발/운영 구성항목을 구분해 요청에 연결합니다. 이 메뉴는 GitHub/Jenkins 소스·배포 목록인 IT자원 메뉴와 다릅니다.

## 16. IT자산 현황·자산 대장·내 지급 자산

IT자산 현황은 허용된 자산 집계와 최근 정보를, 자산 대장은 검색/필터·상세·상태/위치/계약/이력을, 내 지급 자산은 본인 지급 정보와 이력을 제공합니다. 등록/수정/지급/반납/이동/폐기 동작은 자산 관리자 등 해당 권한에만 표시됩니다. 지급은 대상자, 이동/반납 등은 위치·창고와 상태 제약을 확인합니다.

활용 예: user1이 ‘내 지급 자산’에서 노트북 자산번호를 확인해 점검 요청에 적습니다. 반납이 필요하면 자산 관리자에게 요청하고, 관리자 조치 후 보관/지급 이력이 바뀌었는지 확인합니다.

## 17. 구매 요청·승인

권한이 있으면 구매 요청 메뉴에서 품목·수량·승인자·연결 서비스요청을 작성하고 목록/상세를 조회합니다. 지정 승인자는 승인/반려와 사유, 신청자는 허용 상태에서 취소를 수행합니다. 승인 후 구매 담당자는 공급업체/계약을 선택해 발주로 진행합니다.

활용 예: 노트북 지급 SR과 연결해 수량1의 구매 요청을 만듭니다. 승인 요청을 중복 등록하지 말고 기존 상태를 확인합니다. 반려 사유를 확인한 뒤 정책에 맞게 새 요청을 준비합니다.

## 18. 발주·입고·공급업체·계약

구매/재고 관리자에게 제공되는 발주 목록/상세는 수량·공급업체·계약·상태 동작·입고를, 공급업체·계약은 기준정보·계약 기간·자산 연결을 제공합니다. 입고 시 수량·창고·일련번호를 확인하고 부분 입고/초과/중복 제약을 따릅니다. 일반 요청자는 권한이 없으면 이 메뉴가 표시되지 않습니다.

활용 예: 발주10대 중3대가 도착하면 입고3대를 기록하고 잔량을 확인합니다. 같은 일련번호를 다시 입력해 다른 자산으로 중복 생성하지 않습니다.

## 19. 창고·재고·재고 이동 이력

권한 있는 담당자는 창고/품목 기준정보·재고 잔량을 조회/등록하고 출발/도착 창고 이동, 사용자/서비스요청 출고, 추적 방식에 따른 개별 자산 선택을 수행합니다. 이동 이력에서 결과·담당자·대상·수량을 조회합니다. 현재 가용 재고보다 큰 수량이나 다른 창고의 개별 자산은 선택할 수 없습니다.

활용 예: 동일 품목의 사용 가능한 자산을 본사 창고에서 지사로 이동한 후 양쪽 잔량과 이동 행을 확인합니다. 처리 중 오류가 나면 중복 제출보다 기존 이력 확인을 먼저 합니다.

## 20. IT자원: 소스 변경·빌드·배포

권한이 있으면 IT자원 현황과 소스 변경/배포 목록·상세를 조회합니다. 검색·상태·기간/대상 필터, 저장소·커밋·빌드·배포 환경·결과·외부 링크를 사용합니다. 이 메뉴는 GitHub/Jenkins의 수집 스냅샷을 관리하며 화면의 행을 조회하는 것과 실제 외부 배포 실행은 다릅니다.

활용 예: 변경 후 오류 신고가 들어오면 배포 목록에서 해당 환경·시각의 실패 결과를 찾고 연관 소스 변경/빌드 링크를 담당자에게 전달합니다. 실제 수집 연결이 없으면 샘플 데이터를 현장 수집 결과로 해석하지 않습니다.

## 21. 알림함

알림함은 본인에게 허용된 업무 이벤트를 보여 주며 연결 업무 열기와 읽음 처리를 제공합니다. 읽음은 업무 처리 완료가 아닙니다. 상단 수와 내가 할 일 수는 서로 다른 집계입니다.

활용 예: 승인 알림을 읽은 뒤 실제 승인 화면에서 결정해야 합니다. 알림만 읽고 승인 절차가 끝났다고 생각하지 않습니다.

## 22. 내 계정 보안

비밀번호 변경은 현재/새/확인값과 정책을 따릅니다. 재인증은 관리·개인정보 등 민감 기능을 위해 현재 비밀번호와 필요 시 OTP를 다시 확인합니다. MFA는 등록 안내·비밀키/QR·OTP 확인·복구코드 보관, 해제는 본인 확인 절차를 따릅니다. 세션은 현재 로그인/다른 접속 이력을 확인하고 허용된 회수를 수행합니다. 최초 변경 강제 상태에서는 먼저 비밀번호를 바꿉니다.

활용 예: 새 developer1으로 로그인해 초기 비밀번호를 변경한 뒤 콘솔을 사용합니다. 공유 PC를 떠날 때 로그아웃하고, 의심 접속이 있으면 세션을 회수한 뒤 관리자에게 문의합니다. 복구코드는 공개 댓글에 올리지 않습니다.

## 23. 실제 연습 시나리오 3가지

정상: [실습] 계정 생성 건 → user_auth1 승인 → worker1이 worker2 배정 → worker2 조치 → user1 예 확인 → user1 만족도5점 → 자동 종료.

재조치: [실습] 공유폴더 건에서 user1이 아니오와 ‘특정 하위 폴더 권한 없음’을 제출 → worker2 보완 → user1 예 → 만족도 제출.

입력 오류: [실습] 개발 도구 건의 만족도에서6 입력 → 범위 안내 →5로 수정. 이미 다른 사람이 처리한 화면이면 입력을 복사하고 새로고침합니다. 다른 계정으로 대신 점수를 제출하지 않습니다.

## 24. 자주 발생하는 상황

메뉴 없음: 역할·그룹·조직 권한 확인. 카탈로그 없음: 신청 공개 대상/사용 여부 확인. 처리 버튼 없음: 현재 담당자·현재 태스크·완료 여부 확인. 조회 전용: 해당 단계는 읽기만 허용된 정상 상태일 수 있음. 저장 실패: 필수/형식/숫자 범위/시간대/버전 충돌 메시지 확인. 확인 후 미종료: 만족도 태스크 완료 여부 확인. 이미 처리됨: 새로고침 후 상태 확인. 비밀번호 실패: 반복 시도로 잠그지 말고 관리자에게 연락.

활용 예: worker1이 배정 후 조치 폼이 없으면 worker2에게 할당된 정상 상태인지 먼저 확인합니다. 관리자에게 화면 오류를 문의할 때 요청 번호·단계·발생 시각·오류 메시지를 전달하며 비밀번호는 보내지 않습니다.

## 25. 메뉴별 기능 전체 색인

다음 부록은 사용자 포털의 입력·조회·버튼을 메뉴별로 찾아보는 색인입니다. 본문 활용 예와 함께 읽습니다. 현재 계정에 모든 메뉴가 동시에 보이지 않으며, 관리자 기능은 해당 역할이 있는 경우에만 나타납니다. 반복 행은 행 스키마로 정의하고 ‘선택 항목’에는 실제 업무/사용자 이름이 표시됩니다. 최신 서비스요청은 위7단계와 그룹별 입력 제한을 우선합니다.

### 부록 UI-ACCOUNT_SECURITY · 내 계정 보안

경로: /account/security

UI-ACCOUNT_SECURITY-E001 · 포털 — a; 링크 이동: /

UI-ACCOUNT_SECURITY-E002 · 입력 항목 — p

UI-ACCOUNT_SECURITY-E003 · 입력 항목 — p

UI-ACCOUNT_SECURITY-E004 · action — hidden

UI-ACCOUNT_SECURITY-E005 · 현재 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E006 · 새 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E007 · 새 비밀번호 확인 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E008 · MFA 인증번호 또는 복구 코드 — text; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E009 · 비밀번호 변경 — submit; 폼 제출: submit → 현재 URL POST

UI-ACCOUNT_SECURITY-E010 · action — hidden

UI-ACCOUNT_SECURITY-E011 · 현재 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E012 · MFA 인증번호 또는 복구 코드 — text; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E013 · 재인증 — submit; 폼 제출: submit → 현재 URL POST

UI-ACCOUNT_SECURITY-E014 · 인증 앱에서 열기 — a; 링크 이동: 선택 항목

UI-ACCOUNT_SECURITY-E015 · action — hidden

UI-ACCOUNT_SECURITY-E016 · 현재 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E017 · 인증번호 — text; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E018 · MFA 등록 — submit; 폼 제출: submit → 현재 URL POST

UI-ACCOUNT_SECURITY-E019 · action — hidden

UI-ACCOUNT_SECURITY-E020 · 현재 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E021 · 인증번호 또는 복구 코드 — text; 필수(조건부 여부는 화면 표시 따름)

UI-ACCOUNT_SECURITY-E022 · MFA 해제 — submit; 폼 제출: submit → 현재 URL POST


### 부록 UI-ACTIVATE_ACCOUNT · 초대 계정 비밀번호 설정

경로: /activate/<str:uid>/

UI-ACTIVATE_ACCOUNT-E001 · 입력 항목 — p

UI-ACTIVATE_ACCOUNT-E002 · token — hidden

UI-ACTIVATE_ACCOUNT-E003 · 새 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACTIVATE_ACCOUNT-E004 · 비밀번호 확인 — password; 필수(조건부 여부는 화면 표시 따름)

UI-ACTIVATE_ACCOUNT-E005 · 계정 활성화 — submit; 폼 제출: submit → 현재 URL POST


### 부록 UI-ASSET_DETAIL · 자산 상세

경로: /assets/<uuid:id>

UI-ASSET_DETAIL-E001 · ← 자산 목록 — a; 링크 이동: /assets

UI-ASSET_DETAIL-E002 · 자산번호 — 조회/표시

UI-ASSET_DETAIL-E003 · 모델 — 조회/표시

UI-ASSET_DETAIL-E004 · 위치 — 조회/표시

UI-ASSET_DETAIL-E005 · 제조사 · 일련번호 — 조회/표시

UI-ASSET_DETAIL-E006 · 사용자 — 조회/표시

UI-ASSET_DETAIL-E007 · 재고 품목 — 조회/표시

UI-ASSET_DETAIL-E008 · 현재 보관 창고 — 조회/표시

UI-ASSET_DETAIL-E009 · 관련 서비스 요청 → — a; 링크 이동: /portal/requests/선택 항목

UI-ASSET_DETAIL-E010 · 다음 이력 → — a; 링크 이동: ?cursor=선택 항목

UI-ASSET_DETAIL-E011 · 입력 항목 — div

UI-ASSET_DETAIL-E012 · 자산 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-ASSET_DETAIL-E013 · 모델 — text; 최대 문자 200

UI-ASSET_DETAIL-E014 · 제조사 — text; 최대 문자 200

UI-ASSET_DETAIL-E015 · 일련번호 — text; 최대 문자 200

UI-ASSET_DETAIL-E016 · 수정 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-ASSET_DETAIL-E017 · 기본 자산 정보 공개 — checkbox

UI-ASSET_DETAIL-E018 · 정보 수정 — submit; 폼 제출: asset-update → /api/v1/assets/선택 항목

UI-ASSET_DETAIL-E019 · 입력 항목 — div

UI-ASSET_DETAIL-E020 · 처리 동작 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 동작 선택, 선택 항목

UI-ASSET_DETAIL-E021 · 수령자 — select; 선택: 수령자 선택, 선택 항목

UI-ASSET_DETAIL-E022 · 처리 후 위치 — text; 최대 문자 200

UI-ASSET_DETAIL-E023 · 서비스 요청 연결 · 선택 — select; 선택: 별도 요청 연결 없음, 선택 항목 · 선택 항목

UI-ASSET_DETAIL-E024 · 반납 창고 — select; 선택: 창고 선택, 선택 항목

UI-ASSET_DETAIL-E025 · 처리 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-ASSET_DETAIL-E026 · 자산 처리 — submit; 폼 제출: asset-action → /api/v1/assets/선택 항목/actions


### 부록 UI-ASSET_LIST · IT 자산

경로: /assets

UI-ASSET_LIST-E001 · + 자산 등록 — a; 링크 이동: /assets/new

UI-ASSET_LIST-E002 · 검색 — text; 최대 문자 200

UI-ASSET_LIST-E003 · 자산 상태 — select; 선택: 모든 상태, 선택 항목

UI-ASSET_LIST-E004 · 조회 — submit; 폼 제출: submit →

UI-ASSET_LIST-E005 · 자산 — 조회/표시

UI-ASSET_LIST-E006 · 상태 — 조회/표시

UI-ASSET_LIST-E007 · 모델 — 조회/표시

UI-ASSET_LIST-E008 · 위치 — 조회/표시

UI-ASSET_LIST-E009 · 사용자 — 조회/표시

UI-ASSET_LIST-E010 · 선택 항목 — a; 링크 이동: /assets/선택 항목

UI-ASSET_LIST-E011 · 다음 페이지 → — a; 링크 이동: ?q=선택 항목&status=선택 항목&cursor=선택 항목


### 부록 UI-ASSET_NEW · 자산 등록

경로: /assets/new

UI-ASSET_NEW-E001 · ← 자산 목록 — a; 링크 이동: /assets

UI-ASSET_NEW-E002 · 입력 항목 — div

UI-ASSET_NEW-E003 · 자산번호 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 80

UI-ASSET_NEW-E004 · 자산 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-ASSET_NEW-E005 · 제조사 — text; 최대 문자 200

UI-ASSET_NEW-E006 · 모델 — text; 최대 문자 200

UI-ASSET_NEW-E007 · 일련번호 — text; 최대 문자 200

UI-ASSET_NEW-E008 · 보관 위치 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-ASSET_NEW-E009 · 등록 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-ASSET_NEW-E010 · 조직 직원에게 기본 자산 정보 공개 — checkbox

UI-ASSET_NEW-E011 · 자산 등록 — submit; 폼 제출: asset-create → /api/v1/assets


### 부록 UI-BASE · 공통 셸·상단·사이드바·내 정보

경로: /, /account/security, /activate/<str:uid>/, /approvals, /assets, /assets/<uuid:id>, /assets/new, /catalog, /catalog/items/<uuid:id>, /cis, /cis/<uuid:id>, /contracts, /inventory, /inventory/movements, /login/mfa/, /my-assets, /notifications, /portal/incidents, /portal/incidents/<uuid:id>, /portal/incidents/new, /portal/requests, /portal/requests/<uuid:id>, /processes, /processes/<uuid:id>, /procurement/orders, /procurement/orders/<uuid:id>, /procurement/requisitions, /procurement/requisitions/<uuid:id>, /resources/changes, /resources/changes/<uuid:id>, /resources/deployments, /resources/deployments/<uuid:id>, /systems/asset, /systems/resource, /systems/service, /work/incidents, /work/incidents/<uuid:id>, /work/requests

UI-BASE-E001 · 본문으로 이동 — a; 링크 이동: #main

UI-BASE-E002 · 업무 포털 — a; 링크 이동: /

UI-BASE-E003 · ⌂ 통합 홈 ↗ — a; 링크 이동: /

UI-BASE-E004 · 선택 항목 › — a; 링크 이동: 선택 항목

UI-BASE-E005 · 선택 항목 선택 항목 — a; 링크 이동: 선택 항목

UI-BASE-E006 · 메뉴 닫기 — button; 클라이언트 조작: 메뉴 닫기

UI-BASE-E007 · 메뉴 열기 — button; 클라이언트 조작: 메뉴 열기

UI-BASE-E008 · 통합 ITSM — a; 링크 이동: /

UI-BASE-E009 · 선택 항목 — a; 링크 이동: 선택 항목

UI-BASE-E010 · 운영 콘솔 새 탭 열기 — a; 링크 이동: /console

UI-BASE-E011 · 내 계정 보안 — a; 링크 이동: /account/security

UI-BASE-E012 · 알림 선택 항목 — a; 링크 이동: /notifications

UI-BASE-E013 · 선택 항목 — button; 클라이언트 조작: 선택 항목

UI-BASE-E014 · 로그아웃 — submit; 폼 제출: submit → /logout/

UI-BASE-E015 · 입력 항목 — p

UI-BASE-E016 · 비밀번호 변경 — a; 링크 이동: /account/security

UI-BASE-E017 · 통합 포털 — a; 링크 이동: /

UI-BASE-E018 · 닫기 — button; 클라이언트 조작: 닫기

UI-BASE-E019 · data-profile-content — div

UI-BASE-E020 · 비밀번호 변경·내 계정 보안 — a; 링크 이동: /account/security


### 부록 UI-CATALOG_DETAIL · 서비스 신청

경로: /catalog/items/<uuid:id>

UI-CATALOG_DETAIL-E001 · ← 서비스 카탈로그 — a; 링크 이동: /catalog

UI-CATALOG_DETAIL-E002 · 입력 항목 — div

UI-CATALOG_DETAIL-E003 · 선택 항목 * — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 4000

UI-CATALOG_DETAIL-E004 · 선택 항목 * — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택하십시오., 선택 항목

UI-CATALOG_DETAIL-E005 · 선택 항목 * — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택하십시오., 예, 아니오

UI-CATALOG_DETAIL-E006 · 선택 항목 * —  number date text ; 필수(조건부 여부는 화면 표시 따름); 최대 문자 2000; 최소 -1000000000; 최대 1000000000

UI-CATALOG_DETAIL-E007 · 취소 — a; 링크 이동: /catalog

UI-CATALOG_DETAIL-E008 · 서비스 신청 → — submit; 폼 제출: request-create → /api/v1/requests


### 부록 UI-CATALOG_MANAGE · 카탈로그 관리

경로: /console/catalog, /work/catalog

UI-CATALOG_MANAGE-E001 · 입력 항목 — div

UI-CATALOG_MANAGE-E002 · 서비스 코드 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 40

UI-CATALOG_MANAGE-E003 · expected_version — hidden

UI-CATALOG_MANAGE-E004 · 서비스 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-CATALOG_MANAGE-E005 · 적용 워크플로우 — select; 선택: 메뉴 기본값 · 선택 항목 v선택 항목 기존 고정 처리 방식, 선택 항목 · v선택 항목

UI-CATALOG_MANAGE-E006 · 서비스 설명 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-CATALOG_MANAGE-E007 · 처리 그룹 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 그룹 선택, 선택 항목

UI-CATALOG_MANAGE-E008 · 지정 승인자 — select; 선택: 승인자 선택, 선택 항목

UI-CATALOG_MANAGE-E009 · 승인 필요 — checkbox

UI-CATALOG_MANAGE-E010 · 조직 전체 공개 — checkbox

UI-CATALOG_MANAGE-E011 · 신규 신청 허용 — checkbox

UI-CATALOG_MANAGE-E012 · 특정 그룹 공개 — select; 선택: 선택 항목

UI-CATALOG_MANAGE-E013 · + 항목 추가 — button; 클라이언트 조작: + 항목 추가

UI-CATALOG_MANAGE-E014 · 카탈로그 게시 — submit; 폼 제출: catalog-publish → /api/v1/catalog/versions

UI-CATALOG_MANAGE-E015 · 항목 식별자 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 40

UI-CATALOG_MANAGE-E016 · 항목 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 100

UI-CATALOG_MANAGE-E017 · 입력 종류 — select; 선택: 짧은 글, 긴 글, 정수, 선택, 날짜, 예 · 아니오

UI-CATALOG_MANAGE-E018 · 선택지 · 쉼표로 구분 — text

UI-CATALOG_MANAGE-E019 · 필수 항목 — checkbox

UI-CATALOG_MANAGE-E020 · 항목 제거 — button; 클라이언트 조작: 항목 제거

UI-CATALOG_MANAGE-E021 · 서비스 — 조회/표시

UI-CATALOG_MANAGE-E022 · 버전 — 조회/표시

UI-CATALOG_MANAGE-E023 · 신청 — 조회/표시

UI-CATALOG_MANAGE-E024 · 승인 — 조회/표시


### 부록 UI-CATALOG · 필요한 서비스를 신청하십시오.

경로: /catalog

UI-CATALOG-E001 · 서비스 검색 — text; 최대 문자 200

UI-CATALOG-E002 · 검색 — submit; 폼 제출: submit →

UI-CATALOG-E003 · 선택 항목 선택 항목 선택 항목 워크플로우 처리 승인 필요 바로 접수 신청하기 → — a; 링크 이동: /catalog/items/선택 항목

UI-CATALOG-E004 · 다음 페이지 → — a; 링크 이동: ?q=선택 항목&cursor=선택 항목


### 부록 UI-CONTRACTS · 공급업체 · 계약

경로: /contracts

UI-CONTRACTS-E001 · 입력 항목 — div

UI-CONTRACTS-E002 · 공급업체 코드 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 80

UI-CONTRACTS-E003 · 공급업체 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-CONTRACTS-E004 · 업무 연락처 — text; 최대 문자 200

UI-CONTRACTS-E005 · 공급업체 등록 — submit; 폼 제출: supplier → /api/v1/procurement/suppliers

UI-CONTRACTS-E006 · 입력 항목 — div

UI-CONTRACTS-E007 · 계약 코드 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 80

UI-CONTRACTS-E008 · 계약 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-CONTRACTS-E009 · 계약 공급업체 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 공급업체 선택, 선택 항목

UI-CONTRACTS-E010 · 시작일 — date; 필수(조건부 여부는 화면 표시 따름)

UI-CONTRACTS-E011 · 종료일 — date; 필수(조건부 여부는 화면 표시 따름)

UI-CONTRACTS-E012 · 계약 통화 — select; 선택: KRW, USD, EUR

UI-CONTRACTS-E013 · 계약 금액 한도 — number; 필수(조건부 여부는 화면 표시 따름); 최소 0.01

UI-CONTRACTS-E014 · 계약 메모 — textarea; 최대 문자 10000

UI-CONTRACTS-E015 · 계약 등록 — submit; 폼 제출: contract → /api/v1/procurement/contracts

UI-CONTRACTS-E016 · 계약 — 조회/표시

UI-CONTRACTS-E017 · 공급업체 — 조회/표시

UI-CONTRACTS-E018 · 유효기간 — 조회/표시

UI-CONTRACTS-E019 · 한도 / 확정 발주 / 잔여 — 조회/표시

UI-CONTRACTS-E020 · 다음 페이지 → — a; 링크 이동: ?cursor=선택 항목

UI-CONTRACTS-E021 · 입력 항목 — div

UI-CONTRACTS-E022 · 자산 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 자산 선택, 선택 항목 · 선택 항목

UI-CONTRACTS-E023 · 연결 계약 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 계약 선택, 선택 항목 · 선택 항목

UI-CONTRACTS-E024 · 연결 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-CONTRACTS-E025 · 자산 계약 연결 — submit; 폼 제출: asset-contract → /api/v1/procurement/asset-contracts


### 부록 UI-DASHBOARD_TASKS · 내가 할 일 공통 영역

경로: /, /systems/asset, /systems/resource, /systems/service

UI-DASHBOARD_TASKS-E001 · 선택 항목 — a; 링크 이동: 선택 항목

UI-DASHBOARD_TASKS-E002 · 업무 — 조회/표시

UI-DASHBOARD_TASKS-E003 · 유형 — 조회/표시

UI-DASHBOARD_TASKS-E004 · 현재 단계 — 조회/표시

UI-DASHBOARD_TASKS-E005 · 생성일 — 조회/표시

UI-DASHBOARD_TASKS-E006 · 선택 항목 — a; 링크 이동: 선택 항목


### 부록 UI-DELIVERY_LIST · 선택 항목

경로: /resources/changes, /resources/changes/<uuid:id>, /resources/deployments, /resources/deployments/<uuid:id>

UI-DELIVERY_LIST-E001 · IT자원 현황 — a; 링크 이동: /systems/resource

UI-DELIVERY_LIST-E002 · 제공자 · 원문 식별자 — 조회/표시

UI-DELIVERY_LIST-E003 · 상태 — 조회/표시

UI-DELIVERY_LIST-E004 · 저장소 · 브랜치 — 조회/표시

UI-DELIVERY_LIST-E005 · 커밋 — 조회/표시

UI-DELIVERY_LIST-E006 · 빌드 결과 — 조회/표시

UI-DELIVERY_LIST-E007 · 서비스 · 버전 — 조회/표시

UI-DELIVERY_LIST-E008 · 대상 환경 — 조회/표시

UI-DELIVERY_LIST-E009 · 외부 계정 — 조회/표시

UI-DELIVERY_LIST-E010 · 발생 시각 — 조회/표시

UI-DELIVERY_LIST-E011 · 수신 시각 — 조회/표시

UI-DELIVERY_LIST-E012 · 원문에서 확인 ↗ — a; 링크 이동: 선택 항목

UI-DELIVERY_LIST-E013 · 제목·저장소·서비스 검색 — text; 최대 문자 150

UI-DELIVERY_LIST-E014 · 상태 — select; 선택: 전체, 선택 항목

UI-DELIVERY_LIST-E015 · build_status — hidden

UI-DELIVERY_LIST-E016 · 조회 — submit; 폼 제출: submit → 현재 URL 조회 조건

UI-DELIVERY_LIST-E017 · 제목 — 조회/표시

UI-DELIVERY_LIST-E018 · 저장소 · 브랜치 서비스 · 버전 · 환경 — 조회/표시

UI-DELIVERY_LIST-E019 · 상태 — 조회/표시

UI-DELIVERY_LIST-E020 · 외부 계정 — 조회/표시

UI-DELIVERY_LIST-E021 · 발생 시각 — 조회/표시

UI-DELIVERY_LIST-E022 · 선택 항목 — a; 링크 이동: 선택 항목

UI-DELIVERY_LIST-E023 · 이전 — a; 링크 이동: ?선택 항목&page=선택 항목

UI-DELIVERY_LIST-E024 · 다음 — a; 링크 이동: ?선택 항목&page=선택 항목


### 부록 UI-DELIVERY_OVERVIEW · IT자원 요약 현황

경로: /, /systems/asset, /systems/resource, /systems/service

UI-DELIVERY_OVERVIEW-E001 · 선택 항목 선택 항목 — a; 링크 이동: 선택 항목

UI-DELIVERY_OVERVIEW-E002 · 전체 보기 → — a; 링크 이동: /resources/changes

UI-DELIVERY_OVERVIEW-E003 · 저장소 · 브랜치 — 조회/표시

UI-DELIVERY_OVERVIEW-E004 · 변경 제목 · PR/커밋 — 조회/표시

UI-DELIVERY_OVERVIEW-E005 · 변경 계정 — 조회/표시

UI-DELIVERY_OVERVIEW-E006 · 검토 상태 — 조회/표시

UI-DELIVERY_OVERVIEW-E007 · 빌드 — 조회/표시

UI-DELIVERY_OVERVIEW-E008 · 변경일 — 조회/표시

UI-DELIVERY_OVERVIEW-E009 · 선택 항목 — a; 링크 이동: 선택 항목

UI-DELIVERY_OVERVIEW-E010 · 전체 보기 → — a; 링크 이동: /resources/deployments

UI-DELIVERY_OVERVIEW-E011 · 서비스 — 조회/표시

UI-DELIVERY_OVERVIEW-E012 · 배포 버전 — 조회/표시

UI-DELIVERY_OVERVIEW-E013 · 대상 환경 — 조회/표시

UI-DELIVERY_OVERVIEW-E014 · 승인·실행 상태 — 조회/표시

UI-DELIVERY_OVERVIEW-E015 · 배포 계정 — 조회/표시

UI-DELIVERY_OVERVIEW-E016 · 배포일 — 조회/표시

UI-DELIVERY_OVERVIEW-E017 · 선택 항목 — a; 링크 이동: 선택 항목


### 부록 UI-DETAIL · 장애 상세

경로: /portal/incidents/<uuid:id>, /work/incidents/<uuid:id>

UI-DETAIL-E001 · ← 목록으로 — a; 링크 이동: /work /portal /incidents

UI-DETAIL-E002 · 담당 그룹 — 조회/표시

UI-DETAIL-E003 · 담당자 — 조회/표시

UI-DETAIL-E004 · 우선순위 — 조회/표시

UI-DETAIL-E005 · 입력 항목 — div

UI-DETAIL-E006 · 담당자 배정 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 담당자 선택, 선택 항목

UI-DETAIL-E007 · 배정 저장 — submit; 폼 제출: assign → /api/v1/incidents/선택 항목/assign

UI-DETAIL-E008 · 입력 항목 — div

UI-DETAIL-E009 · 다음 동작 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 동작 선택, 처리 시작 대기로 전환 처리 재개 해결 완료 해결 확인 · 종료 재개방

UI-DETAIL-E010 · 사유 대기·재개방 시 필수 — textarea; 최대 문자 10000

UI-DETAIL-E011 · 해결 내용 해결 완료 시 필수 — textarea; 최대 문자 10000

UI-DETAIL-E012 · 상태 변경 — submit; 폼 제출: transition → /api/v1/incidents/선택 항목/transitions

UI-DETAIL-E013 · 입력 항목 — div

UI-DETAIL-E014 · 연결 해제 — submit; 폼 제출: detach → /api/v1/incidents/선택 항목/resources/선택 항목

UI-DETAIL-E015 · 입력 항목 — div

UI-DETAIL-E016 · 대상 연결 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 대상 선택, 자산 · 선택 항목, CI · 선택 항목

UI-DETAIL-E017 · 연결 — submit; 폼 제출: attach → /api/v1/incidents/선택 항목/resources

UI-DETAIL-E018 · 대화와 처리 기록 — summary; 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음

UI-DETAIL-E019 · 입력 항목 — div

UI-DETAIL-E020 · 댓글 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-DETAIL-E021 · 댓글 공개 범위 — select; 선택: 공개 · 요청자에게 표시, 내부 · 담당자만 표시

UI-DETAIL-E022 · 댓글 등록 — submit; 폼 제출: comment → /api/v1/incidents/선택 항목/comments

UI-DETAIL-E023 · 상태 이력 — summary; 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음


### 부록 UI-INVENTORY · 창고 · 재고

경로: /inventory

UI-INVENTORY-E001 · 수불 이력 → — a; 링크 이동: /inventory/movements

UI-INVENTORY-E002 · 품목 — 조회/표시

UI-INVENTORY-E003 · 창고 — 조회/표시

UI-INVENTORY-E004 · 추적 방식 — 조회/표시

UI-INVENTORY-E005 · 현재 수량 — 조회/표시

UI-INVENTORY-E006 · 다음 페이지 → — a; 링크 이동: ?cursor=선택 항목

UI-INVENTORY-E007 · 입력 항목 — div

UI-INVENTORY-E008 · 출발 재고 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 품목 · 창고 선택, 선택 항목 · 선택 항목 · 선택 항목개

UI-INVENTORY-E009 · 도착 창고 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 창고 선택, 선택 항목

UI-INVENTORY-E010 · 이동 수량 — number; 필수(조건부 여부는 화면 표시 따름); 최소 1; 최대 1000000

UI-INVENTORY-E011 · 이동할 개별 자산 — select; 선택: 선택 항목 · 선택 항목

UI-INVENTORY-E012 · 이동 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-INVENTORY-E013 · 재고 이동 — submit; 폼 제출: stock-transfer → /api/v1/inventory/transfer

UI-INVENTORY-E014 · 입력 항목 — div

UI-INVENTORY-E015 · 출고 재고 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 수량 품목 선택, 선택 항목 · 선택 항목 · 선택 항목개

UI-INVENTORY-E016 · 출고 수량 — number; 필수(조건부 여부는 화면 표시 따름); 최소 1; 최대 1000000

UI-INVENTORY-E017 · 수령자 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택하십시오., 선택 항목

UI-INVENTORY-E018 · 사용 위치 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-INVENTORY-E019 · 관련 서비스 요청 · 선택 — select; 선택: 연결 없음, 선택 항목 · 선택 항목

UI-INVENTORY-E020 · 출고 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-INVENTORY-E021 · 소모품 출고 — submit; 폼 제출: stock-issue → /api/v1/inventory/issue

UI-INVENTORY-E022 · 입력 항목 — div

UI-INVENTORY-E023 · 창고 코드 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 80

UI-INVENTORY-E024 · 창고 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-INVENTORY-E025 · 창고 위치 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-INVENTORY-E026 · 창고 등록 — submit; 폼 제출: stockroom → /api/v1/inventory/stockrooms

UI-INVENTORY-E027 · 입력 항목 — div

UI-INVENTORY-E028 · 품목 코드 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 80

UI-INVENTORY-E029 · 품목 이름 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-INVENTORY-E030 · 추적 방식 — select; 선택: 수량 품목, 일련번호 장비

UI-INVENTORY-E031 · 품목 제조사 · 장비 필수 — text; 최대 문자 200

UI-INVENTORY-E032 · 품목 모델 — text; 최대 문자 200

UI-INVENTORY-E033 · 품목 등록 — submit; 폼 제출: stock-item → /api/v1/inventory/items


### 부록 UI-LIST · 장애 목록

경로: /portal/incidents, /work/incidents

UI-LIST-E001 · + 장애 접수 — a; 링크 이동: /portal/incidents/new

UI-LIST-E002 · 상태 — select; 선택: 전체, 접수, 배정, 처리 중, 대기, 해결, 종료

UI-LIST-E003 · 적용 — submit; 폼 제출: submit → 현재 URL 조회 조건

UI-LIST-E004 · 요청 · 제목 — 조회/표시

UI-LIST-E005 · 상태 — 조회/표시

UI-LIST-E006 · 우선순위 — 조회/표시

UI-LIST-E007 · 담당자 — 조회/표시

UI-LIST-E008 · SLA 해결 기한 — 조회/표시

UI-LIST-E009 · 접수일 — 조회/표시

UI-LIST-E010 · 선택 항목 — a; 링크 이동: /work /portal /incidents/선택 항목

UI-LIST-E011 · 다음 페이지 → — a; 링크 이동: ?status=선택 항목&cursor=선택 항목


### 부록 UI-MFA_LOGIN · 추가 인증

경로: /login/mfa/

UI-MFA_LOGIN-E001 · 입력 항목 — p

UI-MFA_LOGIN-E002 · 인증번호 또는 복구 코드 — text; 필수(조건부 여부는 화면 표시 따름)

UI-MFA_LOGIN-E003 · 인증 — submit; 폼 제출: submit → 현재 URL POST


### 부록 UI-MY_ASSETS · 내 지급 자산

경로: /my-assets

UI-MY_ASSETS-E001 · 자산 — 조회/표시

UI-MY_ASSETS-E002 · 모델 — 조회/표시

UI-MY_ASSETS-E003 · 위치 — 조회/표시

UI-MY_ASSETS-E004 · 상태 — 조회/표시

UI-MY_ASSETS-E005 · 선택 항목 — a; 링크 이동: /assets/선택 항목

UI-MY_ASSETS-E006 · 관련 요청 확인 → — a; 링크 이동: /portal/requests/선택 항목

UI-MY_ASSETS-E007 · 다음 이력 → — a; 링크 이동: ?cursor=선택 항목


### 부록 UI-NEW · 장애 등록

경로: /portal/incidents/new

UI-NEW-E001 · ← 요청 목록 — a; 링크 이동: /portal/incidents

UI-NEW-E002 · 입력 항목 — div

UI-NEW-E003 · 제목 * — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-NEW-E004 · 상세 내용 * — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-NEW-E005 · 영향도 — select; 선택: 낮음 · 개인 업무, 보통 · 일부 부서, 높음 · 조직 전체

UI-NEW-E006 · 긴급도 — select; 선택: 낮음 · 우회 가능, 보통 · 업무 지연, 높음 · 업무 중단

UI-NEW-E007 · 관련 자산 또는 CI 선택 — select; 선택: 선택하지 않음, 자산 · 선택 항목, CI · 선택 항목

UI-NEW-E008 · 취소 — a; 링크 이동: /portal/incidents

UI-NEW-E009 · 장애 접수 → — submit; 폼 제출: create → /api/v1/incidents


### 부록 UI-NOTIFICATIONS · 알림함

경로: /notifications

UI-NOTIFICATIONS-E001 · 선택 항목 — a; 링크 이동: 선택 항목

UI-NOTIFICATIONS-E002 · 입력 항목 — div

UI-NOTIFICATIONS-E003 · 확인 — submit; 폼 제출: notification-read → /api/v1/notifications/선택 항목/read

UI-NOTIFICATIONS-E004 · 다음 페이지 → — a; 링크 이동: ?cursor=선택 항목


### 부록 UI-PORTAL · 통합 포털

경로: /

UI-PORTAL-E001 · ↗ ▦ ⌘ SYSTEM 선택 항목 선택 항목 선택 항목 서비스 요청 장애 · 승인 SLA 자산 대장 구매 · 계약 재고 소스 변경 빌드 현황 배포 현황 — a; 링크 이동: 선택 항목

UI-PORTAL-E002 · 01 서비스 요청하기 필요한 서비스를 찾아 신청하세요 ↗ — a; 링크 이동: /catalog

UI-PORTAL-E003 · 02 장애 접수하기 IT 이용 중 발생한 문제를 알려주세요 ↗ — a; 링크 이동: /portal/incidents/new

UI-PORTAL-E004 · 03 내 지급 자산 사용 중인 자산과 지급 이력을 확인하세요 ↗ — a; 링크 이동: /my-assets

UI-PORTAL-E005 · 04 구성항목 찾아보기 조회 가능한 구성항목을 확인하세요 ↗ — a; 링크 이동: /cis

UI-PORTAL-E006 · 서비스 승인 대기 선택 항목 건 — a; 링크 이동: /approvals

UI-PORTAL-E007 · 읽지 않은 알림 선택 항목 건 — a; 링크 이동: /notifications

UI-PORTAL-E008 · 전체 현황 → — a; 링크 이동: /systems/resource


### 부록 UI-PROCESS_FIELD · 태스크 동적 입력 필드

경로: 상위 화면 공통 영역

UI-PROCESS_FIELD-E001 · 선택 항목 * — select; 필수(조건부 여부는 화면 표시 따름); 선택: 담당자 선택, 선택 항목

UI-PROCESS_FIELD-E002 · 선택 항목 * — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택, 예, 아니오

UI-PROCESS_FIELD-E003 · 선택 항목 * — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 선택 항목


### 부록 UI-PROCESS_INBOX · 워크플로우 업무·결재 목록/상세

경로: /processes, /processes/<uuid:id>

UI-PROCESS_INBOX-E001 · 목록 — a; 링크 이동: /processes

UI-PROCESS_INBOX-E002 · 연결된 서비스요청 — a; 링크 이동: /portal/requests/선택 항목

UI-PROCESS_INBOX-E003 · 상위 프로세스 · 선택 항목 — a; 링크 이동: /processes/선택 항목

UI-PROCESS_INBOX-E004 · task_id — hidden

UI-PROCESS_INBOX-E005 · 처리 결과 — select; 선택: 승인, 반려, 업무 완료

UI-PROCESS_INBOX-E006 · 처리 사유·의견 — text; 최대 문자 2000

UI-PROCESS_INBOX-E007 · 처리·다음 단계 진행 — submit; 폼 제출: flow-act → /api/v1/process-runs/act/선택 항목

UI-PROCESS_INBOX-E008 · 선택 항목 — a; 링크 이동: /processes/선택 항목

UI-PROCESS_INBOX-E009 · 운영자 재할당 — summary; 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음

UI-PROCESS_INBOX-E010 · task_id — hidden

UI-PROCESS_INBOX-E011 · 담당자 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택 항목

UI-PROCESS_INBOX-E012 · 재할당 사유 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 2000

UI-PROCESS_INBOX-E013 · 재할당 — submit; 폼 제출: flow-reassign → /api/v1/process-runs/reassign/선택 항목

UI-PROCESS_INBOX-E014 · task_id — hidden

UI-PROCESS_INBOX-E015 · 반려·취소 하위 작업 재실행 사유 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 2000

UI-PROCESS_INBOX-E016 · 실패 하위 작업 재실행 — submit; 폼 제출: flow-retry_children → /api/v1/process-runs/retry_children/선택 항목

UI-PROCESS_INBOX-E017 · task_id — hidden

UI-PROCESS_INBOX-E018 · 결과 조정 사유 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 2000

UI-PROCESS_INBOX-E019 · 완료된 하위 결과 확정 — submit; 폼 제출: flow-resolve_outputs → /api/v1/process-runs/resolve_outputs/선택 항목

UI-PROCESS_INBOX-E020 · 대기 만료 처리 사유 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 2000

UI-PROCESS_INBOX-E021 · 만료된 대기 진행 — submit; 폼 제출: flow-tick → /api/v1/process-runs/tick/선택 항목

UI-PROCESS_INBOX-E022 · 취소 사유 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 2000

UI-PROCESS_INBOX-E023 · 진행 중인 하위 실행도 취소됨을 확인합니다. — checkbox; 필수(조건부 여부는 화면 표시 따름)

UI-PROCESS_INBOX-E024 · 실행 취소 — submit; 폼 제출: flow-cancel → /api/v1/process-runs/cancel/선택 항목

UI-PROCESS_INBOX-E025 · 선택 항목 · v선택 항목 — a; 링크 이동: ?start=선택 항목

UI-PROCESS_INBOX-E026 · version_id — hidden

UI-PROCESS_INBOX-E027 · 업무 제목 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 300

UI-PROCESS_INBOX-E028 · 프로세스 시작 — submit; 폼 제출: flow-start → /api/v1/process-runs/start

UI-PROCESS_INBOX-E029 · 조회 가능 — a; 링크 이동: ?scope=all

UI-PROCESS_INBOX-E030 · 내 시작 건 — a; 링크 이동: ?scope=mine

UI-PROCESS_INBOX-E031 · 내 처리 대기 — a; 링크 이동: ?scope=assigned

UI-PROCESS_INBOX-E032 · 업무 — 조회/표시

UI-PROCESS_INBOX-E033 · 프로세스·버전 — 조회/표시

UI-PROCESS_INBOX-E034 · 상태 — 조회/표시

UI-PROCESS_INBOX-E035 · 시작일 — 조회/표시

UI-PROCESS_INBOX-E036 · 선택 항목 — a; 링크 이동: /processes/선택 항목

UI-PROCESS_INBOX-E037 · 이전 — a; 링크 이동: ?scope=선택 항목&page=선택 항목

UI-PROCESS_INBOX-E038 · 다음 — a; 링크 이동: ?scope=선택 항목&page=선택 항목


### 부록 UI-PURCHASE_ORDER_DETAIL · 발주 상세

경로: /procurement/orders, /procurement/orders/<uuid:id>

UI-PURCHASE_ORDER_DETAIL-E001 · ← 발주 목록 — a; 링크 이동: /procurement/orders

UI-PURCHASE_ORDER_DETAIL-E002 · 발주 / 입고 / 잔량 — 조회/표시

UI-PURCHASE_ORDER_DETAIL-E003 · 단가 · 합계 — 조회/표시

UI-PURCHASE_ORDER_DETAIL-E004 · 입력 항목 — div

UI-PURCHASE_ORDER_DETAIL-E005 · 동작 — select; 선택: 발주 확정, 발주 취소

UI-PURCHASE_ORDER_DETAIL-E006 · 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-PURCHASE_ORDER_DETAIL-E007 · 발주 처리 — submit; 폼 제출: purchase-order-action → /api/v1/procurement/orders/선택 항목/actions

UI-PURCHASE_ORDER_DETAIL-E008 · 입력 항목 — div

UI-PURCHASE_ORDER_DETAIL-E009 · 입고 창고 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 창고 선택, 선택 항목

UI-PURCHASE_ORDER_DETAIL-E010 · 이번 입고 수량 — number; 필수(조건부 여부는 화면 표시 따름); 최소 1; 최대 선택 항목

UI-PURCHASE_ORDER_DETAIL-E011 · 입고 참조번호 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 80

UI-PURCHASE_ORDER_DETAIL-E012 · 개별 장비 · 한 줄에 자산번호,일련번호 — textarea; 필수(조건부 여부는 화면 표시 따름)

UI-PURCHASE_ORDER_DETAIL-E013 · 입고 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-PURCHASE_ORDER_DETAIL-E014 · 입고 확정 — submit; 폼 제출: purchase-receipt → /api/v1/procurement/orders/선택 항목/receipts

UI-PURCHASE_ORDER_DETAIL-E015 · 선택 항목 → — a; 링크 이동: /assets/선택 항목


### 부록 UI-PURCHASE_ORDERS · 발주 · 입고

경로: /procurement/orders

UI-PURCHASE_ORDERS-E001 · 구매 요청 → — a; 링크 이동: /procurement/requisitions

UI-PURCHASE_ORDERS-E002 · 발주 — 조회/표시

UI-PURCHASE_ORDERS-E003 · 공급업체 — 조회/표시

UI-PURCHASE_ORDERS-E004 · 수량 · 입고 — 조회/표시

UI-PURCHASE_ORDERS-E005 · 상태 — 조회/표시

UI-PURCHASE_ORDERS-E006 · 금액 — 조회/표시

UI-PURCHASE_ORDERS-E007 · 선택 항목 — a; 링크 이동: /procurement/orders/선택 항목

UI-PURCHASE_ORDERS-E008 · 다음 페이지 → — a; 링크 이동: ?cursor=선택 항목


### 부록 UI-PURCHASE_REQUEST_DETAIL · 구매요청 상세

경로: /procurement/requisitions, /procurement/requisitions/<uuid:id>

UI-PURCHASE_REQUEST_DETAIL-E001 · ← 구매 요청 — a; 링크 이동: /procurement/requisitions

UI-PURCHASE_REQUEST_DETAIL-E002 · 수량 — 조회/표시

UI-PURCHASE_REQUEST_DETAIL-E003 · 승인 단가 한도 — 조회/표시

UI-PURCHASE_REQUEST_DETAIL-E004 · 예산 합계 한도 — 조회/표시

UI-PURCHASE_REQUEST_DETAIL-E005 · 사유 — 조회/표시

UI-PURCHASE_REQUEST_DETAIL-E006 · 입력 항목 — div

UI-PURCHASE_REQUEST_DETAIL-E007 · 결정 — select; 선택: 승인, 반려

UI-PURCHASE_REQUEST_DETAIL-E008 · 결정 사유 · 반려 시 필수 — textarea; 최대 문자 10000

UI-PURCHASE_REQUEST_DETAIL-E009 · 구매 결정 저장 — submit; 폼 제출: purchase-decision → /api/v1/procurement/requisitions/선택 항목/decision

UI-PURCHASE_REQUEST_DETAIL-E010 · 입력 항목 — div

UI-PURCHASE_REQUEST_DETAIL-E011 · 공급업체 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 공급업체 선택, 선택 항목

UI-PURCHASE_REQUEST_DETAIL-E012 · 계약 · 선택 — select; 선택: 계약 없음, 선택 항목 · 선택 항목

UI-PURCHASE_REQUEST_DETAIL-E013 · 발주 단가 · 선택 항목 — number; 필수(조건부 여부는 화면 표시 따름); 최소 0.01; 최대 선택 항목

UI-PURCHASE_REQUEST_DETAIL-E014 · 발주 초안 생성 — submit; 폼 제출: purchase-order → /api/v1/procurement/orders

UI-PURCHASE_REQUEST_DETAIL-E015 · 입력 항목 — div

UI-PURCHASE_REQUEST_DETAIL-E016 · 취소 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-PURCHASE_REQUEST_DETAIL-E017 · 요청 취소 — submit; 폼 제출: purchase-cancel-request → /api/v1/procurement/requisitions/선택 항목/cancel


### 부록 UI-PURCHASE_REQUESTS · 구매 요청 · 승인

경로: /procurement/requisitions

UI-PURCHASE_REQUESTS-E001 · 발주 목록 → — a; 링크 이동: /procurement/orders

UI-PURCHASE_REQUESTS-E002 · 입력 항목 — div

UI-PURCHASE_REQUESTS-E003 · 품목 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택하십시오., 선택 항목 · 선택 항목

UI-PURCHASE_REQUESTS-E004 · 수량 — number; 필수(조건부 여부는 화면 표시 따름); 최소 1; 최대 1000000

UI-PURCHASE_REQUESTS-E005 · 통화 — select; 선택: KRW, USD, EUR

UI-PURCHASE_REQUESTS-E006 · 승인 요청 단가 한도 — number; 필수(조건부 여부는 화면 표시 따름); 최소 0.01

UI-PURCHASE_REQUESTS-E007 · 구매 승인자 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 구매 관리자 선택, 선택 항목

UI-PURCHASE_REQUESTS-E008 · 관련 서비스 요청 · 선택 — select; 선택: 연결 없음, 선택 항목 · 선택 항목

UI-PURCHASE_REQUESTS-E009 · 구매 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-PURCHASE_REQUESTS-E010 · 구매 요청 — submit; 폼 제출: purchase-request → /api/v1/procurement/requisitions

UI-PURCHASE_REQUESTS-E011 · 품목 — 조회/표시

UI-PURCHASE_REQUESTS-E012 · 수량 — 조회/표시

UI-PURCHASE_REQUESTS-E013 · 예산 한도 — 조회/표시

UI-PURCHASE_REQUESTS-E014 · 승인자 — 조회/표시

UI-PURCHASE_REQUESTS-E015 · 상태 — 조회/표시

UI-PURCHASE_REQUESTS-E016 · 선택 항목 — a; 링크 이동: /procurement/requisitions/선택 항목

UI-PURCHASE_REQUESTS-E017 · 다음 페이지 → — a; 링크 이동: ?cursor=선택 항목


### 부록 UI-REQUEST_ASSETS · 서비스요청 자산 연결

경로: /portal/requests/<uuid:id>

UI-REQUEST_ASSETS-E001 · 선택 항목 — a; 링크 이동: /assets/선택 항목

UI-REQUEST_ASSETS-E002 · 입력 항목 — div

UI-REQUEST_ASSETS-E003 · 지급할 자산 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 보관 중인 자산 선택, 선택 항목 · 선택 항목

UI-REQUEST_ASSETS-E004 · 지급 후 위치 — text; 필수(조건부 여부는 화면 표시 따름); 최대 문자 200

UI-REQUEST_ASSETS-E005 · 지급 사유 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-REQUEST_ASSETS-E006 · 요청에 연결해 지급 — submit; 폼 제출: request-asset-issue →


### 부록 UI-REQUEST_DETAIL · 서비스요청 상세

경로: /portal/requests/<uuid:id>

UI-REQUEST_DETAIL-E001 · SLA 합의 시각·기한 관리 — a; 링크 이동: /console/slm/agreements/선택 항목

UI-REQUEST_DETAIL-E002 · ← 서비스 요청 목록 — a; 링크 이동: /portal/requests

UI-REQUEST_DETAIL-E003 · 업무·결재 진행 화면 → — a; 링크 이동: /processes/선택 항목

UI-REQUEST_DETAIL-E004 · 선택 항목 — 조회/표시

UI-REQUEST_DETAIL-E005 · 이전 요청 확인 → — a; 링크 이동: /portal/requests/선택 항목

UI-REQUEST_DETAIL-E006 · 지정 승인자 — 조회/표시

UI-REQUEST_DETAIL-E007 · 승인 상태 — 조회/표시

UI-REQUEST_DETAIL-E008 · 결정 사유 — 조회/표시

UI-REQUEST_DETAIL-E009 · 입력 항목 — div

UI-REQUEST_DETAIL-E010 · 승인 결정 — select; 선택: 승인, 반려

UI-REQUEST_DETAIL-E011 · 결정 사유 반려 시 필수 — textarea; 최대 문자 10000

UI-REQUEST_DETAIL-E012 · 결정 저장 — submit; 폼 제출: request-decision → /api/v1/requests/선택 항목/decision

UI-REQUEST_DETAIL-E013 · 처리 그룹 — 조회/표시

UI-REQUEST_DETAIL-E014 · 담당자 — 조회/표시

UI-REQUEST_DETAIL-E015 · 입력 항목 — div

UI-REQUEST_DETAIL-E016 · 담당자 배정 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 담당자 선택, 선택 항목

UI-REQUEST_DETAIL-E017 · 배정 저장 — submit; 폼 제출: request-assign → /api/v1/requests/선택 항목/assign

UI-REQUEST_DETAIL-E018 · 입력 항목 — div

UI-REQUEST_DETAIL-E019 · 다음 동작 — select; 필수(조건부 여부는 화면 표시 따름); 선택: 선택하십시오., 처리 시작 처리 완료 확인 · 종료 신청 취소

UI-REQUEST_DETAIL-E020 · 처리 내용 · 취소 사유 — textarea; 최대 문자 10000

UI-REQUEST_DETAIL-E021 · 요청 처리 — submit; 폼 제출: request-action → /api/v1/requests/선택 항목/actions

UI-REQUEST_DETAIL-E022 · 다시 신청하기 → — a; 링크 이동: /catalog/items/선택 항목?resubmission_of=선택 항목

UI-REQUEST_DETAIL-E023 · 대화 — summary; 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음

UI-REQUEST_DETAIL-E024 · 입력 항목 — div

UI-REQUEST_DETAIL-E025 · 댓글 — textarea; 필수(조건부 여부는 화면 표시 따름); 최대 문자 10000

UI-REQUEST_DETAIL-E026 · 댓글 공개 범위 — select; 선택: 공개 · 요청자에게 표시, 내부 · 처리 담당자만 표시

UI-REQUEST_DETAIL-E027 · 댓글 등록 — submit; 폼 제출: comment → /api/v1/requests/선택 항목/comments

UI-REQUEST_DETAIL-E028 · 처리 이력 — summary; 상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음


### 부록 UI-REQUEST_LIST · 승인함 서비스 요청 처리 전체 서비스 요청 내 서비스 요청

경로: /approvals, /portal/requests, /work/requests

UI-REQUEST_LIST-E001 · + 서비스 신청 — a; 링크 이동: /catalog

UI-REQUEST_LIST-E002 · 상태 — select; 선택: 전체, 선택 항목

UI-REQUEST_LIST-E003 · 적용 — submit; 폼 제출: submit →

UI-REQUEST_LIST-E004 · 서비스 요청 — 조회/표시

UI-REQUEST_LIST-E005 · 상태 — 조회/표시

UI-REQUEST_LIST-E006 · 담당자 — 조회/표시

UI-REQUEST_LIST-E007 · 접수일 — 조회/표시

UI-REQUEST_LIST-E008 · 선택 항목 — a; 링크 이동: /portal/requests/선택 항목

UI-REQUEST_LIST-E009 · 다음 페이지 → — a; 링크 이동: ?status=선택 항목&cursor=선택 항목


### 부록 UI-RESOURCE_DETAIL · 구성항목 상세

경로: /cis, /cis/<uuid:id>

UI-RESOURCE_DETAIL-E001 · ← 목록으로 — a; 링크 이동: /cis /assets

UI-RESOURCE_DETAIL-E002 · 번호 — 조회/표시

UI-RESOURCE_DETAIL-E003 · 유형 모델 — 조회/표시

UI-RESOURCE_DETAIL-E004 · 상태 위치 — 조회/표시


### 부록 UI-RESOURCES · 구성항목 · CI IT 자산

경로: /cis, /cis/<uuid:id>

UI-RESOURCES-E001 · 이름 검색 — text; 최대 문자 200

UI-RESOURCES-E002 · 검색 — submit; 폼 제출: submit →

UI-RESOURCES-E003 · 번호 — 조회/표시

UI-RESOURCES-E004 · 이름 — 조회/표시

UI-RESOURCES-E005 · 유형 모델 — 조회/표시

UI-RESOURCES-E006 · 상태 위치 — 조회/표시

UI-RESOURCES-E007 · 선택 항목 — a; 링크 이동: /cis /assets /선택 항목

UI-RESOURCES-E008 · 다음 페이지 → — a; 링크 이동: ?q=선택 항목&cursor=선택 항목


### 부록 UI-SLA_CARD · SLA 현황 카드

경로: /portal/incidents/<uuid:id>, /work/incidents/<uuid:id>

UI-SLA_CARD-E001 · 응답 목표 시간 사용률 — 조회/표시; 최대 100

UI-SLA_CARD-E002 · 해결 목표 시간 사용률 — 조회/표시; 최대 100


### 부록 UI-STOCK_MOVEMENTS · 입출고 · 이동 이력

경로: /inventory/movements

UI-STOCK_MOVEMENTS-E001 · ← 재고 현황 — a; 링크 이동: /inventory

UI-STOCK_MOVEMENTS-E002 · 품목 · 동작 — 조회/표시

UI-STOCK_MOVEMENTS-E003 · 수량 — 조회/표시

UI-STOCK_MOVEMENTS-E004 · 출발 → 도착 — 조회/표시

UI-STOCK_MOVEMENTS-E005 · 담당자 — 조회/표시

UI-STOCK_MOVEMENTS-E006 · 시각 — 조회/표시

UI-STOCK_MOVEMENTS-E007 · 다음 페이지 → — a; 링크 이동: ?cursor=선택 항목


### 부록 UI-SYSTEM_HOME · 시스템별 업무 현황

경로: /systems/asset, /systems/resource, /systems/service

UI-SYSTEM_HOME-E001 · 선택 항목 ＋ — a; 링크 이동: 선택 항목

UI-SYSTEM_HOME-E002 · 선택 항목 선택 항목 건 ↗ — a; 링크 이동: 선택 항목

UI-SYSTEM_HOME-E003 · 번호 · 이름 — 조회/표시

UI-SYSTEM_HOME-E004 · 상태 — 조회/표시

UI-SYSTEM_HOME-E005 · 상세 — 조회/표시

UI-SYSTEM_HOME-E006 · 선택 항목 — a; 링크 이동: 선택 항목

UI-SYSTEM_HOME-E007 · 선택 항목 상세 보기 — a; 링크 이동: 선택 항목

UI-SYSTEM_HOME-E008 · 선택 항목 — a; 링크 이동: 선택 항목

UI-SYSTEM_HOME-E009 · 선택 항목 → — a; 링크 이동: 선택 항목


### 부록 UI-LOGIN · 로그인

경로: /login/

UI-LOGIN-E001 · 입력 항목 — div

UI-LOGIN-E002 · next — hidden

UI-LOGIN-E003 · 아이디 — text; 필수(조건부 여부는 화면 표시 따름)

UI-LOGIN-E004 · 비밀번호 — password; 필수(조건부 여부는 화면 표시 따름)

UI-LOGIN-E005 · 로그인 → — submit; 폼 제출: submit → 현재 URL POST


### 부록 UI-JS_SHELL · 공통 조작·키보드·반응형

경로: 상위 화면 공통 영역

UI-JS_SHELL-E001 · 모바일 사이드바 열기/닫기 — 버튼; 680px 이하에서 메뉴 버튼 표시. aria-expanded 갱신; 열면 첫 링크로 포커스

UI-JS_SHELL-E002 · 메뉴 배경 클릭 — 버튼; 배경 클릭 시 메뉴 닫고 버튼 포커스 복원

UI-JS_SHELL-E003 · Escape 메뉴 닫기 — 키보드; 메뉴 열린 상태에서만 닫기

UI-JS_SHELL-E004 · 메뉴 포커스 순환 — Tab/Shift+Tab; 열린 메뉴 링크 안에서 키보드 순환

UI-JS_SHELL-E005 · 모바일 너비 이탈 — 반응형; 680px 초과로 전환 시 메뉴 닫기

UI-JS_SHELL-E006 · 데스크톱 사이드바 접기 — 공통 조작; 2026-11-17 구현: 사이드바 접기·220~480px 폭 조절·브라우저 설정 유지. 본문 공통 조작 참조.

UI-JS_SHELL-E007 · 사이드바 폭 드래그 조절 — 공통 조작; 2026-11-17 구현: 사이드바 접기·220~480px 폭 조절·브라우저 설정 유지. 본문 공통 조작 참조.

UI-JS_SHELL-E008 · 사이드바 상태 저장 — 공통 조작; 2026-11-17 구현: 사이드바 접기·220~480px 폭 조절·브라우저 설정 유지. 본문 공통 조작 참조.

UI-JS_SHELL-E009 · 장문 입력 높이 조절 — 드래그; textarea의 기본 세로 resize 허용; 데이터 자동 저장은 아님

UI-JS_SHELL-E010 · 넓은 표 가로 스크롤 — 스크롤; table-wrap 내부에서 가로 이동; 화면 전체 너비 확장 방지

UI-JS_SHELL-E011 · 미저장 변경 경고 — 브라우저 이동; data-track-changes 폼 수정 후 이동 시 확인; 저장 성공 후 경고 해제

UI-JS_SHELL-E012 · 중복 제출 방지 — 상태; 처리 중 제출 버튼 비활성; 실패 시 오류 표시 및 버튼 복원

UI-JS_SHELL-E013 · 본인 정보: 이름 — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E014 · 본인 정보: 로그인 ID — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E015 · 본인 정보: 부서 — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E016 · 본인 정보: 이메일 — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E017 · 본인 정보: 연락처 — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E018 · 본인 정보: 적용 역할·배정 경로 — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E019 · 본인 정보: 소속 그룹·배정 경로 — 조회; 상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환

UI-JS_SHELL-E020 · 본인 정보 모달 열기 — 상호작용; 비동기 조회 중 불러오는 중 표시; 응답 성공 시 내용 교체

UI-JS_SHELL-E021 · 본인 정보 모달 닫기 — 상호작용; 닫기 버튼·Escape·모달 바깥 클릭으로 닫기

UI-JS_SHELL-E022 · 지급 동작 선택 — 상호작용; 대상자 필수; 서비스요청 선택 시 요청자 자동 선택

UI-JS_SHELL-E023 · 반납 동작 선택 — 상호작용; 반납 창고 필수; 창고 선택 시 위치 자동 반영

UI-JS_SHELL-E024 · 일련번호 재고 선택 — 상호작용; 출발 창고·품목에 맞는 자산만 선택 가능

UI-JS_SHELL-E025 · 엔티티 유형 전환 — 상호작용; 유형에 맞는 선택값·코드·참조·길이/정밀도 컨트롤 활성화


### 최신 SR 구성 보완

요청 등록7개 필드, 전체 화면19개 필드/5그룹, 만족도 정수1~5 및 작업 시간 최소0, 할당된 열린 태스크만 입력·처리합니다. 숫자 최소/최대 속성은 화면 디자이너 상세 속성에서 설정하며 등록 화면은 연결 공통 화면 배치를 재사용합니다. 기존 개별 항목 색인은 이전 버전의 다른 업무 기능도 포함하므로 실제 새 프로세스는 본문 예제를 따릅니다.
