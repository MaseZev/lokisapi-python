import base64
import io
import aiofiles
import asyncio
from typing import Union, Optional, TYPE_CHECKING
from PIL import Image
if TYPE_CHECKING:
    from .async_client import AsyncLokisApiClient

try:
    _RESAMPLE = Image.Resampling.LANCZOS
except Exception:
    _RESAMPLE = Image.LANCZOS


async def encode_image_to_base64(image_path: str) -> str:
    async with aiofiles.open(image_path, "rb") as image_file:
        image_bytes = await image_file.read()
        return base64.b64encode(image_bytes).decode('utf-8')


async def encode_image_from_bytes(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')


async def decode_base64_to_image(base64_string: str) -> Image.Image:
    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA")
    return image


async def save_base64_image(base64_string: str, output_path: str):
    image = await decode_base64_to_image(base64_string)
    image.save(output_path)


async def resize_image_for_api(image_path: str, target_size: tuple) -> str:
    async with aiofiles.open(image_path, "rb") as f:
        image_bytes = await f.read()
    with Image.open(io.BytesIO(image_bytes)) as img:
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        if img.size[0] > target_size[0] or img.size[1] > target_size[1]:
            img.thumbnail(target_size, _RESAMPLE)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return await encode_image_from_bytes(buffer.getvalue())


def validate_image_size(size: Union[str, tuple]) -> bool:
    valid_sizes = [
        "256x256", "512x512", "1024x1024", 
        "1792x1024", "1024x1792"
    ]
    
    if isinstance(size, str):
        return size in valid_sizes
    elif isinstance(size, tuple) and len(size) == 2:
        size_str = f"{size[0]}x{size[1]}"
        return size_str in valid_sizes
    
    return False


def estimate_tokens(text: str) -> int:

    return max(1, len(text) // 4 + 1)


def validate_api_key_format(api_key: str) -> bool:
    return api_key.startswith("sk-") and len(api_key) > 10


async def format_model_info(model_id: str, client: Optional['AsyncLokisApiClient'] = None) -> dict:
    if client:
        try:
            model = await client.get_model(model_id)
            return {
                "id": model.id,
                "name": model.id,
                "provider": model.owned_by,
                "category": "unknown",
                "supports_text": True,
                "supports_thinking": model_id in await client.get_thinking_models(),
                "supports_images": model_id in await client.get_image_models(),
                "deprecated": False,
                "limits": {
                    "rpm": None,
                    "tpm": None,
                    "rpd": None
                }
            }
        except Exception:
            pass
    
    from .models_config import ALL_MODELS
    
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return {
                "id": model["id"],
                "name": model["name"],
                "provider": model.get("provider", "Unknown"),
                "category": model["category"],
                "supports_text": model.get("supports_text", False),
                "supports_thinking": model.get("supports_thinking", False),
                "supports_images": model.get("supports_images", False),
                "deprecated": model.get("deprecated", False),
                "limits": {
                    "rpm": model.get("rpm"),
                    "tpm": model.get("tpm"),
                    "rpd": model.get("rpd")
                }
            }
    
    return {"error": f"Model '{model_id}' not found"}


def get_supported_models(category: str = "all") -> list:
    from .models_config import ALL_MODELS
    
    if category == "all":
        return [model["id"] for model in ALL_MODELS]
    elif category == "text":
        return [model["id"] for model in ALL_MODELS if model.get("supports_text", False)]
    elif category == "image":
        return [model["id"] for model in ALL_MODELS if model.get("supports_images", False)]
    elif category == "thinking":
        return [model["id"] for model in ALL_MODELS if model.get("supports_thinking", False)]
    elif category == "deprecated":
        return [model["id"] for model in ALL_MODELS if model.get("deprecated", False)]
    else:
        return []


def get_model_limits(model_id: str) -> dict:
    from .models_config import ALL_MODELS
    
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return {
                "rpm": model.get("rpm"),
                "tpm": model.get("tpm"),
                "rpd": model.get("rpd")
            }
    
    return {"rpm": None, "tpm": None, "rpd": None}


def is_model_deprecated(model_id: str) -> bool:
    from .models_config import ALL_MODELS
    
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return model.get("deprecated", False)
    
    return False


def get_model_provider(model_id: str) -> str:
    from .models_config import ALL_MODELS
    
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return model.get("provider", "Unknown")
    
    return "Unknown"


def validate_model_support(model_id: str, feature: str) -> bool:
    from .models_config import ALL_MODELS
    
    for model in ALL_MODELS:
        if model["id"] == model_id:
            if feature == "text":
                return model.get("supports_text", False)
            elif feature == "image":
                return model.get("supports_images", False)
            elif feature == "thinking":
                return model.get("supports_thinking", False)
    
    return False


def get_model_category(model_id: str) -> str:
    from .models_config import ALL_MODELS
    
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return model.get("category", "unknown")
    
    return "unknown"


def format_error_message(error: Exception) -> str:
    if hasattr(error, 'error_code') and error.error_code:
        return f"[{error.error_code}] {str(error)}"
    return str(error)


def get_retry_delay(error: Exception) -> Optional[int]:
    if hasattr(error, 'retry_after') and error.retry_after:
        return error.retry_after
    return None


def is_rate_limit_error(error: Exception) -> bool:
    from .exceptions import RateLimitError
    return isinstance(error, RateLimitError)


def is_authentication_error(error: Exception) -> bool:
    from .exceptions import AuthenticationError
    return isinstance(error, AuthenticationError)


def is_network_error(error: Exception) -> bool:
    from .exceptions import NetworkError
    return isinstance(error, NetworkError)


def is_model_error(error: Exception) -> bool:
    from .exceptions import ModelNotFoundError, ModelNotSupportedError
    return isinstance(error, (ModelNotFoundError, ModelNotSupportedError))


def get_error_details(error: Exception) -> dict:
    if hasattr(error, 'details') and error.details:
        return error.details
    return {}


def format_model_list(models: list, show_deprecated: bool = False) -> str:
    if not models:
        return "No models available"
    
    lines = []
    for model in models:
        if isinstance(model, dict):
            model_id = model.get("id", "unknown")
            provider = model.get("provider", "Unknown")
            deprecated = model.get("deprecated", False)
        else:
            model_id = getattr(model, 'id', 'unknown')
            provider = getattr(model, 'owned_by', 'Unknown')
            deprecated = getattr(model, 'deprecated', False)
        
        if deprecated and not show_deprecated:
            continue
            
        status = " (deprecated)" if deprecated else ""
        lines.append(f"- {model_id} ({provider}){status}")
    
    return "\n".join(lines)


def get_cache_file_path() -> str:
    import os
    return os.path.join(os.path.expanduser("~"), ".lokisapi_models_cache.json")


async def clear_cache_file():
    import os
    cache_file = get_cache_file_path()
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
        except Exception:
            pass


def get_cache_file_size() -> int:
    import os
    cache_file = get_cache_file_path()
    if os.path.exists(cache_file):
        try:
            return os.path.getsize(cache_file)
        except Exception:
            pass
    return 0


async def batch_process_images(image_paths: list, target_size: tuple) -> list:
    tasks = [resize_image_for_api(path, target_size) for path in image_paths]
    return await asyncio.gather(*tasks)


async def batch_encode_images(image_paths: list) -> list:
    tasks = [encode_image_to_base64(path) for path in image_paths]
    return await asyncio.gather(*tasks)


async def batch_save_images(base64_images: list, output_paths: list) -> None:
    tasks = [save_base64_image(img, path) for img, path in zip(base64_images, output_paths)]
    await asyncio.gather(*tasks)
