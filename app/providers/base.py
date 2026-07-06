from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderResponse:
    model_name: str
    output: str
    latency_ms: int
    estimated_output_tokens: int


class BaseProvider(Protocol):
    model_name: str

    async def generate(
        self,
        *,
        task_type: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse: ...
