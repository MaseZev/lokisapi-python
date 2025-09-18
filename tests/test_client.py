"""
Tests for LokisApi client.
"""

import pytest
from unittest.mock import Mock, patch
from lokisapi import (
    LokisApiClient, ChatMessage, ChatRole, ImageGenerationRequest,
    ImageEditRequest, ImageSize, ImageQuality, ImageStyle,
    ReasoningEffort, AuthenticationError, RateLimitError, APIError
)


class TestLokisApiClient:
    """Test cases for LokisApiClient."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = LokisApiClient("test-api-key")
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.api_key == "test-api-key"
        assert self.client.base_url == "https://lokisapi.online/v1"
        assert "Authorization" in self.client.session.headers
        assert self.client.session.headers["Authorization"] == "Bearer test-api-key"
    
    def test_client_initialization_custom_url(self):
        """Test client initialization with custom URL."""
        client = LokisApiClient("test-api-key", "https://custom.api.com/v1")
        assert client.base_url == "https://custom.api.com/v1"
    
    @patch('lokisapi.client.requests.Session.post')
    def test_generate_image_success(self, mock_post):
        """Test successful image generation."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "img-123",
            "object": "list",
            "created": 1234567890,
            "model": "dall-e-3",
            "data": [{"url": "https://example.com/image.png"}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test request
        request = ImageGenerationRequest(
            prompt="A beautiful sunset",
            size=ImageSize.SIZE_1024,
            quality=ImageQuality.HD,
            style=ImageStyle.VIVID
        )
        
        response = self.client.generate_image(request)
        
        assert response.id == "img-123"
        assert response.model == "dall-e-3"
        assert len(response.data) == 1
        assert response.data[0]["url"] == "https://example.com/image.png"
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://lokisapi.online/v1/images/generations"
        assert call_args[1]["json"]["prompt"] == "A beautiful sunset"
        assert call_args[1]["json"]["size"] == "1024x1024"
        assert call_args[1]["json"]["quality"] == "hd"
        assert call_args[1]["json"]["style"] == "vivid"
    
    @patch('lokisapi.client.requests.Session.post')
    def test_edit_image_success(self, mock_post):
        """Test successful image editing."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "img-edit-123",
            "object": "list",
            "created": 1234567890,
            "model": "dall-e-3",
            "data": [{"url": "https://example.com/edited.png"}]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test request
        request = ImageEditRequest(
            image="base64_image_data",
            prompt="Add a rainbow",
            size=ImageSize.SIZE_1024
        )
        
        response = self.client.edit_image(request)
        
        assert response.id == "img-edit-123"
        assert response.model == "dall-e-3"
        assert len(response.data) == 1
        assert response.data[0]["url"] == "https://example.com/edited.png"
    
    @patch('lokisapi.client.requests.Session.post')
    def test_chat_completion_success(self, mock_post):
        """Test successful chat completion."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-5",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test request
        messages = [ChatMessage(ChatRole.USER, "Hello")]
        response = self.client.create_chat_completion(
            ChatCompletionRequest(messages=messages, model="gpt-5")
        )
        
        assert response.id == "chatcmpl-123"
        assert response.model == "gpt-5"
        assert len(response.choices) == 1
        assert response.choices[0]["message"]["content"] == "Hello!"
    
    @patch('lokisapi.client.requests.Session.post')
    def test_chat_with_thinking(self, mock_post):
        """Test chat completion with thinking enabled."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gemini-2.5-pro",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Thinking response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test request with thinking
        messages = [ChatMessage(ChatRole.USER, "Solve this math problem")]
        request = ChatCompletionRequest(
            messages=messages,
            model="gemini-2.5-pro",
            thinking=True,
            thinking_budget=2000
        )
        
        response = self.client.create_chat_completion(request)
        
        assert response.choices[0]["message"]["content"] == "Thinking response"
        
        # Verify thinking parameters were sent
        call_args = mock_post.call_args
        assert call_args[1]["json"]["thinking"] is True
        assert call_args[1]["json"]["thinking_budget"] == 2000
    
    @patch('lokisapi.client.requests.Session.post')
    def test_chat_with_reasoning_effort(self, mock_post):
        """Test chat completion with reasoning effort."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-5",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Reasoning response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Test request with reasoning effort
        messages = [ChatMessage(ChatRole.USER, "Explain quantum physics")]
        request = ChatCompletionRequest(
            messages=messages,
            model="gpt-5",
            reasoning_effort=ReasoningEffort.HIGH
        )
        
        response = self.client.create_chat_completion(request)
        
        assert response.choices[0]["message"]["content"] == "Reasoning response"
        
        # Verify reasoning effort was sent
        call_args = mock_post.call_args
        assert call_args[1]["json"]["reasoning_effort"] == "high"
    
    @patch('lokisapi.client.requests.Session.get')
    def test_list_models_success(self, mock_get):
        """Test successful model listing."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "object": "list",
            "data": [
                {
                    "id": "gpt-5",
                    "object": "model",
                    "created": 1234567890,
                    "owned_by": "OpenAI"
                },
                {
                    "id": "gemini-2.5-pro",
                    "object": "model", 
                    "created": 1234567890,
                    "owned_by": "Google"
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        models = self.client.list_models()
        
        assert len(models) == 2
        assert models[0].id == "gpt-5"
        assert models[0].owned_by == "OpenAI"
        assert models[1].id == "gemini-2.5-pro"
        assert models[1].owned_by == "Google"
    
    @patch('lokisapi.client.requests.Session.post')
    def test_authentication_error(self, mock_post):
        """Test authentication error handling."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        request = ImageGenerationRequest(prompt="Test")
        
        with pytest.raises(AuthenticationError):
            self.client.generate_image(request)
    
    @patch('lokisapi.client.requests.Session.post')
    def test_rate_limit_error(self, mock_post):
        """Test rate limit error handling."""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        request = ImageGenerationRequest(prompt="Test")
        
        with pytest.raises(RateLimitError):
            self.client.generate_image(request)
    
    @patch('lokisapi.client.requests.Session.post')
    def test_api_error(self, mock_post):
        """Test API error handling."""
        # Mock 400 response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_post.return_value = mock_response
        
        request = ImageGenerationRequest(prompt="Test")
        
        with pytest.raises(APIError) as exc_info:
            self.client.generate_image(request)
        
        assert exc_info.value.status_code == 400
        assert "Bad request" in str(exc_info.value)
    
    def test_generate_image_simple(self):
        """Test simple image generation method."""
        with patch.object(self.client, 'generate_image') as mock_generate:
            mock_response = Mock()
            mock_response.data = [{"url": "https://example.com/image.png"}]
            mock_generate.return_value = mock_response
            
            response = self.client.generate_image_simple(
                prompt="Test prompt",
                size=ImageSize.SIZE_1024,
                quality=ImageQuality.HD,
                style=ImageStyle.VIVID
            )
            
            assert response.data[0]["url"] == "https://example.com/image.png"
            mock_generate.assert_called_once()
    
    def test_edit_image_simple(self):
        """Test simple image editing method."""
        with patch.object(self.client, 'edit_image') as mock_edit:
            mock_response = Mock()
            mock_response.data = [{"url": "https://example.com/edited.png"}]
            mock_edit.return_value = mock_response
            
            response = self.client.edit_image_simple(
                image="base64_data",
                prompt="Edit prompt",
                size=ImageSize.SIZE_1024
            )
            
            assert response.data[0]["url"] == "https://example.com/edited.png"
            mock_edit.assert_called_once()
    
    def test_chat_convenience_method(self):
        """Test chat convenience method."""
        with patch.object(self.client, 'create_chat_completion') as mock_chat:
            mock_response = Mock()
            mock_response.choices = [{"message": {"content": "Hello!"}}]
            mock_chat.return_value = mock_response
            
            messages = [ChatMessage(ChatRole.USER, "Hello")]
            response = self.client.chat(
                messages=messages,
                model="gpt-5",
                thinking=True,
                reasoning_effort=ReasoningEffort.HIGH
            )
            
            assert response.choices[0]["message"]["content"] == "Hello!"
            mock_chat.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
