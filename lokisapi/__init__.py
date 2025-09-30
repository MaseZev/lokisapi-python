from .client import LokisApiClient
from .async_client import AsyncLokisApiClient

from .models import (
    ChatMessage, ChatRole, ImageGenerationRequest, ImageEditRequest,
    ChatCompletionRequest, Model, ImageGenerationResponse, ImageEditResponse,
    ChatCompletionResponse, ChatCompletionChunk,
    ImageSize, ImageQuality, ImageStyle, ReasoningEffort
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
    async_encode_image_to_base64, async_encode_image_from_bytes, async_decode_base64_to_image,
    async_save_base64_image, async_resize_image_for_api, async_format_model_info,
    batch_process_images, batch_encode_images, batch_save_images
)

from .models_config import (
    ALL_MODELS, GEMINI_MODELS, OPENAI_MODELS, THINKING_MODELS,
    IMAGE_MODELS, TEXT_MODELS, OPENAI_MODEL_MAPPING
)

from .config import Settings
from .logging_config import setup_logging, get_logger
from .validators import (
    validate_api_key, validate_temperature, validate_max_tokens,
    validate_image_size as validate_image_size_format,
    validate_prompt, validate_messages, validate_base64_image,
    validate_thinking_budget
)
from .batch_utils import (
    batch_process_sync, batch_process_async, chunk_list,
    batch_chat_completions, batch_image_generations,
    batch_chat_completions_async, batch_image_generations_async
)

__version__ = "1.1.0"
__author__ = "LokisApi Team"

__all__ = [
    "LokisApiClient", "AsyncLokisApiClient",
    "ChatMessage", "ChatRole", "ImageGenerationRequest", "ImageEditRequest",
    "ChatCompletionRequest", "Model", "ImageGenerationResponse", "ImageEditResponse",
    "ChatCompletionResponse", "ChatCompletionChunk",
    "ImageSize", "ImageQuality", "ImageStyle", "ReasoningEffort",
    "LokisApiError", "AuthenticationError", "RateLimitError", "APIError",
    "ValidationError", "NetworkError", "ModelNotFoundError", "ModelNotSupportedError",
    "QuotaExceededError", "TokenLimitError", "RequestLimitError", "ServiceUnavailableError",
    "ImageProcessingError",
    "encode_image_to_base64", "encode_image_from_bytes", "decode_base64_to_image",
    "save_base64_image", "resize_image_for_api", "validate_image_size",
    "estimate_tokens", "format_model_info", "get_supported_models",
    "validate_api_key_format",
    "async_encode_image_to_base64", "async_encode_image_from_bytes", "async_decode_base64_to_image",
    "async_save_base64_image", "async_resize_image_for_api", "async_format_model_info",
    "batch_process_images", "batch_encode_images", "batch_save_images",
    "ALL_MODELS", "GEMINI_MODELS", "OPENAI_MODELS", "THINKING_MODELS",
    "IMAGE_MODELS", "TEXT_MODELS", "OPENAI_MODEL_MAPPING",
    "Settings", "setup_logging", "get_logger",
    "validate_api_key", "validate_temperature", "validate_max_tokens",
    "validate_image_size_format", "validate_prompt", "validate_messages",
    "validate_base64_image", "validate_thinking_budget",
    "batch_process_sync", "batch_process_async", "chunk_list",
    "batch_chat_completions", "batch_image_generations",
    "batch_chat_completions_async", "batch_image_generations_async",
]
