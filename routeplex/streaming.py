"""Streaming types and SSE parser for the RoutePlex SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class StreamEvent:
    """A single event from a streaming response.

    Attributes:
        type: Event type — ``"start"``, ``"delta"``, ``"done"``, or ``"error"``.
        content: Text content (only for ``delta`` events).
        model_used: Model that generated the response (only for ``done``).
        provider: Provider name (only for ``done``).
        usage: Token usage dict (only for ``done``).
        finish_reason: Why generation stopped (only for ``done``).
        error: Error message (only for ``error`` events).
        raw: The raw parsed JSON dict for this event.
    """
    type: str
    content: Optional[str] = None
    model_used: Optional[str] = None
    provider: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        if self.type == "delta":
            return self.content or ""
        return f"[{self.type}]"


def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single SSE data line into a dict, or None if not parseable."""
    import json

    line = line.strip()
    if not line or line.startswith(":"):
        return None
    if line == "data: [DONE]":
        return None
    if line.startswith("data: "):
        try:
            return json.loads(line[6:])
        except (json.JSONDecodeError, ValueError):
            return None
    return None
