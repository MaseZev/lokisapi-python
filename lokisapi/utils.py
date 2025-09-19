"""
Utility functions for LokisApi library.
"""

import base64
import io
from typing import Union, Optional, TYPE_CHECKING
from PIL import Image
if TYPE_CHECKING:
    from .client import LokisApiClient

try:
    _RESAMPLE = Image.Resampling.LANCZOS
except Exception:
    _RESAMPLE = Image.LANCZOS


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded image string
        
    Example:
        >>> base64_image = encode_image_to_base64("path/to/image.jpg")
        >>> print(base64_image[:50])  # Shows first 50 characters
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def encode_image_from_bytes(image_bytes: bytes) -> str:
    """
    Encode image bytes to base64 string.
    
    Args:
        image_bytes: Image data as bytes
        
    Returns:
        Base64 encoded image string
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def decode_base64_to_image(base64_string: str) -> Image.Image:
    """
    Decode base64 string to PIL Image.
    
    Args:
        base64_string: Base64 encoded image string
        
    Returns:
        PIL Image object
        
    Example:
        >>> image = decode_base64_to_image(base64_string)
        >>> image.show()  # Display the image
    """
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]
    
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    return image


def save_base64_image(base64_string: str, output_path: str) -> None:
    """
    Save base64 encoded image to file.
    
    Args:
        base64_string: Base64 encoded image string
        output_path: Path where to save the image
        
    Example:
        >>> save_base64_image(base64_string, "output.png")
    """
   
    if ',' in base64_string:
        base64_string = base64_string.split(',', 1)[1]
    image_data = base64.b64decode(base64_string)
    with open(output_path, "wb") as f:
        f.write(image_data)


def resize_image_for_api(image_path: str, max_size: tuple = (1024, 1024)) -> str:
    """
    Resize image to fit API requirements and return base64.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum size (width, height)
        
    Returns:
        Base64 encoded resized image
        
    Example:
        >>> resized_base64 = resize_image_for_api("large_image.jpg", (1024, 1024))
    """
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, _RESAMPLE)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return encode_image_from_bytes(img_bytes.getvalue())


def validate_image_size(size: Union[str, tuple]) -> bool:
    """
    Validate if image size is supported by the API.
    
    Args:
        size: Image size as string (e.g., "1024x1024") or tuple (1024, 1024)
        
    Returns:
        True if size is valid, False otherwise
        
    Example:
        >>> validate_image_size("1024x1024")  # True
        >>> validate_image_size("999x999")   # False
    """
    valid_sizes = [
        "256x256", "512x512", "1024x1024", 
        "1792x1024", "1024x1792"
    ]
    
    if isinstance(size, tuple):
        size = f"{size[0]}x{size[1]}"
    
    return size in valid_sizes


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text (rough approximation).
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
        
    Example:
        >>> tokens = estimate_tokens("Hello, world!")
        >>> print(tokens)  # Approximately 3-4 tokens
    """
    # Rough estimation: 1 token per 4 characters
    return max(1, len(text) // 4 + 1)


def format_model_info(model_id: str, client: Optional['LokisApiClient'] = None) -> dict:
    """
    Get formatted information about a model.
    
    Args:
        model_id: Model identifier
        client: Optional LokisApiClient instance for automatic model discovery
        
    Returns:
        Dictionary with model information
        
    Example:
        >>> info = format_model_info("gpt-5")
        >>> print(info["name"])  # "GPT-5"
        
        >>> # With automatic model discovery
        >>> client = LokisApiClient("your-api-key")
        >>> info = format_model_info("gpt-5", client)
    """
    # Try to get model from client first (if provided)
    if client:
        try:
            model = client.get_model(model_id)
            return {
                "id": model.id,
                "name": model.id,  # Use ID as name since we don't have display name
                "provider": model.owned_by,
                "category": "unknown",  # Will be determined by model manager
                "supports_text": True,  # Assume all models support text unless image-only
                "supports_thinking": model_id in client.get_thinking_models(),
                "supports_images": model_id in client.get_image_models(),
                "deprecated": False,  # Assume not deprecated unless specified
                "limits": {
                    "rpm": None,
                    "tpm": None,
                    "rpd": None
                }
            }
        except Exception:
            pass  # Fall back to static config
    
    # Fall back to static configuration
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


def get_supported_models(category: Optional[str] = None) -> list:
    """
    Get list of supported models, optionally filtered by category.
    
    Args:
        category: Optional category filter ("text", "image", "deprecated")
        
    Returns:
        List of model IDs
        
    Example:
        >>> text_models = get_supported_models("text")
        >>> image_models = get_supported_models("image")
    """
    from .models_config import ALL_MODELS
    
    if category:
        return [model["id"] for model in ALL_MODELS if model["category"] == category]
    else:
        return [model["id"] for model in ALL_MODELS if not model.get("deprecated", False)]


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format (basic check).
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if format looks valid, False otherwise
        
    Example:
        >>> is_valid = validate_api_key_format("sk-...")
        >>> print(is_valid)  # True or False
    """
    if not api_key or len(api_key) < 10:
        return False
    
    # Basic checks for common API key patterns
    valid_prefixes = ["sk-", "AIzaSy", "Bearer "]
    
    # Remove Bearer prefix if present
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]
    
    # Check if it starts with a valid prefix
    return any(api_key.startswith(prefix) for prefix in valid_prefixes)
