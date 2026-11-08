'use strict';
document.querySelectorAll('.api-form').forEach(form => {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const inputs = new FormData(form), kind = form.dataset.kind;
    const payload = {}, number = name => Number(inputs.get(name));
    if (form.dataset.version) payload.expected_version = Number(form.dataset.version);
    if (kind === 'entity-save') {
      Object.assign(payload, {code:inputs.get('code'), name:inputs.get('name'), reason:inputs.get('reason'), fields:[]});
      form.querySelectorAll('[data-entity-field-row]').forEach(row=>{
        const value=key=>row.querySelector('[data-field="'+key+'"]').value;
        const field={key:value('key'),label:value('label'),type:value('type'),required:row.querySelector('[data-field="required"]').checked};
        if(field.type==='choice')field.options=value('options').split(',').map(v=>v.trim()).filter(Boolean);
        if(field.type==='reference')field.target_entity_id=value('target_entity_id');
        payload.fields.push(field);
      });
    } else if (kind === 'entity-publish') {
      payload.reason=inputs.get('reason');
    } else if (kind === 'entity-record') {
      payload.schema_version_id=form.dataset.schema;
      payload.values={};
      form.querySelectorAll('[data-entity-value]').forEach(input=>{
        if(input.value==='')return;
        let value=input.value;
        if(input.dataset.type==='integer')value=Number(value);
        if(input.dataset.type==='boolean')value=value==='true';
        payload.values[input.dataset.key]=value;
      });
    } else if (kind === 'plugin-configure') {
      Object.assign(payload, {enabled:inputs.has('enabled'), reason:inputs.get('reason'),
        manifest_digest:form.dataset.digest,
        configuration:{trim:inputs.has('trim'), collapse_spaces:inputs.has('collapse_spaces')}});
    } else if (kind === 'plugin-preview') {
      Object.assign(payload, {manifest_digest:form.dataset.digest, input:{text:inputs.get('text')}});
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
      payload.roles = inputs.getAll('roles');
    } else if (kind === 'account' || kind === 'revoke-sessions') {
      payload.reason=inputs.get('reason');
      if (kind === 'account') payload.active=inputs.get('active')==='true';
    } else if (kind === 'membership') {
      payload.active = inputs.get('active') === 'on';
    } else if (kind === 'sla-calendar') {
      Object.assign(payload, {name: inputs.get('name'), timezone: inputs.get('timezone'),
        weekdays:inputs.getAll('weekdays').map(Number), starts_at:inputs.get('starts_at'), ends_at:inputs.get('ends_at'),
        holidays:inputs.get('holidays').split(/[\n,]+/).map(s=>s.trim()).filter(Boolean)});
    } else if (kind === 'sla-policy') {
      Object.assign(payload, {name:inputs.get('name'), calendar_id:inputs.get('calendar_id'), priority:number('priority'),
        response_minutes:number('response_minutes'), resolution_minutes:number('resolution_minutes'),
        warning_percent:number('warning_percent'), pause_on_pending:inputs.get('pause_on_pending')==='on'});
    } else if (kind === 'catalog-publish') {
      Object.assign(payload, {code:inputs.get('code'), name:inputs.get('name'), description:inputs.get('description'),
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
    if (form.dataset.payload !== serialized) {
      form.dataset.payload = serialized;
      form.dataset.key = crypto.randomUUID();
    }
    const button = event.submitter || form.querySelector('button[type="submit"], button'), error = form.querySelector('.form-error');
    button.disabled = true;
    error.hidden = true;
    let url = form.dataset.url;
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
      if (kind === 'plugin-preview') {
        const output = form.querySelector('[data-plugin-output]');
        output.textContent = result.output.text;
        output.hidden = false;
        button.disabled = false;
      }
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
    control('target_entity_id').value=field.target_entity_id || '';
    function updateType(){
      row.querySelector('[data-choice-settings]').hidden=control('type').value!=='choice';
      row.querySelector('[data-reference-settings]').hidden=control('type').value!=='reference';
    }
    control('type').addEventListener('change',updateType);
    row.querySelector('[data-remove-field]').addEventListener('click',()=>row.remove());
    updateType();
    entityFields.appendChild(fragment);
  }
  const initial=JSON.parse(document.getElementById('entity-draft-fields').textContent);
  initial.forEach(addEntityField);
  if(!initial.length)addEntityField({key:'title',label:'제목',type:'text',required:true});
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
