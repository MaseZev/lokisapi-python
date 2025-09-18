"""
Basic usage examples for LokisApi Python library.
"""

from lokisapi import (
    LokisApiClient, ChatMessage, ChatRole, ImageGenerationRequest, ImageEditRequest,
    ImageSize, ImageQuality, ImageStyle, ReasoningEffort, THINKING_MODELS,
    encode_image_to_base64, estimate_tokens, format_model_info
)


def main():
    # Initialize the client with your API key
    client = LokisApiClient("YOUR_API_KEY")
    
    print("=== LokisApi Python Library Examples ===\n")
    
    # Example 1: List available models
    print("1. Available Models:")
    try:
        models = client.list_models()
        for model in models:
            print(f"   - {model.id} (owned by: {model.owned_by})")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 2: Simple chat completion
    print("2. Simple Chat Completion:")
    try:
        messages = [
            ChatMessage(ChatRole.USER, "Привет! Как дела?")
        ]
        response = client.chat(messages, model="gpt-5")
        print(f"   Response: {response.choices[0]['message']['content']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 3: Streaming chat completion
    print("3. Streaming Chat Completion:")
    try:
        messages = [
            ChatMessage(ChatRole.USER, "Расскажи короткую историю о коте")
        ]
        print("   Streaming response: ", end="")
        for chunk in client.chat(messages, model="gpt-5", stream=True):
            if chunk.choices[0].get('delta', {}).get('content'):
                print(chunk.choices[0]['delta']['content'], end="")
        print("\n")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 4: Image generation
    print("4. Image Generation:")
    try:
        response = client.generate_image_simple(
            prompt="A beautiful sunset over mountains",
            size=ImageSize.SIZE_1024,
            quality=ImageQuality.HD,
            style=ImageStyle.VIVID
        )
        print(f"   Generated {len(response.data)} image(s)")
        for i, image_data in enumerate(response.data):
            print(f"   Image {i+1}: {image_data.get('url', 'No URL available')}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 4.5: Image editing (if you have an image file)
    print("4.5. Image Editing:")
    try:
        # This example assumes you have an image file
        # image_base64 = encode_image_to_base64("path/to/your/image.jpg")
        # response = client.edit_image_simple(
        #     image=image_base64,
        #     prompt="Add a rainbow to the sky",
        #     size=ImageSize.SIZE_1024
        # )
        # print(f"   Edited {len(response.data)} image(s)")
        print("   (Skipped - requires an actual image file)")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 5: Advanced chat with system message
    print("5. Advanced Chat with System Message:")
    try:
        messages = [
            ChatMessage(ChatRole.SYSTEM, "Ты - полезный ассистент, который отвечает на русском языке."),
            ChatMessage(ChatRole.USER, "Объясни, что такое искусственный интеллект простыми словами.")
        ]
        response = client.chat(messages, model="gpt-5", temperature=0.7)
        print(f"   Response: {response.choices[0]['message']['content']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 6: Advanced chat with Thinking (Gemini 2.5)
    print("6. Advanced Chat with Thinking (Gemini 2.5):")
    try:
        messages = [
            ChatMessage(ChatRole.USER, "Реши эту математическую задачу: Если у меня есть 15 яблок и я съедаю 3 каждый день, сколько дней мне хватит?")
        ]
        response = client.chat(
            messages, 
            model="gemini-2.5-pro",
            thinking=True,
            thinking_budget=2000
        )
        print(f"   Response: {response.choices[0]['message']['content']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 7: Advanced chat with Reasoning Effort (GPT-5)
    print("7. Advanced Chat with Reasoning Effort (GPT-5):")
    try:
        messages = [
            ChatMessage(ChatRole.USER, "Объясни квантовую физику простыми словами")
        ]
        response = client.chat(
            messages, 
            model="gpt-5",
            reasoning_effort=ReasoningEffort.HIGH
        )
        print(f"   Response: {response.choices[0]['message']['content']}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 8: Model information
    print("8. Model Information:")
    try:
        model_info = format_model_info("gpt-5")
        print(f"   GPT-5 info: {model_info}")
        
        print(f"   Models supporting Thinking: {THINKING_MODELS}")
        print(f"   Estimated tokens for 'Hello world': {estimate_tokens('Hello world')}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 9: Advanced Image Generation
    print("9. Advanced Image Generation:")
    try:
        request = ImageGenerationRequest(
            prompt="A futuristic city with flying cars and neon lights",
            model="dall-e-3",
            size=ImageSize.SIZE_1024,
            quality=ImageQuality.HD,
            style=ImageStyle.VIVID
        )
        response = client.generate_image(request)
        print(f"   Generated {len(response.data)} image(s)")
        for i, image_data in enumerate(response.data):
            print(f"   Image {i+1}: {image_data.get('url', 'No URL available')}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    main()
