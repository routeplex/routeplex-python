"""Type definitions for the RoutePlex SDK."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class RoutePlexError(Exception):
    """Base exception for all RoutePlex errors."""

    def __init__(self, message: str, code: str = "unknown", status: int = 0, details: Any = None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.details = details


class AuthenticationError(RoutePlexError):
    """Raised when the API key is invalid or missing."""
    pass


class RateLimitError(RoutePlexError):
    """Raised when rate or quota limits are exceeded."""
    pass


class ValidationError(RoutePlexError):
    """Raised for invalid request parameters."""
    pass


class ProviderError(RoutePlexError):
    """Raised when upstream providers fail."""
    pass


class ContentPolicyError(RoutePlexError):
    """Raised when content moderation blocks the request."""
    pass


# Map API error codes to exception classes
_ERROR_MAP = {
    "unauthenticated": AuthenticationError,
    "invalid_api_key": AuthenticationError,
    "expired_api_key": AuthenticationError,
    "rate_limited": RateLimitError,
    "daily_limit_exceeded": RateLimitError,
    "daily_cost_limit_exceeded": RateLimitError,
    "quota_exceeded": RateLimitError,
    "validation_error": ValidationError,
    "invalid_model": ValidationError,
    "invalid_mode": ValidationError,
    "empty_messages": ValidationError,
    "bad_request": ValidationError,
    "content_policy_violation": ContentPolicyError,
    "content_moderation_flagged": ContentPolicyError,
    "blocked_url": ContentPolicyError,
    "provider_error": ProviderError,
    "provider_timeout": ProviderError,
    "provider_unavailable": ProviderError,
    "all_providers_failed": ProviderError,
}


def _raise_for_error(status: int, body: dict) -> None:
    """Raise the appropriate RoutePlexError from an API error response."""
    err = body.get("error", {})
    code = err.get("code", "unknown")
    message = err.get("message", "Unknown error")
    details = err.get("details")
    exc_cls = _ERROR_MAP.get(code, RoutePlexError)
    raise exc_cls(message=message, code=code, status=status, details=details)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Message:
    """A chat message."""
    role: str
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role="user", content=content)

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role="assistant", content=content)


@dataclass(frozen=True)
class Usage:
    """Token usage and cost for a request."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    internal_reasoning_tokens: Optional[int] = None


@dataclass(frozen=True)
class ChatResponse:
    """Response from a chat completion."""
    id: str
    output: str
    model_used: str
    provider: str
    routing_mode: str
    usage: Usage
    fallback_used: bool = False
    latency_ms: Optional[int] = None
    enhancement: Optional[Dict[str, Any]] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.output


@dataclass(frozen=True)
class EstimateResponse:
    """Cost estimate for a chat request."""
    model: str
    input_tokens: int
    max_output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    confidence: str
    pricing: Dict[str, float] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnhanceResponse:
    """Enhanced prompt result."""
    enhanced_prompt: str
    changed: bool
    query_type: str
    detected_language: Optional[str] = None
    original_prompt: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Model:
    """An available model."""
    id: str
    display_name: str
    provider: str
    tier: str
    context_window: int = 0
    max_output: int = 0
    status: str = "available"
    raw: Dict[str, Any] = field(default_factory=dict)
