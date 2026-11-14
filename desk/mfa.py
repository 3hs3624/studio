"""TOTP with encrypted seeds, replay prevention and one-use recovery codes."""
import base64, hashlib, hmac, secrets, struct, time
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password


def cipher():
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(('mfa:'+settings.SECRET_KEY).encode()).digest()))


def new_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip('=')


def encrypt(value):return cipher().encrypt(value.encode()).decode()
def decrypt(value):return cipher().decrypt(value.encode()).decode()


def token(secret,counter):
    raw=hmac.new(base64.b32decode(secret+'='*((8-len(secret)%8)%8)),struct.pack('>Q',counter),hashlib.sha1).digest()
    offset=raw[-1]&15
    return str((struct.unpack('>I',raw[offset:offset+4])[0]&0x7fffffff)%1000000).zfill(6)


def verify(secret,value,last=-1):
    if not isinstance(value,str) or not value.isascii() or not value.isdigit() or len(value)!=6:return None
    now=int(time.time())//30
    if last>=now-1 and last>=0 and hmac.compare_digest(token(secret,last),value):return None
    for counter in (now,now-1,now+1):
        if counter>last and hmac.compare_digest(token(secret,counter),value):return counter
    return None


def verify_state(state,value):
    try:counter=verify(decrypt(state.mfa_secret),value,state.mfa_last_counter)
    except Exception:counter=None
    if counter is not None:
        state.mfa_last_counter=counter;state.save(update_fields=['mfa_last_counter']);return True
    for index,old in enumerate(state.recovery_hashes):
        if check_password(value,old):
            state.recovery_hashes=[v for i,v in enumerate(state.recovery_hashes) if i!=index]
            state.save(update_fields=['recovery_hashes']);return True
    return False


def recovery_codes():
    values=[secrets.token_hex(8) for _ in range(10)]
    return values,[make_password(value) for value in values]
