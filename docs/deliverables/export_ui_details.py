import ast,bisect,hashlib,json,re,html,argparse,tempfile
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description='Export source-grounded UI controls; no business records or secrets are read.')
parser.add_argument('--tree',required=True,help='GitHub recursive tree JSON for verified source commit')
parser.add_argument('--commit',required=True)
parser.add_argument('--work-dir',default='/tmp/studio-ui-details')
args=parser.parse_args()
if not re.fullmatch(r'[a-f0-9]{40}',args.commit):parser.error('full commit SHA required')
Path(args.work_dir).mkdir(parents=True,exist_ok=True)
OUT=ROOT/'docs/deliverables/ui-details';OUT.mkdir(exist_ok=True)
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'{%.*?%}','',s,flags=re.S))).strip()
class Node:
 def __init__(self,tag='',attrs=(),parent=None,line=1,conditions=()):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[];self.line=line;self.conditions=list(conditions)
 def text(self):return clean(' '.join(c if isinstance(c,str) else c.text() for c in self.children))
 def ancestors(self):
  n=self.parent
  while n:yield n;n=n.parent
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.nodes=[];self.conditions=[]
 def handle_starttag(self,t,a):
  n=Node(t,a,self.stack[-1],self.getpos()[0],self.conditions);self.nodes.append(n);self.stack[-1].children.append(n)
  if t not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(n)
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s)
 def parse(self,s):
  pos=0
  for m in re.finditer(r'{%\s*(.*?)\s*%}',s,re.S):
   self.feed(s[pos:m.start()]);t=clean(m.group(1));w=t.split(' ',1)[0]
   if w in ('if','for'):self.conditions.append(t)
   elif w in ('elif','else','empty'):
    if self.conditions:self.conditions[-1]=t+' (앞 분기 제외)'
   elif w in ('endif','endfor'):
    if self.conditions:self.conditions.pop()
   self.feed('\n'*m.group().count('\n')+' ');pos=m.end()
  self.feed(s[pos:]);return self
# Route -> view -> template evidence, including dynamic render branches.
urltree=ast.parse((ROOT/'config/urls.py').read_text());routes=[]
for n in ast.walk(urltree):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='path' and len(n.args)>1 and isinstance(n.args[0],ast.Constant):
  routes.append({'path':'/'+n.args[0].value,'view':ast.unparse(n.args[1]),'kwargs':ast.unparse(n.args[2]) if len(n.args)>2 else ''})
viewinfo={};templateviews={}
for path in sorted(set([ROOT/'desk/views.py',*ROOT.glob('desk/*views.py')])):
 mod=path.stem
 for f in ast.walk(ast.parse(path.read_text())):
  if not isinstance(f,(ast.FunctionDef,ast.ClassDef)):continue
  body=ast.get_source_segment(path.read_text(),f) or '';templates=sorted(set(re.findall(r"['\"]((?:desk|registration)/[^'\"]+\.html)['\"]",body)))
  templates+=['desk/'+t for t in re.findall(r"render_page\(request,['\"]([^'\"]+\.html)",body)]
  permissions=sorted(set(re.findall(r"(?:require|has_permission|require_permission)\([^,]+,\s*['\"]([^'\"]+)",body)))
  obj={'view':mod+'.'+f.name,'source':str(path.relative_to(ROOT))+':'+str(f.lineno),'permissions':permissions,'routes':[r['path'] for r in routes if r['view'].startswith(mod+'.'+f.name)],'templates':templates}
  viewinfo[obj['view']]=obj
  for t in templates:templateviews.setdefault(t,[]).append(obj)
