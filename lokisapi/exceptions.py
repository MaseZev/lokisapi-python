"""
Custom exceptions for LokisApi library.
"""

from typing import Optional, Dict, Any


class LokisApiError(Exception):
    """Base exception for all LokisApi errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(LokisApiError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", error_code: str = "AUTH_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)


class RateLimitError(LokisApiError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT", 
                 retry_after: Optional[int] = None, limit_type: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.retry_after = retry_after
        self.limit_type = limit_type  # 'rpm', 'tpm', 'rpd', 'ip', 'account', etc.
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (retry after {self.retry_after} seconds)"
        return base_msg


class APIError(LokisApiError):
    """Raised when API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 error_code: Optional[str] = None, response_data: Optional[Dict[str, Any]] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.status_code:
            return f"HTTP {self.status_code}: {base_msg}"
        return base_msg


class ValidationError(LokisApiError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None, 
                 error_code: str = "VALIDATION_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.field = field
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.field:
            return f"{base_msg} (field: {self.field})"
        return base_msg


class NetworkError(LokisApiError):
    """Raised when network request fails."""
    
    def __init__(self, message: str = "Network request failed", error_code: str = "NETWORK_ERROR", 
                 timeout: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.timeout = timeout
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.timeout:
            return f"{base_msg} (timeout: {self.timeout}s)"
        return base_msg


class ModelNotFoundError(LokisApiError):
    """Raised when requested model is not found."""
    
    def __init__(self, model_id: str, error_code: str = "MODEL_NOT_FOUND", details: Optional[Dict[str, Any]] = None):
        message = f"Model '{model_id}' not found"
        super().__init__(message, error_code, details)
        self.model_id = model_id


class ModelNotSupportedError(LokisApiError):
    """Raised when model doesn't support requested feature."""
    
    def __init__(self, model_id: str, feature: str, error_code: str = "MODEL_NOT_SUPPORTED", 
                 details: Optional[Dict[str, Any]] = None):
        message = f"Model '{model_id}' does not support {feature}"
        super().__init__(message, error_code, details)
        self.model_id = model_id
        self.feature = feature


class QuotaExceededError(RateLimitError):
    """Raised when quota is exceeded."""
    
    def __init__(self, message: str = "Quota exceeded", quota_type: Optional[str] = None,
                 retry_after: Optional[int] = None, error_code: str = "QUOTA_EXCEEDED",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, retry_after=retry_after, limit_type=quota_type, details=details)
        self.quota_type = quota_type  # 'daily', 'monthly', 'per_key', etc.


class TokenLimitError(RateLimitError):
    """Raised when token limit is exceeded."""
    
    def __init__(self, message: str = "Token limit exceeded", limit_type: Optional[str] = None,
                 retry_after: Optional[int] = None, error_code: str = "TOKEN_LIMIT",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, retry_after=retry_after, limit_type=limit_type, details=details)
        self.limit_type = limit_type  # 'per_minute', 'per_day', 'per_request', etc.


class RequestLimitError(RateLimitError):
    """Raised when request limit is exceeded."""
    
    def __init__(self, message: str = "Request limit exceeded", limit_type: Optional[str] = None,
                 retry_after: Optional[int] = None, error_code: str = "REQUEST_LIMIT",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, retry_after=retry_after, limit_type=limit_type, details=details)
        self.limit_type = limit_type  # 'per_minute', 'per_day', 'per_hour', etc.


class ServiceUnavailableError(APIError):
    """Raised when service is temporarily unavailable."""
    
    def __init__(self, message: str = "Service temporarily unavailable", 
                 retry_after: Optional[int] = None, error_code: str = "SERVICE_UNAVAILABLE",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 503, error_code, response_data=None, details=details)
        self.retry_after = retry_after


class ImageProcessingError(LokisApiError):
    """Raised when image processing fails."""
    
    def __init__(self, message: str = "Image processing failed", operation: Optional[str] = None,
                 error_code: str = "IMAGE_PROCESSING_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, details)
        self.operation = operation  # 'encode', 'decode', 'resize', 'validate', etc.
