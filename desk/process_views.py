from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from .views import context
from . import services as s,process_engine as engine
from .permissions import require,allowed
from .models import (Person,Group,Department,ProcessDefinition,ProcessVersion,ProcessReview,ProcessRun,ProcessTask,ProcessBinding,ProcessRetirement,ProcessVote)
from .access_graph import departments_tree
from .models import IntegrationVersion


def versions(actor,kind):return ProcessVersion.objects.filter(organization=actor.organization,definition__kind=kind,definition__active=True,processretirement__isnull=True).select_related('definition').order_by('definition__name','-version')

@login_required
def manage(request,kind='WORKFLOW',id=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'workflow.manage')
        value=engine.definition(actor,id) if id else None
        if value and value.kind!=kind:s.fail('NOT_FOUND','정의 유형이 다릅니다.',404)
        base={'WORKFLOW':'/console/workflows','APPROVAL':'/console/approval-lines','SCREEN':'/console/screens'}[kind]
        tab=request.GET.get('tab','design')
        if tab not in ('design','versions','bindings','runs'):s.fail('NOT_FOUND','탭을 찾을 수 없습니다.',404)
        from .identity_views import tabs
        c.update(**tabs(base+'/'+str(id) if id else base,tab,[('design','설계·초안'),('versions','버전·검토·게시'),('bindings','업무 메뉴 연결'),('runs','실행 현황')]),
            process_kind=kind,process_base=base,process_definition=value,process_definitions=ProcessDefinition.objects.filter(organization=actor.organization,kind=kind).order_by('name'),
            process_versions=value.versions.order_by('-version') if value else [],screen_versions=versions(actor,'SCREEN'),approval_versions=versions(actor,'APPROVAL'),workflow_versions=versions(actor,'WORKFLOW'))
        from .organization_views import catalog
        targets={'USER':[{'id':str(p.id),'name':p.display_name+' · '+p.user.username} for p in Person.objects.filter(organization=actor.organization,active=True,user__is_active=True).select_related('profile','user')],
          'ROLE':[{'id':r['key'],'name':r['name']} for r in catalog(actor)],'GROUP':[{'id':str(g.id),'name':g.name} for g in Group.objects.filter(organization=actor.organization,active=True)],
          'DEPARTMENT':[{'id':str(d.id),'name':d.indent+d.name} for d in departments_tree(actor.organization) if d.active]}
        c.update(process_api_options=[dict(id=str(v.id),label=v.definition.name+' · v'+str(v.version)) for v in IntegrationVersion.objects.filter(organization=actor.organization,definition__active=True).select_related('definition')],process_screen_options=[dict(id=str(v.id),label=v.definition.name+' · v'+str(v.version),graph=v.graph) for v in versions(actor,'SCREEN')],process_approval_options=[dict(id=str(v.id),label=v.definition.name+' · v'+str(v.version)) for v in versions(actor,'APPROVAL')],process_workflow_options=[dict(id=str(v.id),label=v.definition.name+' · v'+str(v.version)) for v in versions(actor,'WORKFLOW')],process_targets=targets,process_draft=value.draft if value else {'fields':[],'read_only':[],'columns':3} if kind=='SCREEN' else {'stages':[]} if kind=='APPROVAL' else {'start':'start','fields':[],'nodes':[{'key':'start','label':'시작','type':'START','next':'end'},{'key':'end','label':'종료','type':'END'}]},
          process_reviews=ProcessReview.objects.filter(definition=value).select_related('reviewer').order_by('-created_at')[:20] if value else [],
          binding=ProcessBinding.objects.filter(organization=actor.organization,menu_key='service-request').select_related('version__definition').first(),
          process_runs=ProcessRun.objects.filter(organization=actor.organization,version__definition=value).order_by('-created_at')[:100] if value else ProcessRun.objects.filter(organization=actor.organization).order_by('-created_at')[:100])
        return render(request,'desk/process-manage.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)

@login_required
def inbox(request,id=None):
    try:
        c=context(request);actor=c['actor'];require(actor,'workflow.use')
        c['available_processes']=[d for d in ProcessDefinition.objects.filter(organization=actor.organization,kind='WORKFLOW',active=True,published__isnull=False,published__processretirement__isnull=True).select_related('published') if not d.published.graph.get('catalog_only')]
        if id:
            run=engine.run_for(actor,id)
            tasks=list(run.tasks.order_by('created_at','id'))
            for task in tasks:
                task.can_act=task.status=='OPEN' and task.kind in ('TASK','APPROVAL') and str(actor.id) in task.person_ids and actor.id in engine.recipients(actor,task.selector,run) and not (task.kind=='APPROVAL' and run.started_by_id==actor.id) and not ProcessVote.objects.filter(task=task,actor=actor).exists()
                task.participants=Person.objects.filter(organization=actor.organization,id__in=task.person_ids).select_related('profile')
                task.children=ProcessRun.objects.filter(organization=actor.organization,id__in=task.child_ids).select_related('version__definition')
                node=next(n for n in run.graph['nodes'] if n['key']==task.node_key)
                task.output_fields=[{**field,'value':run.data.get(field['key'],''),'required':True,'read_only':False} for field in run.graph.get('fields',[]) if field['key'] in node.get('output_mapping',{})]
                task.screen_columns=node.get('screen',{}).get('columns',2)
                task.fields=engine.task_fields(actor,run,node,task,task.can_act)
            c.update(process_run=run,run_tasks=tasks,run_events=run.events.select_related('actor').order_by('created_at','id'),can_manage_process=allowed(actor,'workflow.manage'),can_cancel_process=run.started_by_id==actor.id or allowed(actor,'workflow.manage'),reassign_people=Person.objects.filter(organization=actor.organization,active=True,user__is_active=True).select_related('profile'),run_parent=run.parent_task.run if run.parent_task_id else None)
        else:
            query=ProcessRun.objects.filter(organization=actor.organization).select_related('version__definition','started_by')
            if not allowed(actor,'workflow.manage'):query=query.filter(Q(started_by=actor)|Q(tasks__assignments__person=actor)).distinct()
            from .data_access import restrict
            query=restrict(actor,'workflow-inbox',query,'started_by','tasks__assignments__person_id')
            scope=request.GET.get('scope','all')
            if scope=='assigned':query=query.filter(tasks__assignments__person=actor,tasks__status='OPEN').distinct()
            elif scope=='mine':query=query.filter(started_by=actor)
            from django.core.paginator import Paginator
            c['run_page']=Paginator(query.order_by('-created_at','-id'),25).get_page(request.GET.get('page',1));c['run_scope']=scope
            start=request.GET.get('start')
            if start:
                value=engine.version(actor,start,'WORKFLOW',True)
                c.update(start_version=value,start_graph=engine.compile_graph(actor,value))
        return render(request,'desk/process-inbox.html',c)
    except s.BusinessError as exc:return HttpResponse(exc.message,status=exc.status)
