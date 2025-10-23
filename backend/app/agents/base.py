from __future__ import annotations
import uuid
from typing import Dict, Any
from datetime import datetime
from app.agents.interfaces import Agent, AgentConfig, AgentContext, AgentReport
from app.services.events import emit_event


class BaseAgent(Agent):
    def __init__(self, role: str, version: str = "1.0.0"):
        self.id = str(uuid.uuid4())
        self.role = role
        self.version = version
        self.config: AgentConfig | None = None
        self.context: AgentContext | None = None
        self.started_at: datetime | None = None

    def init(self, config: AgentConfig, context: AgentContext) -> None:
        self.config = config
        self.context = context
        emit_event("agent.started", {
            "agent_id": self.id, "role": self.role, "trace_id": context.trace_id
        })

    def plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {"plan": ["execute"], "task": task}

    def run(self, task: Dict[str, Any]) -> AgentReport:
        self.started_at = datetime.utcnow()
        return AgentReport(
            agent_id=self.id,
            status="completed",
            started_at=self.started_at,
            finished_at=datetime.utcnow(),
            summary={"message": "noop"}
        )

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "role": self.role, "version": self.version}

    def shutdown(self) -> None:
        if self.context:
            emit_event("agent.stopped", {"agent_id": self.id, "trace_id": self.context.trace_id})

