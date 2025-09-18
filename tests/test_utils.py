"""
Tests for LokisApi utilities.
"""

import pytest
import base64
import io
from unittest.mock import patch, mock_open
from lokisapi.utils import (
    encode_image_to_base64, encode_image_from_bytes, decode_base64_to_image,
    save_base64_image, resize_image_for_api, validate_image_size,
    estimate_tokens, format_model_info, get_supported_models,
    validate_api_key_format
)


class TestImageUtils:
    """Test cases for image utilities."""
    
    def test_encode_image_to_base64(self):
        """Test encoding image file to base64."""
        test_data = b"fake_image_data"
        
        with patch("builtins.open", mock_open(read_data=test_data)):
            result = encode_image_to_base64("test.jpg")
            
        expected = base64.b64encode(test_data).decode('utf-8')
        assert result == expected
    
    def test_encode_image_from_bytes(self):
        """Test encoding image bytes to base64."""
        test_data = b"fake_image_data"
        result = encode_image_from_bytes(test_data)
        
        expected = base64.b64encode(test_data).decode('utf-8')
        assert result == expected
    
    def test_decode_base64_to_image(self):
        """Test decoding base64 to PIL Image."""
        # Create a simple test image
        from PIL import Image
        test_image = Image.new('RGB', (10, 10), color='red')
        
        # Convert to base64
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        # Test with data URL prefix
        data_url = f"data:image/png;base64,{base64_data}"
        
        # Decode
        decoded_image = decode_base64_to_image(data_url)
        
        assert decoded_image.size == (10, 10)
        assert decoded_image.mode == 'RGBA'  # PIL converts to RGBA for PNG
    
    def test_save_base64_image(self):
        """Test saving base64 image to file."""
        test_data = b"fake_image_data"
        base64_data = base64.b64encode(test_data).decode('utf-8')
        
        with patch("builtins.open", mock_open()) as mock_file:
            save_base64_image(base64_data, "output.png")
            
        mock_file.assert_called_once_with("output.png", "wb")
    
    def test_validate_image_size_valid(self):
        """Test image size validation with valid sizes."""
        valid_sizes = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]
        
        for size in valid_sizes:
            assert validate_image_size(size) is True
    
    def test_validate_image_size_invalid(self):
        """Test image size validation with invalid sizes."""
        invalid_sizes = ["999x999", "2048x2048", "100x100", "invalid"]
        
        for size in invalid_sizes:
            assert validate_image_size(size) is False
    
    def test_validate_image_size_tuple(self):
        """Test image size validation with tuple input."""
        assert validate_image_size((1024, 1024)) is True
        assert validate_image_size((999, 999)) is False


class TestModelUtils:
    """Test cases for model utilities."""
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        # Test with different text lengths
        assert estimate_tokens("Hello") >= 1
        assert estimate_tokens("Hello, world!") >= 2
        assert estimate_tokens("A" * 100) >= 25  # Roughly 25 tokens for 100 chars
    
    def test_format_model_info_valid(self):
        """Test formatting model info for valid model."""
        info = format_model_info("gpt-5")
        
        assert "error" not in info
        assert info["id"] == "gpt-5"
        assert info["name"] == "GPT-5"
        assert info["provider"] == "OpenAI"
        assert info["supports_text"] is True
        assert info["supports_thinking"] is False
        assert info["supports_images"] is False
    
    def test_format_model_info_invalid(self):
        """Test formatting model info for invalid model."""
        info = format_model_info("invalid-model")
        
        assert "error" in info
        assert "not found" in info["error"]
    
    def test_get_supported_models_no_filter(self):
        """Test getting all supported models."""
        models = get_supported_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gpt-5" in models
        assert "gemini-2.5-pro" in models
        assert "dall-e-3" in models
    
    def test_get_supported_models_with_filter(self):
        """Test getting models filtered by category."""
        text_models = get_supported_models("text")
        image_models = get_supported_models("image")
        
        assert isinstance(text_models, list)
        assert isinstance(image_models, list)
        assert "gpt-5" in text_models
        assert "dall-e-3" in image_models
    
    def test_validate_api_key_format_valid(self):
        """Test API key format validation with valid keys."""
        valid_keys = [
            "sk-1234567890abcdef",
            "AIzaSy1234567890abcdef",
            "Bearer sk-1234567890abcdef"
        ]
        
        for key in valid_keys:
            assert validate_api_key_format(key) is True
    
    def test_validate_api_key_format_invalid(self):
        """Test API key format validation with invalid keys."""
        invalid_keys = [
            "",
            "short",
            "invalid-key",
            "1234567890"
        ]
        
        for key in invalid_keys:
            assert validate_api_key_format(key) is False


class TestImageProcessing:
    """Test cases for image processing utilities."""
    
    @patch('lokisapi.utils.Image.open')
    @patch('lokisapi.utils.Image.new')
    def test_resize_image_for_api(self, mock_new, mock_open):
        """Test resizing image for API."""
        # Mock PIL Image
        mock_image = mock_open.return_value.__enter__.return_value
        mock_image.mode = 'RGB'
        mock_image.size = (2000, 2000)  # Large image
        mock_image.convert.return_value = mock_image
        mock_image.thumbnail.return_value = None
        
        # Mock BytesIO
        with patch('lokisapi.utils.io.BytesIO') as mock_bytesio:
            mock_bytes = mock_bytesio.return_value
            mock_bytes.getvalue.return_value = b"resized_image_data"
            
            result = resize_image_for_api("large_image.jpg", (1024, 1024))
            
            # Verify image was resized
            mock_image.thumbnail.assert_called_once()
            assert result == base64.b64encode(b"resized_image_data").decode('utf-8')
    
    @patch('lokisapi.utils.Image.open')
    def test_resize_image_for_api_small_image(self, mock_open):
        """Test resizing small image (no resize needed)."""
        # Mock PIL Image
        mock_image = mock_open.return_value.__enter__.return_value
        mock_image.mode = 'RGB'
        mock_image.size = (500, 500)  # Small image
        mock_image.convert.return_value = mock_image
        
        # Mock BytesIO
        with patch('lokisapi.utils.io.BytesIO') as mock_bytesio:
            mock_bytes = mock_bytesio.return_value
            mock_bytes.getvalue.return_value = b"original_image_data"
            
            result = resize_image_for_api("small_image.jpg", (1024, 1024))
            
            # Verify image was not resized (thumbnail not called)
            mock_image.thumbnail.assert_not_called()
            assert result == base64.b64encode(b"original_image_data").decode('utf-8')


if __name__ == "__main__":
    pytest.main([__file__])
