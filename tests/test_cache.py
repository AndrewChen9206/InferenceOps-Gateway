from app.schemas.inference import CachedInferenceResult


def test_cached_inference_result_contains_only_cacheable_fields() -> None:
    cached_result = CachedInferenceResult(
        selected_model="cheap-model",
        output="cached output",
        estimated_input_tokens=10,
        estimated_output_tokens=20,
    )

    data = cached_result.model_dump()

    assert data == {
        "selected_model": "cheap-model",
        "output": "cached output",
        "estimated_input_tokens": 10,
        "estimated_output_tokens": 20,
    }

    assert "request_id" not in data
    assert "user_id" not in data
    assert "cache_hit" not in data
    assert "latency_ms" not in data
    assert "estimated_cost_usd" not in data
    assert "policy" not in data
