"""
OpenRouter Provider for Swarm MCP Server

Provides access to free-tier models for non-coding tasks:
- Llama 3.2 3B: Fast data/fixture generation
- Llama 3.3 70B: Quality prose/documentation
- User-configurable additional models

Rate limits: 20 req/min, 200 req/day (free tier)
"""

import os
import json
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free model aliases → OpenRouter model IDs
FREE_MODELS = {
    "llama-3.2-3b": "meta-llama/llama-3.2-3b-instruct:free",
    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct:free",
    "llama-3.1-405b": "meta-llama/llama-3.1-405b-instruct:free",
    "gemma-3-27b": "google/gemma-3-27b-it:free",
    "qwen-vl-7b": "qwen/qwen2.5-vl-7b-instruct:free",
    "hermes-3-405b": "nousresearch/hermes-3-llama-3.1-405b:free",
    "gemini-flash-exp": "google/gemini-2.0-flash-exp:free",
}


class RateLimiter:
    """
    Rate limiter for OpenRouter free tier.
    
    Limits:
    - 20 requests per minute
    - 200 requests per day
    """
    
    def __init__(self, requests_per_minute: int = 20, requests_per_day: int = 200):
        self.rpm_limit = requests_per_minute
        self.rpd_limit = requests_per_day
        
        # Track requests in sliding windows
        self.minute_requests = deque(maxlen=requests_per_minute)
        self.day_requests = deque(maxlen=requests_per_day)
    
    def can_request(self) -> tuple[bool, Optional[str]]:
        """Check if request is allowed under rate limits."""
        now = datetime.now()
        
        # Clean old requests
        minute_ago = now - timedelta(minutes=1)
        day_ago = now - timedelta(days=1)
        
        # Remove expired minute requests
        while self.minute_requests and self.minute_requests[0] < minute_ago:
            self.minute_requests.popleft()
        
        # Remove expired day requests
        while self.day_requests and self.day_requests[0] < day_ago:
            self.day_requests.popleft()
        
        # Check limits
        if len(self.minute_requests) >= self.rpm_limit:
            return False, f"Rate limit: {self.rpm_limit} requests/minute exceeded"
        
        if len(self.day_requests) >= self.rpd_limit:
            return False, f"Rate limit: {self.rpd_limit} requests/day exceeded"
        
        return True, None
    
    def record_request(self):
        """Record a successful request."""
        now = datetime.now()
        self.minute_requests.append(now)
        self.day_requests.append(now)


# Global rate limiter instance
_rate_limiter = RateLimiter()


def call_openrouter(
    prompt: str,
    model_alias: str = "llama-3.3-70b",
    system_prompt: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.7
) -> str:
    """
    Call OpenRouter API with specified model.
    
    Args:
        prompt: User prompt/task
        model_alias: Model alias from FREE_MODELS or full model ID
        system_prompt: Optional system prompt
        json_mode: Request JSON output (not supported by all models)
        temperature: Sampling temperature (0.0-1.0)
    
    Returns:
        Model response text
    
    Raises:
        RuntimeError: If API key missing or rate limit exceeded
        Exception: On API errors
    """
    # Check API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY not set. Get a free key at https://openrouter.ai/keys"
        )
    
    # Check rate limits
    can_request, error_msg = _rate_limiter.can_request()
    if not can_request:
        raise RuntimeError(error_msg)
    
    # Resolve model ID
    model_id = FREE_MODELS.get(model_alias, model_alias)
    logger.info(f"🤖 Calling OpenRouter: {model_id}")
    
    # Build messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Build request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/swarm-mcp",  # Required by OpenRouter
        "X-Title": "Swarm MCP Server"
    }
    
    payload: Dict[str, Any] = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
    }
    
    # Add JSON mode if requested (not all models support this)
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    
    try:
        # Use httpx for async-compatible requests
        import httpx
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(OPENROUTER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Record successful request
            _rate_limiter.record_request()
            
            logger.info(f"✅ OpenRouter response: {len(content)} chars")
            return content
    
    except ImportError:
        raise RuntimeError(
            "httpx not installed. Run: pip install httpx>=0.27.0"
        )
    except Exception as e:
        logger.error(f"❌ OpenRouter error: {e}")
        raise


def call_openrouter_json(
    prompt: str,
    model_alias: str = "llama-3.3-70b",
    system_prompt: Optional[str] = None
) -> dict:
    """
    Call OpenRouter and parse JSON response.
    
    Convenience wrapper that enforces JSON mode and parses response.
    Falls back to extracting JSON from markdown code blocks if needed.
    """
    content = call_openrouter(
        prompt=prompt,
        model_alias=model_alias,
        system_prompt=system_prompt,
        json_mode=True
    )
    
    # Try to parse JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to extract from markdown code block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        return json.loads(content)
