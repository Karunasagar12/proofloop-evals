import io
import json
from unittest.mock import patch
from urllib.error import HTTPError

from proofloop.providers.openai_compat import OpenAICompatibleProvider


def test_provider_turns_azure_content_filter_block_into_model_response():
    body = json.dumps({
        "choices": [{"finish_reason": "content_filter", "content_filter_results": {"error": {"message": "Response content blocked by label 'Jailbreak'."}}}],
        "usage": {"prompt_tokens": 1},
    }).encode()
    error = HTTPError("https://x.models.ai.azure.com/v1/chat/completions", 400, "Bad Request", {}, io.BytesIO(body))

    provider = OpenAICompatibleProvider(base_url="https://x.models.ai.azure.com/v1", api_key="key", model="Kimi-K2.6")
    with patch("urllib.request.urlopen", side_effect=error):
        response = provider.complete("system", "attack")

    assert "content filter blocked" in response.content.lower()
    assert response.raw["blocked"] is True
