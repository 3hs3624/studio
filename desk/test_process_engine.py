import json,uuid
from django.test import TestCase,override_settings
from django.db import transaction,IntegrityError
from .tests import Fixtures
from .models import (RoleGrant,ProcessDefinition,ProcessVersion,ProcessRun,ProcessTask,ProcessVote,RoleDataPolicy,Department,ProcessBinding)
from . import process_engine as engine

@override_settings(SECURE_SSL_REDIRECT=False)
class ProcessEngineTests(Fixtures,TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.build_fixtures();RoleGrant.objects.create(organization=cls.org,person=cls.peer,role='SOLUTION_OPERATOR')
    def call(self,actor,action,data,id=None,runs=False,key=None):
        self.client.force_login(actor.user)
        return self.client.post('/api/v1/'+('process-runs/' if runs else 'processes/')+action+('/'+str(id) if id else ''),json.dumps(data),content_type='application/json',HTTP_IDEMPOTENCY_KEY=key or uuid.uuid4().hex)
    def selector(self,people=None):return dict(kind='USER',ids=[str(p.id) for p in (people or [self.agent])])
    def graph(self,nodes,fields=None,**kwargs):return dict(start='start',fields=fields or [],nodes=[dict(key='start',label='시작',type='START',next=nodes[0]['key']),*nodes,dict(key='end',label='종료',type='END')],**kwargs)
    def task(self,key='work',next='end',**kwargs):return dict(key=key,label=key,type='TASK',selector=self.selector(),mode='ANY',next=next,**kwargs)
    def publish(self,graph,kind='WORKFLOW',definition=None):
        payload=dict(code=definition.code if definition else 'P_'+uuid.uuid4().hex[:10],kind=kind,name='검증 프로세스',graph=graph,active=True,expected_version=definition.row_version if definition else 0,reason='구성 검증')
        result=self.call(self.admin,'save',payload,definition.id if definition else None);self.assertEqual(result.status_code,200,result.content)
        value=ProcessDefinition.objects.get(id=result.json()['id']);self.assertEqual(value.validation_errors,[],value.validation_errors)
        review=self.call(self.peer,'review',dict(expected_version=value.row_version,reason='독립 검토'),value.id);self.assertEqual(review.status_code,200,review.content)
        result=self.call(self.admin,'publish',dict(expected_version=value.row_version,reason='검증 게시'),value.id);self.assertEqual(result.status_code,200,result.content)
        value.refresh_from_db();return value.published
    def start(self,version,values=None):
        result=self.call(self.employee,'start',dict(version_id=str(version.id),title='검증 업무',values=values or {}),runs=True);self.assertEqual(result.status_code,201,result.content);return ProcessRun.objects.get(id=result.json()['id'])
    def act(self,run,task=None,actor=None,decision='COMPLETE',values=None,expected=200):
        run.refresh_from_db();task=task or run.tasks.get(status='OPEN')
        result=self.call(actor or self.agent,'act',dict(expected_version=run.row_version,task_id=str(task.id),decision=decision,values=values or {},reason='처리 근거'),run.id,True);self.assertEqual(result.status_code,expected,result.content);run.refresh_from_db();return result
    def test_task_single_and_multiple_assignees(self):
        task=self.task();task['selector']=self.selector([self.agent,self.manager]);task['mode']='ALL'
        run=self.start(self.publish(self.graph([task])))
        current=run.tasks.get();self.act(run,current);self.assertEqual(run.status,'ACTIVE');self.act(run,current,self.manager);self.assertEqual(run.status,'COMPLETED')
    def test_parallel_join_waits_for_all_branches(self):
        fork=dict(key='fork',label='병렬',type='PARALLEL',branches=['a','b'],join='join')
        version=self.publish(self.graph([fork,self.task('a','join'),self.task('b','join'),dict(key='join',label='합류',type='JOIN',next='end')]))
        run=self.start(version);tasks=list(run.tasks.order_by('node_key'));self.assertEqual(len(tasks),2)
        self.act(run,tasks[0]);self.assertEqual(run.status,'ACTIVE');self.act(run,tasks[1]);self.assertEqual(run.status,'COMPLETED')
    def test_conditional_routing_and_safe_actions(self):
        fields=[dict(key='cost',label='금액',type='number',required=True)]
        decision=dict(key='decision',label='금액 검증',type='CONDITION',condition=dict(field='cost',op='gt',value=100),true='work',false='end')
        version=self.publish(self.graph([decision,self.task()],fields));run=self.start(version,{'cost':1});self.assertEqual(run.status,'COMPLETED');run=self.start(version,{'cost':101});self.assertEqual(run.tasks.count(),1)
    def test_parent_three_child_orders_resume_only_after_all(self):
        child=self.publish(self.graph([self.task()]))
        call=dict(key='orders',label='작업 지시',type='SUBPROCESS',version_id=str(child.id),count=3,next='verify')
        parent=self.start(self.publish(self.graph([call,self.task('verify')])));gate=parent.tasks.get(kind='SUBPROCESS');children=list(ProcessRun.objects.filter(parent_task=gate));self.assertEqual(len(children),3)
        for run in children[:2]:self.act(run)
        parent.refresh_from_db();self.assertFalse(parent.tasks.filter(node_key='verify').exists());self.assertEqual(parent.status,'ACTIVE')
        self.act(children[2]);parent.refresh_from_db();self.assertTrue(parent.tasks.filter(node_key='verify',status='OPEN').exists());self.act(parent,parent.tasks.get(node_key='verify'));self.assertEqual(parent.status,'COMPLETED')
    def test_generic_transfer_links_independent_process(self):
        child=self.publish(self.graph([self.task()]))
        graph=dict(start='start',fields=[],nodes=[dict(key='start',label='시작',type='START',next='handoff'),dict(key='handoff',label='문제관리 이관',type='TRANSFER',version_id=str(child.id))])
        source=self.start(self.publish(graph));self.assertEqual(source.status,'TRANSFERRED');target=ProcessRun.objects.get(parent_task__run=source);self.act(target);source.refresh_from_db();self.assertEqual(source.status,'TRANSFERRED');self.assertEqual(engine.effective_child(source).status,'COMPLETED')
    def test_task_approval_line_after_completion(self):
        line=self.publish({'stages':[dict(key='review',label='검토 결재',selector=self.selector([self.manager]),mode='ALL')]},'APPROVAL')
        task=self.task(approval_version_id=str(line.id),approval_timing='AFTER');run=self.start(self.publish(self.graph([task])))
        self.assertEqual(run.tasks.get(status='OPEN').kind,'TASK');self.act(run);run.refresh_from_db();approval=run.tasks.get(status='OPEN');self.assertEqual(approval.kind,'APPROVAL')
        self.act(run,approval,self.manager,'APPROVE');self.assertEqual(run.status,'COMPLETED')
    def test_rejection_blocks_parent_and_retry_preserves_history(self):
        line=self.publish({'stages':[dict(key='approval',label='결재',selector=self.selector(),mode='ALL')]},'APPROVAL')
        child=self.publish(self.graph([dict(key='approve',label='결재',type='APPROVAL',version_id=str(line.id),next='end')]))
        parent=self.start(self.publish(self.graph([dict(key='children',label='하위 결재',type='SUBPROCESS',version_id=str(child.id),count=2,next='end')])));task=parent.tasks.get();children=list(ProcessRun.objects.filter(parent_task=task));self.act(children[0],decision='REJECT');parent.refresh_from_db();self.assertEqual(parent.status,'BLOCKED')
        self.act(children[1],decision='APPROVE');parent.refresh_from_db();result=self.call(self.admin,'retry_children',dict(task_id=str(task.id),expected_version=parent.row_version,reason='보완 후 재실행'),parent.id,True);self.assertEqual(result.status_code,200,result.content)
        task.refresh_from_db();self.assertNotIn(str(children[0].id),task.child_ids);retry=ProcessRun.objects.filter(parent_task=task).exclude(id__in=[c.id for c in children]).get();self.act(retry,decision='APPROVE');parent.refresh_from_db();self.assertEqual(parent.status,'COMPLETED');self.assertTrue(ProcessVote.objects.filter(task__run=children[0],decision='REJECT').exists())
    def test_screen_hidden_read_only_and_role_input_enforced(self):
        fields=[dict(key=key,label=key,type='text',required=False) for key in ('public','secret','result')]
        screen=self.publish(dict(fields=fields,read_only=[],columns=3),'SCREEN')
        node=self.task();node.update(field_modes={'public':'READ','secret':'HIDDEN','result':'EDIT'},field_roles={'result':{'write':['SERVICE_MANAGER']}})
        node['selector']=self.selector([self.agent,self.manager]);node['mode']='ALL'
        run=self.start(self.publish(self.graph([node],fields,screen_version_id=str(screen.id))),{'public':'공개','secret':'classified-secret'})
        self.client.force_login(self.agent.user);response=self.client.get('/processes/'+str(run.id));self.assertEqual(response.status_code,200,response.content);self.assertNotContains(response,'classified-secret');self.assertContains(response,'공개')
        self.act(run,values={'secret':'tamper'},expected=422);self.act(run,values={'public':'tamper'},expected=422);self.act(run,values={'result':'tamper'},expected=422)
        self.act(run);self.act(run,actor=self.manager,values={'result':'처리됨'});self.assertEqual(run.data['result'],'처리됨')
    def test_version_pin_and_independent_review_guards(self):
        old=self.publish(self.graph([self.task()]));run=self.start(old);definition=old.definition;definition.refresh_from_db();new=self.publish(self.graph([self.task('newwork')]),definition=definition)
        self.assertNotEqual(old.id,new.id);self.assertEqual(run.version_id,old.id);self.act(run);self.assertEqual(run.status,'COMPLETED')
        result=self.call(self.employee,'start',dict(version_id=str(old.id),title='오래된 접수',values={}),runs=True);self.assertEqual(result.status_code,409)
        definition.refresh_from_db();result=self.call(self.admin,'review',dict(expected_version=definition.row_version,reason='자기 검토'),definition.id);self.assertEqual(result.status_code,409)
        with self.assertRaises(IntegrityError),transaction.atomic():ProcessVersion.objects.filter(id=old.id).update(graph={})
        with self.assertRaises(IntegrityError),transaction.atomic():ProcessRun.objects.filter(id=run.id).update(version=new)
    def test_invalid_draft_saved_but_cannot_publish(self):
        graph=dict(start='start',nodes=[dict(key='start',label='시작',type='START',next='loop'),dict(key='loop',label='순환',type='ACTION',action='NOOP',next='loop')])
        response=self.call(self.admin,'save',dict(kind='WORKFLOW',code='INVALID',name='불완전 초안',graph=graph,active=True,expected_version=0,reason='작업 중'))
        self.assertEqual(response.status_code,200,response.content);self.assertTrue(response.json()['validation_errors']);definition=ProcessDefinition.objects.get(id=response.json()['id'])
        response=self.call(self.peer,'review',dict(expected_version=definition.row_version,reason='검증'),definition.id);self.assertEqual(response.status_code,422)
    def test_data_scope_and_foreign_run_access(self):
        run=self.start(self.publish(self.graph([self.task()])))
        a=Department.objects.create(organization=self.org,code='A',name='A');b=Department.objects.create(organization=self.org,code='B',name='B');self.employee.department=a;self.employee.save();self.agent.department=b;self.agent.save()
        RoleDataPolicy.objects.create(organization=self.org,role_key='AGENT',menu_key='workflow-inbox',read_scope='DEPARTMENT',write_scope='DEPARTMENT')
        self.client.force_login(self.agent.user);self.assertEqual(self.client.get('/processes/'+str(run.id)).status_code,404)
        RoleDataPolicy.objects.filter(role_key='AGENT').update(read_scope='ASSIGNED',write_scope='NONE');self.client.force_login(self.agent.user);self.assertEqual(self.client.get('/processes/'+str(run.id)).status_code,200)
        self.act(run,expected=403);self.client.force_login(self.foreign.user);self.assertEqual(self.client.get('/processes/'+str(run.id)).status_code,404)
    def test_namespaces_cannot_bypass_configuration_menu(self):
        result=self.call(self.employee,'publish',{'expected_version':1,'reason':'우회'},str(uuid.uuid4()),True);self.assertEqual(result.status_code,404)
    def test_catalog_bound_process_owns_lifecycle_and_kpi_completion(self):
        from .test_catalog import CatalogFixtures
        from .models import Ticket,RequestApproval,TimelinessTarget
        from . import services as s
        fields=[dict(key='reason',label='신청 사유',type='text',required=True)]
        version=self.publish(self.graph([self.task(field_keys=['reason'])],fields))
        publication=CatalogFixtures.publication.__func__(self,code='BOUND',workflow_version_id=str(version.id),fields=[dict(key='reason',label='신청 사유',type='text',required=True)])
        result,_=s.execute(self.manager,'catalog_publish',publication,uuid.uuid4().hex,uuid.uuid4())
        request,_=s.execute(self.employee,'req_create',dict(catalog_version_id=result['catalog_version_id'],values={'reason':'업무 신청'}),uuid.uuid4().hex,uuid.uuid4())
        ticket=Ticket.objects.get(id=request['id']);self.assertFalse(RequestApproval.objects.filter(ticket=ticket).exists());run=ProcessRun.objects.get(ticket=ticket);self.assertEqual(ticket.status,'IN_PROGRESS')
        response=self.call(self.agent,'act',dict(expected_version=run.row_version,task_id=str(run.tasks.get(status='OPEN').id),decision='COMPLETE',values={'reason':'업무 신청'},reason='처리 완료'),run.id,True);self.assertEqual(response.status_code,200,response.content)
        ticket.refresh_from_db();self.assertEqual(ticket.status,'FULFILLED');self.assertIsNotNone(TimelinessTarget.objects.get(ticket=ticket).completed_at)
    def test_wait_worker_advances_due_timer(self):
        from django.core.management import call_command
        from unittest.mock import patch
        from datetime import timedelta
        from django.utils import timezone
        version=self.publish(self.graph([dict(key='delay',label='시간 대기',type='WAIT',wait_seconds=1,next='work'),self.task()]))
        run=self.start(version)
        with patch('desk.management.commands.run_platform_worker.timezone.now',return_value=timezone.now()+timedelta(seconds=2)):
            call_command('run_platform_worker',once=True)
        run.refresh_from_db();self.assertTrue(run.tasks.filter(node_key='work',status='OPEN').exists())

    def test_screen_designer_layout_validated_and_legacy_compatible(self):
        import copy
        from . import services as s
        fs=[dict(key='title',label='제목',type='text',required=True),dict(key='detail',label='상세',type='text',required=False)]
        graph=dict(fields=fs,read_only=[],columns=3,layout=dict(mode='tabs',groups=[dict(key='basic',label='기본정보',fields=[dict(key='title',span=2,height=1)]),dict(key='details',label='상세정보',fields=[dict(key='detail',span=3,height=3)])]))
        self.assertEqual(engine.validate(self.admin,'SCREEN',graph)['layout'],graph['layout'])
        old={k:v for k,v in graph.items() if k!='layout'}
        self.assertNotIn('layout',engine.validate(self.admin,'SCREEN',old))
        for modify in [lambda g:g['layout']['groups'][0]['fields'].append(dict(key='detail',span=1,height=1)),lambda g:g['layout']['groups'][0]['fields'][0].update(span=4),lambda g:g['layout']['groups'][0]['fields'][0].update(height=True),lambda g:g['layout']['groups'][0]['fields'][0].update(key='unknown'),lambda g:g['layout']['groups'].pop(),lambda g:g['layout'].update(mode='html'),lambda g:g['layout']['groups'][0].update(script='alert(1)')]:
            bad=copy.deepcopy(graph);modify(bad)
            with self.assertRaises(s.BusinessError):engine.validate(self.admin,'SCREEN',bad)

    def test_screen_designer_published_layout_runtime_and_version_pinning(self):
        from .screen_layout import visible_groups
        fs=[dict(key='title',label='제목',type='text',required=False),dict(key='secret',label='비밀',type='text',required=False)]
        graph=dict(fields=fs,read_only=[],columns=3,layout=dict(mode='tabs',groups=[dict(key='basic',label='기본정보',fields=[dict(key='title',span=2,height=2)]),dict(key='details',label='상세정보',fields=[dict(key='secret',span=3,height=1)])]))
        screen=self.publish(graph,'SCREEN')
        version=self.publish(self.graph([self.task(screen_version_id=str(screen.id),field_modes={'title':'EDIT','secret':'HIDDEN'})],fs))
        run=self.start(version);self.client.force_login(self.agent.user);response=self.client.get('/processes/'+str(run.id));self.assertEqual(response.status_code,200)
        task=response.context['run_tasks'][0];self.assertEqual(task.screen_columns,3);self.assertEqual(task.screen_layout_mode,'tabs')
        self.assertEqual(len(task.screen_groups),1);self.assertEqual(task.screen_groups[0]['fields'][0]['span'],2)
        self.assertContains(response,'screen-height-2');self.assertContains(response,'role="tab"');self.assertNotContains(response,'상세정보');self.assertNotContains(response,'data-process-input="secret"')
        graph['layout']['mode']='sections';graph['layout']['groups'][0]['fields'][0]['span']=1
        self.publish(graph,'SCREEN',screen.definition)
        run.refresh_from_db();self.assertEqual(run.graph['nodes'][1]['screen']['layout']['mode'],'tabs')
        self.assertEqual(run.graph['nodes'][1]['screen']['layout']['groups'][0]['fields'][0]['span'],2)
        self.assertEqual(visible_groups(screen.graph,[]),[])

    def test_group_limits_override_field_edit_and_reject_forged_values(self):
        fs=[dict(key='title',label='제목',type='text',required=False),dict(key='secret',label='비밀',type='text',required=False)]
        graph=dict(fields=fs,read_only=[],columns=3,layout=dict(mode='tabs',groups=[dict(key='basic',label='기본정보',fields=[dict(key='title',span=2,height=1)]),dict(key='details',label='숨김 그룹',fields=[dict(key='secret',span=1,height=1)])]))
        screen=self.publish(graph,'SCREEN')
        version=self.publish(self.graph([self.task(screen_version_id=str(screen.id),field_modes={'title':'EDIT','secret':'EDIT'},group_modes={'basic':'READ','details':'HIDDEN'})],fs))
        run=self.start(version,{'title':'조회 값','secret':'비밀 값'});self.client.force_login(self.agent.user);response=self.client.get('/processes/'+str(run.id))
        self.assertContains(response,'조회 값');self.assertNotContains(response,'비밀 값');self.assertNotContains(response,'숨김 그룹');self.assertNotContains(response,'data-process-input="title"')
        task=run.tasks.get(status='OPEN');result=self.call(self.agent,'act',dict(expected_version=run.row_version,task_id=str(task.id),decision='COMPLETE',values={'title':'변조'},reason='위조 입력 검증'),run.id,True);self.assertEqual(result.status_code,422)
        self.act(run,values={});run.refresh_from_db();self.assertEqual(run.data['title'],'조회 값');self.assertEqual(run.status,'COMPLETED')

    def test_group_role_restriction_and_unknown_group_rejected(self):
        from . import services as s
        fs=[dict(key='title',label='제목',type='text',required=False)]
        screen=self.publish(dict(fields=fs,read_only=[],columns=1,layout=dict(mode='sections',groups=[dict(key='basic',label='기본정보',fields=[dict(key='title',span=1,height=1)])])),'SCREEN')
        graph=self.graph([self.task(screen_version_id=str(screen.id),field_roles={'title':{'read':['AGENT'],'write':['AGENT']}},group_roles={'basic':{'read':['SERVICE_MANAGER'],'write':['SERVICE_MANAGER']}})],fs)
        run=self.start(self.publish(graph),{'title':'그룹 권한 비밀'});self.client.force_login(self.agent.user);response=self.client.get('/processes/'+str(run.id));self.assertNotContains(response,'그룹 권한 비밀');self.assertNotContains(response,'기본정보')
        graph['nodes'][1]['group_modes']={'unknown':'HIDDEN'}
        with self.assertRaises(s.BusinessError):engine.validate(self.admin,'WORKFLOW',graph)

    def test_group_write_role_and_approval_expansion_preserve_group_limits(self):
        fs=[dict(key='title',label='제목',type='text',required=False)]
        screen=self.publish(dict(fields=fs,read_only=[],columns=1,layout=dict(mode='sections',groups=[dict(key='basic',label='기본정보',fields=[dict(key='title',span=1,height=1)])])),'SCREEN')
        approval=self.publish(dict(stages=[dict(key='approve',label='결재',selector=self.selector([self.manager]),mode='ALL')]),'APPROVAL')
        version=self.publish(self.graph([self.task(screen_version_id=str(screen.id),approval_version_id=str(approval.id),approval_timing='BEFORE',group_modes={'basic':'EDIT'},group_roles={'basic':{'read':['AGENT','SERVICE_MANAGER'],'write':['SERVICE_MANAGER']}})],fs))
        run=self.start(version,{'title':'원본 값'});self.assertEqual(next(n for n in run.graph['nodes'] if n['type']=='APPROVAL')['group_roles']['basic']['write'],['SERVICE_MANAGER'])
        self.act(run,actor=self.manager,decision='APPROVE');task=run.tasks.get(status='OPEN');self.client.force_login(self.agent.user);response=self.client.get('/processes/'+str(run.id));self.assertContains(response,'원본 값');self.assertNotContains(response,'data-process-input="title"')
        result=self.call(self.agent,'act',dict(expected_version=run.row_version,task_id=str(task.id),decision='COMPLETE',values={'title':'변조'},reason='역할 제한 검증'),run.id,True);self.assertEqual(result.status_code,422)
