from __future__ import annotations
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.agents.interfaces import AgentReport
from app.services.optimizer import StrategyOptimizer
from app.services.datastore import ds_get
from app.services.io.partitions import read_ohlcv_range


class OptimizerAgent(BaseAgent):
    def __init__(self, role: str = "optimize", version: str = "1.0.0"):
        super().__init__(role, version)

    def run(self, task: Dict[str, Any]) -> AgentReport:
        optimizer = StrategyOptimizer()
        data = task.get("data")
        if data is None and self.context:
            parts = task.get("partitions")
            if isinstance(parts, dict) and {"symbol", "start", "end"}.issubset(parts.keys()):
                data = read_ohlcv_range(symbol=parts["symbol"], start=parts["start"], end=parts["end"])
            if data is None:
                data = ds_get(self.context.trace_id, "market_data")
        res = optimizer.optimize(
            data=data,
            strategy_config=task["strategy_config"],
            param_grid=task.get("param_grid", {}),
            optimization_metric=task.get("metric", "sharpe_ratio"),
            top_n=task.get("top_n", 5),
        )
        return AgentReport(
            agent_id=self.id,
            status="completed",
            started_at=self.started_at,
            finished_at=None,
            summary=res,
        )
