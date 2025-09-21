"""
Main client for LokisApi interactions.
"""

import json
import requests
from typing import List, Iterator, Optional, Dict, Any, Union
from urllib.parse import urljoin

from .models import (
    ChatMessage, ChatRole, ImageGenerationRequest, ImageEditRequest, ChatCompletionRequest,
    Model, ImageGenerationResponse, ImageEditResponse, ChatCompletionResponse, ChatCompletionChunk,
    ImageSize, ImageQuality, ImageStyle, ReasoningEffort
)
from .exceptions import (
    LokisApiError, AuthenticationError, RateLimitError, APIError,
    ValidationError, NetworkError, ModelNotFoundError, ModelNotSupportedError,
    QuotaExceededError, TokenLimitError, RequestLimitError, ServiceUnavailableError
)
from .model_cache import ModelManager


class LokisApiClient:
    """
    Main client for interacting with LokisApi services.
    
    This client provides methods for:
    - Image generation using DALL-E models
    - Chat completions using GPT models
    - Model management and listing
    """
    
    def __init__(self, api_key: str, base_url: str = "https://lokisapi.online/v1", 
                 model_cache_duration: float = 3600):
        """
        Initialize the LokisApi client.
        
        Args:
            api_key: Your LokisApi API key
            base_url: Base URL for the API (default: https://lokisapi.online/v1)
            model_cache_duration: Model cache duration in seconds (default: 1 hour)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'lokisapi-python/1.0.0'
        })
        
        # Initialize model manager for automatic model discovery
        self.model_manager = ModelManager(self, cache_duration=model_cache_duration)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> requests.Response:
        """
        Make a request to the LokisApi.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            stream: Whether to stream the response
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        url = urljoin(self.base_url + '/', endpoint)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, stream=stream, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, stream=stream, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle different status codes with detailed error information
            if response.status_code == 401:
                error_details = self._extract_error_details(response)
                raise AuthenticationError(
                    "Invalid API key or authentication failed",
                    details=error_details
                )
            elif response.status_code == 429:
                error_details = self._extract_error_details(response)
                retry_after = self._extract_retry_after(response)
                limit_type = self._extract_limit_type(response)
                
                if 'quota' in str(error_details).lower():
                    raise QuotaExceededError(
                        "Quota exceeded",
                        quota_type=limit_type,
                        retry_after=retry_after,
                        details=error_details
                    )
                elif 'token' in str(error_details).lower():
                    raise TokenLimitError(
                        "Token limit exceeded",
                        limit_type=limit_type,
                        retry_after=retry_after,
                        details=error_details
                    )
                elif 'request' in str(error_details).lower():
                    raise RequestLimitError(
                        "Request limit exceeded",
                        limit_type=limit_type,
                        retry_after=retry_after,
                        details=error_details
                    )
                else:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        retry_after=retry_after,
                        limit_type=limit_type,
                        details=error_details
                    )
            elif response.status_code == 503:
                error_details = self._extract_error_details(response)
                retry_after = self._extract_retry_after(response)
                raise ServiceUnavailableError(
                    "Service temporarily unavailable",
                    retry_after=retry_after,
                    details=error_details
                )
            elif response.status_code >= 400:
                error_details = self._extract_error_details(response)
                error_message = self._extract_error_message(response)
                raise APIError(
                    error_message,
                    status_code=response.status_code,
                    response_data=error_details,
                    details=error_details
                )
            
            return response
            
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {str(e)}", timeout=30)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network request failed: {str(e)}")
    
    def _extract_error_details(self, response: requests.Response) -> Dict[str, Any]:
        """Extract error details from response."""
        try:
            return response.json()
        except:
            return {"raw_response": response.text}
    
    def _extract_error_message(self, response: requests.Response) -> str:
        """Extract error message from response."""
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                # Try different common error message fields
                for field in ['error', 'message', 'detail', 'description']:
                    if field in error_data:
                        error_value = error_data[field]
                        if isinstance(error_value, dict) and 'message' in error_value:
                            return error_value['message']
                        elif isinstance(error_value, str):
                            return error_value
                return str(error_data)
            return str(error_data)
        except:
            return f"HTTP {response.status_code}: {response.text}"
    
    def _extract_retry_after(self, response: requests.Response) -> Optional[int]:
        """Extract retry-after header from response."""
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return None
    
    def _extract_limit_type(self, response: requests.Response) -> Optional[str]:
        """Extract limit type from error response."""
        try:
            error_data = response.json()
            error_message = str(error_data).lower()
            
            if 'rpm' in error_message or 'requests per minute' in error_message:
                return 'rpm'
            elif 'tpm' in error_message or 'tokens per minute' in error_message:
                return 'tpm'
            elif 'rpd' in error_message or 'requests per day' in error_message:
                return 'rpd'
            elif 'daily' in error_message:
                return 'daily'
            elif 'monthly' in error_message:
                return 'monthly'
            elif 'account' in error_message:
                return 'account'
            elif 'ip' in error_message:
                return 'ip'
        except:
            pass
        return None
    
    def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """
        Generate an image using DALL-E.
        
        Args:
            request: Image generation request parameters
            
        Returns:
            ImageGenerationResponse with generated image data
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> request = ImageGenerationRequest(
            ...     prompt="A beautiful sunset over mountains",
            ...     size=ImageSize.SIZE_1024
            ... )
            >>> response = client.generate_image(request)
            >>> print(response.data[0]['url'])
        """
        response = self._make_request('POST', 'images/generations', request.to_dict())
        return ImageGenerationResponse.from_dict(response.json())
    
    def edit_image(self, request: ImageEditRequest) -> ImageEditResponse:
        """
        Edit an image using DALL-E.
        
        Args:
            request: Image editing request parameters
            
        Returns:
            ImageEditResponse with edited image data
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> request = ImageEditRequest(
            ...     image="base64_encoded_image_data",
            ...     prompt="Add a rainbow to the sky",
            ...     size=ImageSize.SIZE_1024
            ... )
            >>> response = client.edit_image(request)
            >>> print(response.data[0]['url'])
        """
        response = self._make_request('POST', 'images/edits', request.to_dict())
        return ImageEditResponse.from_dict(response.json())
    
    def create_chat_completion(
        self, 
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Create a chat completion.
        
        Args:
            request: Chat completion request parameters
            
        Returns:
            ChatCompletionResponse with completion data
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> messages = [ChatMessage(ChatRole.USER, "Привет!")]
            >>> request = ChatCompletionRequest(messages=messages)
            >>> response = client.create_chat_completion(request)
            >>> print(response.choices[0]['message']['content'])
        """
        response = self._make_request('POST', 'chat/completions', request.to_dict())
        return ChatCompletionResponse.from_dict(response.json())
    
    def create_chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionChunk]:
        """
        Create a streaming chat completion.
        
        Args:
            request: Chat completion request parameters (stream must be True)
            
        Yields:
            ChatCompletionChunk objects as they arrive
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> messages = [ChatMessage(ChatRole.USER, "Привет!")]
            >>> request = ChatCompletionRequest(messages=messages, stream=True)
            >>> for chunk in client.create_chat_completion_stream(request):
            ...     print(chunk.choices[0].get('delta', {}).get('content', ''), end='')
        """
        if not request.stream:
            request.stream = True
        
        response = self._make_request('POST', 'chat/completions', request.to_dict(), stream=True)
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data.strip() == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data)
                        yield ChatCompletionChunk.from_dict(chunk_data)
                    except json.JSONDecodeError:
                        continue
    
    def list_models(self, force_refresh: bool = False) -> List[Model]:
        """
        List all available models (automatically cached).
        
        Args:
            force_refresh: Force refresh from API instead of using cache
            
        Returns:
            List of available models
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> models = client.list_models()
            >>> for model in models:
            ...     print(f"{model.id} - {model.owned_by}")
        """
        return self.model_manager.get_models(force_refresh)
    
    def get_model(self, model_id: str, force_refresh: bool = False) -> Model:
        """
        Get information about a specific model (automatically cached).
        
        Args:
            model_id: ID of the model to retrieve
            force_refresh: Force refresh from API instead of using cache
            
        Returns:
            Model information
            
        Raises:
            ModelNotFoundError: If model is not found
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> model = client.get_model("gpt-5")
            >>> print(f"Model: {model.id}, Created: {model.created}")
        """
        return self.model_manager.get_model(model_id, force_refresh)
    
    def get_thinking_models(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of models that support thinking (Gemini 2.5).
        
        Args:
            force_refresh: Force refresh from API instead of using cache
            
        Returns:
            List of model IDs that support thinking
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> thinking_models = client.get_thinking_models()
            >>> print(f"Thinking models: {thinking_models}")
        """
        return self.model_manager.get_thinking_models(force_refresh)
    
    def get_image_models(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of models that support image generation/editing.
        
        Args:
            force_refresh: Force refresh from API instead of using cache
            
        Returns:
            List of model IDs that support images
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> image_models = client.get_image_models()
            >>> print(f"Image models: {image_models}")
        """
        return self.model_manager.get_image_models(force_refresh)
    
    def get_text_models(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of models that support text generation.
        
        Args:
            force_refresh: Force refresh from API instead of using cache
            
        Returns:
            List of model IDs that support text
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> text_models = client.get_text_models()
            >>> print(f"Text models: {text_models}")
        """
        return self.model_manager.get_text_models(force_refresh)
    
    def get_models_by_category(self, category: str, force_refresh: bool = False) -> List[Model]:
        """
        Get models filtered by category.
        
        Args:
            category: Model category ('text', 'image', 'deprecated')
            force_refresh: Force refresh from API instead of using cache
            
        Returns:
            List of models in category
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> text_models = client.get_models_by_category("text")
            >>> print(f"Text models count: {len(text_models)}")
        """
        return self.model_manager.get_models_by_category(category, force_refresh)
    
    def refresh_models_cache(self):
        """
        Force refresh the models cache from API.
        
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> client.refresh_models_cache()
        """
        self.model_manager.get_models(force_refresh=True)
    
    def clear_models_cache(self):
        """
        Clear the models cache.
        
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> client.clear_models_cache()
        """
        self.model_manager.clear_cache()
    
    def get_models_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the models cache.
        
        Returns:
            Dictionary with cache information
            
        Example:
            >>> client = LokisApiClient("your-api-key")
            >>> cache_info = client.get_models_cache_info()
            >>> print(f"Cache age: {cache_info['age_seconds']} seconds")
        """
        return self.model_manager.get_cache_info()
    
    # Convenience methods for common use cases
    
    def chat(
        self, 
        messages: List[ChatMessage], 
        model: str = "gpt-5",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        thinking: bool = False,
        thinking_budget: int = 1000,
        reasoning_effort: Union[ReasoningEffort, str] = ReasoningEffort.MEDIUM
    ) -> Union[ChatCompletionResponse, Iterator[ChatCompletionChunk]]:
        """
        Convenience method for chat completion.
        
        Args:
            messages: List of chat messages
            model: Model to use (default: gpt-5)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            thinking: Enable thinking mode for Gemini 2.5 models
            thinking_budget: Budget for thinking mode
            reasoning_effort: Reasoning effort for GPT-5 models
            
        Returns:
            ChatCompletionResponse or Iterator[ChatCompletionChunk] if streaming
        """
        request = ChatCompletionRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            thinking=thinking,
            thinking_budget=thinking_budget,
            reasoning_effort=reasoning_effort
        )
        
        if stream:
            return self.create_chat_completion_stream(request)
        else:
            return self.create_chat_completion(request)
    
    def generate_image_simple(
        self, 
        prompt: str, 
        size: Union[ImageSize, str] = ImageSize.SIZE_1024,
        model: str = "dall-e-3",
        quality: Union[ImageQuality, str] = ImageQuality.STANDARD,
        style: Union[ImageStyle, str] = ImageStyle.VIVID
    ) -> ImageGenerationResponse:
        """
        Convenience method for simple image generation.
        
        Args:
            prompt: Image generation prompt
            size: Image size (default: 1024x1024)
            model: Model to use (default: dall-e-3)
            quality: Image quality (default: standard)
            style: Image style (default: vivid)
            
        Returns:
            ImageGenerationResponse
        """
        request = ImageGenerationRequest(
            prompt=prompt,
            size=size,
            model=model,
            quality=quality,
            style=style
        )
        return self.generate_image(request)
    
    def edit_image_simple(
        self, 
        image: str,
        prompt: str, 
        size: Union[ImageSize, str] = ImageSize.SIZE_1024,
        model: str = "dall-e-3",
        quality: Union[ImageQuality, str] = ImageQuality.STANDARD,
        style: Union[ImageStyle, str] = ImageStyle.VIVID
    ) -> ImageEditResponse:
        """
        Convenience method for simple image editing.
        
        Args:
            image: Base64 encoded image data
            prompt: Image editing prompt
            size: Image size (default: 1024x1024)
            model: Model to use (default: dall-e-3)
            quality: Image quality (default: standard)
            style: Image style (default: vivid)
            
        Returns:
            ImageEditResponse
        """
        request = ImageEditRequest(
            image=image,
            prompt=prompt,
            size=size,
            model=model,
            quality=quality,
            style=style
        )
        return self.edit_image(request)
