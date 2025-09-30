import json
import aiohttp
import asyncio
from typing import List, Iterator, Optional, Dict, Any, Union, AsyncIterator
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
from .async_model_cache import AsyncModelManager
from .config import Settings


class AsyncLokisApiClient:
    
    def __init__(self, api_key: str, base_url: str = "https://lokisapi.online/v1", 
                 model_cache_duration: float = 3600,
                 timeout_seconds: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model_cache_duration = model_cache_duration
        self._timeout_seconds = timeout_seconds
        self._session: Optional[aiohttp.ClientSession] = None
        self._model_manager: Optional[AsyncModelManager] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            timeout = aiohttp.ClientTimeout(total=self._timeout_seconds)
            self._session = aiohttp.ClientSession(headers=headers, timeout=timeout)
            
            if self._model_manager is None:
                self._model_manager = AsyncModelManager(self, cache_duration=self.model_cache_duration)
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> aiohttp.ClientResponse:
        await self._ensure_session()
        url = urljoin(self.base_url + '/', endpoint)
        
        try:
            request_headers = None
            if stream:
                request_headers = {
                    'Accept': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            if method.upper() == 'GET':
                response = await self._session.get(url, headers=request_headers)
            elif method.upper() == 'POST':
                response = await self._session.post(url, json=data, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status == 401:
                error_details = await self._extract_error_details(response)
                raise AuthenticationError(
                    "Invalid API key or authentication failed",
                    details=error_details
                )
            elif response.status == 429:
                error_details = await self._extract_error_details(response)
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
            elif response.status == 503:
                error_details = await self._extract_error_details(response)
                retry_after = self._extract_retry_after(response)
                raise ServiceUnavailableError(
                    "Service temporarily unavailable",
                    retry_after=retry_after,
                    details=error_details
                )
            elif response.status >= 400:
                error_details = await self._extract_error_details(response)
                error_message = await self._extract_error_message(response)
                raise APIError(
                    error_message,
                    status_code=response.status,
                    response_data=error_details,
                    details=error_details
                )
            
            return response
            
        except aiohttp.ClientTimeout:
            raise NetworkError("Request timeout", timeout=self._timeout_seconds)
        except aiohttp.ClientConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network request failed: {str(e)}")

    @classmethod
    def from_settings(cls, settings: Settings, model_cache_duration: float = 3600) -> 'AsyncLokisApiClient':
        return cls(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model_cache_duration=model_cache_duration,
            timeout_seconds=settings.timeout_seconds,
        )

    @classmethod
    def from_env(cls, prefix: str = "LOKISAPI_", model_cache_duration: float = 3600) -> 'AsyncLokisApiClient':
        settings = Settings.from_env(prefix)
        return cls.from_settings(settings, model_cache_duration=model_cache_duration)
    
    async def _extract_error_details(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        try:
            return await response.json()
        except:
            return {"raw_response": await response.text()}
    
    async def _extract_error_message(self, response: aiohttp.ClientResponse) -> str:
        try:
            error_data = await response.json()
            if isinstance(error_data, dict):
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
            return f"HTTP {response.status}: {await response.text()}"
    
    def _extract_retry_after(self, response: aiohttp.ClientResponse) -> Optional[int]:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                pass
        return None
    
    def _extract_limit_type(self, response: aiohttp.ClientResponse) -> Optional[str]:
        try:
            error_message = str(response.headers).lower()
            
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
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        response = await self._make_request('POST', 'images/generations', request.to_dict())
        data = await response.json()
        return ImageGenerationResponse.from_dict(data)
    
    async def edit_image(self, request: ImageEditRequest) -> ImageEditResponse:
        response = await self._make_request('POST', 'images/edits', request.to_dict())
        data = await response.json()
        return ImageEditResponse.from_dict(data)
    
    async def create_chat_completion(
        self, 
        request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        response = await self._make_request('POST', 'chat/completions', request.to_dict())
        data = await response.json()
        return ChatCompletionResponse.from_dict(data)
    
    async def create_chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        if not request.stream:
            request.stream = True
        
        response = await self._make_request('POST', 'chat/completions', request.to_dict(), stream=True)
        
        async for line in response.content:
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data)
                        yield ChatCompletionChunk.from_dict(chunk_data)
                    except json.JSONDecodeError:
                        continue

    async def chat_stream_text(
        self,
        request: ChatCompletionRequest
    ) -> AsyncIterator[str]:
        """Yield only text content from streaming chat completion."""
        if not request.stream:
            request.stream = True
        response = await self._make_request('POST', 'chat/completions', request.to_dict(), stream=True)
        async for line in response.content:
            if not line:
                continue
            line = line.decode('utf-8')
            if not line.startswith('data: '):
                continue
            data = line[6:]
            if data.strip() == '[DONE]':
                break
            try:
                chunk_data = json.loads(data)
                choices = chunk_data.get('choices', [])
                if choices:
                    delta = choices[0].get('delta', {})
                    text = delta.get('content')
                    if text:
                        yield text
            except json.JSONDecodeError:
                continue
    
    async def list_models(self, force_refresh: bool = False) -> List[Model]:
        return await self._model_manager.get_models(force_refresh)
    
    async def get_model(self, model_id: str, force_refresh: bool = False) -> Model:
        return await self._model_manager.get_model(model_id, force_refresh)
    
    async def get_thinking_models(self, force_refresh: bool = False) -> List[str]:
        return await self._model_manager.get_thinking_models(force_refresh)
    
    async def get_image_models(self, force_refresh: bool = False) -> List[str]:
        return await self._model_manager.get_image_models(force_refresh)
    
    async def get_text_models(self, force_refresh: bool = False) -> List[str]:
        return await self._model_manager.get_text_models(force_refresh)
    
    async def get_models_by_category(self, category: str, force_refresh: bool = False) -> List[Model]:
        return await self._model_manager.get_models_by_category(category, force_refresh)
    
    async def refresh_models_cache(self):
        await self._model_manager.get_models(force_refresh=True)
    
    async def clear_models_cache(self):
        await self._model_manager.clear_cache()
    
    async def get_models_cache_info(self) -> Dict[str, Any]:
        return await self._model_manager.get_cache_info()
    
    async def chat(
        self, 
        messages: List[ChatMessage], 
        model: str = "gpt-5",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        thinking: bool = False,
        thinking_budget: int = 1000,
        reasoning_effort: Union[ReasoningEffort, str] = ReasoningEffort.MEDIUM
    ) -> Union[ChatCompletionResponse, AsyncIterator[ChatCompletionChunk]]:
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
            return await self.create_chat_completion(request)
    
    async def generate_image_simple(
        self, 
        prompt: str, 
        size: Union[ImageSize, str] = ImageSize.SIZE_1024,
        model: str = "dall-e-3",
        quality: Union[ImageQuality, str] = ImageQuality.STANDARD,
        style: Union[ImageStyle, str] = ImageStyle.VIVID
    ) -> ImageGenerationResponse:
        request = ImageGenerationRequest(
            prompt=prompt,
            size=size,
            model=model,
            quality=quality,
            style=style
        )
        return await self.generate_image(request)
    
    async def edit_image_simple(
        self, 
        image: str,
        prompt: str, 
        size: Union[ImageSize, str] = ImageSize.SIZE_1024,
        model: str = "dall-e-3",
        quality: Union[ImageQuality, str] = ImageQuality.STANDARD,
        style: Union[ImageStyle, str] = ImageStyle.VIVID
    ) -> ImageEditResponse:
        request = ImageEditRequest(
            image=image,
            prompt=prompt,
            size=size,
            model=model,
            quality=quality,
            style=style
        )
        return await self.edit_image(request)
