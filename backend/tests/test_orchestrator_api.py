import json
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_orchestrate_empty_plan():
    resp = client.post("/api/v1/agents/orchestrate", json={"plan": [], "default_backend": "memory"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["steps"] == 0
    assert "reports" in data


def test_kinds_lists_builtin_agents():
    resp = client.get("/api/v1/agents/kinds")
    assert resp.status_code == 200
    kinds = resp.json()["kinds"]
    assert set(["backtest", "optimize", "data_scout"]).issubset(set(kinds))


def test_auto_plan_shape():
    payload = {
        "symbol": "BTC-USD",
        "timeframe": "1h",
        "strategy_config": {"name": "sma_crossover", "params": {"fast": 10, "slow": 20}},
        "optimization": {"param_grid": {"fast": [5, 10], "slow": [20, 30]}}
    }
    resp = client.post("/api/v1/agents/auto_plan", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "trace_id" in data
    assert len(data.get("stages", [])) == 2
    assert "costs" in data


def test_admin_endpoints_list_and_purge():
    # list returns available backends
    resp = client.get("/api/v1/agents/admin/list/demo-trace")
    assert resp.status_code == 200
    data = resp.json()
    artifacts = data.get("artifacts", {})
    assert isinstance(artifacts, dict)
    # local backend should return items structure even if empty
    if "local" in artifacts:
        assert "items" in artifacts["local"]

    # purge returns success
    resp = client.post("/api/v1/agents/admin/purge/demo-trace")
    assert resp.status_code == 200
    assert resp.json().get("purged") is True


def test_admin_janitor_runs():
    resp = client.post("/api/v1/agents/admin/janitor", json={"max_age_hours": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert "enabled" in body
