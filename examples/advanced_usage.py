"""
Advanced usage examples for LokisApi Python library.
"""

import asyncio
import time
from typing import List
from lokisapi import (
    LokisApiClient, ChatMessage, ChatRole, ImageGenerationRequest, 
    ImageSize, ChatCompletionRequest
)


class AdvancedLokisApiClient(LokisApiClient):
    """Extended client with additional functionality."""
    
    def chat_with_context(
        self, 
        conversation_history: List[ChatMessage], 
        new_message: str,
        model: str = "gpt-5",
        max_context_length: int = 10
    ) -> str:
        """
        Chat with conversation context management.
        
        Args:
            conversation_history: Previous conversation messages
            new_message: New user message
            model: Model to use
            max_context_length: Maximum number of messages to keep in context
            
        Returns:
            Assistant's response
        """
        # Add new user message
        conversation_history.append(ChatMessage(ChatRole.USER, new_message))
        
        # Keep only recent messages if context is too long
        if len(conversation_history) > max_context_length:
            conversation_history = conversation_history[-max_context_length:]
        
        # Get response
        response = self.chat(conversation_history, model=model)
        assistant_message = response.choices[0]['message']['content']
        
        # Add assistant response to history
        conversation_history.append(ChatMessage(ChatRole.ASSISTANT, assistant_message))
        
        return assistant_message
    
    def generate_multiple_images(
        self, 
        prompts: List[str], 
        size: str = "1024x1024",
        model: str = "dall-e-3"
    ) -> List[dict]:
        """
        Generate multiple images from different prompts.
        
        Args:
            prompts: List of image generation prompts
            size: Image size
            model: Model to use
            
        Returns:
            List of image data dictionaries
        """
        results = []
        for i, prompt in enumerate(prompts):
            print(f"Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
            try:
                response = self.generate_image_simple(prompt, size, model)
                results.extend(response.data)
                # Add delay to respect rate limits
                time.sleep(1)
            except Exception as e:
                print(f"Error generating image {i+1}: {e}")
                results.append({"error": str(e)})
        return results
    
    def chat_with_streaming_and_save(
        self, 
        messages: List[ChatMessage], 
        model: str = "gpt-5",
        filename: str = "chat_output.txt"
    ) -> str:
        """
        Chat with streaming response and save to file.
        
        Args:
            messages: Chat messages
            model: Model to use
            filename: Output filename
            
        Returns:
            Complete response text
        """
        full_response = ""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== Chat Conversation ===\n\n")
            
            # Write input messages
            for msg in messages:
                f.write(f"{msg.role.value}: {msg.content}\n")
            f.write(f"\n{model} response:\n")
            
            # Stream response
            for chunk in self.chat(messages, model=model, stream=True):
                if chunk.choices[0].get('delta', {}).get('content'):
                    content = chunk.choices[0]['delta']['content']
                    full_response += content
                    f.write(content)
                    f.flush()  # Ensure content is written immediately
        
        return full_response


def demonstrate_conversation_context():
    """Demonstrate conversation with context management."""
    print("=== Conversation with Context Management ===")
    
    client = AdvancedLokisApiClient("YOUR_API_KEY")
    conversation = []
    
    # Start conversation
    response1 = client.chat_with_context(
        conversation, 
        "Привет! Меня зовут Алексей. Расскажи мне о себе."
    )
    print(f"Assistant: {response1}\n")
    
    # Continue conversation with context
    response2 = client.chat_with_context(
        conversation, 
        "А что ты можешь делать?"
    )
    print(f"Assistant: {response2}\n")
    
    # Use context from previous messages
    response3 = client.chat_with_context(
        conversation, 
        "Как дела, Алексей?"
    )
    print(f"Assistant: {response3}\n")


def demonstrate_batch_image_generation():
    """Demonstrate batch image generation."""
    print("=== Batch Image Generation ===")
    
    client = AdvancedLokisApiClient("YOUR_API_KEY")
    
    prompts = [
        "A serene mountain landscape at sunrise",
        "A bustling city street at night",
        "A peaceful garden with blooming flowers",
        "A futuristic space station",
        "A cozy cabin in the woods"
    ]
    
    results = client.generate_multiple_images(prompts)
    
    print(f"\nGenerated {len(results)} images:")
    for i, result in enumerate(results):
        if 'error' in result:
            print(f"  Image {i+1}: Error - {result['error']}")
        else:
            print(f"  Image {i+1}: {result.get('url', 'No URL')}")


def demonstrate_streaming_with_save():
    """Demonstrate streaming chat with file output."""
    print("=== Streaming Chat with File Output ===")
    
    client = AdvancedLokisApiClient("YOUR_API_KEY")
    
    messages = [
        ChatMessage(ChatRole.SYSTEM, "Ты - творческий писатель."),
        ChatMessage(ChatRole.USER, "Напиши короткий рассказ о роботе, который мечтает стать художником.")
    ]
    
    response = client.chat_with_streaming_and_save(
        messages, 
        model="gpt-5",
        filename="robot_story.txt"
    )
    
    print(f"Story saved to 'robot_story.txt'")
    print(f"Response length: {len(response)} characters")


def demonstrate_error_handling():
    """Demonstrate proper error handling."""
    print("=== Error Handling Examples ===")
    
    # Test with invalid API key
    try:
        client = LokisApiClient("invalid-key")
        models = client.list_models()
    except Exception as e:
        print(f"Expected error with invalid key: {type(e).__name__}: {e}")
    
    # Test with invalid model
    try:
        client = LokisApiClient("YOUR_API_KEY")
        messages = [ChatMessage(ChatRole.USER, "Hello")]
        response = client.chat(messages, model="invalid-model")
    except Exception as e:
        print(f"Expected error with invalid model: {type(e).__name__}: {e}")
    
    # Test with invalid image prompt
    try:
        client = LokisApiClient("YOUR_API_KEY")
        response = client.generate_image_simple("", size="1024x1024")
    except Exception as e:
        print(f"Expected error with empty prompt: {type(e).__name__}: {e}")


def main():
    """Run all advanced examples."""
    print("=== Advanced LokisApi Examples ===\n")
    
    # Uncomment the examples you want to run:
    
    # demonstrate_conversation_context()
    # demonstrate_batch_image_generation()
    # demonstrate_streaming_with_save()
    # demonstrate_error_handling()
    
    print("To run examples, uncomment the desired functions in main()")
    print("Make sure to replace 'YOUR_API_KEY' with your actual API key")


if __name__ == "__main__":
    main()
