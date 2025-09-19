import time
import json
import os
import asyncio
import aiofiles
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .models import Model
from .exceptions import NetworkError, APIError, ModelNotFoundError


@dataclass
class ModelCache:
    models: List[Model]
    cached_at: float
    cache_duration: float = 3600


class AsyncModelManager:
    
    def __init__(self, client, cache_duration: float = 3600, cache_file: Optional[str] = None):
        self.client = client
        self.cache_duration = cache_duration
        self.cache_file = cache_file or os.path.join(os.path.expanduser("~"), ".lokisapi_models_cache.json")
        self._cache: Optional[ModelCache] = None
        self._lock = asyncio.Lock()
    
    async def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                async with aiofiles.open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.loads(await f.read())
                    models = [Model.from_dict(m) for m in data.get('models', [])]
                    cached_at = data.get('cached_at', 0)
                    self._cache = ModelCache(models=models, cached_at=cached_at, cache_duration=self.cache_duration)
            except Exception:
                self._cache = None
    
    async def _save_cache(self):
        if self._cache:
            try:
                data = {
                    'models': [model.to_dict() for model in self._cache.models],
                    'cached_at': self._cache.cached_at,
                    'cache_duration': self._cache.cache_duration
                }
                async with aiofiles.open(self.cache_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception:
                pass
    
    def _is_cache_valid(self) -> bool:
        if not self._cache:
            return False
        return time.time() - self._cache.cached_at < self._cache.cache_duration
    
    async def _fetch_models_from_api(self) -> List[Model]:
        try:
            response = await self.client._make_request('GET', 'models')
            data = await response.json()
            
            if not isinstance(data, dict) or "data" not in data:
                raise APIError("Invalid response format from /v1/models endpoint")
            
            models = [Model.from_dict(m) for m in data["data"]]
            
            for model in models:
                model.supports_text = True
                model.supports_thinking = False
                model.supports_images = False
                model.deprecated = False

                if "gemini-2.5" in model.id:
                    model.supports_thinking = True
                
                if "dall-e" in model.id:
                    model.supports_images = True
                    model.supports_text = False

                raw_model_data = next((item for item in data["data"] if item["id"] == model.id), None)
                if raw_model_data and raw_model_data.get("deprecated"):
                    model.deprecated = True

            return models
        except (NetworkError, APIError) as e:
            raise
        except Exception as e:
            raise APIError(f"Unexpected error fetching models: {e}")
    
    async def get_models(self, force_refresh: bool = False) -> List[Model]:
        async with self._lock:
            if self._cache is None:
                await self._load_cache()
            
            if force_refresh or not self._is_cache_valid():
                try:
                    models = await self._fetch_models_from_api()
                    self._cache = ModelCache(models=models, cached_at=time.time(), cache_duration=self.cache_duration)
                    await self._save_cache()
                except (NetworkError, APIError):
                    if self._cache:
                        pass
                    else:
                        raise
            
            return self._cache.models if self._cache else []
    
    async def get_model(self, model_id: str, force_refresh: bool = False) -> Model:
        models = await self.get_models(force_refresh)
        for model in models:
            if model.id == model_id:
                return model
        raise ModelNotFoundError(model_id)
    
    async def get_thinking_models(self, force_refresh: bool = False) -> List[str]:
        models = await self.get_models(force_refresh)
        return [m.id for m in models if m.supports_thinking]
    
    async def get_image_models(self, force_refresh: bool = False) -> List[str]:
        models = await self.get_models(force_refresh)
        return [m.id for m in models if m.supports_images]
    
    async def get_text_models(self, force_refresh: bool = False) -> List[str]:
        models = await self.get_models(force_refresh)
        return [m.id for m in models if m.supports_text]
    
    async def get_models_by_category(self, category: str, force_refresh: bool = False) -> List[Model]:
        all_models = await self.get_models(force_refresh)
        if category == "text":
            return [m for m in all_models if m.supports_text and not m.supports_images and not m.deprecated]
        elif category == "image":
            return [m for m in all_models if m.supports_images and not m.deprecated]
        elif category == "thinking":
            return [m for m in all_models if m.supports_thinking and not m.deprecated]
        elif category == "deprecated":
            return [m for m in all_models if m.deprecated]
        return []
    
    async def clear_cache(self):
        async with self._lock:
            self._cache = None
            if os.path.exists(self.cache_file):
                try:
                    os.remove(self.cache_file)
                except Exception:
                    pass
    
    async def get_cache_info(self) -> Dict[str, Any]:
        if self._cache is None:
            await self._load_cache()
            
        if not self._cache:
            return {
                "cached": False,
                "age_seconds": 0,
                "expires_in_seconds": 0,
                "models_count": 0
            }
        
        now = time.time()
        age = now - self._cache.cached_at
        expires_in = max(0, self._cache.cache_duration - age)
        
        return {
            "cached": True,
            "age_seconds": age,
            "expires_in_seconds": expires_in,
            "models_count": len(self._cache.models)
        }
