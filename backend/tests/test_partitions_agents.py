import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.services.io.partitions import write_ohlcv_partition


client = TestClient(app)


def _mk_df():
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"]),
        "open": [1.0, 1.1],
        "high": [1.2, 1.3],
        "low": [0.9, 1.0],
        "close": [1.05, 1.2],
        "volume": [100, 200],
        "symbol": ["BTC-USD", "BTC-USD"],
        "source": ["test", "test"],
    })
    return df


def test_backtest_with_partitions_path():
    df = _mk_df()
    res = write_ohlcv_partition(df)
    # Create agent via API and run backtest with partition ref
    r = client.post("/api/v1/agents/create", json={"kind": "backtest", "name": "bt"})
    agent_id = r.json()["agent_id"]
    task = {
        "agent_id": agent_id,
        "task": {
            "partitions": {"symbol": "BTC-USD", "start": "2024-01-01T00:00:00Z", "end": "2024-01-01T02:00:00Z"},
            "strategy_config": {"name": "noop", "params": {}},
        },
    }
    resp = client.post("/api/v1/agents/run", json=task)
    assert resp.status_code == 200
    body = resp.json()
    assert body["agent_id"] == agent_id
