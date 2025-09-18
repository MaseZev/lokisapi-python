"""
Model caching and automatic model discovery for LokisApi.
"""

import time
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .models import Model
from .exceptions import NetworkError, APIError, ModelNotFoundError


@dataclass
class ModelCache:
    """Cache for models with metadata."""
    models: List[Model]
    cached_at: float
    cache_duration: float = 3600  # 1 hour default cache


class ModelManager:
    """Manages model discovery and caching."""
    
    def __init__(self, client, cache_duration: float = 3600, cache_file: Optional[str] = None):
        """
        Initialize model manager.
        
        Args:
            client: LokisApiClient instance
            cache_duration: Cache duration in seconds (default: 1 hour)
            cache_file: Optional file path for persistent cache
        """
        self.client = client
        self.cache_duration = cache_duration
        self.cache_file = cache_file or os.path.join(os.path.expanduser("~"), ".lokisapi_models_cache.json")
        self._cache: Optional[ModelCache] = None
    
    def get_models(self, force_refresh: bool = False) -> List[Model]:
        """
        Get models from cache or API.
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            List of available models
        """
        # Check if we need to refresh cache
        if force_refresh or self._should_refresh_cache():
            try:
                self._refresh_cache()
            except Exception as e:
                # If API fails, try to use cached models
                if self._cache and self._cache.models:
                    print(f"Warning: Failed to refresh models from API ({e}), using cached models")
                    return self._cache.models
                else:
                    # If no cache available, raise the error
                    raise
        
        return self._cache.models if self._cache else []
    
    def get_model(self, model_id: str, force_refresh: bool = False) -> Model:
        """
        Get specific model by ID.
        
        Args:
            model_id: Model identifier
            force_refresh: Force refresh from API
            
        Returns:
            Model instance
            
        Raises:
            ModelNotFoundError: If model is not found
        """
        models = self.get_models(force_refresh)
        
        for model in models:
            if model.id == model_id:
                return model
        
        raise ModelNotFoundError(model_id)
    
    def get_models_by_category(self, category: str, force_refresh: bool = False) -> List[Model]:
        """
        Get models filtered by category.
        
        Args:
            category: Model category ('text', 'image', 'deprecated')
            force_refresh: Force refresh from API
            
        Returns:
            List of models in category
        """
        models = self.get_models(force_refresh)
        return [model for model in models if self._get_model_category(model.id) == category]
    
    def get_thinking_models(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of models that support thinking.
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            List of model IDs that support thinking
        """
        models = self.get_models(force_refresh)
        thinking_models = []
        
        for model in models:
            if self._supports_thinking(model.id):
                thinking_models.append(model.id)
        
        return thinking_models
    
    def get_image_models(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of models that support image generation/editing.
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            List of model IDs that support images
        """
        models = self.get_models(force_refresh)
        image_models = []
        
        for model in models:
            if self._supports_images(model.id):
                image_models.append(model.id)
        
        return image_models
    
    def get_text_models(self, force_refresh: bool = False) -> List[str]:
        """
        Get list of models that support text generation.
        
        Args:
            force_refresh: Force refresh from API
            
        Returns:
            List of model IDs that support text
        """
        models = self.get_models(force_refresh)
        text_models = []
        
        for model in models:
            if self._supports_text(model.id):
                text_models.append(model.id)
        
        return text_models
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed."""
        if not self._cache:
            return True
        
        return time.time() - self._cache.cached_at > self._cache.cache_duration
    
    def _refresh_cache(self):
        """Refresh cache from API."""
        try:
            # Try to get models from API
            models_data = self.client._make_request('GET', 'models')
            models_response = models_data.json()
            
            # Parse models
            models = []
            for model_data in models_response.get('data', []):
                model = Model.from_dict(model_data)
                models.append(model)
            
            # Update cache
            self._cache = ModelCache(
                models=models,
                cached_at=time.time(),
                cache_duration=self.cache_duration
            )
            
            # Save to file
            self._save_cache_to_file()
            
        except Exception as e:
            # Try to load from file if API fails
            if self._load_cache_from_file():
                return
            
            # If both API and file fail, raise error
            raise NetworkError(f"Failed to fetch models from API: {e}")
    
    def _save_cache_to_file(self):
        """Save cache to file."""
        if not self._cache:
            return
        
        try:
            cache_data = {
                'models': [
                    {
                        'id': model.id,
                        'object': model.object,
                        'created': model.created,
                        'owned_by': model.owned_by
                    }
                    for model in self._cache.models
                ],
                'cached_at': self._cache.cached_at,
                'cache_duration': self._cache.cache_duration
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to save models cache to file: {e}")
    
    def _load_cache_from_file(self) -> bool:
        """Load cache from file."""
        try:
            if not os.path.exists(self.cache_file):
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cached_at = cache_data.get('cached_at', 0)
            cache_duration = cache_data.get('cache_duration', self.cache_duration)
            
            if time.time() - cached_at > cache_duration:
                return False
            
            # Load models
            models = []
            for model_data in cache_data.get('models', []):
                model = Model.from_dict(model_data)
                models.append(model)
            
            self._cache = ModelCache(
                models=models,
                cached_at=cached_at,
                cache_duration=cache_duration
            )
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to load models cache from file: {e}")
            return False
    
    def _get_model_category(self, model_id: str) -> str:
        """Determine model category based on model ID."""
        if model_id.startswith('gemini'):
            if 'deprecated' in model_id or model_id in ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro']:
                return 'deprecated'
            return 'text'
        elif model_id.startswith('gpt') or model_id.startswith('o1') or model_id.startswith('o3'):
            return 'text'
        elif model_id.startswith('dall-e'):
            return 'image'
        else:
            return 'unknown'
    
    def _supports_thinking(self, model_id: str) -> bool:
        """Check if model supports thinking."""
        thinking_models = [
            'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite'
        ]
        return model_id in thinking_models
    
    def _supports_images(self, model_id: str) -> bool:
        """Check if model supports image generation/editing."""
        image_models = ['dall-e-3']
        return model_id in image_models
    
    def _supports_text(self, model_id: str) -> bool:
        """Check if model supports text generation."""
        # All models except pure image models support text
        return not self._supports_images(model_id) or model_id in ['gpt-4o', 'gpt-4o-mini']
    
    def clear_cache(self):
        """Clear the model cache."""
        self._cache = None
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except Exception as e:
            print(f"Warning: Failed to remove cache file: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache."""
        if not self._cache:
            return {'cached': False}
        
        return {
            'cached': True,
            'cached_at': self._cache.cached_at,
            'cache_duration': self._cache.cache_duration,
            'models_count': len(self._cache.models),
            'age_seconds': time.time() - self._cache.cached_at,
            'expires_in_seconds': self._cache.cache_duration - (time.time() - self._cache.cached_at)
        }
