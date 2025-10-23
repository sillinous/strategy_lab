"""Lightweight event emitter (in-memory placeholder)."""
from typing import Dict, Any, Callable, List

_subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}


def emit_event(event_type: str, payload: Dict[str, Any]) -> None:
    for cb in _subscribers.get(event_type, []):
        try:
            cb(payload)
        except Exception:
            pass


def subscribe(event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    _subscribers.setdefault(event_type, []).append(callback)

