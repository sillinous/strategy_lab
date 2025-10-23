"""Simple in-memory KV store and registry placeholder.

Replace with Redis/DB-backed implementations later.
"""
from typing import Dict, Any

_kv: Dict[str, Any] = {}
_agents: Dict[str, Dict[str, Any]] = {}


def kv_set(key: str, value: Any) -> None:
    _kv[key] = value


def kv_get(key: str, default=None):
    return _kv.get(key, default)


def register_agent(agent_id: str, info: Dict[str, Any]) -> None:
    _agents[agent_id] = info


def get_agent(agent_id: str) -> Dict[str, Any] | None:
    return _agents.get(agent_id)


def list_agents() -> Dict[str, Dict[str, Any]]:
    return _agents

