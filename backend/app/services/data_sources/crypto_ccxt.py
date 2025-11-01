from __future__ import annotations
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime

try:
    import ccxt  # type: ignore
except Exception:
    ccxt = None

from app.services.data_sources.base import DataSource, OHLCV_SCHEMA, enforce_schema


class CCXTCryptoOHLCV(DataSource):
    name = "ccxt_ohlcv"

    def __init__(self, exchange: str = "binance"):
        if ccxt is None:
            raise RuntimeError("ccxt is required for CCXTCryptoOHLCV")
        if not hasattr(ccxt, exchange):
            raise ValueError(f"Unknown exchange: {exchange}")
        self.exchange = getattr(ccxt, exchange)()

    def fetch(
        self,
        *,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        timeframe: str = "1h",
        limit: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        ms_start = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000) if start else None
        ms_end = int(pd.Timestamp(end, tz="UTC").timestamp() * 1000) if end else None
        tf = timeframe
        # ccxt: fetchOHLCV(symbol, timeframe='1m', since=None, limit=None, params={})
        data = self.exchange.fetch_ohlcv(symbol, timeframe=tf, since=ms_start, limit=limit or 500)
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df["symbol"] = symbol
        df["source"] = self.name
        df = enforce_schema(df, OHLCV_SCHEMA)
        if end:
            df = df[df["timestamp"] <= pd.Timestamp(end, tz="UTC")]
        return df

