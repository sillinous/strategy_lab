import pandas as pd

from app.services.data_sources.base import enforce_schema, OHLCV_SCHEMA


def test_enforce_schema_orders_and_types():
    df = pd.DataFrame({
        "open": [1.0],
        "high": [2.0],
        "low": [0.5],
        "close": [1.5],
        "volume": [100.0],
        "timestamp": ["2024-01-01T00:00:00Z"],
        "symbol": ["BTC-USD"],
        "source": ["test"],
    })
    out = enforce_schema(df, OHLCV_SCHEMA)
    assert list(out.columns) == list(OHLCV_SCHEMA.keys())
    assert pd.api.types.is_datetime64tz_dtype(out["timestamp"])  # UTC

