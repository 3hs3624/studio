# 통합 ITSM 산출물

기준일: 2026-11-16 (KST). 구현 기준 main `2f4fb35ece8033b5111e500ca953b09d967f6960`.

기존 Google 문서 ID를 유지해 내용을 갱신했습니다. 위치: [내 드라이브 > ChatGPT > Studio](https://drive.google.com/drive/folders/1EcLumP9y5m_ETDOO4duzDzKz_VJSaEfU).

| 문서 | 링크 | 이번 반영 |
|---|---|---|
| 기능명세서 | [Google Docs](https://docs.google.com/document/d/1n6ccDPYnk-V94MTnkmA1b07ICd5T97AU4YOAWqvckbE/edit) | 디자이너·미리보기·그룹 통제·관리 목록/상세·대시보드 범위·타입 검증·미구현 경계 |
| 화면설계서 | [Google Slides](https://docs.google.com/presentation/d/1S9cnZDnVPF22GKFNXm5aPFo7DPE_GiJVqet4fI0UoqQ/edit) | 개요 19페이지 + 항목 상세 326페이지. 65개 화면/컴포넌트·1,200개 항목 및 발표자 노트 정의 |
| 테이블정의서 | [Google Sheets](https://docs.google.com/spreadsheets/d/1H9-xXoyRq6cSLZFXds42D4M609-Rfl81mC-6ujZ0p9A/edit) | 101개 테이블·880개 필드·136개 명시적 제약/인덱스, JSON 구성 계약 추가 |
| 코드정의서 | [Google Sheets](https://docs.google.com/spreadsheets/d/1hF7cdLWFoBEl-xLdgRprnkpuiKkS2vhykauiw1bfIqc/edit) | 302개 정의. 논리 유형21개·조회 범위3개·그룹 표시2개·태스크 모드3개·기본값 함수3개 추가 |

기능명세서의 저장소 사본: [functional-spec.md](functional-spec.md). 사용법: [화면 디자이너](../form-designer.md), [워크플로우 편집](../workflow-editor.md), [할 일 범위](../dashboard-tasks.md). 미완료 항목: [개선 진행 기록](../configuration-upgrade-status.md).

## 확인 근거와 한계

- [Django checks 43698760583](https://github.com/3hs3624/studio/actions/runs/43698760583): SQLite·PostgreSQL·임시 접근 작업 성공.
- [Local AP DB Docker 43698760668](https://github.com/3hs3624/studio/actions/runs/43698760668): 분리 스택 작업 성공.
- Render `dep-dbsninh42hec738hfs40`, 2026-11-15 18:22:03 KST live. 2026-11-16 배포 메타데이터에서 구현 커밋과 일치 확인.
- 화면은 합성 데이터 기반입니다. 기존 IAM/API 등 캡처는 11/14, 변경된 UI는 11/15 검증 캡처입니다. 실운영 고객 데이터나 외부 시스템 연결 검수를 뜻하지 않습니다.
- 물리 DB 타입 매핑·복합 업무 PK·UI 인덱스 DDL·스키마 이관 작업자, Group→Set→Field 등은 미완료입니다. 명세에 완료 기능처럼 표기하지 않습니다.
- 테이블정의서는 Django 모델 메타데이터이며 실제 운영 DB의 네이티브 타입·트리거·암묵적 인덱스를 실사한 자료가 아닙니다. 최근 UI 기능은 기존 JSON 구조를 사용하며 마이그레이션은 0020까지입니다.
- URL 배포, 설치형, 노트북 Docker는 같은 소스 체계를 사용하나 사용자 환경의 소스·이미지 업데이트는 각각 필요합니다.

## 메타데이터 재생성

검증한 소스 체크아웃에서 다음을 실행합니다. 실제 업무 레코드·비밀번호·인증 키는 읽지 않습니다. 커밋과 기준일은 확인한 값으로 명시해야 합니다.

```bash
DEBUG=1 .venv/bin/python docs/deliverables/export_metadata.py /tmp/studio-metadata.json \
  --commit 2f4fb35ece8033b5111e500ca953b09d967f6960 --as-of 2026-11-16
```

생성 파일은 문서 업데이트 입력이며 자동 업로드하지 않습니다. 기존 문서의 사용자 편집·서식과 대조하여 변경 범위만 적용합니다.


## 화면·기능 개별 정의

[상세 색인](ui-details/README.md)에서 화면/공통 컴포넌트/동적 UI 65개와 항목 1,200개를 확인합니다. 항목마다 ID·형식·필수/길이/범위·선택값·표시 조건·동작·API·검증·소스 위치를 기록했습니다. 반복 데이터는 행의 스키마 단위이며 실제 사용자/업무 값은 포함하지 않습니다.

Google 기능명세서의 ‘화면·항목별 상세 정의’ 탭과 화면설계서의 상세 페이지/발표자 노트는 같은 ID를 사용합니다. 사이드바 모바일 열기/닫기·Escape·포커스와 공통 팝업·키보드·드래그 조작도 정의했습니다. 데스크톱 사이드바 접기·사용자 폭 조절·브라우저 설정 유지는 2026-11-17 구현했습니다. [조작·예외 상세](../sidebar-navigation.md)를 참조합니다.

추출 기준: main `55affa25b682ab2b758b0c4bf5c935b9f237d575`의 관련 소스 80개 Git blob SHA 일치. 정적 소스 대조이며 모든 화면/권한/브라우저 조합을 새로 실행 검수한 결과는 아닙니다.

재생성은 해당 커밋의 GitHub recursive tree JSON을 준비한 후 다음을 실행합니다.

```bash
python docs/deliverables/export_ui_details.py --tree /tmp/remote-tree.json \
  --commit 55affa25b682ab2b758b0c4bf5c935b9f237d575 --work-dir /tmp/studio-ui-details
```
