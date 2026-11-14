"""A request-local graph snapshot; reset again after taking the write lock."""
from contextvars import ContextVar
from functools import wraps
CACHE=ContextVar('organization_access_cache',default=None)

def clear():
    cache=CACHE.get()
    if cache is not None:cache.clear()

def cached(name):
    def decorate(function):
        @wraps(function)
        def wrapped(*args):
            cache=CACHE.get()
            if cache is None:return function(*args)
            key=(name,tuple((type(arg).__name__,str(getattr(arg,'id',arg)),str(getattr(arg,'department_id',''))) for arg in args))
            if key not in cache:cache[key]=function(*args)
            return cache[key]
        return wrapped
    return decorate

class AccessCacheMiddleware:
    def __init__(self,get_response):self.get_response=get_response
    def __call__(self,request):
        token=CACHE.set({})
        try:return self.get_response(request)
        finally:CACHE.reset(token)