TITLES={'base':'공통 셸·상단·사이드바·내 정보','console-base':'운영 콘솔 공통 셸','screen-designer':'화면 디자이너·필드 속성·미리보기','process-manage':'화면/워크플로우/결재선 상세','process-fields':'프로세스 항목표','process-field':'태스크 동적 입력 필드','process-list':'화면/워크플로우/결재선 목록','process-create':'화면/워크플로우/결재선 생성','dashboard-tasks':'내가 할 일 공통 영역','configuration-impact':'초안 변경 영향도','console-tabs':'공통 상세 탭','request-assets':'서비스요청 자산 연결','sla-card':'SLA 현황 카드'}
TITLES.update({'access-departments':'부서 선택 목록','access-people':'사용자·그룹 선택 목록','delivery-overview':'IT자원 요약 현황','delivery-home':'IT자원 업무 홈','system-home':'시스템별 업무 현황','new':'장애 등록','detail':'장애 상세','list':'장애 목록','process-inbox':'워크플로우 업무·결재 목록/상세','request-detail':'서비스요청 상세','resource-detail':'구성항목 상세','purchase-request-detail':'구매요청 상세','purchase-order-detail':'발주 상세','asset-detail':'자산 상세','catalog-detail':'서비스 신청','portal':'통합 포털','plugins':'플러그인 목록/상세','security-policies':'보안정책 목록/상세','timeliness-agreement':'KPI 기준일·기한 조정'})
# UI data-* actions with explicit behavior: these are client actions, not new server APIs.
ACTIONS={
'data-designer-undo':'최근 편집 이전 상태로 복원; 실행 취소 이력이 없으면 비활성', 'data-designer-redo':'실행 취소한 다음 상태 복원; 다시 실행 이력 없으면 비활성',
'data-designer-preview':'편집 중 배치를 별도 미리보기 모달에 표시; 입력값 저장 안 함','data-designer-cancel':'미적용 변경을 버리고 디자이너 닫기','data-designer-apply':'현재 배치를 항목표에 반영하고 닫기; 서버 저장은 별도','data-designer-save':'사유와 배치를 원래 화면 저장 폼으로 전달해 초안 저장·검증',
'data-designer-add':'선택 그룹에 해당 논리 유형 필드 추가; 드래그 시 놓은 그룹/위치에 추가','data-designer-add-group':'고유 그룹 키로 새 그룹 추가 후 선택','data-designer-remove-group':'선택 그룹 삭제; 포함 필드는 남은 그룹으로 이동','data-designer-properties':'선택 필드 상세 속성 모달 열기','data-designer-up':'선택 필드를 앞 순서로 이동','data-designer-down':'선택 필드를 뒤 순서로 이동','data-designer-duplicate':'선택 필드를 새 식별자로 복제','data-designer-delete':'선택 필드 및 배치에서 제거','data-property-cancel':'속성 변경 미적용 후 닫기','data-preview-close':'미리보기 종료 후 편집 상태 복귀','data-preview-desktop':'미리보기 데스크톱 너비로 전환','data-preview-mobile':'미리보기 모바일 너비로 전환',
'data-copy-load':'선택 사용자/부서 할당을 조회하고 복제할 역할·그룹 선택 목록과 토큰 갱신','data-read-spec':'OpenAPI 문서 작업 목록 조회; 파싱 오류 표시','data-import-spec':'선택 작업의 설정을 현재 API 초안에 가져오기; 자동 게시하지 않음','data-add-input':'API 입력 정의 행 추가','data-add-mapping':'API 응답 매핑 행 추가','data-job-id':'API 실행 결과 상세 조회; 조회 실패 안내 표시',
'data-policy-preview':'보안정책 적용 전 미리보기; 결과만 표시하며 저장하지 않음',
}
# Form operation contracts complement exact HTML attributes.
RULES={
'user-create':'초대/초기 비밀번호 방식 선택; 정책 검증·중복 ID/조직 경계 검사; 복제 토큰 재검증; 성공 시 생성 사용자 상세',
'user-save':'개인정보 조회는 별도 권한·재인증·접근 이력; 부서·연락처·만료일 수정 시 사유·행 버전 검사',
'user-reset':'비밀번호 정책을 검증해 임시 비밀번호 설정 및 변경 강제; 비밀값을 문서/로그에 기록하지 않음',
'flow-save':'그래프 구조·참조·역할·순환·필드/그룹 규칙 검증; expected_version 충돌 검사; 초안 저장만 수행',
'flow-review':'작성자와 다른 검토자, 현재 초안 해시 및 버전 확인 후 독립 검토 기록',
'flow-publish':'동일 초안의 유효한 독립 검토 확인 후 불변 게시 버전 생성; 진행 중 실행 유지',
'process-task':'할당·현재 자격·행 버전·필수값·그룹/필드 수정 권한 검사 후 태스크 처리',
'request-decision':'지정 승인자만 결정; 자기 결재 배제·반려 사유 검증; 상태/버전 충돌 차단',
'request-assign':'허용된 처리 그룹 구성원만 배정; 변경 사유/버전 검사',
'comment':'공개/내부 범위와 작성 자격 검사; 내부 댓글은 요청자에게 반환하지 않음',
'entity-save':'고정 필드와 업무 키 충돌·논리 유형·관계 대상/카디널리티 검증; 초안 수정',
'entity-publish':'게시 스키마 불변; 기존 레코드 참조 버전 보존; 물리 테이블 DDL 아님',
'org-menus':'메뉴/콘솔 버튼/행 범위를 역할에 매핑; 서버 URL/API 권한도 검사',
'asset-action':'ISSUE는 지급 대상 필수, ISSUE/RETURN/MOVE/VERIFY는 위치 필수; RETURN은 창고 필수; 상태 전이 검사',
}
def label_for(n,p):
 if n.attrs.get('aria-label'):return n.attrs['aria-label']
 wrap=next((a for a in n.ancestors() if a.tag=='label'),None)
 if wrap:
  own=clean(' '.join(c for c in wrap.children if isinstance(c,str)))
  if own:return own
 if n.attrs.get('id'):
  labs=[x.text() for x in p.nodes if x.tag=='label' and x.attrs.get('for')==n.attrs['id']]
  if labs:return labs[0]
 if n.tag in ('button','a','summary','th','dt'):return n.text() or n.attrs.get('title') or n.attrs.get('href') or ('관리 열(화면 제목은 공백)' if n.tag=='th' else '이름 없는 '+n.tag)
 return n.attrs.get('placeholder') or n.attrs.get('name') or n.attrs.get('id') or next((k for k in n.attrs if k.startswith('data-')),'입력 항목')
def source_conditions(raw,offset):
 stack=[]
 for match in re.finditer(r'{%\s*(.*?)\s*%}',raw[:offset],re.S):
  token=clean(match.group(1));word=token.split(' ',1)[0]
  if word in ('if','for'):stack.append(token)
  elif word in ('elif','else','empty'):
   if stack:stack[-1]=token+' (앞 분기 제외)'
  elif word in ('endif','endfor'):
   if stack:stack.pop()
 return stack

