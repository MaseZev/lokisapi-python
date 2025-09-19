"""
Data models for LokisApi library.
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class ImageSize(str, Enum):
    """Supported image sizes for DALL-E generation."""
    SIZE_256 = "256x256"
    SIZE_512 = "512x512"
    SIZE_1024 = "1024x1024"
    SIZE_1792 = "1792x1024"
    SIZE_1024_1792 = "1024x1792"


class ImageQuality(str, Enum):
    """Supported image qualities for DALL-E generation."""
    STANDARD = "standard"
    HD = "hd"


class ImageStyle(str, Enum):
    """Supported image styles for DALL-E generation."""
    VIVID = "vivid"
    NATURAL = "natural"


class ChatRole(str, Enum):
    """Chat message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ReasoningEffort(str, Enum):
    """Reasoning effort levels for GPT-5 models."""
    MINIMAL = "minimal"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: ChatRole
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API requests."""
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclass
class ImageGenerationRequest:
    """Request parameters for image generation."""
    prompt: str
    model: str = "dall-e-3"
    n: int = 1
    size: Union[ImageSize, str] = ImageSize.SIZE_1024
    quality: Union[ImageQuality, str] = ImageQuality.STANDARD
    style: Union[ImageStyle, str] = ImageStyle.VIVID
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return {
            "model": self.model,
            "prompt": self.prompt,
            "n": self.n,
            "size": self.size.value if hasattr(self.size, 'value') else self.size,
            "quality": self.quality.value if hasattr(self.quality, 'value') else self.quality,
            "style": self.style.value if hasattr(self.style, 'value') else self.style
        }


@dataclass
class ImageEditRequest:
    """Request parameters for image editing."""
    image: str  # Base64 encoded image
    prompt: str
    model: str = "dall-e-3"
    n: int = 1
    size: Union[ImageSize, str] = ImageSize.SIZE_1024
    quality: Union[ImageQuality, str] = ImageQuality.STANDARD
    style: Union[ImageStyle, str] = ImageStyle.VIVID
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return {
            "model": self.model,
            "image": self.image,
            "prompt": self.prompt,
            "n": self.n,
            "size": self.size.value if hasattr(self.size, 'value') else self.size,
            "quality": self.quality.value if hasattr(self.quality, 'value') else self.quality,
            "style": self.style.value if hasattr(self.style, 'value') else self.style
        }


@dataclass
class ChatCompletionRequest:
    """Request parameters for chat completion."""
    messages: List[ChatMessage]
    model: str = "gpt-5"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[Union[str, List[str]]] = None
    thinking: bool = False  # For Gemini 2.5 models
    thinking_budget: int = 1000  # For Gemini 2.5 models
    reasoning_effort: Union[ReasoningEffort, str] = ReasoningEffort.MEDIUM  # For GPT-5 models
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        data = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in self.messages],
            "temperature": self.temperature,
            "stream": self.stream,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "thinking": self.thinking,
            "thinking_budget": self.thinking_budget,
            "reasoning_effort": self.reasoning_effort.value if hasattr(self.reasoning_effort, 'value') else self.reasoning_effort
        }
        
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens
        if self.stop is not None:
            data["stop"] = self.stop
            
        return data


@dataclass
class Model:
    """Represents an available model."""
    id: str
    object: str
    created: int
    owned_by: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """Create Model from API response."""
        return cls(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            owned_by=data["owned_by"]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Model to dictionary (includes optional capability flags if present)."""
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "owned_by": self.owned_by,
            # Optional fields possibly injected by managers
            "supports_text": getattr(self, "supports_text", None),
            "supports_thinking": getattr(self, "supports_thinking", None),
            "supports_images": getattr(self, "supports_images", None),
            "deprecated": getattr(self, "deprecated", None),
        }


@dataclass
class ImageGenerationResponse:
    """Response from image generation API."""
    id: str
    object: str
    created: int
    model: str
    data: List[Dict[str, Any]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageGenerationResponse':
        """Create ImageGenerationResponse from API response."""
        return cls(
            id=data.get("id", f"img-{data['created']}"),
            object=data.get("object", "list"),
            created=data["created"],
            model=data.get("model", "dall-e-3"),
            data=data["data"]
        )


@dataclass
class ImageEditResponse:
    """Response from image editing API."""
    id: str
    object: str
    created: int
    model: str
    data: List[Dict[str, Any]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageEditResponse':
        """Create ImageEditResponse from API response."""
        return cls(
            id=data.get("id", f"img-edit-{data['created']}"),
            object=data.get("object", "list"),
            created=data["created"],
            model=data.get("model", "dall-e-3"),
            data=data["data"]
        )


@dataclass
class ChatCompletionResponse:
    """Response from chat completion API."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionResponse':
        """Create ChatCompletionResponse from API response."""
        return cls(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=data["choices"],
            usage=data["usage"]
        )


@dataclass
class ChatCompletionChunk:
    """Streaming chunk from chat completion API."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatCompletionChunk':
        """Create ChatCompletionChunk from API response."""
        return cls(
            id=data["id"],
            object=data["object"],
            created=data["created"],
            model=data["model"],
            choices=data["choices"]
        )
