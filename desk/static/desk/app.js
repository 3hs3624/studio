'use strict';
document.querySelectorAll('.api-form').forEach(form => {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const inputs = new FormData(form), kind = form.dataset.kind;
    const payload = {}, number = name => Number(inputs.get(name));
    if (form.dataset.version) payload.expected_version = Number(form.dataset.version);
    if (kind === 'create') {
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
    const button = form.querySelector('button[type="submit"], button'), error = form.querySelector('.form-error');
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
      if (kind === 'create') location.assign('/portal/incidents/' + result.id);
      else if (kind === 'request-create') location.assign('/portal/requests/' + result.id);
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
