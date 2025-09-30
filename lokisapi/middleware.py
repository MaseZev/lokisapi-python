from typing import Callable, Any, Dict, Optional
from functools import wraps
import time


class Middleware:
    def process_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return data
    
    def process_response(self, endpoint: str, response: Any) -> Any:
        return response
    
    def process_error(self, endpoint: str, error: Exception) -> None:
        pass


class LoggingMiddleware(Middleware):
    def __init__(self, logger=None):
        self.logger = logger
    
    def process_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if self.logger:
            self.logger.info(f"Request to {endpoint}")
        return data
    
    def process_response(self, endpoint: str, response: Any) -> Any:
        if self.logger:
            self.logger.info(f"Response from {endpoint}")
        return response


class TimingMiddleware(Middleware):
    def __init__(self):
        self.timings = {}
        self.start_time = None
    
    def process_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self.start_time = time.time()
        return data
    
    def process_response(self, endpoint: str, response: Any) -> Any:
        if self.start_time:
            duration = time.time() - self.start_time
            self.timings[endpoint] = duration
        return response


class RateLimitMiddleware(Middleware):
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def process_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = time.time()
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        
        if len(self.requests) >= self.max_requests:
            raise Exception(f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds}s")
        
        self.requests.append(now)
        return data


class MiddlewareManager:
    def __init__(self):
        self.middlewares = []
    
    def add(self, middleware: Middleware):
        self.middlewares.append(middleware)
    
    def process_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        for middleware in self.middlewares:
            data = middleware.process_request(endpoint, data)
        return data
    
    def process_response(self, endpoint: str, response: Any) -> Any:
        for middleware in reversed(self.middlewares):
            response = middleware.process_response(endpoint, response)
        return response
    
    def process_error(self, endpoint: str, error: Exception):
        for middleware in self.middlewares:
            middleware.process_error(endpoint, error)
