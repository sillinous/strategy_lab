from __future__ import annotations
from typing import Protocol, Dict, Any, Iterable, Optional
import pandas as pd


class DataSource(Protocol):
    name: str

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
        """Fetch data into a standard DataFrame schema for the modality."""
        ...


OHLCV_SCHEMA = {
    "timestamp": "datetime64[ns, UTC]",
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "float64",
    "symbol": "string",
    "source": "string",
}


def enforce_schema(df: pd.DataFrame, schema: Dict[str, str]) -> pd.DataFrame:
    df = df.copy()
    for col, dtype in schema.items():
        if col not in df.columns:
            df[col] = pd.NA
        if dtype.startswith("datetime64"):
            df[col] = pd.to_datetime(df[col], utc=True)
        else:
            try:
                df[col] = df[col].astype(dtype)
            except Exception:
                pass
    df = df[list(schema.keys())]
    return df.sort_values("timestamp")

