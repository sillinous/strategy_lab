from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime

from app.agents.factory import AgentFactory
from app.agents.interfaces import AgentConfig, AgentContext, AgentReport
from app.services.datastore import ds_put


class Orchestrator:
    """
    Minimal orchestrator to run multi-step tasks.
    It materializes agents per step and aggregates reports.
    """

    def __init__(self, trace_id: str | None = None):
        self.trace_id = trace_id or str(datetime.utcnow().timestamp())

    def run_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a list of steps, each step defines: kind, name, params, task."""
        reports: List[Dict[str, Any]] = []
        started = datetime.utcnow()
        for step in plan:
            cfg = AgentConfig(name=step.get("name", step["kind"]), role=step["kind"], params=step.get("params", {}))
            ctx = AgentContext(trace_id=self.trace_id)
            agent = AgentFactory.create_agent(step["kind"], cfg, ctx)
            task = step.get("task", {})
            t0 = datetime.utcnow()
            try:
                report: AgentReport = agent.run(task)
            except Exception as e:
                # Synthesize a failed report with error info
                report = AgentReport(
                    agent_id=agent.id,
                    status="failed",
                    started_at=t0,
                    finished_at=datetime.utcnow(),
                    summary={},
                    error={"message": str(e), "type": type(e).__name__},
                )
            t1 = datetime.utcnow()
            # Update compute cost
            try:
                from app.services.costs import add_compute
                add_compute(self.trace_id, int((t1 - t0).total_seconds() * 1000))
            except Exception:
                pass
            rep_dict = report.dict()
            rep_dict["metrics"] = {"compute_ms": int((t1 - t0).total_seconds() * 1000)}
            reports.append(rep_dict)
            # Optionally store report summary for downstream inspection
            storage_cfg = step.get("storage") or {}
            if storage_cfg.get("store_report"):
                ds_put(self.trace_id, key=f"report_{step.get('name', step['kind'])}", value=report.dict(), backend=storage_cfg.get("backend"))
        return {
            "trace_id": self.trace_id,
            "started_at": started.isoformat(),
            "finished_at": datetime.utcnow().isoformat(),
            "steps": len(plan),
            "reports": reports,
        }
