from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.config import get_settings
from app.services.costs import _costs, clear as clear_costs
from app.services.datastore import ds_clear, _backends  # type: ignore


def purge_trace(trace_id: str) -> Dict[str, Any]:
    ds_clear(trace_id)
    clear_costs(trace_id)
    return {"trace_id": trace_id, "purged": True}


def janitor_run(max_age_hours: int | None = None) -> Dict[str, Any]:
    settings = get_settings()
    threshold_hours = max_age_hours if max_age_hours is not None else settings.STORAGE_TTL_HOURS
    if not threshold_hours:
        return {"enabled": False, "purged": []}
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=threshold_hours)
    purged: List[str] = []
    # Use costs bucket timestamps as a heuristic of last update time
    for trace_id, entry in list(_costs.items()):
        try:
            updated_at = datetime.fromisoformat(entry.get("updated_at"))
        except Exception:
            continue
        if updated_at < cutoff:
            purge_trace(trace_id)
            purged.append(trace_id)
    return {"enabled": True, "purged": purged, "cutoff": cutoff.isoformat()}

