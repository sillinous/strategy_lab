from __future__ import annotations
from typing import Optional, Dict, Any
from pathlib import Path
import pandas as pd

from app.core.config import get_settings


def ohlcv_partition_path(base: str, symbol: str, ts: pd.Timestamp) -> Path:
    # Partition by symbol/date=YYYY-MM-DD
    symbol_sanitized = symbol.replace("/", "-")
    date_part = ts.strftime("%Y-%m-%d")
    return Path(base) / "datasets" / "ohlcv" / symbol_sanitized / f"date={date_part}"


def write_ohlcv_partition(df: pd.DataFrame, *, base: Optional[str] = None) -> Dict[str, Any]:
    s = get_settings()
    base_path = base or s.LOCAL_STORAGE_BASE
    if df.empty:
        return {"written": 0, "partitions": []}
    partitions = []
    for date, group in df.groupby(df["timestamp"].dt.date):
        ts = pd.Timestamp(date, tz="UTC")
        p = ohlcv_partition_path(base_path, df["symbol"].iloc[0], ts)
        p.mkdir(parents=True, exist_ok=True)
        file = p / "part.parquet"
        group.to_parquet(file, index=False)
        partitions.append(str(file))
    return {"written": len(partitions), "partitions": partitions}


def read_ohlcv_range(symbol: str, start: Optional[str], end: Optional[str], *, base: Optional[str] = None) -> pd.DataFrame:
    s = get_settings()
    base_path = base or s.LOCAL_STORAGE_BASE
    start_ts = pd.Timestamp(start, tz="UTC") if start else None
    end_ts = pd.Timestamp(end, tz="UTC") if end else None
    # naive scan: iterate dates between start and end
    if not start_ts or not end_ts:
        return pd.DataFrame()
    days = pd.date_range(start_ts.normalize(), end_ts.normalize(), freq="D")
    frames = []
    for day in days:
        p = ohlcv_partition_path(base_path, symbol, day)
        f = p / "part.parquet"
        if f.exists():
            df = pd.read_parquet(f)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    mask = pd.Series(True, index=df.index)
    if start_ts is not None:
        mask &= pd.to_datetime(df["timestamp"], utc=True) >= start_ts
    if end_ts is not None:
        mask &= pd.to_datetime(df["timestamp"], utc=True) <= end_ts
    return df.loc[mask]

