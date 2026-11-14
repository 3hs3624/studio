'use strict';
document.querySelectorAll('.api-form').forEach(form => {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const inputs = new FormData(form), kind = form.dataset.kind;
    const payload = {}, number = name => Number(inputs.get(name));
    if (form.dataset.version) payload.expected_version = Number(form.dataset.version);
    let policyPreview=false;
    if(kind?.startsWith('kpi-')){
      if(kind==='kpi-policy'){for(const key of ['name','ticket_type','basis','calendar_id','reason'])payload[key]=inputs.get(key);payload.target_minutes=Number(inputs.get('target_minutes'));}
      if(kind==='kpi-report'){for(const key of ['starts_on','ends_on','cohort'])payload[key]=inputs.get(key);}
      if(kind==='kpi-adjust'){for(const key of ['agreed_start_at','requested_due_at','agreed_due_at','reason'])payload[key]=inputs.get(key);}
    } else if(kind?.startsWith('flow-')) {
      payload.reason=inputs.get('reason')||'';
      if(kind==='flow-save'){
        Object.assign(payload,{kind:inputs.get('kind'),code:inputs.get('code'),name:inputs.get('name'),active:inputs.has('active')});
        try{payload.graph=window.buildProcessGraph();}catch(reason){const box=form.querySelector('.form-error');box.textContent=reason.message;box.hidden=false;return;}
      }
      if(inputs.has('version_id'))payload.version_id=inputs.get('version_id');
      if(inputs.has('task_id'))payload.task_id=inputs.get('task_id');
      if(inputs.has('decision'))payload.decision=inputs.get('decision');
      if(kind==='flow-reassign')payload.person_ids=inputs.getAll('person_ids');
      if(['flow-start','flow-act','flow-resolve_outputs'].includes(kind)){
        payload.values={};form.querySelectorAll('[data-process-input]').forEach(input=>{if(input.value==='')return;payload.values[input.dataset.processInput]=input.dataset.processType==='number'?Number(input.value):input.dataset.processType==='boolean'?input.value==='true':input.value;});
        if(kind==='flow-start')payload.title=inputs.get('title');
      }
    } else if (kind?.startsWith('org-')) {
      payload.reason=inputs.get('reason');
      if(kind==='org-department'){for(const key of ['code','name','description','parent_id'])payload[key]=inputs.get(key);payload.active=inputs.has('active');}
      if(['org-role-targets','org-group-targets'].includes(kind)){for(const key of ['person_ids','department_ids','group_ids'])if(kind==='org-role-targets'||key!=='group_ids')payload[key]=inputs.getAll(key);payload.include_children=inputs.has('include_children');}
      if(kind==='org-menus'){payload.menu_keys=inputs.getAll('menu_keys');payload.console_button=inputs.has('console_button');payload.data_scopes={};form.querySelectorAll('[data-scope-menu]').forEach(input=>{payload.data_scopes[input.dataset.scopeMenu]??={};payload.data_scopes[input.dataset.scopeMenu][input.dataset.scopeAction]=input.value;});}
    } else if (kind === 'security-policy') {
      payload.configuration={};form.querySelectorAll('[data-policy-field]').forEach(input=>{payload.configuration[input.dataset.policyField]=input.dataset.policyType==='boolean'?input.checked:input.dataset.policyType==='integer'?Number(input.value):input.value;});
      payload.reason=inputs.get('reason');payload.apply_confirmed=inputs.has('apply_confirmed');
      policyPreview=!!event.submitter?.hasAttribute('data-policy-preview');
    } else if (['role-save','group-save'].includes(kind)) {
      Object.assign(payload,{code:inputs.get('code'),name:inputs.get('name'),description:inputs.get('description'),active:inputs.has('active'),reason:inputs.get('reason')});
      if(kind==='role-save')payload.permissions=inputs.getAll('permissions');
    } else if (kind === 'role-grant') {
      Object.assign(payload,{person_id:inputs.get('person_id'),active:inputs.has('active'),reason:inputs.get('reason')});
    } else if (kind === 'user-create' || kind === 'user-save') {
      for(const key of ['username','full_name','given_name','family_name','email','phone','employee_id','expires_on','department_id'])if(inputs.has(key))payload[key]=inputs.get(key);
      payload.reason=inputs.get('reason');if(kind==='user-create'){payload.allocation_token=inputs.get('allocation_token');payload.role_keys=inputs.getAll('copy_roles');payload.group_ids=inputs.getAll('copy_groups');payload.invite=inputs.has('invite');if(!payload.invite)payload.password=inputs.get('password');}
    } else if (kind === 'user-reset') {
      Object.assign(payload,{password:inputs.get('password'),reason:inputs.get('reason')});
    } else if(['user-action','manage-delete','user-invite','user-session'].includes(kind)) {
      payload.reason=inputs.get('reason');if(kind==='user-session')payload.session_id=inputs.get('session_id');
    } else if (kind === 'code-group') {
      Object.assign(payload,{code:inputs.get('code'),name:inputs.get('name'),description:inputs.get('description'),active:inputs.has('active'),reason:inputs.get('reason')});
    } else if(kind === 'code-items') {
      payload.reason=inputs.get('reason');
      payload.items=Array.from(form.querySelectorAll('[data-code-item]')).map(row=>{
        const get=key=>row.querySelector('[data-code="'+key+'"]');
        return {code:get('code').value,label:get('label').value,description:get('description').value,sort_order:Number(get('sort_order').value),active:get('active').checked};
      });
    } else if (kind === 'entity-save') {
      Object.assign(payload, {code:inputs.get('code'), name:inputs.get('name'), reason:inputs.get('reason'), fields:[]});
      form.querySelectorAll('[data-entity-field-row]').forEach(row=>{
        const value=key=>row.querySelector('[data-field="'+key+'"]').value;
        const field={key:value('key'),label:value('label'),type:value('type'),required:row.querySelector('[data-field="required"]').checked};
        if(field.type==='choice'){if(value('code_group_id'))field.code_group_id=value('code_group_id');else field.options=value('options').split(',').map(v=>v.trim()).filter(Boolean);}
        if(field.type==='reference'){field.target_entity_id=value('target_entity_id');field.relationship=value('relationship');}
        payload.fields.push(field);
      });
      payload.junction=inputs.has('junction_enabled')?{left_field:inputs.get('junction_left'),right_field:inputs.get('junction_right')}:{};
    } else if (kind === 'entity-publish') {
      payload.reason=inputs.get('reason');
    } else if (kind === 'entity-record') {
      payload.schema_version_id=form.dataset.schema;
      payload.values={};
      form.querySelectorAll('[data-entity-value]').forEach(input=>{
        let value=input.multiple?Array.from(input.selectedOptions).map(option=>option.value).filter(Boolean):input.value;
        if(value==='' || (Array.isArray(value) && !value.length))return;
        if(input.dataset.type==='integer')value=Number(value);
        if(input.dataset.type==='boolean')value=value==='true';
        payload.values[input.dataset.key]=value;
      });
    } else if (kind === 'plugin-configure') {
      const configuration={};
      form.querySelectorAll('[data-plugin-setting]').forEach(input=>{
        configuration[input.dataset.pluginSetting]=input.dataset.settingType==='boolean'?input.checked:input.dataset.settingType==='integer'?Number(input.value):input.value;
      });
      Object.assign(payload,{enabled:inputs.has('enabled'),reason:inputs.get('reason'),manifest_digest:form.dataset.digest,configuration});
    } else if (kind === 'plugin-preview' || kind === 'plugin-issue') {
      const data={};form.querySelectorAll('[data-plugin-input]').forEach(input=>{data[input.dataset.pluginInput]=input.value;});
      Object.assign(payload,{manifest_digest:form.dataset.digest,input:data});
    } else if (kind === 'create') {
      Object.assign(payload, {title: inputs.get('title'), description: inputs.get('description'), impact: number('impact'), urgency: number('urgency')});
    } else if (kind === 'assign') {
      const [group_id, assignee_id] = inputs.get('assignment').split(':');
      Object.assign(payload, {group_id, assignee_id});
    } else if (kind === 'transition') {
      Object.assign(payload, {action: inputs.get('action'), reason: inputs.get('reason'), resolution: inputs.get('resolution')});
    } else if (kind === 'comment') {
      Object.assign(payload, {body: inputs.get('body'), visibility: inputs.get('visibility')});
    } else if (kind === 'roles') {
      payload.roles = inputs.getAll('roles');payload.reason=inputs.get('reason');
    } else if (kind === 'account' || kind === 'revoke-sessions') {
      payload.reason=inputs.get('reason');
      if (kind === 'account') payload.active=inputs.get('active')==='true';
    } else if (kind === 'membership') {
      payload.active = inputs.get('active') === 'on';payload.reason=inputs.get('reason');
    } else if (kind === 'sla-calendar') {
      Object.assign(payload, {name: inputs.get('name'), timezone: inputs.get('timezone'),
        weekdays:inputs.getAll('weekdays').map(Number), starts_at:inputs.get('starts_at'), ends_at:inputs.get('ends_at'),
        holidays:inputs.get('holidays').split(/[\n,]+/).map(s=>s.trim()).filter(Boolean)});
    } else if (kind === 'sla-policy') {
      Object.assign(payload, {name:inputs.get('name'), calendar_id:inputs.get('calendar_id'), priority:number('priority'),
        response_minutes:number('response_minutes'), resolution_minutes:number('resolution_minutes'),
        warning_percent:number('warning_percent'), pause_on_pending:inputs.get('pause_on_pending')==='on'});
    } else if (kind === 'catalog-publish') {
      Object.assign(payload, {workflow_version_id:inputs.get('workflow_version_id')||null,code:inputs.get('code'), name:inputs.get('name'), description:inputs.get('description'),
        fulfillment_group_id:inputs.get('fulfillment_group_id'), approval_required:inputs.get('approval_required')==='on',
        approver_id:inputs.get('approval_required')==='on' ? inputs.get('approver_id') : null,
        public_to_org:inputs.get('public_to_org')==='on', audience_group_ids:inputs.getAll('audience_group_ids'),
        available:inputs.get('available')==='on',expected_version:number('expected_version'), fields:[]});
      form.querySelectorAll('.catalog-field-row').forEach(row=>{
        const value=key=>row.querySelector('[data-field="'+key+'"]').value;
        const field={key:value('key'),label:value('label'),type:value('type'),required:row.querySelector('[data-field="required"]').checked};
        if(field.type==='choice')field.options=value('options').split(',').map(s=>s.trim()).filter(Boolean);
        payload.fields.push(field);
      });
      payload.junction=inputs.has('junction_enabled')?{left_field:inputs.get('junction_left'),right_field:inputs.get('junction_right')}:{};
    } else if (kind === 'request-create') {
      payload.catalog_version_id=form.dataset.catalogVersion;
      payload.values={};
      if(form.dataset.resubmission)payload.resubmission_of=form.dataset.resubmission;
      form.querySelectorAll('[data-answer]').forEach(input=>{
        if(input.value==='')return;
        const type=input.dataset.answerType;
        payload.values[input.dataset.answer]=type==='integer' ? Number(input.value) : type==='boolean' ? input.value==='true' : input.value;
      });
    } else if (kind === 'request-assign') {
      payload.assignee_id=inputs.get('assignee_id');
    } else if (kind === 'request-decision') {
      Object.assign(payload,{decision:inputs.get('decision'),reason:inputs.get('reason')});
    } else if (kind === 'request-action') {
      Object.assign(payload,{action:inputs.get('action'),reason:inputs.get('reason')});
    } else if (kind === 'asset-create' || kind === 'asset-update') {
      Object.assign(payload,{name:inputs.get('name'),manufacturer:inputs.get('manufacturer'),model:inputs.get('model'),
        serial_number:inputs.get('serial_number'),portal_visible:inputs.get('portal_visible')==='on',reason:inputs.get('reason')});
      if(kind==='asset-create')Object.assign(payload,{asset_no:inputs.get('asset_no'),location:inputs.get('location')});
    } else if (kind === 'asset-action') {
      const action=inputs.get('action');
      Object.assign(payload,{action,reason:inputs.get('reason')});
      if(action!=='RETIRE')payload.location=inputs.get('location');
      if(action==='ISSUE')payload.person_id=inputs.get('person_id');
      if(action==='RETURN' && inputs.get('stockroom_id'))payload.stockroom_id=inputs.get('stockroom_id');
      if(['ISSUE','RETURN'].includes(action) && inputs.get('service_request_id')){
        const option=form.querySelector('[name="service_request_id"]').selectedOptions[0];
        payload.service_request_id=option.value;payload.expected_request_version=Number(option.dataset.version);
      }
    } else if (kind === 'request-asset-issue') {
      const option=form.querySelector('[name="asset_id"]').selectedOptions[0];
      form.dataset.url='/api/v1/assets/'+option.value+'/actions';
      Object.assign(payload,{action:'ISSUE',person_id:form.dataset.recipient,location:inputs.get('location'),
        reason:inputs.get('reason'),expected_version:Number(option.dataset.version),
        service_request_id:form.dataset.requestId,expected_request_version:Number(form.dataset.requestVersion)});
    } else if (kind === 'supplier') {
      Object.assign(payload,{code:inputs.get('code'),name:inputs.get('name'),contact:inputs.get('contact')});
    } else if (kind === 'contract') {
      for(const key of ['code','name','supplier_id','starts_on','ends_on','currency','amount','notes'])payload[key]=inputs.get(key);
    } else if (kind === 'stockroom') {
      Object.assign(payload,{code:inputs.get('code'),name:inputs.get('name'),location:inputs.get('location')});
    } else if (kind === 'stock-item') {
      for(const key of ['code','name','tracking','manufacturer','model'])payload[key]=inputs.get(key);
    } else if (kind === 'purchase-request') {
      Object.assign(payload,{item_id:inputs.get('item_id'),quantity:number('quantity'),currency:inputs.get('currency'),
        max_unit_price:inputs.get('max_unit_price'),approver_id:inputs.get('approver_id'),reason:inputs.get('reason')});
      if(inputs.get('source_request_id'))payload.source_request_id=inputs.get('source_request_id');
    } else if (kind === 'purchase-decision') {
      Object.assign(payload,{decision:inputs.get('decision'),reason:inputs.get('reason')});
    } else if (kind === 'purchase-cancel-request') {
      payload.reason=inputs.get('reason');
    } else if (kind === 'purchase-order') {
      Object.assign(payload,{requisition_id:form.dataset.requisition,supplier_id:inputs.get('supplier_id'),
        contract_id:inputs.get('contract_id')||null,unit_price:inputs.get('unit_price')});
    } else if (kind === 'purchase-order-action') {
      Object.assign(payload,{action:inputs.get('action'),reason:inputs.get('reason')});
    } else if (kind === 'purchase-receipt') {
      Object.assign(payload,{stockroom_id:inputs.get('stockroom_id'),reference:inputs.get('reference'),
        quantity:number('quantity'),reason:inputs.get('reason'),serials:[]});
      if(form.dataset.tracking==='SERIALIZED')payload.serials=inputs.get('serials').split(/\n/).filter(line=>line.trim()).map(line=>{
        const parts=line.split(',');return {asset_no:parts[0]?.trim(),serial_number:parts[1]?.trim()};
      });
    } else if (kind === 'stock-transfer' || kind === 'stock-issue') {
      const option=form.querySelector('[name="balance"]').selectedOptions[0];
      Object.assign(payload,{item_id:option.dataset.item,source_id:option.dataset.source,expected_source_version:Number(option.dataset.version),
        quantity:number('quantity'),reason:inputs.get('reason')});
      if(kind==='stock-transfer'){
        const versions=JSON.parse(document.getElementById('stock-balance-versions').textContent);
        payload.target_id=inputs.get('target_id');payload.expected_target_version=versions[option.dataset.item+':'+payload.target_id]||0;
        payload.asset_ids=[];payload.asset_versions={};
        if(option.dataset.tracking==='SERIALIZED')for(const asset of form.querySelector('[name="asset_ids"]').selectedOptions){
          payload.asset_ids.push(asset.value);payload.asset_versions[asset.value]=Number(asset.dataset.version);
        }
      }else{
        Object.assign(payload,{person_id:inputs.get('person_id'),destination:inputs.get('destination')});
        if(inputs.get('service_request_id')){
          const request=form.querySelector('[name="service_request_id"]').selectedOptions[0];
          payload.service_request_id=request.value;payload.expected_request_version=Number(request.dataset.version);
        }
      }
    } else if (kind === 'asset-contract') {
      Object.assign(payload,{asset_id:inputs.get('asset_id'),contract_id:inputs.get('contract_id'),reason:inputs.get('reason')});
    }
    if ((kind === 'attach' || kind === 'create') && inputs.get('resource')) {
      const [resource_type, resource_id] = inputs.get('resource').split(':');
      if (kind === 'create') payload.resources = [{resource_type, resource_id}];
      else Object.assign(payload, {resource_type, resource_id});
    }
    const serialized = JSON.stringify(payload);
    const fingerprint=['user-create','user-save','user-reset'].includes(kind)?Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(serialized)))).map(v=>v.toString(16).padStart(2,'0')).join(''):serialized;
    if (kind === 'plugin-preview' || form.dataset.payload !== fingerprint) {
      form.dataset.payload = fingerprint;
      form.dataset.key = crypto.randomUUID();
    }
    const button = event.submitter || form.querySelector('button[type="submit"], button'), error = form.querySelector('.form-error');
    button.disabled = true;
    error.hidden = true;
    let url = policyPreview?form.dataset.previewUrl:form.dataset.url;
    const method = form.dataset.method || 'POST';
    if (method === 'DELETE') url += '?expected_version=' + payload.expected_version;
    try {
      const response = await fetch(url, {method, credentials:'same-origin',
        headers:{'Content-Type':'application/json', 'X-CSRFToken': inputs.get('csrfmiddlewaretoken'), 'Idempotency-Key':form.dataset.key},
        ...(method !== 'DELETE' ? {body: serialized} : {})});
      const result = response.status === 204 ? {} : await response.json();
      if (!response.ok) {
        let message = result.error?.message || '처리에 실패했습니다.';
        if (result.error?.code === 'VERSION_CONFLICT') message += ' 입력을 복사해 두신 뒤 페이지를 새로고침하십시오.';
        throw new Error(message);
      }
      if(!policyPreview)document.dispatchEvent(new CustomEvent('configuration-saved',{detail:form}));
      if(policyPreview){const output=form.querySelector('[data-policy-output]');output.textContent=result.output.text;output.hidden=false;button.disabled=false;return;}
      if(kind==='user-invite'){const output=form.querySelector('[data-invitation-output]');output.textContent=result.invitation_url;output.hidden=false;button.disabled=false;return;}
      if (kind === 'plugin-preview' || kind === 'plugin-issue') {
        const output = form.querySelector('[data-plugin-output]');
        output.textContent = typeof result.output.text==='string'?result.output.text:JSON.stringify(result.output,null,2);
        if(kind==='plugin-issue')button.textContent='발급 결과 다시 확인';
        output.hidden = false;
        button.disabled = false;
      }
      else if(kind==='kpi-report')location.assign('/console/slm/reports/'+result.id+'/csv');
      else if(kind==='kpi-policy')location.reload();
      else if(kind==='kpi-adjust')location.reload();
      else if(kind?.startsWith('flow-'))location.assign(kind==='flow-start'||!form.dataset.detailBase?'/processes/'+result.id:form.dataset.detailBase+'/'+result.id+(kind==='flow-save'?'':'?tab=versions'));
      else if(kind==='org-department')location.assign('/console/access?tab=departments&selected='+result.id);
      else if(kind==='org-delete')location.assign('/console/access?tab=departments');
      else if (kind === 'manage-delete') location.assign(form.dataset.listUrl);
      else if (kind === 'role-save') location.assign('/console/roles/'+result.id);
      else if (kind === 'group-save') location.assign('/console/groups/'+result.id);
      else if (kind === 'user-create') location.assign('/console/users/'+result.id+'?tab=security');
      else if (kind === 'code-group') location.assign('/console/codes/'+result.id);
      else if (kind === 'entity-save') location.assign((form.dataset.detailBase || '/console/entities') + '/' + result.id);
      else if (kind === 'create') location.assign('/portal/incidents/' + result.id);
      else if (kind === 'request-create') location.assign('/portal/requests/' + result.id);
      else if (kind === 'asset-create') location.assign('/assets/' + result.id);
      else if (kind === 'purchase-request') location.assign('/procurement/requisitions/' + result.id);
      else if (kind === 'purchase-order') location.assign('/procurement/orders/' + result.id);
      else location.reload();
    } catch (err) {
      error.textContent = err.message || '연결을 확인하고 다시 시도하십시오.';
      error.hidden = false;
      error.focus();
      button.disabled = false;
    }
  });
});

