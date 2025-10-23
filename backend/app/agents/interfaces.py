"""
Agent interfaces and models for the Strategy Lab agent ecosystem.
"""
from __future__ import annotations
from typing import Optional, Dict, Any, Protocol
from pydantic import BaseModel, Field
from datetime import datetime


class AgentContext(BaseModel):
    trace_id: str = Field(..., description="Correlation ID for tracing")
    caller: Optional[str] = Field(None, description="Invoker identity")
    permissions: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentConfig(BaseModel):n+    name: str
    version: str = "1.0.0"
    role: str
    params: Dict[str, Any] = Field(default_factory=dict)


class AgentReport(BaseModel):
    agent_id: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    summary: Dict[str, Any] = Field(default_factory=dict)


class Agent(Protocol):
    id: str
    role: str
    version: str

    def init(self, config: AgentConfig, context: AgentContext) -> None: ...
    def plan(self, task: Dict[str, Any]) -> Dict[str, Any]: ...
    def run(self, task: Dict[str, Any]) -> AgentReport: ...
    def health(self) -> Dict[str, Any]: ...
    def shutdown(self) -> None: ...

