"""
RoutePlex Python SDK - Multi-model AI gateway.

Route requests across OpenAI, Anthropic, and Google Gemini through a unified API.

Usage:
    from routeplex import RoutePlex

    client = RoutePlex(api_key="rp_live_YOUR_KEY")
    response = client.chat("What is Python?")
    print(response.output)

Learn more at https://routeplex.com
"""

__version__ = "0.1.0"

from routeplex.client import RoutePlex
from routeplex.types import (
    ChatResponse,
    Message,
    Usage,
    EstimateResponse,
    EnhanceResponse,
    Model,
    ModelPricing,
    ModelCapabilities,
    RoutePlexError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ProviderError,
    ContentPolicyError,
)
from routeplex.streaming import StreamEvent

__all__ = [
    "RoutePlex",
    "ChatResponse",
    "StreamEvent",
    "Message",
    "Usage",
    "EstimateResponse",
    "EnhanceResponse",
    "Model",
    "ModelPricing",
    "ModelCapabilities",
    "RoutePlexError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "ProviderError",
    "ContentPolicyError",
]