const fieldButton=document.getElementById('add-catalog-field');
if(fieldButton){
  let fieldCount=0;
  fieldButton.addEventListener('click',()=>{
    const container=document.getElementById('catalog-fields');
    if(container.children.length>=20)return;
    const fragment=document.getElementById('catalog-field-template').content.cloneNode(true);
    const row=fragment.querySelector('.catalog-field-row');
    row.querySelector('[data-field="key"]').value='field_'+(++fieldCount);
    row.querySelector('.remove-field').addEventListener('click',()=>row.remove());
    container.appendChild(fragment);
    row.querySelector('[data-field="label"]').focus();
  });
  const versions=JSON.parse(document.getElementById('catalog-version-map').textContent);
  const code=document.getElementById('catalog-code');
  code.addEventListener('input',()=>{
    document.querySelector('#catalog-publish-form [name="expected_version"]').value=versions[code.value.trim().toUpperCase()]||0;
  });
}

document.querySelectorAll('.asset-action-form').forEach(form=>{
  const action=form.querySelector('[name="action"]');
  const person=form.querySelector('[name="person_id"]');
  const location=form.querySelector('[name="location"]');
  const request=form.querySelector('[name="service_request_id"]');
  const warehouse=form.querySelector('[name="stockroom_id"]');
  function update(){
    const selected=action.value;
    form.querySelector('[data-asset-recipient]').hidden=selected!=='ISSUE';
    form.querySelector('[data-asset-location]').hidden=!['ISSUE','RETURN','MOVE','VERIFY'].includes(selected);
    form.querySelector('[data-asset-request]').hidden=!['ISSUE','RETURN'].includes(selected);
    person.required=selected==='ISSUE';location.required=['ISSUE','RETURN','MOVE','VERIFY'].includes(selected);
    if(warehouse){form.querySelector('[data-return-warehouse]').hidden=selected!=='RETURN';warehouse.required=selected==='RETURN';}
  }
  action.addEventListener('change',update);
  request.addEventListener('change',()=>{
    const option=request.selectedOptions[0];
    if(action.value==='ISSUE' && option.dataset.person)person.value=option.dataset.person;
  });
  if(warehouse)warehouse.addEventListener('change',()=>{const option=warehouse.selectedOptions[0];if(option.dataset.location)location.value=option.dataset.location;});
  update();
});

