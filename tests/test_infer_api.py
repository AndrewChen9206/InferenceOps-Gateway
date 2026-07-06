from fastapi.testclient import TestClient


def test_infer_returns_mock_response(client: TestClient) -> None:
    payload = {
        "user_id": "andrew",
        "task_type": "ocr_cleanup",
        "prompt": "Clean and normalize this OCR text...",
        "policy": "cost_aware",
        "temperature": 0.0,
        "max_tokens": 256,
        "cache": True,
    }

    response = client.post("/v1/infer", json=payload)

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


def test_infer_rejects_unknown_user(client: TestClient) -> None:
    payload = {
        "user_id": "unknown-user",
        "task_type": "ocr_cleanup",
        "prompt": "Clean and normalize this OCR text...",
        "policy": "cost_aware",
        "temperature": 0.0,
        "max_tokens": 256,
        "cache": True,
    }

    response = client.post("/v1/infer", json=payload)

    assert response.status_code == 400
    assert "Unknown user_id" in response.json()["detail"]