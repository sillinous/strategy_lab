from __future__ import annotations
from typing import Protocol, Any, Dict, Optional


class BaseStorageBackend(Protocol):
    name: str

    def put(self, trace_id: str, key: str, value: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...

    def get(self, trace_id: str, key: str) -> Any:
        ...

    def delete(self, trace_id: str, key: str) -> None:
        ...

    def clear(self, trace_id: str) -> None:
        ...

