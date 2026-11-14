'use strict';
(()=>{
const form=document.getElementById('process-editor');if(!form)return;
const read=id=>JSON.parse(document.getElementById(id).textContent),draft=read('process-draft'),targets=read('process-targets'),screens=read('process-screens'),approvals=read('process-approvals'),workflows=read('process-workflows'),apis=read('process-apis'),kind=form.dataset.processKind;
const positions={...(draft.positions||{})};let sequence=0;
const el=(tag,text)=>{const item=document.createElement(tag);if(text!==undefined)item.textContent=text;return item;};
const input=(value='',type='text')=>{const item=el('input');item.type=type;item.value=value??'';if(type==='text')item.maxLength=2000;return item;};
const select=(options,value,multiple=false)=>{const item=el('select');item.multiple=multiple;if(multiple)item.size=4;for(const option of options){const entry=el('option',option.name??option.label??option.id);entry.value=option.id;entry.selected=multiple?(value||[]).includes(option.id):option.id===value;item.append(entry);}return item;};
const label=(name,item)=>{const box=el('label',name);box.append(item);return box;};
const checkbox=checked=>{const item=input('','checkbox');item.checked=!!checked;return item;};
const setData=(node,name,value)=>{node.dataset[name]=value;return node;};
const fieldBody=form.querySelector('[data-process-fields]'),nodeBody=form.querySelector('[data-process-nodes]');
function fields(){return fieldBody?Array.from(fieldBody.children).map(row=>({key:row.querySelector('[data-p=key]').value,label:row.querySelector('[data-p=label]').value,type:row.querySelector('[data-p=type]').value,required:row.querySelector('[data-p=required]').checked,...(row.querySelector('[data-p=group_id]').value?{group_id:row.querySelector('[data-p=group_id]').value}:{})})):[];}
function addField(field={key:'field_'+(++sequence),label:'새 항목',type:'text',required:false}){
 const row=el('tr');for(const [key,node] of [['key',input(field.key)],['label',input(field.label)],['type',select([{id:'text',name:'문자'},{id:'number',name:'숫자'},{id:'boolean',name:'예·아니오'},{id:'person',name:'담당자'}],field.type)],['required',checkbox(field.required)],['group_id',select([{id:'',name:'전체 조직'},...(targets.GROUP||[])],field.group_id||'')]]){const cell=el('td');cell.append(setData(node,'p',key));row.append(cell);}
 if(kind==='SCREEN'){const cell=el('td');cell.append(setData(checkbox((draft.read_only||[]).includes(field.key)),'p','readonly'));row.append(cell);}
 const cell=el('td'),remove=el('button','제거');remove.type='button';remove.className='secondary';remove.addEventListener('click',()=>row.remove());cell.append(remove);row.append(cell);fieldBody.append(row);
}
function selectorControls(parent,spec={kind:'USER',ids:[]}){
 spec=spec&&typeof spec==='object'?spec:{kind:'USER',ids:[]};
 const type=select(['USER','ROLE','GROUP','DEPARTMENT','STARTER','FIELD_USER'].map((id,index)=>({id,name:['사용자','역할','그룹','부서','신청자 자동','선택 담당자 필드'][index]})),spec.kind),items=select(spec.kind==='FIELD_USER'?fields().filter(f=>f.type==='person').map(f=>({id:f.key,name:f.label})):targets[spec.kind]||[],spec.ids,true),sub=checkbox(spec.include_children);
 type.dataset.p='selectorKind';items.dataset.p='selectorIds';sub.dataset.p='selectorChildren';type.addEventListener('change',()=>{const replacement=select(type.value==='FIELD_USER'?fields().filter(f=>f.type==='person').map(f=>({id:f.key,name:f.label})):targets[type.value]||[],[],true);replacement.dataset.p='selectorIds';items.replaceChildren(...replacement.children);});
 parent.append(label('할당 유형',type),label('할당 대상 · 복수 선택',items),label('하위 부서 포함',sub));
}
function control(parent,key,text,node){node.dataset.p=key;parent.append(label(text,node));return node;}
function refOptions(values){return [{id:'',name:'선택 안 함'},...values];}
function mapping(value){return Object.entries(value||{}).map(([key,value])=>key+'='+value).join(', ');}
function parseMapping(value){const result={};for(const part of value.split(',').map(v=>v.trim()).filter(Boolean)){const pair=part.split('=').map(v=>v.trim());if(pair.length!==2||!pair[0]||!pair[1]||pair[0] in result)throw Error('항목 매핑은 중복 없이 대상=원본 형식으로 입력하십시오.');result[pair[0]]=pair[1];}return result;}
function scalar(value,key){const field=fields().find(f=>f.key===key);if(field?.type==='number')return Number(value);if(field?.type==='boolean'){if(!['true','false'].includes(value))throw Error('예·아니오 비교 값은 true 또는 false로 입력하십시오.');return value==='true';}return value;}
function fieldRules(row,node){
 const output=row.querySelector('[data-field-rules]');output.replaceChildren();const screen=screens.find(v=>v.id===(row.querySelector('[data-p=screen_version_id]')?.value||form.querySelector('[name=common_screen]')?.value));const fs=screen?.graph.fields||fields();
 for(const field of fs){const line=el('div');line.className='field-access-row';line.dataset.ruleField=field.key;const title=el('strong',field.label+' · '+field.key);line.append(title);
 const mode=node.field_modes?.[field.key]||((node.field_keys||[]).includes(field.key)?'EDIT':screen&&node.type==='TASK'?'EDIT':'READ');control(line,'fieldMode','표시·입력',select([{id:'HIDDEN',name:'숨김'},{id:'READ',name:'조회 전용'},{id:'EDIT',name:'입력 가능'}],mode));
 control(line,'fieldRequired','이 태스크에서 필수',checkbox((node.required_fields||[]).includes(field.key)));control(line,'fieldReadRoles','조회 역할 · 미선택은 제한 없음',select(targets.ROLE,node.field_roles?.[field.key]?.read||[],true));control(line,'fieldWriteRoles','입력 역할 · 미선택은 제한 없음',select(targets.ROLE,node.field_roles?.[field.key]?.write||[],true));output.append(line);}
}
function addNode(node){
 node=node||{key:(kind==='APPROVAL'?'stage_':'node_')+(++sequence),label:kind==='APPROVAL'?'새 결재 단계':'새 업무',type:'TASK',selector:{kind:'USER',ids:[]},mode:'ALL',next:'end'};
 const row=el('section');row.className='process-node';row.dataset.processNode='';const heading=el('div');heading.className='user-create-grid';control(heading,'key','식별자',input(node.key));control(heading,'label','이름',input(node.label));
 if(kind==='WORKFLOW')control(heading,'type','노드 유형',select(['START','TASK','APPROVAL','CONDITION','PARALLEL','JOIN','WAIT','SUBPROCESS','TRANSFER','API','ACTION','END'].map((id,index)=>({id,name:['시작','업무 태스크','독립 결재','조건 분기','병렬 분기','병렬 합류','시간 대기','하위 프로세스 호출','타 프로세스 이관','API 호출','데이터 동작','종료'][index]})),node.type));
 row.append(heading);const details=el('details');details.open=kind==='APPROVAL';details.append(el('summary','할당·연결·결재·화면 설정'));const grid=el('div');grid.className='user-create-grid';selectorControls(grid,node.selector);control(grid,'mode','복수 담당자 처리',select([{id:'ALL',name:'전원 처리'},{id:'ANY',name:'한 명 처리'}],node.mode||'ALL'));
 if(kind==='WORKFLOW'){
 for(const [key,text] of [['next','다음 노드'],['reject','반려 시 노드 · 비우면 반려 종료'],['true','조건 참 경로'],['false','조건 거짓 경로'],['branches','병렬 시작 노드 · 쉼표'],['join','병렬 합류 노드']])control(grid,key,text,input(key==='branches'?(node.branches||[]).join(', '):node[key]||''));
 control(grid,'api_version_id','게시 API 버전',select(refOptions(apis),node.api_version_id||''));
 control(grid,'version_id','하위·이관 프로세스 또는 독립 결재 버전',select(refOptions([...workflows,...approvals]),node.version_id||''));control(grid,'count','하위 작업 수',input(node.count??1,'number'));control(grid,'count_field','하위 작업 수를 정하는 숫자 항목',input(node.count_field||''));
 control(grid,'input_mapping','하위 입력 매핑 · 하위항목=상위항목',input(mapping(node.input_mapping)));control(grid,'output_mapping','하위 결과 매핑 · 상위항목=하위항목',input(mapping(node.output_mapping)));
 control(grid,'approval_version_id','이 태스크의 결재선 버전',select(refOptions(approvals),node.approval_version_id||''));control(grid,'approval_timing','결재 시점',select([{id:'BEFORE',name:'업무 처리 전'},{id:'AFTER',name:'업무 처리 후'}],node.approval_timing||'AFTER'));
 control(grid,'screen_version_id','별도 화면 버전 · 비우면 공통 화면',select(refOptions(screens),node.screen_version_id||''));
 control(grid,'conditionField','조건 데이터 항목',input(node.condition?.field||''));control(grid,'conditionOp','조건 연산자',select(['eq','ne','gt','gte','lt','lte','in','empty'].map((id,index)=>({id,name:['같음','다름','초과','이상','미만','이하','목록 포함','빈 값'][index]})),node.condition?.op||'eq'));control(grid,'conditionValue','비교 값 · 목록은 쉼표 / 논리는 true·false',input(Array.isArray(node.condition?.value)?node.condition.value.join(', '):node.condition?.value??''));
 control(grid,'wait_seconds','대기 시간 · 초',input(node.wait_seconds||60,'number'));control(grid,'action','데이터 동작',select([{id:'NOOP',name:'전이만 수행'},{id:'SET_FIELD',name:'항목 값 설정'}],node.action||'NOOP'));control(grid,'field','설정할 데이터 항목',input(node.field||''));control(grid,'value','설정 값',input(node.value??''));
 }
 details.append(grid);
 if(kind==='WORKFLOW'){const refresh=el('button','공통 화면·데이터 항목으로 필드 규칙 갱신');refresh.type='button';refresh.className='secondary';const rules=el('div');rules.dataset.fieldRules='';details.append(refresh,rules);refresh.addEventListener('click',()=>{const saved=serializeNode(row);fieldRules(row,saved);});}
 row.append(details);const remove=el('button','이 노드 제거');remove.type='button';remove.className='secondary';remove.addEventListener('click',()=>row.remove());row.append(remove);nodeBody.append(row);if(kind==='WORKFLOW')fieldRules(row,node);
}
function serializeNode(row){const value=key=>row.querySelector('[data-p='+key+']')?.value||'',multi=key=>Array.from(row.querySelector('[data-p='+key+']')?.selectedOptions||[]).map(o=>o.value);const node={key:value('key'),label:value('label')};node.selector={kind:value('selectorKind'),ids:multi('selectorIds'),include_children:row.querySelector('[data-p=selectorChildren]').checked};node.mode=value('mode');if(kind==='APPROVAL')return node;
 node.type=value('type');const type=node.type;if(!['TASK','APPROVAL'].includes(type)){delete node.selector;delete node.mode;}
 if(!['END','TRANSFER','PARALLEL','CONDITION'].includes(type))node.next=value('next');
 if(['TASK','APPROVAL'].includes(type)&&value('reject'))node.reject=value('reject');
 if(type==='PARALLEL'){node.branches=value('branches').split(',').map(v=>v.trim()).filter(Boolean);node.join=value('join');}
 if(['SUBPROCESS','TRANSFER','APPROVAL'].includes(type))node.version_id=value('version_id');
 if(type==='API'){node.api_version_id=value('api_version_id');node.input_mapping=parseMapping(value('input_mapping'));node.output_mapping=parseMapping(value('output_mapping'));}
 if(['SUBPROCESS','TRANSFER'].includes(type)){node.count=Number(value('count'));node.count_field=value('count_field');node.input_mapping=parseMapping(value('input_mapping'));node.output_mapping=parseMapping(value('output_mapping'));}
 if(type==='TASK'&&value('approval_version_id')){node.approval_version_id=value('approval_version_id');node.approval_timing=value('approval_timing');}
 if(type==='TASK'&&value('screen_version_id'))node.screen_version_id=value('screen_version_id');
 if(type==='CONDITION'){const field=value('conditionField'),op=value('conditionOp');node.true=value('true');node.false=value('false');node.condition={field,op};if(op!=='empty')node.condition.value=op==='in'?value('conditionValue').split(',').map(v=>scalar(v.trim(),field)):scalar(value('conditionValue'),field);}
 if(type==='WAIT')node.wait_seconds=Number(value('wait_seconds'));
 if(type==='ACTION'){node.action=value('action');if(node.action==='SET_FIELD'){node.field=value('field');node.value=scalar(value('value'),node.field);}}
 if(['TASK','APPROVAL','WAIT','SUBPROCESS','TRANSFER'].includes(type)){node.field_modes={};node.field_roles={};node.required_fields=[];node.field_keys=[];for(const line of row.querySelectorAll('[data-rule-field]')){const key=line.dataset.ruleField,mode=line.querySelector('[data-p=fieldMode]').value;node.field_modes[key]=mode;if(mode==='EDIT')node.field_keys.push(key);if(line.querySelector('[data-p=fieldRequired]').checked)node.required_fields.push(key);node.field_roles[key]={read:Array.from(line.querySelector('[data-p=fieldReadRoles]').selectedOptions).map(v=>v.value),write:Array.from(line.querySelector('[data-p=fieldWriteRoles]').selectedOptions).map(v=>v.value)};}}
 return node;
}
window.buildProcessGraph=()=>{
 if(kind==='SCREEN')return {fields:fields(),read_only:Array.from(fieldBody.children).filter(row=>row.querySelector('[data-p=readonly]').checked).map(row=>row.querySelector('[data-p=key]').value),columns:Number(form.elements.screen_columns.value)};
 const nodes=Array.from(nodeBody.children).map(serializeNode);if(kind==='APPROVAL')return {stages:nodes};
 const graph={catalog_only:form.elements.catalog_only.checked,close_on_complete:form.elements.close_on_complete.checked,ticket_assignee_field:form.elements.ticket_assignee_field.value,start:form.elements.start_node.value,fields:fields(),nodes,positions:Object.fromEntries(Object.entries(positions).filter(([key])=>nodes.some(n=>n.key===key)))};if(form.elements.common_screen.value)graph.screen_version_id=form.elements.common_screen.value;return graph;
};
function draw(){try{
 const graph=window.buildProcessGraph(),svg=form.querySelector('[data-process-canvas]');svg.replaceChildren();const ns='http://www.w3.org/2000/svg',make=name=>document.createElementNS(ns,name);const computed=new Map(graph.nodes.map((node,index)=>[node.key,positions[node.key]||{x:40+(index%3)*330,y:40+Math.floor(index/3)*160}]));let height=300,width=1100;
 for(const point of computed.values()){height=Math.max(height,point.y+180);width=Math.max(width,point.x+300);}svg.setAttribute('viewBox','0 0 '+width+' '+height);svg.setAttribute('width',width);svg.setAttribute('height',height);
 for(const node of graph.nodes){const source=computed.get(node.key),edges=['next','true','false','reject'].filter(k=>node[k]).map(k=>[node[k],k]).concat((node.branches||[]).map(key=>[key,'branch']));for(const [key,label_] of edges){const target=computed.get(key);if(!target)continue;const line=make('path');line.setAttribute('d',`M${source.x+120},${source.y+66} C${source.x+120},${source.y+110} ${target.x+120},${target.y-40} ${target.x+120},${target.y}`);line.setAttribute('class','process-edge');svg.append(line);const text=make('text');text.setAttribute('x',source.x+125);text.setAttribute('y',source.y+90);text.textContent=label_;svg.append(text);}}
 for(const node of graph.nodes){const point=computed.get(node.key),g=make('g'),rect=make('rect'),text=make('text'),caption=make('text');g.setAttribute('transform',`translate(${point.x},${point.y})`);g.setAttribute('tabindex','0');g.setAttribute('role','button');g.setAttribute('aria-label',node.label+' 노드 배치');rect.setAttribute('width','240');rect.setAttribute('height','66');rect.setAttribute('class','process-graph-node');text.setAttribute('x','12');text.setAttribute('y','25');text.textContent=node.label;caption.setAttribute('x','12');caption.setAttribute('y','49');caption.textContent=node.key+' · '+node.type;g.append(rect,text,caption);svg.append(g);let drag=null;
 g.addEventListener('pointerdown',event=>{drag={x:event.clientX,y:event.clientY,point:{...computed.get(node.key)}};g.setPointerCapture(event.pointerId);});g.addEventListener('pointermove',event=>{if(!drag)return;const scale=svg.viewBox.baseVal.width/svg.getBoundingClientRect().width;const location={x:Math.max(0,Math.min(4000,Math.round(drag.point.x+(event.clientX-drag.x)*scale))),y:Math.max(0,Math.min(4000,Math.round(drag.point.y+(event.clientY-drag.y)*scale)))};positions[node.key]=location;g.setAttribute('transform',`translate(${location.x},${location.y})`);});g.addEventListener('pointerup',()=>{drag=null;form.dispatchEvent(new Event('input',{bubbles:true}));draw();});g.addEventListener('keydown',event=>{const offset={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-20],ArrowDown:[0,20]}[event.key];if(offset){event.preventDefault();positions[node.key]={x:Math.max(0,Math.min(4000,point.x+offset[0])),y:Math.max(0,Math.min(4000,point.y+offset[1]))};draw();}});
 }
 }catch(reason){const box=form.querySelector('.form-error');box.textContent=reason.message;box.hidden=false;}}
if(fieldBody){for(const field of Array.isArray(draft.fields)?draft.fields:[])addField(field);form.querySelector('[data-process-add-field]').addEventListener('click',()=>addField());}
if(nodeBody){for(const node of (kind==='APPROVAL'?(Array.isArray(draft.stages)?draft.stages:[]):(Array.isArray(draft.nodes)?draft.nodes:[])))addNode(node);form.querySelector('[data-process-add-node]').addEventListener('click',()=>addNode());}
if(kind==='SCREEN')form.elements.screen_columns.value=String(draft.columns||3);
if(kind==='WORKFLOW'){form.elements.common_screen.value=draft.screen_version_id||'';form.elements.common_screen.addEventListener('change',()=>{const screen=screens.find(v=>v.id===form.elements.common_screen.value);if(screen){const previous=fields();fieldBody.replaceChildren();for(const field of screen.graph.fields)addField(field);for(const field of previous)if(!screen.graph.fields.some(v=>v.key===field.key))addField(field);}for(const row of nodeBody.children)fieldRules(row,serializeNode(row));});form.querySelector('[data-process-preview]').addEventListener('click',draw);draw();}
})();
