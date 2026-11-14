import base64,hashlib,ipaddress,json,socket,ssl,http.client
from urllib.parse import urlsplit,urlencode
from cryptography.fernet import Fernet
from django.conf import settings
from ..models import IntegrationNetworkPolicy

LIMIT=1048576
class TransportError(Exception):
    def __init__(self,code,status=None,retryable=False):self.code=code;self.status=status;self.retryable=retryable;super().__init__(code)

def cipher():return Fernet(base64.urlsafe_b64encode(hashlib.sha256(('integration:'+settings.SECRET_KEY).encode()).digest()))
def seal(value):return cipher().encrypt(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()).decode()
def unseal(value):return json.loads(cipher().decrypt(value.encode()).decode())

def address(organization,url,resolve=True):
    try:
        parsed=urlsplit(url)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:raise ValueError()
        if any(c in url for c in '\r\n\x00') or any(c in parsed.netloc for c in '{}'):raise ValueError()
        port=parsed.port or 443
        if not 1<=port<=65535:raise ValueError()
        policy=IntegrationNetworkPolicy.objects.filter(organization=organization).first()
        if not policy or parsed.hostname.lower() not in policy.allowed_hosts:raise TransportError('HOST_NOT_ALLOWED')
        if not resolve:return parsed,None
        addresses=list(dict.fromkeys(item[4][0] for item in socket.getaddrinfo(parsed.hostname,port,type=socket.SOCK_STREAM)))
        if not addresses:raise TransportError('DNS_EMPTY')
        for item in addresses:
            ip=ipaddress.ip_address(item)
            if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_reserved:raise TransportError('ADDRESS_DENIED')
            if not ip.is_global and not any(ip in ipaddress.ip_network(cidr,strict=False) for cidr in policy.allowed_private_cidrs):raise TransportError('PRIVATE_ADDRESS_DENIED')
        return parsed,addresses[0]
    except TransportError:raise
    except (ValueError,OSError,UnicodeError):raise TransportError('INVALID_URL_OR_DNS') from None

class PinnedConnection(http.client.HTTPSConnection):
    def __init__(self,host,ip,port,timeout):super().__init__(host,port=port,timeout=timeout,context=ssl.create_default_context());self.pinned_ip=ip
    def connect(self):
        self.sock=socket.create_connection((self.pinned_ip,self.port),self.timeout)
        self.sock=self._context.wrap_socket(self.sock,server_hostname=self.host)

def request(organization,method,url,headers,body,timeout):
    parsed,ip=address(organization,url)
    connection=PinnedConnection(parsed.hostname,ip,parsed.port or 443,timeout)
    try:
        path=parsed.path or '/'
        if parsed.query:path+='?'+parsed.query
        connection.request(method,path,body=body,headers=headers)
        response=connection.getresponse();payload=response.read(LIMIT+1)
        if len(payload)>LIMIT:raise TransportError('RESPONSE_TOO_LARGE',response.status)
        if 300<=response.status<400:raise TransportError('REDIRECT_DENIED',response.status)
        if not 200<=response.status<300:raise TransportError('HTTP_ERROR',response.status,response.status in (408,425,429,500,502,503,504))
        return response.status,payload,response.getheader('Content-Type','')
    except TransportError:raise
    except (OSError,ssl.SSLError,http.client.HTTPException):raise TransportError('CONNECTION_FAILED',retryable=True) from None
    finally:connection.close()

def authentication(organization,credential,timeout):
    if not credential:return {},{}
    if not credential.active:raise TransportError('CREDENTIAL_INACTIVE')
    secret=unseal(credential.encrypted_secret);kind=credential.auth_type
    if kind=='NONE':return {},{}
    if kind=='BEARER':return {'Authorization':'Bearer '+secret['token']},{}
    if kind=='BASIC':return {'Authorization':'Basic '+base64.b64encode((secret['username']+':'+secret['password']).encode()).decode()},{}
    if kind=='API_KEY':
        return ({secret['name']:secret['value']},{}) if secret.get('location','HEADER')=='HEADER' else ({},{secret['name']:secret['value']})
    if kind=='OAUTH2_CLIENT':
        headers={'Content-Type':'application/x-www-form-urlencoded','Authorization':'Basic '+base64.b64encode((secret['client_id']+':'+secret['client_secret']).encode()).decode()}
        body=urlencode({'grant_type':'client_credentials',**({'scope':secret['scope']} if secret.get('scope') else {})}).encode()
        _,payload,_=request(organization,'POST',secret['token_url'],headers,body,min(timeout,15))
        try:
            token=json.loads(payload)['access_token']
            if not isinstance(token,str) or not token or len(token)>16384:raise ValueError()
        except (ValueError,KeyError,TypeError):raise TransportError('OAUTH_TOKEN_INVALID') from None
        return {'Authorization':'Bearer '+token},{}
    raise TransportError('AUTH_NOT_SUPPORTED')
