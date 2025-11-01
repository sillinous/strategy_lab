from __future__ import annotations

_ALIASES = {
    "60m": "1h",
    "30m": "30m",
    "15m": "15m",
    "1m": "1m",
    "1min": "1m",
    "1h": "1h",
    "1hr": "1h",
    "1d": "1d",
    "1day": "1d",
}


def normalize_timeframe(tf: str) -> str:
    tf = tf.strip().lower()
    return _ALIASES.get(tf, tf)


def to_pandas_freq(tf: str) -> str:
    tf = normalize_timeframe(tf)
    if tf.endswith("m"):
        return tf.upper()
    if tf.endswith("h"):
        return tf.replace("h", "H")
    if tf.endswith("d"):
        return tf.upper()
    return tf


def resample_ohlcv(df, timeframe: str):
    import pandas as pd

    if df.empty:
        return df
    freq = to_pandas_freq(timeframe)
    x = df.copy()
    x["timestamp"] = pd.to_datetime(x["timestamp"], utc=True)
    x = x.set_index("timestamp")
    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    out = x.resample(freq).agg(agg).dropna().reset_index()
    # carry symbol/source if present
    if "symbol" in df.columns:
        out["symbol"] = df["symbol"].iloc[0]
    if "source" in df.columns:
        out["source"] = df["source"].iloc[0]
    return out

