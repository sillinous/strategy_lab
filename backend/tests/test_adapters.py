import pandas as pd
import types

from app.services.data_sources.base import OHLCV_SCHEMA, enforce_schema


def test_enforce_schema_minimal():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01T00:00:00Z"],
        "open": [1.0],
        "high": [1.1],
        "low": [0.9],
        "close": [1.05],
        "volume": [100.0],
        "symbol": ["TEST"],
        "source": ["x"],
    })
    out = enforce_schema(df, OHLCV_SCHEMA)
    assert list(out.columns) == list(OHLCV_SCHEMA.keys())


def test_yahoo_adapter_mock(monkeypatch):
    from app.services.data_sources import yahoo

    class Dummy:
        def download(self, symbol, start=None, end=None, interval=None, progress=False):
            idx = pd.to_datetime(["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"], utc=True)
            return pd.DataFrame({
                "Open": [1.0, 1.1],
                "High": [1.2, 1.3],
                "Low": [0.9, 1.0],
                "Close": [1.05, 1.2],
                "Volume": [100, 200],
            }, index=idx)

    monkeypatch.setattr(yahoo, "yf", Dummy())
    adapter = yahoo.YahooEquityOHLCV()
    df = adapter.fetch(symbol="AAPL", timeframe="1d")
    assert not df.empty and set(df.columns) == set(OHLCV_SCHEMA.keys())


def test_fred_adapter_mock(monkeypatch):
    from app.services.data_sources.fred import FREDSeries

    class DummyResp:
        def __init__(self):
            self._json = {"observations": [
                {"date": "2024-01-01", "value": "5.0"},
                {"date": "2024-02-01", "value": "5.1"},
            ]}
        def raise_for_status(self):
            return None
        def json(self):
            return self._json

    def dummy_get(url, params=None, timeout=30):
        return DummyResp()

    import app.services.data_sources.fred as fred_mod
    monkeypatch.setenv("FRED_API_KEY", "test")
    monkeypatch.setattr(fred_mod, "requests", types.SimpleNamespace(get=dummy_get))
    f = FREDSeries()
    df = f.fetch(symbol="FEDFUNDS")
    assert list(df.columns) == ["timestamp", "value", "series_id", "source"]
    assert not df.empty

