# RoutePlex Python SDK

[![PyPI](https://img.shields.io/pypi/v/routeplex?label=PyPI&color=blue)](https://pypi.org/project/routeplex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](https://github.com/routeplex/routeplex-python/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776ab)](https://pypi.org/project/routeplex/)

The official Python SDK for [RoutePlex](https://routeplex.com?utm_source=github&utm_medium=readme&utm_campaign=python-sdk), the multi-model AI gateway. Route requests across OpenAI, Anthropic, and Google through a single API.

## Install

```bash
pip install routeplex
```

## Quick Start

```python
from routeplex import RoutePlex

client = RoutePlex(api_key="rp_live_YOUR_KEY")

# Auto-routing — analyzes your prompt, picks the best model
response = client.chat("Explain quantum computing")
print(response.output)
print(f"Model: {response.model_used}")
print(f"Cost: ${response.usage.cost_usd:.6f}")
```

## Features

- **One-liner chat** — pass a string, get a response
- **Prompt-based auto-routing** — RoutePlex analyzes your prompt and picks the best model automatically
- **Strategy routing** — override with `strategy="cost|speed|quality|balanced"` when you know what you want
- **Manual mode** — pick a specific model with `model="gpt-4o-mini"`
- **Prompt enhancement** — auto-improve prompts before sending to the model
- **Test mode** — safe development and CI testing with default-tier models only
- **Cost estimation** — estimate costs before sending (free, no API key needed)
- **Typed errors** — `AuthenticationError`, `RateLimitError`, `ValidationError`, etc.
- **Zero dependencies** — uses only Python stdlib (`urllib`, `json`)

## Routing Modes

RoutePlex supports three ways to route your requests:

### 1. Auto-routing (default) — analyzes your prompt

When you don't specify a model or strategy, RoutePlex **analyzes your prompt** to determine the best model. A simple question gets a fast, cheap model. A complex reasoning task gets a capable one.

```python
# RoutePlex reads your prompt and picks the optimal model
response = client.chat("What is Python?")           # → fast, cheap model
response = client.chat("Prove the Riemann hypothesis approach")  # → powerful model
```

### 2. Strategy routing — you choose the priority

When you specify a strategy, RoutePlex picks the best model for that priority — regardless of prompt content.

```python
response = client.chat("Write a haiku", strategy="speed")      # fastest model
response = client.chat("Analyze this data", strategy="quality") # most capable model
response = client.chat("Summarize this article", strategy="cost") # cheapest model
response = client.chat("General task", strategy="balanced")     # cost/speed/quality tradeoff
```

### 3. Manual mode — you pick the model

```python
response = client.chat("Explain recursion", model="gpt-4o-mini")
```

## Prompt Enhancement

Auto-improve your prompt before it reaches the model. Stateless, free, adds no latency overhead.

```python
# Per-request enhancement
response = client.chat("fix my code", enhance_prompt=True)

# Standalone — preview the enhanced prompt (free, no API key)
result = client.enhance("tell me about kubernetes")
if result.changed:
    print(f"Enhanced: {result.enhanced_prompt}")
```

## Test Mode

Use `test_mode` during development and CI to keep routing on default-tier models only — no premium charges, predictable costs.

```python
# Safe for CI pipelines — will never route to premium models
response = client.chat("Write a unit test for this function.", test_mode=True)
```

> `test_mode` only affects auto-routing. In manual mode you pick the model explicitly, so it has no effect.

## More Examples

### Multi-turn conversations

```python
response = client.chat([
    {"role": "system", "content": "You are a helpful tutor."},
    {"role": "user", "content": "What is recursion?"},
    {"role": "assistant", "content": "Recursion is when a function calls itself..."},
    {"role": "user", "content": "Can you give me a Python example?"},
])
```

### Cost estimation (free)

```python
estimate = client.estimate("Write a blog post about AI")
print(f"Model: {estimate.model}")
print(f"Estimated cost: ${estimate.estimated_cost_usd:.6f}")
```

### List models

```python
models = client.list_models()
for m in models:
    print(f"{m.id} ({m.provider}) — {m.tier}")
```

### Error handling

```python
from routeplex import RoutePlex, RateLimitError, AuthenticationError

try:
    response = client.chat("Hello!")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
```

## Also Works with OpenAI SDK

You can also use RoutePlex with the OpenAI SDK — just change the `base_url`:

```python
from openai import OpenAI

client = OpenAI(
    api_key="rp_live_YOUR_KEY",
    base_url="https://api.routeplex.com/v1",
)

response = client.chat.completions.create(
    model="routeplex-ai",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Ecosystem

| Package | Platform | Install |
|---------|----------|---------|
| [`routeplex`](https://pypi.org/project/routeplex/) | PyPI | `pip install routeplex` |
| [`@routeplex/node`](https://www.npmjs.com/package/@routeplex/node) | npm | `npm install @routeplex/node` |

## Links

- [Website](https://routeplex.com?utm_source=github&utm_medium=readme&utm_campaign=python-sdk)
- [Documentation](https://routeplex.com/docs?utm_source=github&utm_medium=readme&utm_campaign=python-sdk)
- [API Reference & Playground](https://routeplex.com/docs/api-reference/playground?utm_source=github&utm_medium=readme&utm_campaign=python-sdk)
- [Pricing](https://routeplex.com/pricing?utm_source=github&utm_medium=readme&utm_campaign=python-sdk)
- [Changelog](https://routeplex.com/changelog?utm_source=github&utm_medium=readme&utm_campaign=python-sdk)
- [Blog](https://routeplex.com/blog?utm_source=github&utm_medium=readme&utm_campaign=python-sdk)
- [Node.js SDK (GitHub)](https://github.com/routeplex/routeplex-node)
- [Examples](https://github.com/routeplex/routeplex-examples)

## License

MIT — see [LICENSE](https://github.com/routeplex/routeplex-python/blob/main/LICENSE)
