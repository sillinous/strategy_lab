from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_catalog_list_empty_ok():
    r = client.get("/api/v1/catalog/datasets")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "count" in body

