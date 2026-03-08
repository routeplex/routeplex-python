# RoutePlex Python SDK

> **Coming Soon** - The official Python SDK for [RoutePlex](https://routeplex.com), the multi-model AI gateway.

## What is RoutePlex?

RoutePlex is a unified API gateway that intelligently routes your AI requests across **OpenAI**, **Anthropic**, and **Google Gemini** — with smart routing, cost optimization, and built-in content moderation.

## Coming Soon

```python
from routeplex import RoutePlex

client = RoutePlex(api_key="rp_...")

# Auto-route to the best model
response = client.chat("Explain quantum computing")

# Or pick a strategy
response = client.chat(
    "Write a Python function to sort a list",
    strategy="quality",  # cost | balanced | quality | speed
)

print(response.output)
print(f"Model: {response.model_used}")
print(f"Cost: ${response.usage.cost_usd:.6f}")
```

## Features (Planned)

- **Unified API** - One SDK for OpenAI, Anthropic, and Gemini
- **Smart Routing** - Auto-select the best model based on your strategy
- **Cost Tracking** - Real-time cost estimation and tracking
- **Content Moderation** - Built-in 3-layer moderation pipeline
- **OpenAI Compatible** - Drop-in replacement with `base_url` swap
- **Type Safe** - Full type hints and autocompletion

## Get Notified

Star the [GitHub repo](https://github.com/routeplex/routeplex-python) or visit [routeplex.com](https://routeplex.com) to get notified when the SDK launches.

## Current Integration

While the SDK is being built, you can use RoutePlex today via the OpenAI SDK:

```python
from openai import OpenAI

client = OpenAI(
    api_key="rp_your_api_key",
    base_url="https://api.routeplex.com/v1",
)

response = client.chat.completions.create(
    model="routeplex-ai",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## License

MIT
