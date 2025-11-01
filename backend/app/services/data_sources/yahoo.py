from __future__ import annotations
from typing import Optional, Dict, Any
import pandas as pd

try:
    import yfinance as yf  # type: ignore
except Exception:
    yf = None

from app.services.data_sources.base import DataSource, OHLCV_SCHEMA, enforce_schema


class YahooEquityOHLCV(DataSource):
    name = "yahoo_ohlcv"

    def fetch(
        self,
        *,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        timeframe: str = "1d",
        limit: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        if yf is None:
            raise RuntimeError("yfinance is required for YahooEquityOHLCV")
        period = None
        interval = timeframe
        df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)
        if df is None or df.empty:
            return pd.DataFrame(columns=list(OHLCV_SCHEMA.keys()))
        df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Adj Close": "close", "Volume": "volume"})
        df = df.reset_index().rename(columns={"Date": "timestamp", "Datetime": "timestamp"})
        # Ensure UTC tz
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df["symbol"] = symbol
        df["source"] = self.name
        return enforce_schema(df, OHLCV_SCHEMA)

