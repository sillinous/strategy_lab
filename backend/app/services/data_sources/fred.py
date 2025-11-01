from __future__ import annotations
from typing import Optional, Dict, Any
import pandas as pd
import os
import requests


class FREDSeries:
    name = "fred_series"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        if not self.api_key:
            raise RuntimeError("FRED_API_KEY is required for FREDSeries")

    def fetch(
        self,
        *,
        symbol: str,  # series_id
        start: Optional[str] = None,
        end: Optional[str] = None,
        timeframe: str = "1m",
        limit: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        params = {
            "series_id": symbol,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start or "1776-01-01",
        }
        if end:
            params["observation_end"] = end
        url = "https://api.stlouisfed.org/fred/series/observations"
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json().get("observations", [])
        if not data:
            return pd.DataFrame(columns=["timestamp", "value", "series_id", "source"])
        df = pd.DataFrame(data)
        df = df.rename(columns={"date": "timestamp"})
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        # Missing values are "." in FRED
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["series_id"] = symbol
        df["source"] = self.name
        return df[["timestamp", "value", "series_id", "source"]].sort_values("timestamp")

