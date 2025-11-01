from __future__ import annotations
from typing import Dict, Any
from datetime import datetime

from app.core.config import get_settings


_costs: Dict[str, Dict[str, Any]] = {}


def _bucket(trace_id: str) -> Dict[str, Any]:
    b = _costs.setdefault(trace_id, {
        "bytes_written": 0,
        "bytes_read": 0,
        "objects_written": 0,
        "objects_read": 0,
        "compute_ms": 0,
        "updated_at": datetime.utcnow().isoformat(),
    })
    return b


def add_io(trace_id: str, *, bytes_written: int = 0, bytes_read: int = 0, objects_written: int = 0, objects_read: int = 0) -> None:
    b = _bucket(trace_id)
    b["bytes_written"] += int(bytes_written)
    b["bytes_read"] += int(bytes_read)
    b["objects_written"] += int(objects_written)
    b["objects_read"] += int(objects_read)
    b["updated_at"] = datetime.utcnow().isoformat()


def add_compute(trace_id: str, ms: int) -> None:
    b = _bucket(trace_id)
    b["compute_ms"] += int(ms)
    b["updated_at"] = datetime.utcnow().isoformat()


def get_costs(trace_id: str) -> Dict[str, Any]:
    b = _bucket(trace_id)
    s = get_settings()
    kb_w = b["bytes_written"] / 1024.0
    kb_r = b["bytes_read"] / 1024.0
    sec = b["compute_ms"] / 1000.0
    price = kb_w * s.PRICE_PER_KB_WRITE + kb_r * s.PRICE_PER_KB_READ + sec * s.PRICE_PER_SECOND_COMPUTE
    return {**b, "price": price}


def clear(trace_id: str) -> None:
    _costs.pop(trace_id, None)

