from __future__ import annotations
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.agents.interfaces import AgentReport
from app.services.backtester import VectorizedBacktester


class BacktestAgent(BaseAgent):
    def __init__(self, role: str = "backtest", version: str = "1.0.0"):
        super().__init__(role, version)

    def run(self, task: Dict[str, Any]) -> AgentReport:
        df = task["data"]
        strategy_config = task["strategy_config"]
        bt = VectorizedBacktester(
            data=df,
            initial_capital=task.get("initial_capital", 100000.0),
            commission_rate=task.get("commission_rate", 0.001),
            slippage_rate=task.get("slippage_rate", 0.0005),
        )
        result = bt.run(
            strategy_config=strategy_config,
            calculate_indicators=True,
        )
        return AgentReport(
            agent_id=self.id,
            status="completed",
            started_at=self.started_at or result.get("date_range", {}).get("start"),
            finished_at=None,
            summary=result,
        )

