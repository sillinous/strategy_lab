"""
Crypto.com Exchange data connector (stub)

Provides a unified interface to fetch candles compatible with the backtester.
This is a placeholder for Phase 1 with minimal feasibility.
"""
from typing import Literal, Optional
import pandas as pd
import datetime as dt


Timeframe = Literal[
    "1m","3m","5m","15m","30m","45m","1h","2h","4h","6h","8h","12h","1d","3d","1w","2w","1mo"
]


def fetch_ohlc(
    symbol: str,
    timeframe: Timeframe = "1h",
    start: Optional[dt.datetime] = None,
    end: Optional[dt.datetime] = None,
) -> pd.DataFrame:
    """Fetch OHLCV data for a symbol from Crypto.com Exchange.

    Note: This is a stub returning an empty DataFrame; implementation would
    use the public REST endpoints and normalize columns: [Open, High, Low, Close, Volume].
    """
    columns = ["Open", "High", "Low", "Close", "Volume"]
    return pd.DataFrame(columns=columns)