document.querySelectorAll('.stock-transfer-form').forEach(form=>{
  const source=form.querySelector('[name="balance"]'),assets=form.querySelector('[name="asset_ids"]');
  source.addEventListener('change',()=>{
    const option=source.selectedOptions[0],serialized=option.dataset.tracking==='SERIALIZED';
    form.querySelector('[data-serial-transfer]').hidden=!serialized;
    for(const asset of assets.options){asset.disabled=!serialized||asset.dataset.item!==option.dataset.item||asset.dataset.source!==option.dataset.source;asset.selected=false;}
  });
});


const entityFields = document.getElementById('entity-fields');
if (entityFields) {
  let nextField = 0;
  function addEntityField(field = {}) {
    if(entityFields.children.length >= 30)return;
    const fragment = document.getElementById('entity-field-template').content.cloneNode(true);
    const row = fragment.querySelector('[data-entity-field-row]');
    const control = key => row.querySelector('[data-field="'+key+'"]');
    let generatedKey;
    do {generatedKey='field_'+(++nextField);}
    while(Array.from(entityFields.querySelectorAll('[data-field="key"]')).some(input=>input.value===generatedKey));
    control('key').value=field.key || generatedKey;
    control('label').value=field.label || '';
    control('type').value=field.type || 'text';
    control('required').checked=field.required === true;
    control('options').value=(field.options || []).join(', ');
    control('code_group_id').value=field.code_group_id || '';
    control('target_entity_id').value=field.target_entity_id || '';
    control('relationship').value=field.relationship || 'many_to_one';
    function updateType(){
      control('code_group_id').disabled=control('type').value!=='choice';
      control('options').disabled=control('type').value!=='choice' || !!control('code_group_id').value;
      row.querySelectorAll('[data-reference-settings]').forEach(input=>{input.disabled=control('type').value!=='reference';});
    }
    control('type').addEventListener('change',updateType);
    control('code_group_id').addEventListener('change',updateType);
    row.querySelector('[data-remove-field]').addEventListener('click',()=>row.remove());
    row.querySelectorAll('[data-move-field]').forEach(button=>button.addEventListener('click',()=>{
      if(button.dataset.moveField==='-1' && row.previousElementSibling)row.previousElementSibling.before(row);
      if(button.dataset.moveField==='1' && row.nextElementSibling)row.nextElementSibling.after(row);
    }));
    updateType();
    entityFields.appendChild(fragment);
  }
  const initial=JSON.parse(document.getElementById('entity-draft-fields').textContent);
  initial.forEach(addEntityField);

  document.getElementById('add-entity-field').addEventListener('click',()=>addEntityField());
}

