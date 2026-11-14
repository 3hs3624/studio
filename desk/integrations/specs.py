"""Bounded OpenAPI JSON import; remote references are never fetched."""
from urllib.parse import urljoin
from .. import services as s

def operations(document):
    if not isinstance(document,dict) or not (str(document.get('openapi','')).startswith('3.') or document.get('swagger')=='2.0'):s.fail('INVALID_SPEC','OpenAPI 3.x 또는 Swagger 2.0 JSON 문서가 필요합니다.')
    def inspect(value,depth=0):
        if depth>30:s.fail('SPEC_LIMIT','명세 중첩 깊이를 초과했습니다.')
        if isinstance(value,dict):
            if '$ref' in value and not str(value['$ref']).startswith('#/'):s.fail('REMOTE_REF_DENIED','외부 참조는 허용하지 않습니다. 참조를 문서에 포함하십시오.')
            for item in value.values():inspect(item,depth+1)
        elif isinstance(value,list):
            for item in value:inspect(item,depth+1)
    inspect(document)
    result=[]
    for path,methods in document.get('paths',{}).items():
        if not isinstance(path,str) or not path.startswith('/') or not isinstance(methods,dict):continue
        for method,value in methods.items():
            if method.upper() not in ('GET','POST','PUT','PATCH','DELETE') or not isinstance(value,dict):continue
            result.append({'path':path,'method':method.upper(),'label':value.get('summary') or value.get('operationId') or method.upper()+' '+path})
    if not result or len(result)>500:s.fail('SPEC_LIMIT','명세에 1~500개 지원 작업이 필요합니다.')
    return result

def draft(document,method,path):
    options=operations(document)
    if not any(o['method']==method and o['path']==path for o in options):s.fail('INVALID_OPERATION','명세의 작업을 선택하십시오.')
    item=document['paths'][path];op=item[method.lower()];servers=op.get('servers',item.get('servers',document.get('servers',[])))
    base=servers[0].get('url','') if servers else 'https://'+document.get('host','')+document.get('basePath','')
    fields=[]
    for param in item.get('parameters',[])+op.get('parameters',[]):
        if '$ref' in param:continue
        if param.get('in') in ('query','path'):
            schema=param.get('schema',param);key=param.get('name','')
            if key and not any(f['key']==key for f in fields):fields.append(dict(key=key,type={'integer':'number','number':'number','boolean':'boolean'}.get(schema.get('type'),'text'),required=bool(param.get('required',False)),description=param.get('description','')[:500]))
    return dict(url=base.rstrip('/')+path,method=method,input_fields=fields,response_mapping={},request_mapping={},timeout=15,retries=0,effect='READ' if method=='GET' else 'WRITE',target_idempotency=False,documentation='OpenAPI에서 가져온 초안입니다. 본문·인증·매핑·호출 범위를 검토 후 게시하십시오.')
