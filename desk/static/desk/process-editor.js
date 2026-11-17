'use strict';
(()=>{
const form=document.getElementById('process-editor');if(!form)return;
const read=id=>JSON.parse(document.getElementById(id).textContent),draft=read('process-draft'),targets=read('process-targets'),screens=read('process-screens'),approvals=read('process-approvals'),workflows=read('process-workflows'),apis=read('process-apis'),kind=form.dataset.processKind;
const fieldTypes=read('process-field-types');
form.addEventListener('invalid',event=>{for(let parent=event.target.parentElement;parent&&parent!==form;parent=parent.parentElement)if(parent.tagName==='DETAILS')parent.open=true;const row=event.target.closest('[data-process-node]');if(row&&kind==='WORKFLOW')chooseNode(row);},true);
const positions={...(draft.positions||{})};let sequence=0,screenLayout=draft.layout||null;
const el=(tag,text)=>{const item=document.createElement(tag);if(text!==undefined)item.textContent=text;return item;};
const input=(value='',type='text')=>{const item=el('input');item.type=type;item.value=value??'';if(type==='text')item.maxLength=2000;return item;};
const select=(options,value,multiple=false)=>{const item=el('select');item.multiple=multiple;if(multiple)item.size=4;for(const option of options){const entry=el('option',option.name??option.label??option.id);entry.value=option.id;entry.selected=multiple?(value||[]).includes(option.id):option.id===value;item.append(entry);}return item;};
const label=(name,item)=>{const box=el('label',name);box.append(item);return box;};
const checkbox=checked=>{const item=input('','checkbox');item.checked=!!checked;return item;};
const setData=(node,name,value)=>{node.dataset[name]=value;return node;};
let activeNode=null;
const fieldBody=form.querySelector('[data-process-fields]'),nodeBody=form.querySelector('[data-process-nodes]');
function fields(){return fieldBody?Array.from(fieldBody.children).map(row=>{const type=row.querySelector('[data-p=type]').value,extra=JSON.parse(row.dataset.fieldMetadata||'{}');if(!['integer','number'].includes(type)){delete extra.minimum;delete extra.maximum;}if(!['text','textarea','email','phone','url'].includes(type))delete extra.max_length;if(type!=='decimal'){delete extra.precision;delete extra.scale;}if(['person','reference','choice','code'].includes(type))delete extra.default;if(!({datetime:'CURRENT_TIMESTAMP',date:'CURRENT_DATE',uuid:'UUID'}[type]===extra.default_function))delete extra.default_function;return {...extra,key:row.querySelector('[data-p=key]').value,label:row.querySelector('[data-p=label]').value,type,required:row.querySelector('[data-p=required]').checked,...(type==='person'&&row.querySelector('[data-p=group_id]').value?{group_id:row.querySelector('[data-p=group_id]').value}:{})};}):[];}
function addField(field={key:'field_'+(++sequence),label:'새 항목',type:'text',required:false}){
 const row=el('tr');row.dataset.fieldMetadata=JSON.stringify(Object.fromEntries(['max_length','precision','scale','minimum','maximum','description','default','default_function'].filter(k=>field[k]!==undefined).map(k=>[k,field[k]])));for(const [key,node] of [['key',input(field.key)],['label',input(field.label)],['type',select(fieldTypes.map(t=>({id:t.key,name:t.label})),field.type)],['required',checkbox(field.required)],['group_id',select([{id:'',name:'전체 조직'},...(targets.GROUP||[])],field.group_id||'')]]){const cell=el('td');cell.append(setData(node,'p',key));row.append(cell);}
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
 for(const group of screen?.graph.layout?.groups||[]){const line=el('div');line.className='field-access-row group-access-row';line.dataset.ruleGroup=group.key;line.append(el('strong','그룹 · '+group.label));control(line,'groupMode','그룹 표시·입력',select([{id:'EDIT',name:'입력 허용 · 필드 규칙 적용'},{id:'READ',name:'그룹 전체 조회 전용'},{id:'HIDDEN',name:'그룹 전체 숨김'}],node.group_modes?.[group.key]||'EDIT'));line.append(el('span','그룹 제한 우선'));control(line,'groupReadRoles','그룹 조회 역할',select(targets.ROLE,node.group_roles?.[group.key]?.read||[],true));control(line,'groupWriteRoles','그룹 입력 역할',select(targets.ROLE,node.group_roles?.[group.key]?.write||[],true));output.append(line);}

 for(const field of fs){const line=el('div');line.className='field-access-row';line.dataset.ruleField=field.key;const title=el('strong',field.label+' · '+field.key);line.append(title);
 const mode=node.field_modes?.[field.key]||((node.field_keys||[]).includes(field.key)?'EDIT':screen&&node.type==='TASK'?'EDIT':'READ');control(line,'fieldMode','표시·입력',select([{id:'HIDDEN',name:'숨김'},{id:'READ',name:'조회 전용'},{id:'EDIT',name:'입력 가능'}],mode));
 control(line,'fieldRequired','이 태스크에서 필수',checkbox((node.required_fields||[]).includes(field.key)));control(line,'fieldReadRoles','조회 역할 · 미선택은 제한 없음',select(targets.ROLE,node.field_roles?.[field.key]?.read||[],true));control(line,'fieldWriteRoles','입력 역할 · 미선택은 제한 없음',select(targets.ROLE,node.field_roles?.[field.key]?.write||[],true));output.append(line);}
}
function chooseNode(row,scroll=false){
 activeNode=row;for(const other of nodeBody.children){other.hidden=other!==row;other.classList.toggle('selected-node',other===row);}refreshNodePicker();
 if(scroll)row.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function refreshNodePicker(){
 const picker=form.querySelector('[data-node-picker]');if(!picker)return;picker.replaceChildren();
 for(const [index,row] of [...nodeBody.children].entries()){
  const name=row.querySelector('[data-p=label]').value||'이름 없는 단계',type=row.querySelector('[data-p=type]');
  const b=el('button');b.type='button';b.className='workflow-node-choice';b.setAttribute('aria-pressed',String(row===activeNode));b.append(el('strong',(index+1)+'. '+name),el('small',type?.selectedOptions[0]?.textContent||'결재'));b.addEventListener('click',()=>chooseNode(row,true));picker.append(b);
 }
}
function refreshConnections(){
 if(kind!=='WORKFLOW')return;
 const options=[{id:'',name:'단계 선택'},...[...nodeBody.children].map(row=>({id:row.querySelector('[data-p=key]').value,name:row.querySelector('[data-p=label]').value+' · '+row.querySelector('[data-p=key]').value}))];
 for(const row of nodeBody.children)for(const key of ['next','reject','true','false','join']){
  const old=row.querySelector('[data-p='+key+']');if(!old)continue;const value=old.value;
  const replacement=select(options.some(o=>o.id===value)?options:[...options,{id:value,name:value+' · 연결 확인 필요'}],value);replacement.dataset.p=key;old.replaceWith(replacement);
 }
}
function showNodeOptions(row){
 if(kind!=='WORKFLOW')return;
 const type=row.querySelector('[data-p=type]').value;
 const allowed={START:['next'],END:[],JOIN:['next'],TASK:['selectorKind','selectorIds','selectorChildren','mode','next','reject','approval_version_id','approval_timing','screen_version_id'],APPROVAL:['version_id','next','reject'],CONDITION:['conditionField','conditionOp','conditionValue','true','false'],PARALLEL:['branches','join'],WAIT:['wait_seconds','next'],SUBPROCESS:['version_id','count','count_field','input_mapping','output_mapping','next'],TRANSFER:['version_id','input_mapping'],API:['api_version_id','input_mapping','output_mapping','next'],ACTION:['action','field','value','next']}[type]||[];
 const grid=row.querySelector(':scope>details>.user-create-grid');
 for(const label of grid.children){const input=label.querySelector('[data-p]');if(input)label.hidden=!allowed.includes(input.dataset.p)||(input.dataset.p==='approval_timing'&&!row.querySelector('[data-p=approval_version_id]').value)||(input.dataset.p==='selectorChildren'&&row.querySelector('[data-p=selectorKind]').value!=='DEPARTMENT')||(['field','value'].includes(input.dataset.p)&&row.querySelector('[data-p=action]').value!=='SET_FIELD');}
 const rules=row.querySelector('[data-field-rules]');if(rules){rules.parentElement.hidden=!['TASK','APPROVAL','WAIT','SUBPROCESS','TRANSFER'].includes(type);}
}
function addNode(node){
 node=node||{key:(kind==='APPROVAL'?'stage_':'node_')+(++sequence),label:kind==='APPROVAL'?'새 결재 단계':'새 업무',type:'TASK',selector:{kind:'USER',ids:[]},mode:'ALL',next:'end'};
 if(!node.key||[...nodeBody.children].some(r=>r.querySelector('[data-p=key]').value===node.key)){do{node.key='node_'+(++sequence);}while([...nodeBody.children].some(r=>r.querySelector('[data-p=key]').value===node.key));}
 const row=el('section');row.className='process-node';row.dataset.processNode='';row.dataset.nodeKey=node.key;const heading=el('div');heading.className='user-create-grid';control(heading,'key','식별자',input(node.key));control(heading,'label','이름',input(node.label));
 if(kind==='WORKFLOW')control(heading,'type','노드 유형',select(['START','TASK','APPROVAL','CONDITION','PARALLEL','JOIN','WAIT','SUBPROCESS','TRANSFER','API','ACTION','END'].map((id,index)=>({id,name:['시작','업무 태스크','독립 결재','조건 분기','병렬 분기','병렬 합류','시간 대기','하위 프로세스 호출','타 프로세스 이관','API 호출','데이터 동작','종료'][index]})),node.type));
 row.append(heading);const details=el('details');details.open=true;details.append(el('summary',kind==='APPROVAL'?'결재 대상 설정':'이 단계 설정'));const grid=el('div');grid.className='user-create-grid';selectorControls(grid,node.selector);control(grid,'mode','복수 담당자 처리',select([{id:'ALL',name:'전원 처리'},{id:'ANY',name:'한 명 처리'}],node.mode||'ALL'));
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
 if(kind==='WORKFLOW'){const refresh=el('button','공통 화면·데이터 항목으로 필드 규칙 갱신');refresh.type='button';refresh.className='secondary';const rules=el('div');rules.dataset.fieldRules='';const permissions=el('details');permissions.className='node-permissions';permissions.append(el('summary','화면 항목·그룹 권한'),refresh,rules);details.append(permissions);refresh.addEventListener('click',()=>{const saved=serializeNode(row);fieldRules(row,saved);});}
 row.append(details);const remove=el('button','단계 삭제');remove.type='button';remove.className='secondary';remove.addEventListener('click',()=>{const next=row.nextElementSibling||row.previousElementSibling;row.remove();if(kind==='WORKFLOW'){refreshConnections();if(next)chooseNode(next);else{activeNode=null;refreshNodePicker();}draw();}form.dispatchEvent(new Event('input',{bubbles:true}));});row.append(remove);nodeBody.append(row);
 if(kind==='WORKFLOW'){
  fieldRules(row,node);showNodeOptions(row);row.hidden=true;refreshConnections();refreshNodePicker();
  row.addEventListener('input',event=>{if(['label','key','type'].includes(event.target.dataset.p))refreshNodePicker();});
  row.addEventListener('change',event=>{
   if(event.target.dataset.p==='key'){
    const old=row.dataset.nodeKey,current=event.target.value;row.dataset.nodeKey=current;
    if(old&&current&&old!==current){for(const other of nodeBody.children){for(const key of ['next','reject','true','false','join']){const select=other.querySelector('[data-p='+key+']');if(select?.value===old){const option=select.selectedOptions[0];if(option)option.value=current;}}const branches=other.querySelector('[data-p=branches]');if(branches)branches.value=branches.value.split(',').map(key=>key.trim()===old?current:key.trim()).filter(Boolean).join(', ');}if(form.elements.start_node.value===old)form.elements.start_node.value=current;if(positions[old]){positions[current]=positions[old];delete positions[old];}}
   }
   showNodeOptions(row);if(['key','label','type'].includes(event.target.dataset.p))refreshConnections();if(event.target.dataset.p==='screen_version_id')fieldRules(row,serializeNode(row));refreshNodePicker();draw();});
 }

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
 if(['TASK','APPROVAL','WAIT','SUBPROCESS','TRANSFER'].includes(type)){node.group_modes={};node.group_roles={};for(const line of row.querySelectorAll('[data-rule-group]')){const key=line.dataset.ruleGroup;node.group_modes[key]=line.querySelector('[data-p=groupMode]').value;node.group_roles[key]={read:Array.from(line.querySelector('[data-p=groupReadRoles]').selectedOptions).map(v=>v.value),write:Array.from(line.querySelector('[data-p=groupWriteRoles]').selectedOptions).map(v=>v.value)};}node.field_modes={};node.field_roles={};node.required_fields=[];node.field_keys=[];for(const line of row.querySelectorAll('[data-rule-field]')){const key=line.dataset.ruleField,mode=line.querySelector('[data-p=fieldMode]').value;node.field_modes[key]=mode;if(mode==='EDIT')node.field_keys.push(key);if(line.querySelector('[data-p=fieldRequired]').checked)node.required_fields.push(key);node.field_roles[key]={read:Array.from(line.querySelector('[data-p=fieldReadRoles]').selectedOptions).map(v=>v.value),write:Array.from(line.querySelector('[data-p=fieldWriteRoles]').selectedOptions).map(v=>v.value)};}}
 return node;
}
window.buildProcessGraph=()=>{
 if(kind==='SCREEN'){const screen={fields:fields(),read_only:Array.from(fieldBody.children).filter(row=>row.querySelector('[data-p=readonly]').checked).map(row=>row.querySelector('[data-p=key]').value),columns:Number(form.elements.screen_columns.value)};if(screenLayout)screen.layout=window.reconcileScreenLayout?window.reconcileScreenLayout(screenLayout,screen.fields,screen.columns):screenLayout;return screen;}
 const nodes=Array.from(nodeBody.children).map(serializeNode);if(kind==='APPROVAL')return {stages:nodes};
 const graph={catalog_only:form.elements.catalog_only.checked,close_on_complete:form.elements.close_on_complete.checked,ticket_assignee_field:form.elements.ticket_assignee_field.value,start:form.elements.start_node.value,fields:fields(),nodes,positions:Object.fromEntries(Object.entries(positions).filter(([key])=>nodes.some(n=>n.key===key)))};if(form.elements.common_screen.value)graph.screen_version_id=form.elements.common_screen.value;return graph;
};
if(kind==='SCREEN')window.screenEditorBridge={read:()=>window.buildProcessGraph(),apply:screen=>{fieldBody.replaceChildren();for(const f of screen.fields)addField(f);form.elements.screen_columns.value=String(screen.columns);screenLayout=screen.layout;for(const row of fieldBody.children)row.querySelector('[data-p=readonly]').checked=screen.read_only.includes(row.querySelector('[data-p=key]').value);form.dispatchEvent(new Event('input',{bubbles:true}));}};
function draw(){try{
 const graph=window.buildProcessGraph(),svg=form.querySelector('[data-process-canvas]');svg.replaceChildren();const ns='http://www.w3.org/2000/svg',make=name=>document.createElementNS(ns,name);const computed=new Map(graph.nodes.map((node,index)=>[node.key,positions[node.key]||{x:40+(index%3)*330,y:40+Math.floor(index/3)*160}]));let height=300,width=1100;
 for(const point of computed.values()){height=Math.max(height,point.y+180);width=Math.max(width,point.x+300);}svg.setAttribute('viewBox','0 0 '+width+' '+height);svg.setAttribute('width',width);svg.setAttribute('height',height);
 for(const node of graph.nodes){const source=computed.get(node.key),edges=['next','true','false','reject'].filter(k=>node[k]).map(k=>[node[k],k]).concat((node.branches||[]).map(key=>[key,'branch']));for(const [key,label_] of edges){const target=computed.get(key);if(!target)continue;const line=make('path');line.setAttribute('d',`M${source.x+120},${source.y+66} C${source.x+120},${source.y+110} ${target.x+120},${target.y-40} ${target.x+120},${target.y}`);line.setAttribute('class','process-edge');svg.append(line);const text=make('text');text.setAttribute('x',source.x+125);text.setAttribute('y',source.y+90);text.textContent=label_;svg.append(text);}}
 for(const node of graph.nodes){const point=computed.get(node.key),g=make('g'),rect=make('rect'),text=make('text'),caption=make('text');g.setAttribute('transform',`translate(${point.x},${point.y})`);g.setAttribute('tabindex','0');g.setAttribute('role','button');g.setAttribute('aria-label',node.label+' 노드 배치');rect.setAttribute('width','240');rect.setAttribute('height','66');rect.setAttribute('class','process-graph-node');text.setAttribute('x','12');text.setAttribute('y','25');text.textContent=node.label;caption.setAttribute('x','12');caption.setAttribute('y','49');caption.textContent=node.key+' · '+node.type;g.append(rect,text,caption);svg.append(g);let drag=null;
 g.addEventListener('pointerdown',event=>{drag={x:event.clientX,y:event.clientY,point:{...computed.get(node.key)}};g.setPointerCapture(event.pointerId);});g.addEventListener('pointermove',event=>{if(!drag)return;const scale=svg.viewBox.baseVal.width/svg.getBoundingClientRect().width;const location={x:Math.max(0,Math.min(4000,Math.round(drag.point.x+(event.clientX-drag.x)*scale))),y:Math.max(0,Math.min(4000,Math.round(drag.point.y+(event.clientY-drag.y)*scale)))};positions[node.key]=location;g.setAttribute('transform',`translate(${location.x},${location.y})`);});g.addEventListener('click',()=>{const row=[...nodeBody.children].find(r=>r.querySelector('[data-p=key]').value===node.key);if(row)chooseNode(row,true);});g.addEventListener('pointerup',event=>{const moved=drag&&(Math.abs(event.clientX-drag.x)>3||Math.abs(event.clientY-drag.y)>3);drag=null;if(moved){form.dispatchEvent(new Event('input',{bubbles:true}));draw();}else{const row=[...nodeBody.children].find(r=>r.querySelector('[data-p=key]').value===node.key);if(row)chooseNode(row,true);}});g.addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();const row=[...nodeBody.children].find(r=>r.querySelector('[data-p=key]').value===node.key);if(row)chooseNode(row,true);return;}const offset={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-20],ArrowDown:[0,20]}[event.key];if(offset){event.preventDefault();positions[node.key]={x:Math.max(0,Math.min(4000,point.x+offset[0])),y:Math.max(0,Math.min(4000,point.y+offset[1]))};draw();}});
 }
 }catch(reason){const box=form.querySelector('.form-error');box.textContent=reason.message;box.hidden=false;}}
