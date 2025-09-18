"""
LokisApi Python Library

A comprehensive Python library for interacting with LokisApi services.
Supports image generation, image editing, chat completions, and model management.
"""

from .client import LokisApiClient
from .async_client import AsyncLokisApiClient
from .models import (
    ChatMessage, ChatRole, ImageGenerationRequest, ImageEditRequest, 
    ChatCompletionRequest, Model, ImageGenerationResponse, ImageEditResponse,
    ChatCompletionResponse, ChatCompletionChunk, ImageSize, ImageQuality, 
    ImageStyle, ReasoningEffort
)
from .exceptions import (
    LokisApiError, AuthenticationError, RateLimitError, APIError,
    ValidationError, NetworkError, ModelNotFoundError, ModelNotSupportedError,
    QuotaExceededError, TokenLimitError, RequestLimitError, ServiceUnavailableError,
    ImageProcessingError
)
from .utils import (
    encode_image_to_base64, encode_image_from_bytes, decode_base64_to_image,
    save_base64_image, resize_image_for_api, validate_image_size,
    estimate_tokens, format_model_info, get_supported_models,
    validate_api_key_format
)
from .async_utils import (
    encode_image_to_base64 as async_encode_image_to_base64,
    encode_image_from_bytes as async_encode_image_from_bytes,
    decode_base64_to_image as async_decode_base64_to_image,
    save_base64_image as async_save_base64_image,
    resize_image_for_api as async_resize_image_for_api,
    format_model_info as async_format_model_info,
    batch_process_images, batch_encode_images, batch_save_images
)
from .models_config import (
    ALL_MODELS, GEMINI_MODELS, OPENAI_MODELS, THINKING_MODELS,
    IMAGE_MODELS, TEXT_MODELS, OPENAI_MODEL_MAPPING
)

__version__ = "1.0.0"
__author__ = "LokisApi Team"

__all__ = [
    # Main clients
    "LokisApiClient", "AsyncLokisApiClient",
    
    # Models
    "ChatMessage", "ChatRole", "ImageGenerationRequest", "ImageEditRequest",
    "ChatCompletionRequest", "Model", "ImageGenerationResponse", "ImageEditResponse",
    "ChatCompletionResponse", "ChatCompletionChunk",
    
    # Enums
    "ImageSize", "ImageQuality", "ImageStyle", "ReasoningEffort",
    
    # Exceptions
    "LokisApiError", "AuthenticationError", "RateLimitError", "APIError",
    "ValidationError", "NetworkError", "ModelNotFoundError", "ModelNotSupportedError",
    "QuotaExceededError", "TokenLimitError", "RequestLimitError", "ServiceUnavailableError",
    "ImageProcessingError",
    
    # Synchronous utilities
    "encode_image_to_base64", "encode_image_from_bytes", "decode_base64_to_image",
    "save_base64_image", "resize_image_for_api", "validate_image_size",
    "estimate_tokens", "format_model_info", "get_supported_models",
    "validate_api_key_format",
    
    # Asynchronous utilities
    "async_encode_image_to_base64", "async_encode_image_from_bytes", "async_decode_base64_to_image",
    "async_save_base64_image", "async_resize_image_for_api", "async_format_model_info",
    "batch_process_images", "batch_encode_images", "batch_save_images",
    
    # Model configurations
    "ALL_MODELS", "GEMINI_MODELS", "OPENAI_MODELS", "THINKING_MODELS",
    "IMAGE_MODELS", "TEXT_MODELS", "OPENAI_MODEL_MAPPING"
]
