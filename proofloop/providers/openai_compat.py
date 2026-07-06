from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .base import ModelResponse


@dataclass
class OpenAICompatibleProvider:
    base_url: str
    api_key: str
    model: str
    timeout: int = 30

    @property
    def name(self) -> str:
        host = self.base_url.split("//")[-1].split("/")[0]
        return f"{self.model}@{host}"

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> ModelResponse:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        if "azure" in self.base_url.lower() or "openai.azure.com" in self.base_url.lower():
            headers = {"Content-Type": "application/json", "api-key": self.api_key}
        body = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        ).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(errors="replace") if exc.fp else ""
            try:
                error_data = json.loads(error_body)
            except Exception:
                error_data = {}
            choices = error_data.get("choices") or []
            if choices and choices[0].get("finish_reason") == "content_filter":
                message = (
                    choices[0]
                    .get("content_filter_results", {})
                    .get("error", {})
                    .get("message", "Provider content filter blocked this response.")
                )
                return ModelResponse(
                    content=f"I cannot comply with this unsafe request. Provider content filter blocked the response: {message}",
                    model=error_data.get("model", self.model) or self.model,
                    usage=error_data.get("usage", {}),
                    raw={"blocked": True, "error": error_data},
                )
            raise RuntimeError(f"Provider returned {exc.code}: {error_body}") from exc
        return ModelResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", self.model),
            usage=data.get("usage", {}),
            raw=data,
        )
