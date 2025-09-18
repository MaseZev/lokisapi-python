# Changelog

## [1.0.0] - 2024-01-XX

### Added
- **Automatic Model Discovery**: Models are now automatically fetched from API and cached
- **Enhanced Error Handling**: Detailed error types for different scenarios
- **Model Caching**: Intelligent caching system with configurable duration
- **Advanced Rate Limiting**: Specific error types for different limit scenarios
- **Image Editing Support**: Full support for DALL-E image editing
- **Thinking Mode**: Support for Gemini 2.5 Thinking feature
- **Reasoning Effort**: Support for GPT-5 Reasoning Effort levels
- **Model Categories**: Automatic categorization of models (text, image, deprecated)
- **Cache Management**: Methods to refresh, clear, and inspect model cache

### Enhanced
- **Error Messages**: More descriptive error messages with context
- **Model Information**: Automatic detection of model capabilities
- **Network Handling**: Better timeout and connection error handling
- **API Compatibility**: Full compatibility with LokisApi endpoints

### New Exception Types
- `ModelNotFoundError`: When requested model doesn't exist
- `ModelNotSupportedError`: When model doesn't support requested feature
- `QuotaExceededError`: When quota limits are exceeded
- `TokenLimitError`: When token limits are exceeded
- `RequestLimitError`: When request limits are exceeded
- `ServiceUnavailableError`: When service is temporarily down
- `ImageProcessingError`: When image processing fails

### New Client Methods
- `get_thinking_models()`: Get models that support thinking
- `get_image_models()`: Get models that support image generation/editing
- `get_text_models()`: Get models that support text generation
- `get_models_by_category()`: Get models filtered by category
- `refresh_models_cache()`: Force refresh model cache
- `clear_models_cache()`: Clear model cache
- `get_models_cache_info()`: Get cache information

### Model Management
- Automatic model discovery from API
- Intelligent caching with file persistence
- Fallback to cached models when API is unavailable
- Configurable cache duration (default: 1 hour)
- Automatic model capability detection

### Error Handling Improvements
- Detailed error context and metadata
- Automatic retry-after header parsing
- Limit type detection (RPM, TPM, RPD, etc.)
- Network timeout handling
- Connection error handling
- Service availability detection

### Backward Compatibility
- All existing methods remain unchanged
- Default behavior preserved
- Optional parameters for new features
- Graceful fallback to static model config

### Performance
- Reduced API calls through intelligent caching
- Faster model lookups
- Persistent cache across sessions
- Automatic cache invalidation
