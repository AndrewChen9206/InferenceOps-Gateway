from fastapi.testclient import TestClient
from redis.exceptions import RedisError

import app.services.inference_service as inference_service


def build_payload(cache: bool = True) -> dict:
    return {
        "user_id": "andrew",
        "task_type": "ocr_cleanup",
        "prompt": "Clean and normalize this OCR text...",
        "policy": "cost_aware",
        "temperature": 0.0,
        "max_tokens": 256,
        "cache": cache,
    }


def test_infer_returns_mock_response(client: TestClient) -> None:
    response = client.post("/v1/infer", json=build_payload())

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == "andrew"
    assert data["task_type"] == "ocr_cleanup"
    assert data["selected_model"] == "cheap-model"
    assert data["cache_hit"] is False
    assert data["fallback_used"] is False
    assert data["policy"] == "cost_aware"
    assert data["estimated_input_tokens"] >= 1
    assert data["estimated_output_tokens"] >= 1
    assert data["estimated_cost_usd"] >= 0
    assert data["latency_ms"] >= 0
    assert "request_id" in data
    assert "[mock:cheap-model]" in data["output"]


def test_infer_returns_cache_hit_for_repeated_request(client: TestClient) -> None:
    first_response = client.post("/v1/infer", json=build_payload())
    second_response = client.post("/v1/infer", json=build_payload())

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["cache_hit"] is False
    assert second_data["cache_hit"] is True

    assert first_data["estimated_cost_usd"] > 0
    assert second_data["estimated_cost_usd"] == 0

    assert first_data["latency_ms"] >= 1
    assert second_data["latency_ms"] >= 1

    assert second_data["output"] == first_data["output"]
    assert second_data["selected_model"] == first_data["selected_model"]
    assert second_data["request_id"] != first_data["request_id"]


def test_infer_cache_false_does_not_use_cache(client: TestClient) -> None:
    first_response = client.post("/v1/infer", json=build_payload(cache=False))
    second_response = client.post("/v1/infer", json=build_payload(cache=False))

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert first_response.json()["cache_hit"] is False
    assert second_response.json()["cache_hit"] is False


def test_infer_rejects_unknown_user(client: TestClient) -> None:
    payload = build_payload()
    payload["user_id"] = "unknown-user"

    response = client.post("/v1/infer", json=payload)

    assert response.status_code == 400
    assert "Unknown user_id" in response.json()["detail"]


def test_infer_succeeds_when_cache_write_fails(
    client: TestClient,
    monkeypatch,
) -> None:
    async def failing_set_cached_response(*args, **kwargs) -> None:
        raise RedisError("Simulated cache write failure")

    monkeypatch.setattr(
        inference_service,
        "set_cached_response",
        failing_set_cached_response,
    )

    payload = build_payload(cache=True)
    payload["prompt"] = "Unique cache write failure test prompt"

    response = client.post("/v1/infer", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["cache_hit"] is False
    assert data["estimated_cost_usd"] > 0
    assert data["request_id"]
    assert "[mock:cheap-model]" in data["output"]


def test_infer_returns_500_when_model_price_is_missing(
    client: TestClient,
    monkeypatch,
) -> None:
    async def missing_model_price(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.services.inference_service.get_model_price",
        missing_model_price,
    )

    payload = build_payload(cache=False)
    payload["prompt"] = "Missing model price test"

    response = client.post("/v1/infer", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Inference service configuration error."}
