# RoutePlex Python SDK

The official Python SDK for [RoutePlex](https://routeplex.com), the multi-model AI gateway.

## Install

```bash
pip install routeplex
```

## Quick Start

```python
from routeplex import RoutePlex

client = RoutePlex(api_key="rp_your_api_key")

# Simple — one-liner
response = client.chat("Explain quantum computing")
print(response.output)

# With strategy
response = client.chat("Write a Python sorting function", strategy="quality")
print(f"Model: {response.model_used}")
print(f"Cost: ${response.usage.cost_usd:.6f}")
```

## Features

- **One-liner chat** — pass a string, get a response
- **Smart routing** — auto-select the best model with `strategy="cost|speed|quality|balanced"`
- **Manual mode** — pick a specific model with `model="gpt-4o-mini"`
- **Cost estimation** — free, no API key needed
- **Prompt enhancement** — improve prompts before sending
- **Typed errors** — `AuthenticationError`, `RateLimitError`, `ValidationError`, etc.
- **Zero dependencies** — uses only Python stdlib (`urllib`, `json`)

## Usage

### Auto-routing (RoutePlex AI)

```python
# Let RoutePlex pick the best model
response = client.chat("What is Python?")

# Or specify a strategy
response = client.chat("Write a haiku", strategy="speed")
response = client.chat("Analyze this data", strategy="quality")
response = client.chat("Summarize this article", strategy="cost")
```

### Manual model selection

```python
response = client.chat(
    "Explain recursion",
    model="gpt-4o-mini",
    max_output_tokens=1024,
    temperature=0.5,
)
```

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
print(f"Confidence: {estimate.confidence}")
```

### Prompt enhancement (free)

```python
result = client.enhance("tell me about kubernetes")
if result.changed:
    print(f"Enhanced: {result.enhanced_prompt}")
    print(f"Type: {result.query_type}")
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

client = RoutePlex(api_key="rp_your_key")

try:
    response = client.chat("Hello!")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited: {e.message}")
```

## OpenAI SDK Compatible

You can also use RoutePlex with the OpenAI SDK — just change the `base_url`:

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

## Ecosystem

| Package | Platform | Description |
|---------|----------|-------------|
| [`routeplex`](https://pypi.org/project/routeplex/) | PyPI | Python SDK |
| [`@routeplex/node`](https://www.npmjs.com/package/@routeplex/node) | npm | Node.js SDK |

## Links

- [Website](https://routeplex.com)
- [Documentation](https://routeplex.com/docs)
- [API Playground](https://routeplex.com/docs/api-reference/playground)

## License

MIT
