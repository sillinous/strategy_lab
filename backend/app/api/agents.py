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

