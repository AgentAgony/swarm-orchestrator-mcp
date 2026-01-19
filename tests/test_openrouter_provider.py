"""
Unit tests for OpenRouter provider.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_core.providers.openrouter import (
    call_openrouter,
    call_openrouter_json,
    RateLimiter,
    FREE_MODELS
)


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_can_request_initially(self):
        """Should allow requests initially."""
        limiter = RateLimiter(requests_per_minute=20, requests_per_day=200)
        can_request, error = limiter.can_request()
        assert can_request is True
        assert error is None
    
    def test_blocks_after_minute_limit(self):
        """Should block after hitting per-minute limit."""
        limiter = RateLimiter(requests_per_minute=2, requests_per_day=200)
        
        # First two requests should succeed
        limiter.record_request()
        limiter.record_request()
        
        # Third should be blocked
        can_request, error = limiter.can_request()
        assert can_request is False
        assert "requests/minute" in error
    
    def test_blocks_after_day_limit(self):
        """Should block after hitting per-day limit."""
        limiter = RateLimiter(requests_per_minute=20, requests_per_day=2)
        
        # First two requests should succeed
        limiter.record_request()
        limiter.record_request()
        
        # Third should be blocked
        can_request, error = limiter.can_request()
        assert can_request is False
        assert "requests/day" in error


class TestOpenRouterProvider:
    """Test OpenRouter API integration."""
    
    def test_requires_api_key(self):
        """Should raise error if API key not set."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
                call_openrouter("test prompt")
    
    def test_resolves_model_alias(self):
        """Should resolve model aliases to full IDs."""
        assert "meta-llama/llama-3.2-3b-instruct:free" in FREE_MODELS.values()
        assert "meta-llama/llama-3.3-70b-instruct:free" in FREE_MODELS.values()
    
    @patch('httpx.Client')
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    def test_successful_request(self, mock_client):
        """Should make successful API request."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated content"}}]
        }
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = call_openrouter("Test prompt", model_alias="llama-3.2-3b")
        
        assert result == "Generated content"
        assert mock_client_instance.post.called
    
    @patch('httpx.Client')
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    def test_json_mode(self, mock_client):
        """Should parse JSON responses correctly."""
        # Mock HTTP response with JSON
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"key": "value"}'}}]
        }
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = call_openrouter_json("Test prompt")
        
        assert result == {"key": "value"}
    
    @patch('httpx.Client')
    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test-key'})
    def test_json_extraction_from_markdown(self, mock_client):
        """Should extract JSON from markdown code blocks."""
        # Mock response with markdown JSON
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '```json\n{"key": "value"}\n```'}}]
        }
        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        result = call_openrouter_json("Test prompt")
        
        assert result == {"key": "value"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
