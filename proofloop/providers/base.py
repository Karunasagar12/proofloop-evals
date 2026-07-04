from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class ModelResponse:
    content: str
    model: str
    usage: dict[str, int]
    raw: dict


@runtime_checkable
class ModelProvider(Protocol):
    @property
    def name(self) -> str: ...

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> ModelResponse: ...