// Mobile shell navigation is shared by the portal and the operator console.
const shellMenu = document.querySelector('.shell-menu-toggle');
const navigationBackdrop = document.querySelector('.navigation-backdrop');
if (shellMenu && navigationBackdrop) {
  function closeNavigation(restoreFocus = true) {
    document.body.classList.remove('navigation-open');
    shellMenu.setAttribute('aria-expanded', 'false');
    shellMenu.setAttribute('aria-label', '메뉴 열기');
    navigationBackdrop.hidden = true;
    if (restoreFocus) shellMenu.focus();
  }
  shellMenu.addEventListener('click', () => {
    if (document.body.classList.contains('navigation-open')) {closeNavigation(); return;}
    document.body.classList.add('navigation-open');
    shellMenu.setAttribute('aria-expanded', 'true');
    shellMenu.setAttribute('aria-label', '메뉴 닫기');
    navigationBackdrop.hidden = false;
    document.querySelector('#primary-navigation a')?.focus();
  });
  navigationBackdrop.addEventListener('click', () => closeNavigation());
  document.addEventListener('keydown', event => {
    if (!document.body.classList.contains('navigation-open')) return;
    if (event.key === 'Escape') {closeNavigation(); return;}
    if (event.key === 'Tab') {
      const links = Array.from(document.querySelectorAll('#primary-navigation a[href]'))
        .filter(link => link.getClientRects().length > 0);
      const first = links[0], last = links[links.length - 1];
      if (!first) return;
      if (document.activeElement === shellMenu) {
        event.preventDefault(); (event.shiftKey ? last : first).focus();
      } else if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); shellMenu.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); shellMenu.focus();
      }
    }
  });
  document.querySelectorAll('#primary-navigation a').forEach(link => link.addEventListener('click', () => closeNavigation(false)));
  window.matchMedia('(min-width:681px)').addEventListener('change', event => {if(event.matches)closeNavigation(false);});
}


