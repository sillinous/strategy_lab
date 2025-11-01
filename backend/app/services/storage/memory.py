from __future__ import annotations
from typing import Any, Dict, Optional


class MemoryBackend:
    name = "memory"

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def put(self, trace_id: str, key: str, value: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        bucket = self._store.setdefault(trace_id, {})
        bucket[key] = value
        # Update cost tracker
        try:
            import pandas as pd  # local import
            from app.services.costs import add_io
            size = value.memory_usage(deep=True).sum() if isinstance(value, pd.DataFrame) else 0
            add_io(trace_id, bytes_written=size, objects_written=1)
        except Exception:
            pass
        return {"backend": self.name, "dtype": type(value).__name__}

    def get(self, trace_id: str, key: str) -> Any:
        val = self._store.get(trace_id, {}).get(key)
        try:
            import pandas as pd  # local import
            from app.services.costs import add_io
            size = val.memory_usage(deep=True).sum() if isinstance(val, pd.DataFrame) else 0
            add_io(trace_id, bytes_read=size, objects_read=1)
        except Exception:
            pass
        return val

    def delete(self, trace_id: str, key: str) -> None:
        if trace_id in self._store:
            self._store[trace_id].pop(key, None)

    def clear(self, trace_id: str) -> None:
        self._store.pop(trace_id, None)
