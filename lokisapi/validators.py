import re
from typing import Optional, List, Any
from .exceptions import ValidationError
from .models import ImageSize


def validate_api_key(api_key: str) -> bool:
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key is required", field="api_key")
    
    if len(api_key) < 10:
        raise ValidationError("API key is too short", field="api_key")
    
    return True


def validate_temperature(temperature: float) -> bool:
    if not isinstance(temperature, (int, float)):
        raise ValidationError("Temperature must be a number", field="temperature")
    
    if not 0.0 <= temperature <= 2.0:
        raise ValidationError("Temperature must be between 0.0 and 2.0", field="temperature")
    
    return True


def validate_max_tokens(max_tokens: Optional[int]) -> bool:
    if max_tokens is None:
        return True
    
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValidationError("max_tokens must be a positive integer", field="max_tokens")
    
    if max_tokens > 128000:
        raise ValidationError("max_tokens exceeds maximum (128000)", field="max_tokens")
    
    return True


def validate_image_size(size: str) -> bool:
    valid_sizes = [s.value for s in ImageSize]
    
    if size not in valid_sizes:
        raise ValidationError(
            f"Invalid image size '{size}'. Must be one of: {', '.join(valid_sizes)}",
            field="size"
        )
    
    return True


def validate_prompt(prompt: str, min_length: int = 1, max_length: int = 4000) -> bool:
    if not prompt or not isinstance(prompt, str):
        raise ValidationError("Prompt is required", field="prompt")
    
    if len(prompt) < min_length:
        raise ValidationError(f"Prompt too short (min {min_length} chars)", field="prompt")
    
    if len(prompt) > max_length:
        raise ValidationError(f"Prompt too long (max {max_length} chars)", field="prompt")
    
    return True


def validate_messages(messages: List[Any]) -> bool:
    if not messages or not isinstance(messages, list):
        raise ValidationError("At least one message is required", field="messages")
    
    for i, msg in enumerate(messages):
        if not hasattr(msg, 'role') or not hasattr(msg, 'content'):
            raise ValidationError(
                f"Message at index {i} must have 'role' and 'content'",
                field="messages"
            )
        
        if not msg.content:
            raise ValidationError(f"Message at index {i} has empty content", field="messages")
    
    return True


def validate_base64_image(image_data: str) -> bool:
    if not image_data or not isinstance(image_data, str):
        raise ValidationError("Image data is required", field="image")
    
    if image_data.startswith('data:'):
        try:
            image_data = image_data.split(',', 1)[1]
        except IndexError:
            raise ValidationError("Invalid data URI format", field="image")
    
    if not re.match(r'^[A-Za-z0-9+/=]+$', image_data):
        raise ValidationError("Invalid base64 encoding", field="image")
    
    if len(image_data) > 30_000_000:
        raise ValidationError("Image data too large (max ~20MB)", field="image")
    
    return True


def validate_thinking_budget(budget: int) -> bool:
    if not isinstance(budget, int):
        raise ValidationError("Thinking budget must be an integer", field="thinking_budget")
    
    if budget < 0 or budget > 10000:
        raise ValidationError("Thinking budget must be between 0 and 10000", field="thinking_budget")
    
    return True