// Full-page tab links preserve their address; warn before discarding edited forms.
const dirtyConfigurationForms=new Set();
document.addEventListener('input',event=>{const form=event.target.closest('form[data-track-changes]');if(form)dirtyConfigurationForms.add(form);});
document.addEventListener('change',event=>{const form=event.target.closest('form[data-track-changes]');if(form)dirtyConfigurationForms.add(form);});
document.addEventListener('configuration-saved',event=>dirtyConfigurationForms.delete(event.detail));
window.addEventListener('beforeunload',event=>{if(dirtyConfigurationForms.size){event.preventDefault();event.returnValue='';}});
document.querySelectorAll('[data-new-plugin-issue]').forEach(button=>button.addEventListener('click',()=>{
  const form=button.closest('form');delete form.dataset.key;delete form.dataset.payload;
  form.querySelector('[data-plugin-output]').hidden=true;
  form.querySelector('button[type=submit]').textContent='실제 발급';
}));
const addCommonCode=document.getElementById('add-common-code');
if(addCommonCode)addCommonCode.addEventListener('click',()=>{
  const rows=document.getElementById('common-code-items');if(rows.children.length>=100)return;
  const fragment=document.getElementById('common-code-template').content.cloneNode(true);
  rows.appendChild(fragment);dirtyConfigurationForms.add(rows.closest('form'));
});

