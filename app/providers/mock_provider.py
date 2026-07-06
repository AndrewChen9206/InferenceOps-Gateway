import asyncio
import time

from app.providers.base import ProviderResponse


class MockProvider:
    model_name = "cheap-model"

    async def generate(
        self,
        *,
        task_type: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        start_time = time.perf_counter()

        await asyncio.sleep(0.1)

        output = (
            f"[mock:{self.model_name}] "
            f"Completed task '{task_type}' for prompt preview: "
            f"{prompt[:80]}"
        )

        latency_ms = int((time.perf_counter() - start_time) * 1000)
        estimated_output_tokens = max(1, min(max_tokens, len(output) // 4))

        return ProviderResponse(
            model_name=self.model_name,
            output=output,
            latency_ms=latency_ms,
            estimated_output_tokens=estimated_output_tokens,
        )
