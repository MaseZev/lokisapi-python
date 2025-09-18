"""
Example of automatic model discovery and caching.
"""

from lokisapi import LokisApiClient, ChatMessage, ChatRole


def main():
    # Initialize client with automatic model discovery
    client = LokisApiClient("YOUR_API_KEY")
    
    print("=== Automatic Model Discovery Example ===\n")
    
    # Example 1: Get all models (automatically cached)
    print("1. All Available Models:")
    try:
        models = client.list_models()
        print(f"   Found {len(models)} models:")
        for model in models:
            print(f"   - {model.id} (owned by: {model.owned_by})")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 2: Get models by category
    print("2. Models by Category:")
    try:
        text_models = client.get_models_by_category("text")
        image_models = client.get_models_by_category("image")
        
        print(f"   Text models: {len(text_models)}")
        for model in text_models[:3]:  # Show first 3
            print(f"     - {model.id}")
        
        print(f"   Image models: {len(image_models)}")
        for model in image_models:
            print(f"     - {model.id}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 3: Get specific model types
    print("3. Specific Model Types:")
    try:
        thinking_models = client.get_thinking_models()
        image_models = client.get_image_models()
        text_models = client.get_text_models()
        
        print(f"   Thinking models: {thinking_models}")
        print(f"   Image models: {image_models}")
        print(f"   Text models: {len(text_models)} models")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 4: Cache information
    print("4. Cache Information:")
    try:
        cache_info = client.get_models_cache_info()
        if cache_info['cached']:
            print(f"   Models cached: Yes")
            print(f"   Cache age: {cache_info['age_seconds']:.0f} seconds")
            print(f"   Models count: {cache_info['models_count']}")
            print(f"   Expires in: {cache_info['expires_in_seconds']:.0f} seconds")
        else:
            print(f"   Models cached: No")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 5: Force refresh cache
    print("5. Force Refresh Cache:")
    try:
        print("   Refreshing models cache...")
        client.refresh_models_cache()
        print("   ✅ Cache refreshed successfully")
        
        # Check cache info again
        cache_info = client.get_models_cache_info()
        print(f"   New cache age: {cache_info['age_seconds']:.0f} seconds")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 6: Use a specific model
    print("6. Using Specific Model:")
    try:
        # Get a text model
        text_models = client.get_text_models()
        if text_models:
            model_id = text_models[0]  # Use first available text model
            print(f"   Using model: {model_id}")
            
            messages = [ChatMessage(ChatRole.USER, "Hello! What can you do?")]
            response = client.chat(messages, model=model_id)
            print(f"   Response: {response.choices[0]['message']['content'][:100]}...")
        else:
            print("   No text models available")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 7: Error handling for non-existent model
    print("7. Error Handling:")
    try:
        # Try to get a non-existent model
        model = client.get_model("non-existent-model")
        print(f"   Model found: {model.id}")
    except Exception as e:
        print(f"   Expected error: {type(e).__name__}: {e}")
    print()
    
    # Example 8: Clear cache
    print("8. Clear Cache:")
    try:
        client.clear_models_cache()
        print("   ✅ Cache cleared")
        
        cache_info = client.get_models_cache_info()
        print(f"   Cache status: {'Cached' if cache_info['cached'] else 'Not cached'}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    main()
