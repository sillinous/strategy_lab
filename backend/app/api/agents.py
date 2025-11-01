"""Agent management API: list types, create, run, and fetch status."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from app.agents.factory import AgentRegistry, AgentFactory
from app.agents.backtest_agent import BacktestAgent
from app.agents.optimizer_agent import OptimizerAgent
from app.agents.data_scout import DataScoutAgent
from app.agents.interfaces import AgentConfig, AgentContext
from app.agents.orchestrator import Orchestrator
from app.services.costs import get_costs
from app.services.datastore import ds_clear, ds_list
from app.services.janitor import janitor_run
from app.services.memory import register_agent, get_agent, list_agents


# Register built-in agents
AgentRegistry.register("backtest", BacktestAgent)
AgentRegistry.register("optimize", OptimizerAgent)
AgentRegistry.register("data_scout", DataScoutAgent)


router = APIRouter(prefix="/agents", tags=["Agents"])


class CreateAgentRequest(BaseModel):
    kind: str
    name: str
    params: Dict[str, Any] = {}


@router.get("/kinds")
def kinds() -> Dict[str, Any]:
    return {"kinds": AgentRegistry.kinds()}


@router.post("/create")
def create_agent(req: CreateAgentRequest) -> Dict[str, Any]:
    try:
        config = AgentConfig(name=req.name, role=req.kind, params=req.params)
        context = AgentContext(trace_id=str(datetime.utcnow().timestamp()))
        agent = AgentFactory.create_agent(req.kind, config, context)
        register_agent(agent.id, {
            "id": agent.id, "kind": req.kind, "name": req.name, "version": agent.version,
            "created_at": datetime.utcnow().isoformat()
        })
        return {"agent_id": agent.id, "kind": req.kind}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class RunRequest(BaseModel):
    agent_id: str
    task: Dict[str, Any]


_live_agents: Dict[str, Any] = {}


@router.post("/run")
def run(req: RunRequest) -> Dict[str, Any]:
    info = get_agent(req.agent_id)
    if not info:
        raise HTTPException(status_code=404, detail="Agent not found")
    # naive instance cache by id; in real system use orchestrator
    agent = _live_agents.get(req.agent_id)
    if not agent:
        # Recreate instance using kind
        config = AgentConfig(name=info["name"], role=info["kind"], params={})
        context = AgentContext(trace_id=str(datetime.utcnow().timestamp()))
        agent = AgentFactory.create_agent(info["kind"], config, context)
        _live_agents[req.agent_id] = agent
    report = agent.run(req.task)
    return {"agent_id": req.agent_id, "report": report.dict()}


@router.get("/list")
def list_registered_agents() -> Dict[str, Any]:
    return {"agents": list_agents()}


class OrchestrateRequest(BaseModel):
    plan: list[Dict[str, Any]]
    default_backend: str | None = None


@router.post("/orchestrate")
def orchestrate(req: OrchestrateRequest) -> Dict[str, Any]:
    orchestrator = Orchestrator(trace_id=str(datetime.utcnow().timestamp()))
    # Attach backend hint into each step if provided
    plan = [dict(step, storage={"backend": req.default_backend}) if req.default_backend else step for step in req.plan]
    result = orchestrator.run_plan(plan)
    result["costs"] = get_costs(result["trace_id"])
    return result


class AutoPlanRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    strategy_config: Dict[str, Any]
    optimization: Dict[str, Any] | None = None
    default_backend: str | None = None


@router.post("/auto_plan")
def auto_plan(req: AutoPlanRequest) -> Dict[str, Any]:
    # Step 1: Data scout
    orch = Orchestrator(trace_id=str(datetime.utcnow().timestamp()))
    plan = [
        {
            "kind": "data_scout",
            "name": f"fetch_{req.symbol}_{req.timeframe}",
            "task": {"symbol": req.symbol, "timeframe": req.timeframe},
            **({"storage": {"backend": req.default_backend}} if req.default_backend else {}),
        }
    ]
    res1 = orch.run_plan(plan)
    backtest_step = {
        "kind": "backtest",
        "name": "backtest_strategy",
        "task": {
            # Data is pulled from datastore via trace_id
            "strategy_config": req.strategy_config,
        },
    }
    opt_cfg = req.optimization or {}
    optimizer_step = {
        "kind": "optimize",
        "name": "optimize_strategy",
        "task": {
            # Data is pulled from datastore via trace_id
            "strategy_config": req.strategy_config,
            "param_grid": opt_cfg.get("param_grid", {}),
            "metric": opt_cfg.get("metric", "sharpe_ratio"),
            "top_n": opt_cfg.get("top_n", 5),
        },
    }
    res2 = orch.run_plan([backtest_step, optimizer_step])
    return {
        "trace_id": orch.trace_id,
        "stages": [res1, res2],
        "costs": get_costs(orch.trace_id),
    }


@router.get("/costs/{trace_id}")
def get_trace_costs(trace_id: str) -> Dict[str, Any]:
    return {"trace_id": trace_id, "costs": get_costs(trace_id)}


@router.get("/admin/list/{trace_id}")
def admin_list(trace_id: str) -> Dict[str, Any]:
    # Best effort listing per backend (availability for now)
    return {"trace_id": trace_id, "artifacts": ds_list(trace_id)}


@router.post("/admin/purge/{trace_id}")
def admin_purge(trace_id: str) -> Dict[str, Any]:
    ds_clear(trace_id)
    return {"trace_id": trace_id, "purged": True}


class JanitorRequest(BaseModel):
    max_age_hours: int | None = None


@router.post("/admin/janitor")
def admin_janitor(req: JanitorRequest) -> Dict[str, Any]:
    return janitor_run(req.max_age_hours)
