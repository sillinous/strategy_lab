from __future__ import annotations
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.services.storage.memory import MemoryBackend
from app.services.storage.local_parquet import LocalParquetBackend

def _maybe_add_s3(backends: Dict[str, Any]) -> None:
    try:
        from app.services.storage.s3 import S3Backend
        backends["s3"] = S3Backend()
    except Exception:
        # Not enabled or boto3 missing; ignore
        pass


def _maybe_add_gcs(backends: Dict[str, Any]) -> None:
    try:
        from app.services.storage.gcs import GCSBackend
        backends["gcs"] = GCSBackend()
    except Exception:
        pass


def _maybe_add_azure(backends: Dict[str, Any]) -> None:
    try:
        from app.services.storage.azure_blob import AzureBlobBackend
        backends["azure"] = AzureBlobBackend()
    except Exception:
        pass


_backends: Dict[str, Any] = {
    "memory": MemoryBackend(),
    "local": LocalParquetBackend(),
}
_maybe_add_s3(_backends)
_maybe_add_gcs(_backends)
_maybe_add_azure(_backends)


def _choose_backend(preferred: Optional[str] = None) -> Any:
    settings = get_settings()
    backend_name = preferred or getattr(settings, "DEFAULT_STORAGE_BACKEND", "local")
    return _backends[backend_name]


def ds_put(trace_id: str, key: str, value: Any, *, backend: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    b = _choose_backend(backend)
    return b.put(trace_id, key, value, meta)


def ds_get(trace_id: str, key: str, *, backend: Optional[str] = None, default: Any = None) -> Any:
    b = _choose_backend(backend)
    res = b.get(trace_id, key)
    return default if res is None else res


def ds_list(trace_id: str) -> Dict[str, Any]:
    items: Dict[str, Any] = {}
    for name, b in _backends.items():
        try:
            if hasattr(b, "list"):
                items[name] = b.list(trace_id, limit=100)
            else:
                items[name] = {"items": [], "next_cursor": None}
        except Exception:
            items[name] = {"error": "unavailable"}
    return items


def ds_delete(trace_id: str, key: str, *, backend: Optional[str] = None) -> None:
    b = _choose_backend(backend)
    b.delete(trace_id, key)


def ds_clear(trace_id: str, *, backend: Optional[str] = None) -> None:
    # Clear across all backends if none specified
    if backend is None:
        for b in _backends.values():
            try:
                b.clear(trace_id)
            except Exception:
                pass
    else:
        b = _choose_backend(backend)
        b.clear(trace_id)
