from __future__ import annotations
from typing import Dict, Type
from app.agents.base import BaseAgent
from app.agents.interfaces import Agent, AgentConfig, AgentContext


class AgentRegistry:
    _registry: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, kind: str, agent_cls: Type[BaseAgent]):
        cls._registry[kind] = agent_cls

    @classmethod
    def kinds(cls):
        return sorted(cls._registry.keys())

    @classmethod
    def get(cls, kind: str) -> Type[BaseAgent]:
        if kind not in cls._registry:
            raise ValueError(f"Unknown agent kind: {kind}")
        return cls._registry[kind]


class AgentFactory:
    @staticmethod
    def create_agent(kind: str, config: AgentConfig, context: AgentContext) -> Agent:
        agent_cls = AgentRegistry.get(kind)
        agent = agent_cls(role=kind)
        agent.init(config, context)
        return agent

