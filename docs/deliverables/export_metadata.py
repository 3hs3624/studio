"""Export model/code metadata only; never read business records or secrets."""
import os,json,sys
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
info=[['항목','정의'],['기준일','2026-11-14'],['소스 커밋','57d11968946f690f5d8cd2a54faad9f8762df29e'],['마이그레이션','0020_process_api_task'],['범위','Django 모델 메타데이터. 실제 사용자·업무·인증 값은 포함하지 않음'],['동적 엔티티','EntityRecord JSON/게시 EntitySchemaVersion으로 관리. 엔티티 생성 시 물리 테이블을 매번 만들지 않음'],['코드 구분','이 문서는 프로그램 상수·DB 허용값. 운영 공통코드 실제 데이터는 조직별 CodeGroup/CodeItem에서 별도 관리'],['기본 필드','엔티티 고정 필드는 desk/entities/system_fields.py 참고. id·organization_id·schema_version_id·생성/수정자/시각·row_version 등'],['검증','회귀 278개 통과(15개 PG 전용 제외), 후속 집중 23개 통과. CI/배포 상태는 기능명세서 참조']]
Path(sys.argv[1]).write_text(json.dumps({'tables':{'안내':info,'테이블 목록':summary,'필드 정의':fields,'제약·인덱스':constraints},'codes':{'안내':info,'코드 정의':codes}},ensure_ascii=False,indent=2))
print('Exported',len(summary)-1,'tables;',len(fields)-1,'fields;',len(codes)-1,'code definitions')
