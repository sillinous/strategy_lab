from __future__ import annotations
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.agents.interfaces import AgentReport
from app.services.data_sources.crypto_com import fetch_ohlc
from app.services.data_sources.crypto_ccxt import CCXTCryptoOHLCV
from app.services.data_sources.base import enforce_schema, OHLCV_SCHEMA
from app.services.io.partitions import write_ohlcv_partition
from app.services.catalog import register_partitions
from app.services.datastore import ds_put


class DataScoutAgent(BaseAgent):
    def __init__(self, role: str = "data_scout", version: str = "1.0.0"):
        super().__init__(role, version)

    def run(self, task: Dict[str, Any]) -> AgentReport:
        symbol = task["symbol"]
        timeframe = task.get("timeframe", "1h")
        # Prefer standardized source if available; fallback to existing util
        df = None
        try:
            src = CCXTCryptoOHLCV()
            df = src.fetch(symbol=symbol, timeframe=timeframe)
        except Exception:
            raw = fetch_ohlc(symbol=symbol, timeframe=timeframe)
            df = enforce_schema(raw.assign(symbol=symbol, source="crypto_com"), OHLCV_SCHEMA)
        # Write partitions and store a reference
        parts = write_ohlcv_partition(df)
        try:
            register_partitions("ohlcv", symbol, timeframe, parts.get("partitions", []))
        except Exception:
            pass
        if self.context:
            ds_put(self.context.trace_id, key="market_data_partitions", value=parts)
        return AgentReport(
            agent_id=self.id,
            status="completed",
            started_at=self.started_at,
            finished_at=None,
            summary={"symbol": symbol, "timeframe": timeframe, "rows": len(df), "partitions": parts},
        )
