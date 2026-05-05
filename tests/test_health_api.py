from fastapi.testclient import TestClient

from intel_analyst.main import create_app


def test_health_check():
    client = TestClient(create_app())
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "vectorstore_dir" in payload
