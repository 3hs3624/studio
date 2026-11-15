'use strict';
(()=>{
const bridge=window.screenEditorBridge,dialog=document.getElementById('screen-designer');if(!bridge||!dialog)return;
const property=document.getElementById('screen-field-properties'),form=property.querySelector('form'),canvas=dialog.querySelector('[data-designer-canvas]'),query=s=>dialog.querySelector(s),clone=v=>JSON.parse(JSON.stringify(v));
const fieldTypes=JSON.parse(document.getElementById('process-field-types').textContent);
let state,selected='',groupKey='',dragKey='',dragType='',undo=[],redo=[],sequence=0,propertyKey='';
const element=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
const button=(text,action)=>{const b=element('button',text);b.type='button';b.className='secondary';b.addEventListener('click',action);return b;};
window.reconcileScreenLayout=(layout,fields,columns)=>{
 const result=clone(layout),seen=new Set(),keys=new Set(fields.map(f=>f.key));result.groups=result.groups?.length?result.groups:[{key:'basic',label:'기본정보',fields:[]}];
 for(const g of result.groups)g.fields=(g.fields||[]).filter(i=>keys.has(i.key)&&!seen.has(i.key)&&seen.add(i.key)).map(i=>({...i,span:Math.max(1,Math.min(columns,Number(i.span)||1)),height:Math.max(1,Math.min(5,Number(i.height)||1))}));
 for(const f of fields)if(!seen.has(f.key))result.groups[0].fields.push({key:f.key,span:1,height:1});return result;
};
const group=()=>state.layout.groups.find(g=>g.key===groupKey)||state.layout.groups[0];
const locate=key=>{for(const g of state.layout.groups){const item=g.fields.find(i=>i.key===key);if(item)return {group:g,item};}return null;};
const error=message=>{const box=query('[data-designer-error]');box.textContent=message;box.hidden=!message;};
function change(action){undo.push(clone(state));if(undo.length>50)undo.shift();redo=[];action();error('');render();}
function chooseGroup(key){groupKey=key;selected='';render();}
function select(key){selected=key;const found=locate(key);if(found)groupKey=found.group.key;render();canvas.querySelector('[data-designer-field="'+CSS.escape(key)+'"]')?.focus({preventScroll:true});}
function move(key,target,before=''){
 const found=locate(key);if(!found||key===before)return;const destination=state.layout.groups.find(g=>g.key===target);if(!destination)return;
 change(()=>{found.group.fields=found.group.fields.filter(i=>i.key!==key);let index=destination.fields.findIndex(i=>i.key===before);if(index<0)index=destination.fields.length;destination.fields.splice(index,0,found.item);groupKey=target;selected=key;});
}
function addField(type,target=groupKey,before=''){
 if(!fieldTypes.some(f=>f.key===type))return;
 if(state.fields.length>=30){error('화면 항목은 최대 30개입니다.');return;}
 const destination=state.layout.groups.find(g=>g.key===target);if(!destination)return;
 change(()=>{let key;do{key='field_'+(++sequence);}while(state.fields.some(f=>f.key===key));
  state.fields.push({key,label:'새 항목 '+sequence,type,required:false});
  const index=destination.fields.findIndex(f=>f.key===before);destination.fields.splice(index<0?destination.fields.length:index,0,{key,span:1,height:1});selected=key;groupKey=target;
 });
}
function drop(event,target,before=''){
 event.preventDefault();event.stopPropagation();
 if(dragType)addField(dragType,target,before);else if(dragKey)move(dragKey,target,before);
 dragType='';dragKey='';
}
function acceptDrop(node,target){
 node.addEventListener('dragover',event=>{if(!dragType&&!dragKey)return;event.preventDefault();event.stopPropagation();event.dataTransfer.dropEffect=dragType?'copy':'move';node.classList.add('designer-drop-target');});
 node.addEventListener('dragleave',event=>{if(!node.contains(event.relatedTarget))node.classList.remove('designer-drop-target');});
 node.addEventListener('drop',event=>{node.classList.remove('designer-drop-target');drop(event,target,event.target.closest('[data-designer-field]')?.dataset.designerField||'');});
}
function reorder(offset){const found=locate(selected);if(!found)return;const items=found.group.fields,index=items.indexOf(found.item),next=index+offset;if(next<0||next>=items.length)return;change(()=>{items.splice(index,1);items.splice(next,0,found.item);});canvas.querySelector('[data-designer-field="'+CSS.escape(selected)+'"]')?.focus({preventScroll:true});}
function render(){
 state.layout=window.reconcileScreenLayout(state.layout,state.fields,state.columns);if(!state.layout.groups.some(g=>g.key===groupKey))groupKey=state.layout.groups[0].key;
 query('[data-designer-mode]').value=state.layout.mode;query('[data-designer-columns]').value=String(state.columns);query('[data-designer-undo]').disabled=!undo.length;query('[data-designer-redo]').disabled=!redo.length;
 query('[data-designer-group-name]').value=group().label;query('[data-designer-selection]').textContent=state.fields.find(f=>f.key===selected)?.label||'필드를 선택하십시오.';
 const quick=query('[data-designer-quick]'),current=state.fields.find(f=>f.key===selected),location=locate(selected);quick.disabled=!current;for(const input of quick.querySelectorAll('[data-quick]')){const key=input.dataset.quick;if(input.type==='checkbox')input.checked=key==='readonly'?state.read_only.includes(selected):!!current?.required;else input.value=key==='label'?(current?.label||''):(location?.item[key]||1);}quick.querySelector('[data-quick=span]').max=state.columns;
 query('[data-designer-status]').textContent=state.fields.length+'개 필드 · '+state.layout.groups.length+'개 그룹'+(undo.length?' · 저장하지 않은 편집 내용이 있습니다.':'');
 for(const name of ['properties','up','down','delete','duplicate'])query('[data-designer-'+name+']').disabled=!locate(selected);
 const list=query('[data-designer-group-list]');list.replaceChildren();for(const g of state.layout.groups){const b=button(g.label+' ('+g.fields.length+')',()=>chooseGroup(g.key));b.classList.add('designer-group-choice');b.setAttribute('aria-pressed',String(g.key===groupKey));list.append(b);}
 canvas.replaceChildren();canvas.style.setProperty('--designer-columns',state.columns);
 if(state.layout.mode==='tabs'){const tabs=element('div');tabs.className='designer-tabs';for(const g of state.layout.groups){const b=button(g.label,()=>chooseGroup(g.key));b.setAttribute('aria-pressed',String(g.key===groupKey));acceptDrop(b,g.key);tabs.append(b);}canvas.append(tabs);}
 for(const g of state.layout.groups){const section=element('section');section.className='designer-group';section.dataset.designerGroup=g.key;section.hidden=state.layout.mode==='tabs'&&g.key!==groupKey;acceptDrop(section,g.key);section.addEventListener('click',event=>{if(!event.target.closest('[data-designer-field],button,input,select,textarea'))chooseGroup(g.key);});
  const heading=button(g.label,()=>chooseGroup(g.key));heading.classList.add('designer-group-heading');heading.setAttribute('aria-pressed',String(g.key===groupKey));section.append(heading);
  const grid=element('div');grid.className='designer-field-grid';grid.dataset.dropGroup=g.key;acceptDrop(grid,g.key);
  if(!g.fields.length){const hint=element('p');hint.textContent='필드를 추가하거나 이곳으로 끌어 놓으십시오.';hint.className='designer-empty';grid.append(hint);}
  for(const item of g.fields){const f=state.fields.find(f=>f.key===item.key),card=element('div');card.className='designer-field';card.dataset.designerField=f.key;card.draggable=true;card.tabIndex=0;card.setAttribute('aria-label',f.label+' · 필드 이동 및 크기 조정');card.style.setProperty('--field-span',item.span);card.style.setProperty('--field-height',item.height*48+'px');if(selected===f.key)card.classList.add('selected');
   card.append(element('strong',f.label+(f.required?' *':'')));const sample=element('div',(fieldTypes.find(t=>t.key===f.type)?.label||f.type)+' 입력');sample.className='designer-sample';card.append(sample);card.append(element('small',f.key+' · '+item.span+'열 · '+item.height*48+'px'+(state.read_only.includes(f.key)?' · 조회 전용':'')));
   card.addEventListener('click',()=>select(f.key));card.addEventListener('dblclick',()=>{selected=f.key;groupKey=g.key;openProperties();});card.addEventListener('contextmenu',e=>{e.preventDefault();selected=f.key;groupKey=g.key;openProperties();});card.addEventListener('dragstart',e=>{dragType='';dragKey=f.key;e.dataTransfer.setData('text/plain',f.key);e.dataTransfer.effectAllowed='move';});card.addEventListener('dragend',()=>dragKey='');
   card.addEventListener('keydown',e=>{if(e.key==='ContextMenu'||e.shiftKey&&e.key==='F10'){e.preventDefault();selected=f.key;openProperties();}else if(e.ctrlKey&&['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();selected=f.key;reorder(['ArrowUp','ArrowLeft'].includes(e.key)?-1:1);}else if(e.shiftKey&&e.key.startsWith('Arrow')){e.preventDefault();change(()=>{if(e.key==='ArrowLeft')item.span=Math.max(1,item.span-1);if(e.key==='ArrowRight')item.span=Math.min(state.columns,item.span+1);if(e.key==='ArrowUp')item.height=Math.max(1,item.height-1);if(e.key==='ArrowDown')item.height=Math.min(5,item.height+1);});}});
   const resize=button('↘',()=>{});resize.className='designer-resize';resize.setAttribute('aria-label',f.label+' 크기 조정');resize.draggable=false;resize.addEventListener('click',e=>e.stopPropagation());resize.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();selected=f.key;const old=clone(state),start={x:e.clientX,y:e.clientY,span:item.span,height:item.height},step=(grid.getBoundingClientRect().width+16)/state.columns;resize.setPointerCapture(e.pointerId);
    const update=ev=>{item.span=Math.max(1,Math.min(state.columns,start.span+Math.round((ev.clientX-start.x)/step)));item.height=Math.max(1,Math.min(5,start.height+Math.round((ev.clientY-start.y)/48)));card.style.setProperty('--field-span',item.span);card.style.setProperty('--field-height',item.height*48+'px');};
    const finish=()=>{resize.removeEventListener('pointermove',update);resize.removeEventListener('pointerup',finish);resize.removeEventListener('pointercancel',cancel);if(JSON.stringify(old)!==JSON.stringify(state)){undo.push(old);redo=[];}render();};const cancel=()=>{state=old;finish();};resize.addEventListener('pointermove',update);resize.addEventListener('pointerup',finish);resize.addEventListener('pointercancel',cancel);
   });card.append(resize);grid.append(card);
  }section.append(grid);canvas.append(section);
 }
}
function openProperties(){
 const f=state.fields.find(f=>f.key===selected),found=locate(selected);if(!f||!found)return;propertyKey=f.key;
 for(const k of ['key','label','type','max_length','precision','scale','description'])form.elements[k].value=f[k]??'';form.elements.default.value=f.default===undefined?'':JSON.stringify(f.default);form.elements.default_function.value=f.default_function||'';form.elements.required.checked=f.required;form.elements.readonly.checked=state.read_only.includes(f.key);form.elements.span.value=found.item.span;form.elements.span.max=state.columns;form.elements.height.value=found.item.height;
 const options=(select,rows,value)=>{select.replaceChildren();for(const r of rows){const option=element('option',r.label||r.name);option.value=r.key||r.id||'';select.append(option);}select.value=value;};
 options(form.elements.group,state.layout.groups,found.group.key);options(form.elements.group_id,[{id:'',name:'전체 조직'},...JSON.parse(document.getElementById('process-targets').textContent).GROUP],f.group_id||'');property.querySelector('[data-property-error]').hidden=true;property.showModal();
}
form.addEventListener('submit',e=>{e.preventDefault();const key=form.elements.key.value.trim(),label=form.elements.label.value.trim(),span=Number(form.elements.span.value),height=Number(form.elements.height.value);let message='';if(!/^[a-z][a-z0-9_]{0,39}$/.test(key)||state.fields.some(f=>f.key===key&&f.key!==propertyKey))message='식별자는 영문 소문자로 시작하고 중복 없이 입력하십시오.';if(!label)message='표시 이름을 입력하십시오.';if(!Number.isInteger(span)||span<1||span>state.columns||!Number.isInteger(height)||height<1||height>5)message='너비·높이 범위를 확인하십시오.';let defaultValue;try{if(form.elements.default.value!=='')defaultValue=JSON.parse(form.elements.default.value);}catch(error){message='기본값은 JSON 표기로 입력하십시오.';}if(form.elements.default.value!==''&&form.elements.default_function.value)message='기본값과 자동 기본값 중 하나만 선택하십시오.';const fieldType=form.elements.type.value;for(const name of ['max_length','precision','scale']){const input=form.elements[name];if(input.value&&!input.checkValidity())message='길이·정밀도 범위를 확인하십시오.';}if(fieldType==='decimal'&&Number(form.elements.scale.value||2)>Number(form.elements.precision.value||18))message='소수 자릿수는 전체 자릿수 이하여야 합니다.';if(message){const box=property.querySelector('[data-property-error]');box.textContent=message;box.hidden=false;return;}
 change(()=>{const f=state.fields.find(f=>f.key===propertyKey),found=locate(propertyKey);f.key=key;f.label=label;f.type=form.elements.type.value;f.required=form.elements.required.checked;delete f.default;delete f.default_function;if(defaultValue!==undefined)f.default=defaultValue;if(form.elements.default_function.value)f.default_function=form.elements.default_function.value;for(const name of ['max_length','precision','scale','description'])delete f[name];if(['text','textarea','email','phone','url'].includes(f.type)&&form.elements.max_length.value)f.max_length=Number(form.elements.max_length.value);if(f.type==='decimal')for(const name of ['precision','scale'])if(form.elements[name].value!=='')f[name]=Number(form.elements[name].value);if(form.elements.description.value)f.description=form.elements.description.value;delete f.group_id;if(f.type==='person'&&form.elements.group_id.value)f.group_id=form.elements.group_id.value;const index=found.group.fields.indexOf(found.item),destination=state.layout.groups.find(g=>g.key===form.elements.group.value);found.group.fields=found.group.fields.filter(i=>i.key!==propertyKey);destination.fields.splice(destination===found.group?index:destination.fields.length,0,{key,span,height});state.read_only=state.read_only.filter(k=>k!==propertyKey);if(form.elements.readonly.checked)state.read_only.push(key);selected=key;groupKey=form.elements.group.value;});property.close();});
property.querySelector('[data-property-cancel]').addEventListener('click',()=>property.close());
query('[data-designer-properties]').addEventListener('click',openProperties);
for(const b of dialog.querySelectorAll('[data-designer-add]')){
 let dragEndedAt=0;b.draggable=true;b.title+=' · 클릭하거나 그룹으로 끌어 놓기';
 b.addEventListener('click',()=>{if(Date.now()-dragEndedAt>200)addField(b.dataset.designerAdd);});
 b.addEventListener('dragstart',event=>{dragKey='';dragType=b.dataset.designerAdd;event.dataTransfer.setData('text/plain',dragType);event.dataTransfer.effectAllowed='copy';});
 b.addEventListener('dragend',()=>{dragEndedAt=Date.now();dragType='';dragKey='';dialog.querySelectorAll('.designer-drop-target').forEach(node=>node.classList.remove('designer-drop-target'));});
}

query('[data-designer-add-group]').addEventListener('click',()=>{if(state.layout.groups.length>=20){error('그룹은 최대 20개입니다.');return;}change(()=>{let key;do{key='group_'+(++sequence);}while(state.layout.groups.some(g=>g.key===key));state.layout.groups.push({key,label:'새 그룹 '+sequence,fields:[]});groupKey=key;});});
query('[data-designer-group-name]').addEventListener('change',e=>{const name=e.target.value.trim();if(!name){error('그룹 이름을 입력하십시오.');return;}change(()=>group().label=name);});
query('[data-designer-remove-group]').addEventListener('click',()=>{if(state.layout.groups.length===1){error('그룹은 하나 이상 필요합니다.');return;}change(()=>{const old=group(),destination=state.layout.groups.find(g=>g.key!==old.key);destination.fields.push(...old.fields);state.layout.groups=state.layout.groups.filter(g=>g.key!==old.key);groupKey=destination.key;});});
query('[data-designer-search]').addEventListener('input',event=>{const term=event.target.value.trim().toLowerCase();for(const b of dialog.querySelectorAll('[data-designer-add]'))b.hidden=!b.textContent.toLowerCase().includes(term);});
for(const input of query('[data-designer-quick]').querySelectorAll('[data-quick]'))input.addEventListener('change',()=>{
 const field=state.fields.find(f=>f.key===selected),found=locate(selected);if(!field||!found)return;
 const key=input.dataset.quick;if(key==='label'&&!input.value.trim()){input.value=field.label;return;}
 if(['span','height'].includes(key)&&!input.checkValidity()){input.reportValidity();input.value=found.item[key];return;}
 change(()=>{if(key==='label')field.label=input.value.trim();else if(key==='required')field.required=input.checked;else if(key==='readonly'){state.read_only=state.read_only.filter(k=>k!==selected);if(input.checked)state.read_only.push(selected);}else found.item[key]=Number(input.value);});
});
query('[data-designer-duplicate]').addEventListener('click',()=>{
 const original=state.fields.find(f=>f.key===selected),found=locate(selected);if(!original||!found)return;if(state.fields.length>=30){error('화면 항목은 최대 30개입니다.');return;}
 change(()=>{let key;do{key='field_'+(++sequence);}while(state.fields.some(f=>f.key===key));state.fields.push({...clone(original),key,label:original.label+' 복사본'});found.group.fields.splice(found.group.fields.indexOf(found.item)+1,0,{...found.item,key});if(state.read_only.includes(selected))state.read_only.push(key);selected=key;});
});
query('[data-designer-save]').addEventListener('click',()=>{
 const editor=document.getElementById('process-editor'),reason=query('[data-designer-reason]');if(!editor){error('원본 화면 관리에서 저장하십시오.');return;}
 if(!reason.value.trim()){error('저장 사유를 입력하십시오.');reason.focus();return;}
 bridge.apply(clone(state));editor.elements.reason.value=reason.value.trim();dialog.close();editor.requestSubmit();
});
query('[data-designer-delete]').addEventListener('click',()=>{if(!selected)return;change(()=>{for(const g of state.layout.groups)g.fields=g.fields.filter(i=>i.key!==selected);state.fields=state.fields.filter(f=>f.key!==selected);state.read_only=state.read_only.filter(k=>k!==selected);selected='';});});
query('[data-designer-up]').addEventListener('click',()=>reorder(-1));query('[data-designer-down]').addEventListener('click',()=>reorder(1));
query('[data-designer-mode]').addEventListener('change',e=>change(()=>state.layout.mode=e.target.value));query('[data-designer-columns]').addEventListener('change',e=>change(()=>state.columns=Number(e.target.value)));
const preview=document.getElementById('screen-designer-preview'),previewContent=preview.querySelector('[data-preview-content]');
function openPreview(){
 previewContent.replaceChildren();previewContent.classList.remove('preview-mobile');
 preview.querySelector('[data-preview-desktop]').setAttribute('aria-pressed','true');preview.querySelector('[data-preview-mobile]').setAttribute('aria-pressed','false');
 const groups=state.layout.groups.filter(g=>g.fields.length),panels=[],tabs=[];
 const activate=(index,focus=false)=>{for(let i=0;i<panels.length;i++){panels[i].hidden=i!==index;tabs[i].setAttribute('aria-selected',String(i===index));tabs[i].tabIndex=i===index?0:-1;}if(focus)tabs[index].focus();};
 const tablist=element('div');tablist.className='screen-group-tabs';tablist.setAttribute('role','tablist');tablist.setAttribute('aria-label','미리보기 그룹');
 if(state.layout.mode==='tabs')previewContent.append(tablist);
 for(const [index,g] of groups.entries()){
  const section=element('fieldset');section.className='screen-field-group';section.id='preview-group-'+g.key;section.append(element('legend',g.label));
  if(state.layout.mode==='tabs'){
   const tab=button(g.label,()=>activate(index));tab.id='preview-tab-'+g.key;tab.setAttribute('role','tab');tab.setAttribute('aria-controls',section.id);section.setAttribute('role','tabpanel');section.setAttribute('aria-labelledby',tab.id);
   tab.addEventListener('keydown',event=>{const offset=event.key==='ArrowRight'?1:event.key==='ArrowLeft'?-1:0;let next;if(offset)next=(index+offset+groups.length)%groups.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=groups.length-1;else return;event.preventDefault();activate(next,true);});tabs.push(tab);tablist.append(tab);
  }
  const grid=element('div');grid.className='process-form-grid columns-'+state.columns;
  for(const item of g.fields){
   const field=state.fields.find(f=>f.key===item.key);if(!field)continue;
   const label=element('label',field.label+(field.required?' *':''));label.className='screen-field screen-span-'+item.span+' screen-height-'+item.height;
   const value=field.default??'';let control;
   if(state.read_only.includes(field.key)){
    control=element('span',field.type==='boolean'&&typeof value==='boolean'?(value?'예':'아니오'):typeof value==='object'?JSON.stringify(value,null,2):String(value===''?'—':value));control.className='process-readonly';
   }else if(['boolean','person'].includes(field.type)){
    control=element('select');const options=field.type==='boolean'?[['','선택'],['true','예'],['false','아니오']]:[['','사용자 선택']];for(const [key,text] of options){const option=element('option',text);option.value=key;control.append(option);}control.value=value===''?'':String(value);
   }else if(['textarea','json','entityset'].includes(field.type)){
    control=element('textarea');control.value=typeof value==='object'?JSON.stringify(value,null,2):String(value);control.maxLength=field.max_length||(['json','entityset'].includes(field.type)?65535:16384);
   }else{
    control=element('input');control.type=['number','integer'].includes(field.type)?'number':['date','time','month','email','url'].includes(field.type)?field.type:'text';control.value=String(value);control.maxLength=field.max_length||2000;
    if(control.type==='number')control.step=field.type==='integer'?'1':'any';if(field.type==='decimal')control.inputMode='decimal';
   }
   if(control.matches('input,select,textarea')){control.required=!!field.required;control.dataset.previewField=field.key;if(field.default_function)control.placeholder='등록 시 자동으로 설정됩니다.';}
   label.append(control);if(field.description)label.append(element('small',field.description));grid.append(label);
  }
  section.append(grid);panels.push(section);previewContent.append(section);
 }
 if(!groups.length)previewContent.append(element('p','필드를 추가하면 화면을 미리 볼 수 있습니다.'));
 if(tabs.length)activate(0);preview.showModal();
}
query('[data-designer-preview]').addEventListener('click',openPreview);
preview.querySelector('[data-preview-close]').addEventListener('click',()=>preview.close());
for(const mobile of [false,true])preview.querySelector(mobile?'[data-preview-mobile]':'[data-preview-desktop]').addEventListener('click',()=>{previewContent.classList.toggle('preview-mobile',mobile);preview.querySelector('[data-preview-mobile]').setAttribute('aria-pressed',String(mobile));preview.querySelector('[data-preview-desktop]').setAttribute('aria-pressed',String(!mobile));});

query('[data-designer-undo]').addEventListener('click',()=>{if(undo.length){redo.push(clone(state));state=undo.pop();render();}});query('[data-designer-redo]').addEventListener('click',()=>{if(redo.length){undo.push(clone(state));state=redo.pop();render();}});
query('[data-designer-cancel]').addEventListener('click',()=>dialog.close());query('[data-designer-apply]').addEventListener('click',()=>{bridge.apply(clone(state));const note=document.querySelector('[data-designer-applied]');note.textContent='디자이너 배치를 반영했습니다. 초안 저장·검증으로 저장하십시오.';note.hidden=false;dialog.close();});
document.querySelector('[data-screen-designer-open]').addEventListener('click',()=>{state=clone(bridge.read());if(state.fields.some((f,i)=>!/^[a-z][a-z0-9_]{0,39}$/.test(f.key)||state.fields.findIndex(x=>x.key===f.key)!==i)){const box=document.querySelector('#process-editor .form-error');box.textContent='화면 항목 식별자의 형식과 중복을 먼저 확인하십시오.';box.hidden=false;return;}state.layout=window.reconcileScreenLayout(state.layout||{mode:'sections',groups:[{key:'basic',label:'기본정보',fields:[]},{key:'details',label:'상세정보',fields:[]}]},state.fields,state.columns);selected='';groupKey=state.layout.groups[0].key;query('[data-designer-reason]').value=document.querySelector('#process-editor [name=reason]')?.value||'';query('[data-designer-search]').value='';for(const b of dialog.querySelectorAll('[data-designer-add]'))b.hidden=false;undo=[];redo=[];canvas.classList.remove('mobile-preview');error('');render();dialog.showModal();});
})();
