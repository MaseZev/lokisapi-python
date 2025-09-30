import time
import hashlib
import json
from typing import Any, Optional, Dict, Callable
from threading import Lock


class ResponseCache:
    def __init__(self, max_size: int = 100, ttl_seconds: float = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.lock = Lock()
    
    def _make_key(self, *args, **kwargs) -> str:
        key_data = json.dumps([args, sorted(kwargs.items())], sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                
                if time.time() - timestamp < self.ttl_seconds:
                    return value
                else:
                    del self.cache[key]
            
            return None
    
    def set(self, key: str, value: Any):
        with self.lock:
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (value, time.time())
    
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def invalidate(self, key: str):
        with self.lock:
            if key in self.cache:
                del self.cache[key]


def cached(cache: ResponseCache, key_func: Optional[Callable] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache._make_key(*args, **kwargs)
            
            result = cache.get(cache_key)
            
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator
