from __future__ import annotations
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.agents.interfaces import AgentReport
from app.services.data_sources.crypto_com import fetch_ohlc


class DataScoutAgent(BaseAgent):
    def __init__(self, role: str = "data_scout", version: str = "1.0.0"):
        super().__init__(role, version)

    def run(self, task: Dict[str, Any]) -> AgentReport:
        symbol = task["symbol"]
        timeframe = task.get("timeframe", "1h")
        df = fetch_ohlc(symbol=symbol, timeframe=timeframe)
        return AgentReport(
            agent_id=self.id,
            status="completed",
            started_at=self.started_at,
            finished_at=None,
            summary={"symbol": symbol, "timeframe": timeframe, "rows": len(df), "data": df.head(5).to_dict("index")},
        )

