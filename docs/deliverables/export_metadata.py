"""Export model/code metadata only; never read business records or secrets."""
import os,json,sys,argparse,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.apps import apps
from django.db.models import NOT_PROVIDED
from desk.permissions import PERMISSIONS,BUILTIN
from desk.menu_access import MENUS
from desk.process_engine import KINDS
from desk.timeliness import BASES
from desk.integrations.service import PROTOCOLS,AUTH
from desk.data_types import TYPE_META,SCREEN_TYPES
from desk.dashboard_tasks import SCOPES

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('output')
parser.add_argument('--commit',required=True,help='Verified source commit, not an inferred local HEAD')
parser.add_argument('--as-of',required=True,help='Documentation baseline date (YYYY-MM-DD)')
args=parser.parse_args()
if not re.fullmatch(r'[0-9a-f]{40}',args.commit):parser.error('--commit must be a full commit SHA')
if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',args.as_of):parser.error('--as-of must be YYYY-MM-DD')

summary=[['테이블','모델','앱','PK','필드 수','제약 수']];fields=[['테이블','필드','DB 열','Django 타입','최대 길이','NULL','PK','고유','기본값','참조 대상','삭제 정책','인덱스','choices / 설명']];constraints=[['테이블','구분','이름','정의']]
for model in sorted([m for app in ('desk','auth','contenttypes','sessions') for m in apps.get_app_config(app).get_models(include_auto_created=True)],key=lambda m:m._meta.db_table):
 meta=model._meta;summary.append([meta.db_table,model.__name__,meta.app_label,meta.pk.column,len(meta.local_fields),len(meta.constraints)])
 for f in meta.local_fields:
  default='' if f.default is NOT_PROVIDED else f.default.__module__+'.'+f.default.__name__ if callable(f.default) else str(f.default)
  remote=f.remote_field.model._meta.db_table if f.is_relation else ''
  deletion=getattr(f.remote_field.on_delete,'__name__','') if f.is_relation else ''
  choices=json.dumps(list(f.flatchoices),ensure_ascii=False) if f.choices else str(f.verbose_name)
  fields.append([meta.db_table,f.name,f.column,f.get_internal_type(),f.max_length or '',str(f.null),str(f.primary_key),str(f.unique),default,remote,deletion,str(f.db_index),choices])
 for c in meta.constraints:constraints.append([meta.db_table,c.__class__.__name__,c.name,str(getattr(c,'condition',None) or getattr(c,'fields',''))])
 for i in meta.indexes:constraints.append([meta.db_table,'Index',i.name,str(i.fields)])
codes=[['분류','그룹','값','표시·설명','출처']]
for m in apps.get_app_config('desk').get_models():
 for f in m._meta.fields:
  for value,label in f.flatchoices:codes.append(['필드 선택',m.__name__+'.'+f.name,str(value),str(label),'desk/models.py'])
 for c in m._meta.constraints:
  def visit(q):
   for part in getattr(q,'children',[]):
    if isinstance(part,tuple) and part[0].endswith('__in') and isinstance(part[1],(list,tuple)):
     for value in part[1]:codes.append(['DB 허용값',m.__name__+'.'+part[0][:-4],str(value),'제약 '+c.name,'desk/models.py'])
    elif not isinstance(part,tuple):visit(part)
  visit(getattr(c,'condition',None))
for key,(label,scope) in PERMISSIONS.items():codes.append(['기능 권한','PERMISSIONS',key,label+' · '+scope,'desk/permissions.py'])
for key,perms in BUILTIN.items():codes.append(['기본 역할','BUILTIN',key,', '.join(sorted(perms)),'desk/permissions.py'])
for key,(label,pages,apis,cap) in MENUS.items():codes.append(['메뉴','MENUS',key,label+' | '+', '.join(pages)+' | '+cap,'desk/menu_access.py'])
for group,values,source in [('워크플로우 노드',{k:k for k in KINDS},'desk/process_engine.py'),('KPI 기준',BASES,'desk/timeliness.py'),('API 프로토콜',PROTOCOLS,'desk/integrations/service.py'),('API 인증',AUTH,'desk/integrations/service.py')]:
 for key,label in sorted(values.items()):codes.append(['플랫폼 코드',group,key,label,source])
for key,(label,icon,category) in TYPE_META.items():
 codes.append(['논리 필드 유형','TYPE_META',key,label+' · '+category+' · '+('엔티티/화면' if key in SCREEN_TYPES else '엔티티 전용'),'desk/data_types.py'])
