"""
Image processing examples for LokisApi Python library.
"""

import os
from lokisapi import (
    LokisApiClient, ImageGenerationRequest, ImageEditRequest,
    ImageSize, ImageQuality, ImageStyle,
    encode_image_to_base64, decode_base64_to_image, save_base64_image,
    resize_image_for_api, validate_image_size
)


def main():
    # Initialize the client
    client = LokisApiClient("YOUR_API_KEY")
    
    print("=== LokisApi Image Processing Examples ===\n")
    
    # Example 1: Generate multiple images with different styles
    print("1. Generate Multiple Images with Different Styles:")
    try:
        prompts = [
            "A serene mountain landscape at sunrise",
            "A bustling city street at night",
            "A peaceful garden with blooming flowers"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"   Generating image {i}: {prompt}")
            response = client.generate_image_simple(
                prompt=prompt,
                size=ImageSize.SIZE_1024,
                quality=ImageQuality.HD,
                style=ImageStyle.VIVID
            )
            
            if response.data:
                image_url = response.data[0].get('url', 'No URL')
                print(f"   ✅ Image {i} generated: {image_url}")
            else:
                print(f"   ❌ Failed to generate image {i}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 2: Generate images with different sizes
    print("2. Generate Images with Different Sizes:")
    try:
        sizes = [ImageSize.SIZE_256, ImageSize.SIZE_512, ImageSize.SIZE_1024]
        
        for size in sizes:
            print(f"   Generating image with size {size.value}")
            response = client.generate_image_simple(
                prompt="A minimalist abstract art piece",
                size=size,
                quality=ImageQuality.STANDARD,
                style=ImageStyle.NATURAL
            )
            
            if response.data:
                image_url = response.data[0].get('url', 'No URL')
                print(f"   ✅ {size.value} image generated: {image_url}")
            else:
                print(f"   ❌ Failed to generate {size.value} image")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 3: Image editing workflow (if you have an image file)
    print("3. Image Editing Workflow:")
    try:
        # This example shows how to edit an image if you have one
        image_path = "sample_image.jpg"  # Replace with actual image path
        
        if os.path.exists(image_path):
            print(f"   Processing image: {image_path}")
            
            # Encode image to base64
            image_base64 = encode_image_to_base64(image_path)
            print(f"   ✅ Image encoded to base64 ({len(image_base64)} characters)")
            
            # Resize image for API if needed
            resized_base64 = resize_image_for_api(image_path, (1024, 1024))
            print(f"   ✅ Image resized for API ({len(resized_base64)} characters)")
            
            # Edit the image
            edit_response = client.edit_image_simple(
                image=resized_base64,
                prompt="Add a beautiful sunset in the background",
                size=ImageSize.SIZE_1024,
                quality=ImageQuality.HD,
                style=ImageStyle.VIVID
            )
            
            if edit_response.data:
                edited_url = edit_response.data[0].get('url', 'No URL')
                print(f"   ✅ Image edited successfully: {edited_url}")
                
                # Save the edited image locally
                if edited_url.startswith('data:image'):
                    # Extract base64 from data URL
                    base64_data = edited_url.split(',', 1)[1]
                    save_base64_image(base64_data, "edited_image.png")
                    print(f"   ✅ Edited image saved as edited_image.png")
            else:
                print(f"   ❌ Failed to edit image")
        else:
            print(f"   ⚠️ Image file {image_path} not found. Skipping editing example.")
            print(f"   💡 To test image editing, place an image file named 'sample_image.jpg' in this directory.")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 4: Batch image generation with error handling
    print("4. Batch Image Generation with Error Handling:")
    try:
        batch_prompts = [
            "A futuristic robot",
            "A magical forest",
            "A space station",
            "A underwater city",
            "A desert oasis"
        ]
        
        successful_generations = 0
        failed_generations = 0
        
        for i, prompt in enumerate(batch_prompts, 1):
            try:
                print(f"   Generating batch image {i}/{len(batch_prompts)}: {prompt}")
                response = client.generate_image_simple(
                    prompt=prompt,
                    size=ImageSize.SIZE_512,
                    quality=ImageQuality.STANDARD,
                    style=ImageStyle.VIVID
                )
                
                if response.data and response.data[0].get('url'):
                    successful_generations += 1
                    print(f"   ✅ Batch image {i} generated successfully")
                else:
                    failed_generations += 1
                    print(f"   ❌ Batch image {i} failed - no data returned")
                    
            except Exception as batch_error:
                failed_generations += 1
                print(f"   ❌ Batch image {i} failed: {batch_error}")
        
        print(f"   📊 Batch generation complete: {successful_generations} successful, {failed_generations} failed")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 5: Image size validation
    print("5. Image Size Validation:")
    try:
        test_sizes = ["1024x1024", "512x512", "999x999", "2048x2048"]
        
        for size in test_sizes:
            is_valid = validate_image_size(size)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"   {size}: {status}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 6: Advanced image generation with custom parameters
    print("6. Advanced Image Generation with Custom Parameters:")
    try:
        request = ImageGenerationRequest(
            prompt="A cyberpunk cityscape with neon lights and flying cars, highly detailed, cinematic lighting",
            model="dall-e-3",
            n=2,  # Generate 2 images
            size=ImageSize.SIZE_1024,
            quality=ImageQuality.HD,
            style=ImageStyle.VIVID
        )
        
        response = client.generate_image(request)
        
        print(f"   Generated {len(response.data)} images:")
        for i, image_data in enumerate(response.data, 1):
            url = image_data.get('url', 'No URL')
            revised_prompt = image_data.get('revised_prompt', 'No revised prompt')
            print(f"   Image {i}: {url}")
            print(f"   Revised prompt: {revised_prompt}")
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    main()
