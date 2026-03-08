"""
RoutePlex Python SDK - Coming Soon.

The official Python SDK for RoutePlex, the multi-model AI gateway.
Route requests across OpenAI, Anthropic, and Google Gemini through a unified API.

While the SDK is in development, you can use RoutePlex today via the OpenAI SDK:

    from openai import OpenAI

    client = OpenAI(
        api_key="rp_your_api_key",
        base_url="https://api.routeplex.com/v1",
    )

    response = client.chat.completions.create(
        model="routeplex-ai",
        messages=[{"role": "user", "content": "Hello!"}],
    )

Learn more at https://routeplex.com
"""

__version__ = "0.0.1"
__status__ = "coming_soon"


def _coming_soon():
    raise NotImplementedError(
        "The RoutePlex Python SDK is coming soon.\n\n"
        "In the meantime, you can use the OpenAI SDK with RoutePlex:\n\n"
        "    from openai import OpenAI\n"
        '    client = OpenAI(api_key="rp_...", base_url="https://api.routeplex.com/v1")\n\n'
        "Learn more: https://routeplex.com/docs"
    )


class RoutePlex:
    """RoutePlex client - coming soon."""

    def __init__(self, *args, **kwargs):
        _coming_soon()