def collect(path,index):
 raw=path.read_text();p=Parser().parse(raw);rel=str(path.relative_to(ROOT));key=path.stem;sid='UI-'+key.upper().replace('-','_')
 direct=templateviews.get(str(path.relative_to(ROOT/'desk/templates')),[]);title=TITLES.get(key) or next((n.text() for n in p.nodes if n.tag=='h1'),key)
 screen={'id':sid,'name':title,'source':rel,'routes':sorted(set(r for v in direct for r in v['routes'])),'views':direct,'includes':re.findall(r"{%\s*(?:include|extends)\s+['\"]([^'\"]+)",raw),'controls':[],'forms':[]}
 forms=[n for n in p.nodes if n.tag=='form']
 for i,f in enumerate(forms):screen['forms'].append({'id':sid+'-F'+str(i+1).zfill(2),'attrs':f.attrs,'source':rel+':'+str(f.line)})
 tag_offsets={};tag_matches={}
 for n in p.nodes:
  if n.tag not in tag_matches:tag_matches[n.tag]=list(re.finditer('<'+re.escape(n.tag)+r'\b(?:(?:{%.*?%}|{{.*?}})|[^>])*>',raw,re.S))
  at=tag_offsets.get(n.tag,0);tag_offsets[n.tag]=at+1
  if at<len(tag_matches[n.tag]):n.conditions=source_conditions(raw,tag_matches[n.tag][at].start())
  if n.tag not in {'input','select','textarea','button','a','summary','th','dt','progress'} and not (n.attrs.get('role') in ('status','alert','tab') or any(k.endswith(('output','result')) for k in n.attrs if k.startswith('data-'))):continue
  if n.tag=='a' and 'href' not in n.attrs:continue
  if n.attrs.get('name')=='csrfmiddlewaretoken':continue
  form=next((a for a in n.ancestors() if a.tag=='form'),None);fi=forms.index(form)+1 if form in forms else None
  typ=n.attrs.get('type','text' if n.tag=='input' else 'submit' if n.tag=='button' and form else 'button' if n.tag=='button' else n.tag)
  endpoint=form.attrs.get('data-url') or form.attrs.get('action') or ('현재 URL 조회 조건' if form and form.attrs.get('method','').lower()=='get' else '현재 URL POST' if form and form.attrs.get('method','').lower()=='post' else '') if form else ''
  action=next((v for k,v in ACTIONS.items() if k in n.attrs),'')
  kind=(form.attrs.get('data-kind') or form.attrs.get('data-integration-form') or '') if form else ''
  if not action:
   if n.tag=='a':action='링크 이동: '+n.attrs.get('href','')
   elif n.tag=='summary':action='상위 details 영역 접기/펼치기; open 속성이 있으면 초기 펼침; 서버 저장 없음'
   elif n.tag=='button':action=('폼 제출: '+(kind or form.attrs.get('id','') or typ)+' → '+endpoint) if form and typ=='submit' else '클라이언트 조작: '+label_for(n,p)
   elif n.tag in ('th','dt') or n.attrs.get('role') in ('status','alert'):action='조회/상태 표시; 이 항목 자체는 저장하지 않음'
   else:action='입력값을 해당 폼/편집 상태에 반영; 저장/조회 동작은 연결 버튼에서 실행'
  opts=[{'value':x.attrs.get('value',x.text()),'label':x.text()} for x in p.nodes if x.tag=='option' and n in list(x.ancestors())]
  control={'id':sid+'-E'+str(len(screen['controls'])+1).zfill(3),'name':label_for(n,p),'tag':n.tag,'type':typ,'attrs':n.attrs,'options':opts,'condition':' / '.join(n.conditions) or '해당 화면/공통 영역 표시 시','form':sid+'-F'+str(fi).zfill(2) if fi else '', 'operation':kind,'endpoint':endpoint,'behavior':action,'rule':RULES.get(kind,''),'source':rel+':'+str(n.line)}
  if n.tag=='dt':
   sib=n.parent.children if n.parent else []; at=sib.index(n); control['display_value']=next((x.text() for x in sib[at+1:] if isinstance(x,Node) and x.tag=='dd'),'')
  if n.tag=='progress':control['display_value']='value='+n.attrs.get('value','')+'; max='+n.attrs.get('max','')
  screen['controls'].append(control)
 return screen
screens=[collect(p,i) for i,p in enumerate(sorted((ROOT/'desk/templates').rglob('*.html')))];all_controls=[c for s in screens for c in s['controls']]
# Dynamic JS UI controls: helper-key controls are declared individually, not hidden behind an aggregate row.
def add_dynamic(group,key,name,typ,behavior,source,condition='편집기 열림·해당 대상 선택 시',options=''):
 s=next((s for s in screens if s['id']==group),None)
 if not s:
  s={'id':group,'name':{'UI-JS_PROCESS':'프로세스 동적 항목·노드·권한 편집','UI-JS_INTEGRATION':'API 동적 입력·매핑 행','UI-JS_SHELL':'공통 조작·키보드·반응형','UI-JS_DESIGNER':'디자이너 동적 캔버스 조작'}.get(group,group),'source':source.split(':')[0],'routes':[],'views':[],'includes':[],'forms':[],'controls':[]};screens.append(s)
 c={'id':group+'-E'+str(len(s['controls'])+1).zfill(3),'name':name,'tag':'동적 UI','type':typ,'attrs':{'data-key':key},'options':[], 'condition':condition,'form':'','operation':'','endpoint':'클라이언트 편집 상태 → 초안 저장 시 서버 검증','behavior':behavior,'rule':options,'source':source};s['controls'].append(c)
p=ROOT/'desk/static/desk/process-editor.js';raw=p.read_text()
seen=set()
for m in re.finditer(r"control\([^,]+,\s*'([^']+)',\s*'([^']+)',\s*(input|select|checkbox)\(",raw):
 key,name,typ=m.groups()
 if key in seen:continue
 seen.add(key);line=raw.count('\n',0,m.start())+1
 add_dynamic('UI-JS_PROCESS',key,name,{'input':'입력','select':'선택','checkbox':'체크'}[typ], '선택 노드/그룹/필드의 '+key+' 설정 갱신; 초안 저장 시 그래프 검증',str(p.relative_to(ROOT))+':'+str(line))
for key,name,typ,rule in [('next','다음 노드','선택','존재하는 단계 이름으로 선택'),('reject','반려 시 노드','선택','미지정 시 반려 종료'),('true','조건 참 경로','선택','CONDITION 노드'),('false','조건 거짓 경로','선택','CONDITION 노드'),('branches','병렬 시작 노드','입력','쉼표 구분, 연결 대상 검증'),('join','병렬 합류 노드','선택','PARALLEL의 합류 대상'),('selectorKind','담당자 선택 방식','선택','USER/ROLE/GROUP/DEPARTMENT/STARTER/FIELD_USER'),('selectorIds','담당자 대상','다중선택','방식에 맞는 조직 내 대상; FIELD_USER는 사용자형 데이터 필드'),('selectorChildren','하위 부서 포함','체크','DEPARTMENT에서만 표시'),('field.key','항목 식별자','입력','고유 키'),('field.label','항목 표시 이름','입력','필수 표시 이름'),('field.type','항목 유형','선택','화면 논리 유형18개'),('field.required','항목 필수','체크','서버 검증'),('field.group_id','담당자 선택 그룹','선택','사용자형 필드만 적용'),('field.readonly','항목 조회 전용','체크','화면 전체 조회 전용'),('field.remove','항목 제거','버튼','현재 항목표에서 제거'),('node.remove','단계 삭제','버튼','단계 제거; 남은 참조는 게시 전 검증'),('node.pick','단계 목록 선택','버튼','선택한 단계만 편집'),('node.svg','흐름도 상자','클릭/드래그','단계 선택·좌표 이동; Enter/Space 선택'),('rules.refresh','필드 규칙 갱신','버튼','공통 화면·데이터 항목을 기준으로 규칙 다시 표시')]:
 if key not in seen:add_dynamic('UI-JS_PROCESS',key,name,typ,rule,'desk/static/desk/process-editor.js')