if(fieldBody){for(const field of Array.isArray(draft.fields)?draft.fields:[])addField(field);form.querySelector('[data-process-add-field]').addEventListener('click',()=>{addField();const details=fieldBody.closest('details');if(details)details.open=true;fieldBody.lastElementChild.querySelector('input').focus();form.dispatchEvent(new Event('input',{bubbles:true}));});}
if(nodeBody){for(const node of (kind==='APPROVAL'?(Array.isArray(draft.stages)?draft.stages:[]):(Array.isArray(draft.nodes)?draft.nodes:[])))addNode(node);form.querySelector('[data-process-add-node]').addEventListener('click',()=>{addNode();if(kind==='WORKFLOW'){chooseNode(nodeBody.lastElementChild,true);draw();}form.dispatchEvent(new Event('input',{bubbles:true}));});}
if(kind==='SCREEN')form.elements.screen_columns.value=String(draft.columns||3);
if(kind==='WORKFLOW'){const host=form.querySelector('[data-flow-canvas-host]'),map=form.querySelector('[data-flow-map]');if(host&&map)host.append(map);const initial=[...nodeBody.children].find(r=>r.querySelector('[data-p=type]').value==='TASK')||nodeBody.firstElementChild;if(initial)chooseNode(initial);form.elements.common_screen.value=draft.screen_version_id||'';form.elements.common_screen.addEventListener('change',()=>{const screen=screens.find(v=>v.id===form.elements.common_screen.value);if(screen){const previous=fields();fieldBody.replaceChildren();for(const field of screen.graph.fields)addField(field);for(const field of previous)if(!screen.graph.fields.some(v=>v.key===field.key))addField(field);}for(const row of nodeBody.children)fieldRules(row,serializeNode(row));});form.querySelector('[data-process-preview]').addEventListener('click',draw);draw();}
})();
