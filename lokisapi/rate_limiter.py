import time
from typing import Dict, Optional
from threading import Lock
import asyncio


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self.lock = Lock()
    
    def acquire(self) -> bool:
        with self.lock:
            now = time.time()
            self.requests = [t for t in self.requests if now - t < self.window_seconds]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def wait_if_needed(self):
        while not self.acquire():
            time.sleep(0.1)
    
    def time_until_available(self) -> float:
        with self.lock:
            if len(self.requests) < self.max_requests:
                return 0.0
            
            oldest = min(self.requests)
            wait_time = self.window_seconds - (time.time() - oldest)
            return max(0.0, wait_time)


class AsyncRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        async with self.lock:
            now = time.time()
            self.requests = [t for t in self.requests if now - t < self.window_seconds]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    async def wait_if_needed(self):
        while not await self.acquire():
            await asyncio.sleep(0.1)
    
    async def time_until_available(self) -> float:
        async with self.lock:
            if len(self.requests) < self.max_requests:
                return 0.0
            
            oldest = min(self.requests)
            wait_time = self.window_seconds - (time.time() - oldest)
            return max(0.0, wait_time)


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        refill_amount = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + refill_amount)
        self.last_refill = now
    
    def wait_for_tokens(self, tokens: int = 1):
        while not self.consume(tokens):
            time.sleep(0.01)