for key,name,typ,rule in [('input.key','입력 이름','입력','API 입력 필드 식별자'),('input.type','입력 유형','선택','text/number/boolean/json'),('input.required','입력 필수','체크','실행 시 필수 검사'),('input.remove','입력 행 제거','버튼','현재 API 초안에서 행 제거'),('mapping.key','결과 이름','입력','중복 이름 거부'),('mapping.path','응답 경로','입력','매핑할 원본 경로'),('mapping.transform','변환 방식','선택','COPY/STRING/NUMBER/BOOLEAN/TRIM/UPPER/LOWER/DATE'),('mapping.required','결과 필수','체크','필수 경로 누락 시 매핑 실패'),('mapping.remove','결과 행 제거','버튼','현재 매핑 행만 제거')]:add_dynamic('UI-JS_INTEGRATION',key,name,typ,rule,'desk/static/desk/integrations.js:3')
for key,name,typ,rule in [('group.choose','그룹 목록/제목 선택','버튼','추가 버튼과 별개; 선택 그룹과 속성 영역 변경'),('group.tab','그룹 탭 선택','탭','탭 표시 모드에서 대상 그룹으로 전환; 드롭 대상'),('field.select','캔버스 필드 선택','클릭','선택 표시·빠른 속성 갱신'),('field.drag','필드 드래그 이동','드래그','그룹 내 순서 또는 그룹 간 이동; 실행 취소 가능'),('field.resize','필드 크기 핸들','드래그','너비1~화면열수, 높이1~5, 48px 단위'),('field.context','우클릭/더블클릭 속성','마우스','선택 필드의 상세 속성 열기'),('field.keyboard.move','Ctrl+방향키','키보드','필드 앞/뒤 이동'),('field.keyboard.resize','Shift+방향키','키보드','너비/높이 조정'),('field.keyboard.properties','Shift+F10','키보드','필드 상세 속성 열기'),('preview.tabs','미리보기 그룹 탭','탭/키보드','방향키/Home/End 전환; 미리보기 입력값은 저장 안 함'),('dialog.escape','Escape로 디자이너 종료','키보드','미적용 편집 취소')]:add_dynamic('UI-JS_DESIGNER',key,name,typ,rule,'desk/static/desk/screen-designer.js')
for key,name,typ,rule in [('mobile.open','모바일 사이드바 열기/닫기','버튼','680px 이하에서 메뉴 버튼 표시. aria-expanded 갱신; 열면 첫 링크로 포커스'),('mobile.backdrop','메뉴 배경 클릭','버튼','배경 클릭 시 메뉴 닫고 버튼 포커스 복원'),('mobile.escape','Escape 메뉴 닫기','키보드','메뉴 열린 상태에서만 닫기'),('mobile.focus','메뉴 포커스 순환','Tab/Shift+Tab','열린 메뉴 링크 안에서 키보드 순환'),('mobile.breakpoint','모바일 너비 이탈','반응형','680px 초과로 전환 시 메뉴 닫기'),('shell.desktop-collapse','데스크톱 사이드바 접기','버튼','681px 이상 상단 버튼으로 접기/펼치기; 숨긴 메뉴 inert 및 본문 확장; 브라우저 설정 저장'),('shell.width','사이드바 폭 드래그 조절','드래그/키보드','220~min(480, 화면너비45%)px. 기본256px; 좌우10/Shift50; Home/End; 두 번 클릭 초기화; Escape 드래그 취소'),('shell.persist','사이드바 상태 저장','브라우저 설정','studio.sidebar.v1에 width·collapsed 저장; 손상/차단 시 기본값/현재 동작; 서버·다른 장치 동기화 없음'),('textarea.resize','장문 입력 높이 조절','드래그','textarea의 기본 세로 resize 허용; 데이터 자동 저장은 아님'),('table.scroll','넓은 표 가로 스크롤','스크롤','table-wrap 내부에서 가로 이동; 화면 전체 너비 확장 방지'),('form.unsaved','미저장 변경 경고','브라우저 이동','data-track-changes 폼 수정 후 이동 시 확인; 저장 성공 후 경고 해제'),('form.pending','중복 제출 방지','상태','처리 중 제출 버튼 비활성; 실패 시 오류 표시 및 버튼 복원')]:add_dynamic('UI-JS_SHELL',key,name,typ,rule,'desk/static/desk/app.js / desk/static/desk/carbon-ui.css')
for key,name in [('name','이름'),('username','로그인 ID'),('department','부서'),('email','이메일'),('phone','연락처'),('roles','적용 역할·배정 경로'),('groups','소속 그룹·배정 경로')]:add_dynamic('UI-JS_SHELL','profile.'+key,'본인 정보: '+name,'조회','상단 본인 이름 선택 → /account/profile 조회 후 모달에 표시; 조회 실패 안내; 개인정보는 허용된 범위만 반환','desk/static/desk/app.js:442')
for key,name,rule in [('profile.open','본인 정보 모달 열기','비동기 조회 중 불러오는 중 표시; 응답 성공 시 내용 교체'),('profile.close','본인 정보 모달 닫기','닫기 버튼·Escape·모달 바깥 클릭으로 닫기'),('asset.issue','지급 동작 선택','대상자 필수; 서비스요청 선택 시 요청자 자동 선택'),('asset.return','반납 동작 선택','반납 창고 필수; 창고 선택 시 위치 자동 반영'),('inventory.serial','일련번호 재고 선택','출발 창고·품목에 맞는 자산만 선택 가능'),('entity.type','엔티티 유형 전환','유형에 맞는 선택값·코드·참조·길이/정밀도 컨트롤 활성화')]:add_dynamic('UI-JS_SHELL',key,name,'상호작용',rule,'desk/static/desk/app.js')
# Explicit palette expansion: runtime type rows are a finite catalogue, business rows remain parameterized.
meta=ast.literal_eval(next(n.value for n in ast.parse((ROOT/'desk/data_types.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TYPE_META' for t in n.targets)))
for key,(label,icon,category) in meta.items():
 if key not in {'choice','code','reference'}:add_dynamic('UI-JS_DESIGNER','palette.'+key,label+' 필드 추가','아이콘 버튼/드래그',label+' 유형을 선택 그룹 또는 놓은 위치에 추가; 공통 길이/타입 검증','desk/data_types.py:12',options='유형='+key+'; 분류='+category)
# Verify every inspected implementation file exactly matches the chosen Git tree.
remote={x['path']:x.get('sha') for x in json.load(open(args.tree))['tree'] if x['type']=='blob'}
checks=[]
for p in sorted(set([ROOT/'config/urls.py',*ROOT.glob('desk/templates/**/*.html'),*ROOT.glob('desk/static/desk/*.js'),*ROOT.glob('desk/*views.py'),ROOT/'desk/views.py',ROOT/'desk/data_types.py',ROOT/'desk/static/desk/carbon-ui.css'])):
 b=p.read_bytes();digest=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();name=str(p.relative_to(ROOT));checks.append({'path':name,'matches_main':digest==remote.get(name),'sha':digest})
if not all(x['matches_main'] for x in checks):raise SystemExit('Source mismatch: '+str([x['path'] for x in checks if not x['matches_main']]))
for screen in screens:
 screen['used_by']=[other['id'] for other in screens if screen['source'].removeprefix('desk/templates/') in other['includes']]
 screen['effective_routes']=sorted(set(screen['routes']+[route for other in screens if other['id'] in screen['used_by'] for route in other['routes']]))
 if screen['id']=='UI-LOGIN':screen['routes']=screen['effective_routes']=['/login/']
result={'baseline':args.commit,'as_of':'2026-11-16','screens':screens,'routes':routes,'source_checks':checks}
(OUT/'catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'screens':len(screens),'controls':sum(len(s['controls']) for s in screens),'source_files':len(checks),'matched':all(x['matches_main'] for x in checks)},ensure_ascii=False))

import json,re,math
from pathlib import Path
R=ROOT;O=OUT;x=json.load(open(O/'catalog.json'))
RULES={
'account':'계정 활성/중지 전환. 사유·행 버전 검사 및 보호 계정 제한.', 'revoke-sessions':'선택 사용자의 세션을 회수; 현재 세션 여부와 권한 검사.', 'user-action':'잠금 해제/MFA 해제 등 지정 계정 동작; 사유·재인증 정책 적용.', 'user-invite':'초대 링크를 결과 영역에 표시; 개인정보/비밀번호를 복제하지 않음.', 'user-session':'선택 세션 회수; 조직 경계·소유자/관리 권한 검사.',
'role-save':'역할 코드·이름·기능 권한 저장. 시스템 역할 보호 및 코드 중복 검사.', 'group-save':'그룹 정의 저장. 조직별 코드 중복·활성 여부 검사.', 'manage-delete':'역할/그룹 삭제. 참조·보호 항목 검사 후 해당 목록으로 이동.', 'org-delete':'부서 삭제. 하위 부서·소속 사용자·배정 참조를 검사.', 'org-department':'부서 생성/편집. 상위 부서 순환·다른 조직 참조 금지.', 'org-role-targets':'역할에 사용자·부서·그룹을 배정. 하위 부서 포함을 명시적으로 선택.', 'org-group-targets':'그룹에 사용자·부서를 배정. 그룹 중첩 배정 아님.', 'membership':'그룹 소속 활성 상태 변경; 대상·조직·사유 검사.', 'role-grant':'사용자 직접 역할 배정 변경; 보호 관리자 제한·사유 검사.', 'roles':'레거시 직접 역할 체크 목록 저장; 조직/보호 관리자 규칙 유지.',
'flow-act':'현재 태스크의 담당자·자격·행 버전·필수값·그룹/필드 권한을 검증해 처리.', 'flow-bind':'업무 메뉴/카탈로그와 게시 프로세스 버전 연결; 지원 어댑터와 대상 검사.', 'flow-cancel':'실행 취소 및 관련 태스크 상태 변경; 이력·사유 보존.', 'flow-clone':'이전 게시 버전을 새 초안으로 복제; 기존 게시본 불변.', 'flow-reassign':'태스크 담당자 재배정; 조직 내 유효 대상·결재 자격 검사.', 'flow-resolve_outputs':'충돌한 하위 결과를 지정 값으로 해소; 사유와 결과 이력 유지.', 'flow-retire':'게시 버전 신규 실행 퇴역. 이미 진행 중인 실행은 유지.', 'flow-retry_children':'차단된 하위 실행 보완 재시도; 임의로 완료 상태 조작하지 않음.', 'flow-start':'게시 버전으로 실행 생성; 필수값과 시작 권한을 검사하고 버전 고정.', 'flow-tick':'실행의 대기/자동 진행 평가; 완료 조건 전에는 다음 단계 진행 안 함.',
'create':'장애 제목/설명·영향도/긴급도 및 자원 참조 검사 후 장애 상세로 이동.', 'assign':'처리 그룹과 담당자 배정; 유효한 그룹 소속 및 상태 검사.', 'transition':'장애 상태 전이, 해결 내용/사유와 역할·현재 상태를 검증.', 'attach':'장애/요청에 자원 연결; 자원 유형·조회 권한·조직 검사.', 'detach':'지정 자원 연결 제거; 대상 업무 권한·행 버전 검사.',
'request-create':'카탈로그 게시 양식과 필수값·승인자/워크플로우 연결 검사 후 서비스요청 생성.', 'request-action':'허용된 현재 상태의 시작/조치 완료/확인 종료/취소 동작만 실행.', 'request-asset-issue':'선택 요청에 자산 지급. 지급 대상·자산 상태·연결 권한 검사.', 'catalog-publish':'서비스 항목/필드·승인·처리 그룹 검증 후 새 양식 버전 게시.',
'asset-create':'자산 기본정보·자산번호 중복·참조 범위 검증 후 자산 상세로 이동.', 'asset-update':'자산 정보 수정; 변경 버전·조직·수정 권한 검사.', 'asset-contract':'자산과 계약 연결; 조회 가능한 계약·자산 및 기간/중복 규칙 검사.',
'purchase-request':'품목·수량·승인자·연결 요청 검증 후 구매 요청 생성.', 'purchase-decision':'구매 승인/반려. 승인자 자격·현재 상태·반려 사유 검사.', 'purchase-cancel-request':'신청자의 취소 가능 상태만 허용; 사유와 이력 보존.', 'purchase-order':'승인된 구매 요청으로 발주 생성; 공급업체·계약·수량 검사.', 'purchase-order-action':'발주 상태에 허용된 동작만 실행; 이미 입고한 수량 등 제약 유지.', 'purchase-receipt':'입고 창고·수량·일련번호를 검사; 초과 입고/중복 자산 방지.', 'supplier':'공급업체 기준정보 저장; 조직별 식별자/활성 값 검사.', 'contract':'계약 기준정보·공급업체·기간 저장; 참조 범위 검사.', 'stockroom':'창고 기준정보와 위치 저장; 조직 범위 검사.', 'stock-item':'재고 품목·추적 방식을 저장; 코드/참조 검사.', 'stock-transfer':'출발/도착 창고·품목·수량/개별 자산 검사 후 재고 이동.', 'stock-issue':'재고 가용 수량·대상자·연결 서비스요청을 검사해 출고.',
'sla-calendar':'시간대·근무 요일·근무 시간·휴일 검증 후 업무 달력 저장.', 'sla-policy':'우선순위·달력·응답/해결 목표와 대기 정지 규칙 저장.', 'kpi-policy':'적기처리 기준일·업무 달력·목표 시간 버전 저장; 기본 접수시각.', 'kpi-report':'기간과 모집단으로 확정 보고서 산출 후 CSV 다운로드.', 'kpi-adjust':'요청 건의 합의 시작/요청 기한/합의 기한 변경; 사유·이력 보존.',
'code-group':'조직별 공통코드 그룹 생성/편집. 코드 중복과 사유 검사.', 'code-items':'행의 코드·이름·순서·사용 여부를 일괄 저장; 중복·참조 검사.', 'entity-record':'게시 논리 스키마 기준 필수값·유형·관계/조회 권한을 검사해 레코드 저장.', 'plugin-configure':'등록 매니페스트에 맞는 설정·행 버전 검증 후 저장.', 'plugin-preview':'플러그인 입력 시험 결과 표시; 실제 번호 발급과 구분.', 'plugin-issue':'매니페스트 해시·권한·입력을 검증해 업무번호 발급; 결과 재확인 지원.',
'security-policy':'정책 유형별 값/범위를 검증. 미리보기는 결과만 표시; 적용은 사유·버전 검사.', 'notification-read':'접근 가능한 본인 알림을 읽음 처리.',
'save':'API 프로토콜·실행 계정·설정·입출력 매핑 검증 후 초안 저장. 실제 호출/게시와 분리.', 'publish':'현재 API 초안 검증 후 불변 게시 버전 생성.', 'credential':'인증 유형에 맞는 JSON 비밀정보를 서버에 보호 저장; 읽기 화면에 원문 재노출 안 함.', 'network':'HTTPS 호스트·허용 사설 CIDR 정책 검증 후 저장.', 'client':'외부 호출 클라이언트 생성. 발급 정보를 결과 영역에 표시; 인증·속도 제한 적용.', 'client-stop':'선택 외부 호출 클라이언트 중지; 사유 검사.', 'invoke':'게시 API 호출. 쓰기 API는 확인 및 멱등성 규칙 적용; 결과/작업 상태 표시.',
}
attrkeys=['name','id','data-p','data-key','data-field','data-quick','data-process-input','data-entity-value','type','required','readonly','disabled','maxlength','min','max','step','pattern','multiple','checked','value','placeholder','autocomplete','aria-label','aria-controls','aria-expanded']
def attrs(c):
 a=c['attrs'];out=[]
 for k in attrkeys:
  if k in a:out.append(k if a[k] is None or a[k]=='' else k+'='+str(a[k]))
 return '; '.join(out) or '별도 입력 제약 없음/조회 항목'
def options(c):return '; '.join(str(v['value'])+'='+v['label'] for v in c['options'])
def esc(s):return str(s).replace('|','\\|').replace('\n','<br>')
def summarize(c):
 a=c['attrs']; vals=[]
 for k in ['required','readonly','disabled','maxlength','min','max','step','pattern','multiple']:
  if k in a:vals.append(k if a[k] in (None,'') else k+'='+str(a[k]))
 return ', '.join(vals) or ('조회 전용' if c['tag'] in ('th','dt','progress') else '추가 제약은 상세 정의 참조')
# Annotate source-conditional attributes explicitly; HTML's final DOM alone cannot express this.
for ss in x['screens']:
 if ss['id']=='UI-JS_PROCESS':
  allowed={'TASK':['selectorKind','selectorIds','selectorChildren','mode','next','reject','approval_version_id','approval_timing','screen_version_id'],'START':['next'],'END':[],'JOIN':['next'],'APPROVAL':['version_id','next','reject'],'CONDITION':['conditionField','conditionOp','conditionValue','true','false'],'PARALLEL':['branches','join'],'WAIT':['wait_seconds','next'],'SUBPROCESS':['version_id','count','count_field','input_mapping','output_mapping','next'],'TRANSFER':['version_id','input_mapping'],'API':['api_version_id','input_mapping','output_mapping','next'],'ACTION':['action','field','value','next']}
  for cc in ss['controls']:
   key=cc['attrs'].get('data-key','')
   kinds=[k for k,keys in allowed.items() if key in keys]
   if kinds:cc['condition']='WORKFLOW에서 노드 유형 '+','.join(kinds)+'일 때 표시. APPROVAL 정의는 결재 대상/복수 담당 설정 사용.'
   if key=='selectorChildren':cc['condition']+=' 담당자 방식 DEPARTMENT일 때만 표시.'
   if key=='approval_timing':cc['condition']+=' 결재선 버전을 선택한 경우만 표시.'
   if key in ('field','value'):cc['condition']+=' ACTION 동작 SET_FIELD일 때만 표시.'
   if key.startswith(('group','fieldMode','fieldRequired','fieldRead','fieldWrite')) and not key.startswith('field.'):
    cc['condition']='WORKFLOW의 TASK/APPROVAL/WAIT/SUBPROCESS/TRANSFER에서 화면 항목·그룹 권한 영역을 펼친 경우'
for s in x['screens']:
 raw=(R/s['source']).read_text() if (R/s['source']).exists() else ''
 positions={}
 for c in s['controls']:
  if c['tag']=='동적 UI':continue
  tag=c['tag'];matches=list(re.finditer('<'+re.escape(tag)+r'\b(?:(?:{%.*?%}|{{.*?}})|[^>])*>',raw,re.S));i=positions.get(tag,0);positions[tag]=i+1
  if i<len(matches):
   opening=matches[i].group(); c['conditional_attributes']=re.findall(r'{%\s*if\s+(.*?)\s*%}\s*(required|disabled|readonly|checked|selected)',opening)
   if c['conditional_attributes']:c['attribute_note']='; '.join(attr+'는 '+cond+'일 때 적용' for cond,attr in c['conditional_attributes'])
  c['rule']=c['rule'] or RULES.get(c['operation'],'')
 # add API request serialization contract for every form, with individual fields linked.
 for f in s['forms']:
  cs=[c for c in s['controls'] if c['form']==f['id']];f['fields']=[c['id'] for c in cs];f['operation']=f['attrs'].get('data-kind') or f['attrs'].get('data-integration-form','');f['rule']=next((c['rule'] for c in cs if c['rule']),'네이티브 GET/POST 또는 클라이언트 전용 폼. 개별 action/method와 버튼 동작을 따름.')
# finite expansions don't get counted as live data records; all label expressions remain literal evidence.
(O/'catalog.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
index=['# 화면·기능 개별 상세 정의','',f"기준: 2026-11-16, main `{x['baseline']}`. 화면/공통 컴포넌트/동적 편집기 {len(x['screens'])}개, 개별 항목 {sum(len(s['controls']) for s in x['screens'])}개.",'','버튼·입력·조회 열·상태 출력·공통 상호작용을 소스 기준으로 개별 정의했습니다. 반복 행은 스키마 단위로 정의하며 사용자/업무 데이터의 각 인스턴스를 중복 문서화하지 않습니다. 조건부 항목은 실제 조건이 성립할 때만 표시됩니다. HTML 필수/선택 속성과 서버 검증을 구분합니다. 사이드바 기능은 docs/sidebar-navigation.md의 최신 구현을 따릅니다.','', 'Google 문서와 항목 ID를 공통으로 사용합니다. 원본 `{{ }}`는 서버가 채우는 값이며 실제 개인정보가 아닙니다. 정적 소스 대조 결과이며 모든 브라우저·권한 조합의 새 실행 검수를 뜻하지 않습니다.','','## 공통 규칙','','- API 폼: JSON 직렬화, CSRF, Idempotency-Key, expected_version(해당 폼에 선언된 경우). 실패는 폼 오류에 표시하고 버튼을 복원합니다. VERSION_CONFLICT는 입력 보존 후 새로고침을 안내합니다.','- GET 검색은 저장 동작이 아닙니다. 일반 POST 인증 폼은 Django 인증·CSRF 규칙을 따릅니다.','- 화면 노출 조건은 서버 권한의 대체물이 아닙니다. 실제 API는 조직·업무·행·필드/그룹 권한을 별도 검사합니다.','- 동적 항목의 유형별 표시/숨김은 [동적 상세](UI-JS_PROCESS.md), 엔티티/디자이너 메타데이터는 해당 화면 정의를 따릅니다.','- 좁은 화면 사이드바는 680px 이하에서 토글되며 Escape/배경 클릭/메뉴 선택/너비 이탈 시 닫힙니다. 데스크톱 접기·폭 조절·브라우저 저장을 지원합니다.','','## 화면·컴포넌트 색인','','| 화면 ID | 이름 | 개별 항목 | 진입/사용 |','|---|---|---:|---|']
paragraphs=[];slides=[]
for s in x['screens']:
 link=s['id']+'.md';routes=', '.join(s.get('effective_routes') or s['routes']) or '공통/동적 컴포넌트: '+', '.join(s.get('used_by',[]))
 index.append('| ['+s['id']+']('+link+') | '+esc(s['name'])+' | '+str(len(s['controls']))+' | '+esc(routes)+' |')
 md=['# '+s['id']+' · '+s['name'],'','진입/사용: '+routes,'','소스: `'+s['source']+'`','', '연결: '+', '.join('`'+v+'`' for v in s['includes']),'']
 views='; '.join(v['view']+' ['+(', '.join(v['permissions']) or '뷰/공통 컨텍스트·업무 조회 권한')+']' for v in s['views'])
 md+=['뷰·권한 참조(동시 필수 권한 목록 아님): '+(views or '포함하는 상위 화면의 접근 권한 및 개별 표시 조건 적용'),'','## 기능/폼 계약','']
 paragraphs.append(('HEADING_2',s['id']+' · '+s['name']))
 paragraphs.append(('NORMAL_TEXT','진입/사용: '+routes+' / 소스: '+s['source']+' / 권한 참조(동시 필수 아님): '+(views or '상위 화면 및 개별 표시 조건')))
 for f in s['forms']:
  text=f['id']+' · '+(f['operation'] or f['attrs'].get('id','폼'))+' · '+f['attrs'].get('method',f['attrs'].get('data-method','POST(JSON)' if f['attrs'].get('data-url') else '원본 참조'))+' '+f['attrs'].get('data-url',f['attrs'].get('action','현재 화면'))+' / '+f['rule']
  md+=['### '+f['id'],'',text,'','항목: '+', '.join(f['fields']),''];paragraphs.append(('NORMAL_TEXT',text))
 md+=['## 항목별 상세','', '| 항목 ID / 이름 | 형식·입력 속성 | 표시 조건·선택값 | 동작·API·검증 | 소스 |','|---|---|---|---|---|']
 for c in s['controls']:
  conditions=c['condition']; behavior=c['behavior']; constraints=attrs(c); opts=options(c); note=c.get('attribute_note','')
  detail=' / '.join(v for v in [behavior,c['endpoint'],c['rule']] if v)
  md.append('| '+esc(c['id']+' · '+c['name'])+' | '+esc(c['type']+' / '+constraints+(' / '+note if note else ''))+' | '+esc(conditions+(' / 선택값: '+opts if opts else ''))+' | '+esc(detail+(' / 출력값: '+c['display_value'] if c.get('display_value') else ''))+' | `'+esc(c['source'])+'` |')
  text=c['id']+' · '+c['name']+' ['+c['type']+']\n입력/표시: '+constraints+(' / '+note if note else '')+'\n조건: '+conditions+(' / 값: '+opts if opts else '')+'\n동작: '+detail+(' / 출력값: '+c['display_value'] if c.get('display_value') else '')+'\n근거: '+c['source']
  paragraphs.append(('NORMAL_TEXT',text))
 md+=['','## 확인 기준','','정상: 표시 조건에 맞는 계정/상태에서 위 항목이 보이고 입력·동작이 정의와 일치.','예외: 필수/형식/참조/버전/권한 오류에서 저장되지 않고 안내.','공통 컴포넌트는 포함하는 화면에서 같은 정의를 사용. 미구현 항목은 실제 조작으로 검수하지 않음.','']
 (O/link).write_text('\n'.join(md))
 # 4 entries per slide, no truncation of full definitions: long machine details are in native speaker notes.
 for j in range(0,len(s['controls']),4):
  cs=s['controls'][j:j+4];body=[];notes=[]
  for c in cs:
   name=c['name'];name=re.sub(r'{{\s*([^}]+)\s*}}',r'{\1}',name)
   if len(name)>100:name=name[:97]+'…'
   short=' / '.join(v for v in [summarize(c),c.get('attribute_note','')] if v)
   cond=c['condition']; cond=cond if len(cond)<=115 else cond[:112]+'…'
   action=c['behavior'];action=action if len(action)<=145 else action[:142]+'…'
   body.extend([c['id']+'  '+name+' ['+c['type']+']', '형식: '+short+' | 조건: '+cond,'동작: '+action,''])
   notes.append(json.dumps(c,ensure_ascii=False))
  slides.append({'screen':s['id'],'title':s['name'],'part':j//4+1,'total':math.ceil(len(s['controls'])/4),'body':'\n'.join(body).rstrip(),'notes':'항목의 전체 선택값·연결 API·검증·표시 조건·근거는 아래 개별 정의를 따릅니다.\n'+'\n\n'.join(notes),'ids':[c['id'] for c in cs]})
(O/'README.md').write_text('\n'.join(index)+'\n')
(Path(args.work_dir)/'doc-paragraphs.json').write_text(json.dumps(paragraphs,ensure_ascii=False))
(Path(args.work_dir)/'slides-content.json').write_text(json.dumps(slides,ensure_ascii=False))
print(json.dumps({'controls':sum(len(s['controls']) for s in x['screens']),'paragraph_chars':sum(len(t)+1 for _,t in paragraphs),'slides':len(slides),'largest_body':max(len(s['body']) for s in slides)},ensure_ascii=False))
