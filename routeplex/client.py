"""RoutePlex Python SDK client."""

from __future__ import annotations

import urllib.request
import urllib.error
import json
from typing import Any, Dict, List, Optional, Union

from routeplex.types import (
    ChatResponse,
    Message,
    Usage,
    EstimateResponse,
    EnhanceResponse,
    Model,
    _raise_for_error,
)

_DEFAULT_BASE_URL = "https://api.routeplex.com"
_TIMEOUT = 120  # seconds


class RoutePlex:
    """RoutePlex API client.

    Args:
        api_key: Your RoutePlex API key (starts with ``rp_`` or ``sk_live_``).
        base_url: API base URL. Defaults to ``https://api.routeplex.com``.
        timeout: Request timeout in seconds. Defaults to 120.

    Example::

        from routeplex import RoutePlex

        client = RoutePlex(api_key="rp_your_key")

        # Quick one-liner
        response = client.chat("Explain quantum computing")
        print(response.output)

        # Full control
        response = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": "Explain quantum computing"},
            ],
            strategy="quality",
            max_output_tokens=1024,
        )
        print(response.output)
        print(f"Cost: ${response.usage.cost_usd:.6f}")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = _TIMEOUT,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: Union[str, List[Union[Dict[str, str], Message]]],
        *,
        model: Optional[str] = None,
        strategy: Optional[str] = None,
        max_output_tokens: int = 512,
        temperature: Optional[float] = None,
        enhance_prompt: bool = False,
    ) -> ChatResponse:
        """Create a chat completion.

        RoutePlex supports three routing modes:

        - **Auto-routing** (default): omit both ``model`` and ``strategy`` —
          RoutePlex analyzes your prompt and picks the best model automatically.
        - **Strategy routing**: set ``strategy`` to ``"cost"``, ``"speed"``,
          ``"quality"``, or ``"balanced"`` to override auto-routing with a
          fixed priority.
        - **Manual mode**: set ``model`` to a specific model ID.

        Args:
            messages: A string (shorthand for a single user message) or a list
                of message dicts / :class:`Message` objects.
            model: Specific model to use (e.g. ``"gpt-4o-mini"``). Enables
                manual mode — bypasses auto-routing entirely.
            strategy: Routing priority when auto-routing: ``"cost"``,
                ``"speed"``, ``"quality"``, ``"balanced"``. If omitted,
                RoutePlex analyzes the prompt to pick the best model.
            max_output_tokens: Maximum output tokens (1-4096, default 512).
            temperature: Sampling temperature (0-2). None for model default.
            enhance_prompt: Auto-enhance the last user message before sending.

        Returns:
            A :class:`ChatResponse` with ``.output``, ``.usage``, etc.
        """
        msgs = self._normalize_messages(messages)

        body: Dict[str, Any] = {
            "messages": msgs,
            "max_output_tokens": max_output_tokens,
            "enhance_prompt": enhance_prompt,
        }

        if model:
            body["mode"] = "manual"
            body["model"] = model
        else:
            body["mode"] = "routeplex-ai"
            if strategy:
                body["strategy"] = strategy

        if temperature is not None:
            body["temperature"] = temperature

        data = self._post("/api/v1/chat", body, auth=True)
        d = data["data"]
        usage_raw = d.get("usage", {})

        return ChatResponse(
            id=d.get("id", ""),
            output=d.get("output", ""),
            model_used=d.get("model_used", ""),
            provider=d.get("provider", ""),
            routing_mode=d.get("routing_mode", ""),
            fallback_used=d.get("fallback_used", False),
            latency_ms=d.get("latency_ms"),
            usage=Usage(
                input_tokens=usage_raw.get("input_tokens", 0),
                output_tokens=usage_raw.get("output_tokens", 0),
                total_tokens=usage_raw.get("total_tokens", 0),
                cost_usd=usage_raw.get("cost_usd", 0.0),
                internal_reasoning_tokens=usage_raw.get("internal_reasoning_tokens"),
            ),
            enhancement=d.get("enhancement"),
            raw=data,
        )

    # ------------------------------------------------------------------
    # Estimate (free, no auth)
    # ------------------------------------------------------------------

    def estimate(
        self,
        messages: Union[str, List[Union[Dict[str, str], Message]]],
        *,
        model: Optional[str] = None,
        max_output_tokens: int = 512,
    ) -> EstimateResponse:
        """Estimate the cost of a chat request (free, no API key needed).

        Args:
            messages: A string or list of messages.
            model: Model to estimate for. Omit for cheapest available.
            max_output_tokens: Maximum output tokens.

        Returns:
            An :class:`EstimateResponse` with cost and token details.
        """
        msgs = self._normalize_messages(messages)
        body: Dict[str, Any] = {
            "messages": msgs,
            "max_output_tokens": max_output_tokens,
        }
        if model:
            body["model"] = model

        data = self._post("/api/v1/chat/estimate", body, auth=False)
        d = data["data"]

        return EstimateResponse(
            model=d.get("model", ""),
            input_tokens=d.get("input_tokens", 0),
            max_output_tokens=d.get("max_output_tokens", 0),
            total_tokens=d.get("total_tokens", 0),
            estimated_cost_usd=d.get("estimated_cost_usd", 0.0),
            confidence=d.get("confidence", ""),
            pricing=d.get("pricing", {}),
            raw=data,
        )

    # ------------------------------------------------------------------
    # Enhance (free, no auth)
    # ------------------------------------------------------------------

    def enhance(self, prompt: str) -> EnhanceResponse:
        """Enhance a prompt using RoutePlex's prompt optimizer (free).

        Args:
            prompt: The prompt to enhance.

        Returns:
            An :class:`EnhanceResponse` with the improved prompt.
        """
        data = self._post("/api/v1/chat/enhance", {"prompt": prompt}, auth=False)
        d = data["data"]

        return EnhanceResponse(
            enhanced_prompt=d.get("enhanced_prompt", prompt),
            changed=d.get("changed", False),
            query_type=d.get("query_type", ""),
            detected_language=d.get("detected_language"),
            original_prompt=d.get("original_prompt", prompt),
            raw=data,
        )

    # ------------------------------------------------------------------
    # Models (free, no auth)
    # ------------------------------------------------------------------

    def list_models(self) -> List[Model]:
        """List all available models.

        Returns:
            A list of :class:`Model` objects.
        """
        data = self._get("/api/v1/models")
        models = []
        for m in data.get("data", []):
            models.append(Model(
                id=m.get("id", ""),
                display_name=m.get("display_name", m.get("id", "")),
                provider=m.get("provider", ""),
                tier=m.get("tier", "default"),
                context_window=m.get("context_window", 0),
                max_output=m.get("max_output", 0),
                status=m.get("status", "available"),
                raw=m,
            ))
        return models

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _normalize_messages(
        self, messages: Union[str, List[Union[Dict[str, str], Message]]]
    ) -> List[Dict[str, str]]:
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        result = []
        for m in messages:
            if isinstance(m, Message):
                result.append(m.to_dict())
            elif isinstance(m, dict):
                result.append(m)
            else:
                raise TypeError(f"Expected str, dict, or Message, got {type(m)}")
        return result

    def _headers(self, auth: bool = False) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"routeplex-python/0.1.0",
        }
        if auth:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _post(self, path: str, body: dict, auth: bool = True) -> dict:
        url = f"{self._base_url}{path}"
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, headers=self._headers(auth), method="POST"
        )
        return self._send(req)

    def _get(self, path: str, auth: bool = False) -> dict:
        url = f"{self._base_url}{path}"
        req = urllib.request.Request(url, headers=self._headers(auth), method="GET")
        return self._send(req)

    def _send(self, req: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as e:
            body = {}
            try:
                body = json.loads(e.read().decode("utf-8"))
            except Exception:
                pass
            if body.get("success") is False and "error" in body:
                _raise_for_error(e.code, body)
            raise RoutePlexError(
                message=f"HTTP {e.code}: {e.reason}",
                code="http_error",
                status=e.code,
            ) from e
        except urllib.error.URLError as e:
            raise RoutePlexError(
                message=f"Connection failed: {e.reason}",
                code="connection_error",
            ) from e


# Import at module level for type checking
from routeplex.types import RoutePlexError  # noqa: E402