document.addEventListener('click',event=>{const button=event.target.closest('[data-remove-code-row]');if(button){const form=button.closest('form');button.closest('[data-code-item]').remove();dirtyConfigurationForms.add(form);}});

const activationToken=document.getElementById('activation-token');if(activationToken && location.hash){activationToken.value=decodeURIComponent(location.hash.slice(1));history.replaceState(null,'',location.pathname);}


// Native dialogs provide focus containment, Escape dismissal and focus return.
const profileDialog=document.getElementById('self-profile-dialog');
document.querySelectorAll('[data-profile-open]').forEach(button=>button.addEventListener('click',async()=>{
  const content=profileDialog.querySelector('[data-profile-content]');content.textContent='불러오는 중…';profileDialog.showModal();
  try{const response=await fetch('/account/profile',{credentials:'same-origin',headers:{Accept:'application/json'}});if(!response.ok)throw Error('사용자 정보를 불러오지 못했습니다. 다시 로그인하십시오.');const value=await response.json();content.textContent='';const list=document.createElement('dl');for(const [label,text] of [['이름',value.name],['로그인 ID',value.username],['부서',value.department],['이메일',value.email||'—'],['연락처',value.phone||'—'],['적용 역할',value.roles.map(r=>r.name+' ('+r.paths.join(' / ')+')').join(', ')],['소속 그룹',value.groups.map(g=>g.name+' ('+g.paths.join(' / ')+')').join(', ')||'없음']]){const term=document.createElement('dt'),description=document.createElement('dd');term.textContent=label;description.textContent=text;list.append(term,description);}content.append(list);}catch(error){content.textContent=error.message;}
}));
profileDialog?.querySelector('[data-profile-close]').addEventListener('click',()=>profileDialog.close());
profileDialog?.addEventListener('click',event=>{if(event.target===profileDialog){const box=profileDialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)profileDialog.close();}});
document.querySelectorAll('[data-copy-load]').forEach(button=>button.addEventListener('click',async()=>{
 const form=button.closest('form'),kind=button.dataset.copyLoad,id=form.querySelector(kind==='user'?'[data-copy-person]':'[data-copy-department]').value,error=form.querySelector('[data-copy-error]');
 form.querySelector('[name=allocation_token]').value='';for(const selector of ['[data-copy-roles]','[data-copy-groups]'])form.querySelector(selector).textContent='';
 if(!id){error.textContent='복제 원본을 선택하십시오.';return;}
 button.disabled=true;error.textContent='';
 try{const response=await fetch('/api/v1/organization-access/copy?'+new URLSearchParams({kind,id}),{credentials:'same-origin'});const result=await response.json();if(!response.ok)throw Error(result.error?.message||'조회 실패');form.querySelector('[name=allocation_token]').value=result.token;for(const [items,selector,name,key] of [[result.roles,'[data-copy-roles]','copy_roles','key'],[result.groups,'[data-copy-groups]','copy_groups','id']]){const output=form.querySelector(selector);if(!items.length)output.textContent='복제 가능한 항목이 없습니다.';for(const item of items){const label=document.createElement('label'),checkbox=document.createElement('input');label.className='check';checkbox.type='checkbox';checkbox.name=name;checkbox.value=item[key];checkbox.checked=true;label.append(checkbox,document.createTextNode(item.name+' · '+item.paths.join(' / ')));output.append(label);}}}catch(reason){error.textContent=reason.message;}finally{button.disabled=false;}
}));
