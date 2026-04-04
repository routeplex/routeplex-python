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
    ModelPricing,
    ModelCapabilities,
    _raise_for_error,
)
from routeplex.streaming import StreamEvent, parse_sse_line

_DEFAULT_BASE_URL = "https://api.routeplex.com"
_TIMEOUT = 120  # seconds


class RoutePlex:
    """RoutePlex API client.

    Args:
        api_key: Your RoutePlex API key (starts with ``rp_live_``).
        base_url: API base URL. Defaults to ``https://api.routeplex.com``.
        timeout: Request timeout in seconds. Defaults to 120.

    Example::

        from routeplex import RoutePlex

        client = RoutePlex(api_key="rp_live_YOUR_KEY")

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
        test_mode: bool = False,
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
                ``"speed"``, ``"quality"``, ``"balanced"``, or ``"auto"``
                (prompt-based, default). If omitted, defaults to ``"auto"``.
            max_output_tokens: Maximum output tokens (1-4096, default 512).
            temperature: Sampling temperature (0-2). None for model default.
            enhance_prompt: Auto-enhance the last user message before sending.
            test_mode: When True, forces routing to use only default
                (non-premium) models regardless of account settings.

        Returns:
            A :class:`ChatResponse` with ``.output``, ``.usage``, etc.
        """
        msgs = self._normalize_messages(messages)

        body: Dict[str, Any] = {
            "messages": msgs,
            "max_output_tokens": max_output_tokens,
            "enhance_prompt": enhance_prompt,
            "test_mode": test_mode,
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
    # Streaming Chat
    # ------------------------------------------------------------------

    def chat_stream(
        self,
        messages: Union[str, List[Union[Dict[str, str], Message]]],
        *,
        model: Optional[str] = None,
        strategy: Optional[str] = None,
        max_output_tokens: int = 512,
        temperature: Optional[float] = None,
        enhance_prompt: bool = False,
        test_mode: bool = False,
        stream_mode: str = "buffered",
    ):
        """Stream a chat completion, yielding events as they arrive.

        Same parameters as :meth:`chat`, plus:

        Args:
            stream_mode: ``"buffered"`` (default, smooth 50-150ms paced chunks)
                or ``"realtime"`` (minimal ~10ms buffering).

        Yields:
            :class:`StreamEvent` objects. Collect ``delta`` events for text::

                for event in client.chat_stream("Tell me a story"):
                    if event.type == "delta":
                        print(event.content, end="", flush=True)
                    elif event.type == "done":
                        print(f"\\nTokens: {event.usage['total_tokens']}")
        """
        msgs = self._normalize_messages(messages)

        body: Dict[str, Any] = {
            "messages": msgs,
            "max_output_tokens": max_output_tokens,
            "enhance_prompt": enhance_prompt,
            "test_mode": test_mode,
            "stream": True,
            "stream_mode": stream_mode,
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

        url = f"{self._base_url}/api/v1/chat"
        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, headers=self._headers(auth=True), method="POST"
        )

        try:
            resp = urllib.request.urlopen(req, timeout=self._timeout)
        except urllib.error.HTTPError as e:
            body_data = {}
            try:
                body_data = json.loads(e.read().decode("utf-8"))
            except Exception:
                pass
            if body_data.get("success") is False and "error" in body_data:
                _raise_for_error(e.code, body_data)
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

        try:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if line == "data: [DONE]":
                    return
                data = parse_sse_line(line)
                if data is None:
                    continue

                event_type = data.get("type", "")

                if event_type == "start":
                    yield StreamEvent(type="start", raw=data)

                elif event_type == "delta":
                    yield StreamEvent(
                        type="delta",
                        content=data.get("content", ""),
                        raw=data,
                    )

                elif event_type == "done":
                    yield StreamEvent(
                        type="done",
                        model_used=data.get("model_used"),
                        provider=data.get("provider"),
                        usage=data.get("usage"),
                        finish_reason=data.get("finish_reason"),
                        latency_ms=data.get("latency_ms"),
                        raw=data,
                    )

                elif event_type == "error":
                    yield StreamEvent(
                        type="error",
                        error=data.get("message", "Unknown streaming error"),
                        raw=data,
                    )
        finally:
            resp.close()

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
            pricing_raw = m.get("pricing")
            pricing = None
            if pricing_raw:
                pricing = ModelPricing(
                    input_per_1k=pricing_raw.get("input_per_1k", 0),
                    output_per_1k=pricing_raw.get("output_per_1k", 0),
                )
            caps_raw = m.get("capabilities")
            caps = None
            if caps_raw:
                caps = ModelCapabilities(
                    streaming=caps_raw.get("streaming", True),
                    functions=caps_raw.get("functions", False),
                    vision=caps_raw.get("vision", False),
                )
            models.append(Model(
                id=m.get("id", ""),
                display_name=m.get("display_name", m.get("id", "")),
                provider=m.get("provider", ""),
                tier=m.get("tier", "default"),
                context_window=m.get("context_window", 0),
                max_output_tokens=m.get("max_output_tokens", 0),
                health=m.get("health", "healthy"),
                pricing=pricing,
                capabilities=caps,
                aliases=m.get("aliases", []),
                deprecated=m.get("deprecated", False),
                deprecation_date=m.get("deprecation_date"),
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