for key,label in SCOPES:codes.append(['조회 범위','todo_scope',key,label,'desk/dashboard_tasks.py'])
for group,values,source in [('그룹 표시',{'sections':'그룹 나열','tabs':'탭'},'docs/form-designer.md'),('태스크 모드',{'EDIT':'입력 허용 범위','READ':'조회 전용','HIDDEN':'숨김'},'desk/process_engine.py'),('자동 기본값',{'CURRENT_TIMESTAMP':'시간대 포함 현재 일시','CURRENT_DATE':'현재 날짜','UUID':'UUID 생성'},'desk/data_types.py')]:
 for key,label in values.items():codes.append(['화면·프로세스 설정',group,key,label,source])
info=[['항목','정의'],['기준일',args.as_of],['소스 커밋',args.commit],['마이그레이션','0020_process_api_task'],['범위','Django 모델 메타데이터. 실제 사용자·업무·인증 값은 포함하지 않음'],['동적 엔티티','EntityRecord JSON/게시 EntitySchemaVersion으로 관리. 엔티티 생성 시 물리 테이블을 매번 만들지 않음'],['코드 구분','프로그램 상수·DB 허용값. 조직별 운영 코드는 CommonCodeGroup/CommonCodeItem에서 별도 관리'],['기본 필드','id·organization_id·schema_version_id·created_at·created_by·updated_at·updated_by·row_version: 서버 소유 8개'],['검증','CI·배포 증거는 기능명세서 및 docs/deliverables/README.md 참조. 이 스크립트는 DB 실사/운영 검수를 실행하지 않음'],['물리 스키마 제한','네이티브 타입 매핑·복합 업무 PK·UI 인덱스 DDL·스키마 이관 작업자는 미구현. Django 타입을 실제 운영 DB 타입 실사로 간주하지 않음']]
contracts=[['저장 위치','항목','형식·허용값','검증·동작','근거'],
 ['ProcessDefinition.draft_graph / ProcessVersion.graph','fields[]','key,label,type,required,readonly 등','화면/프로세스 최대 30필드; 논리 타입 검증','desk/process_engine.py'],
 ['ProcessVersion.graph','fields[].max_length','정수 1~65535','문자/장문/email/phone/url에만 설정','desk/data_types.py'],
 ['ProcessVersion.graph','fields[].precision / scale','precision 1~38 / scale 0~min(precision,18)','decimal만 허용; 기본 18,2; 문자열로 값 보존','desk/data_types.py'],
 ['ProcessVersion.graph','fields[].default / default_function','리터럴 또는 CURRENT_TIMESTAMP/CURRENT_DATE/UUID','동시 설정 금지; 신규 생성에만 적용; SQL/Python 실행 없음','desk/data_types.py'],
 ['ProcessVersion.graph','layout.mode','sections / tabs','그룹 나열 또는 탭; layout 없는 기존 화면 호환','docs/form-designer.md'],
 ['ProcessVersion.graph','layout.groups[]','key,label,fields[]','최대 20그룹; 필드는 정확히 한 그룹에 포함','docs/form-designer.md'],
 ['ProcessVersion.graph','layout.groups[].fields[]','key,span,height','span 1~화면 열수(최대3); height 1~5, 48px 단위','docs/form-designer.md'],
 ['ProcessVersion.graph 노드','group_modes / group_roles','그룹 식별자별 모드·조회/입력 역할','그룹 제한을 필드 허용으로 해제할 수 없음; 서버에서 숨김/변경 차단','docs/form-designer.md'],
 ['ProcessVersion.graph 노드','field_modes / field_roles','필드별 숨김·조회·입력·역할','화면 조회전용 및 태스크 할당과 함께 제한 합성','desk/process_engine.py'],
 ['EntitySchemaVersion.fields','[]','논리 유형 21개, 관계·메타데이터','게시 JSON 스키마; 물리 컬럼 DDL 아님','desk/data_types.py'],
 ['URL 조회 조건(비저장)','todo_scope','all / department / mine','기본 mine; 부서는 담당자의 현재 부서, 하위 부서 제외; 기존 권한 유지','desk/dashboard_tasks.py']]
Path(args.output).write_text(json.dumps({'tables':{'안내':info,'테이블 목록':summary,'필드 정의':fields,'제약·인덱스':constraints,'JSON 구성 계약':contracts},'codes':{'안내':info,'코드 정의':codes}},ensure_ascii=False,indent=2),encoding='utf-8')
print('Exported',len(summary)-1,'tables;',len(fields)-1,'fields;',len(codes)-1,'code definitions')
