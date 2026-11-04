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
      else location.reload();
    } catch (err) {
      error.textContent = err.message || '연결을 확인하고 다시 시도하십시오.';
      error.hidden = false;
      error.focus();
      button.disabled = false;
    }
  });
});
