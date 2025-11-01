from __future__ import annotations
from typing import Any, Dict, Optional
import os
from pathlib import Path

import pandas as pd


from app.core.config import get_settings


class LocalParquetBackend:
    name = "local"

    def __init__(self, base_path: str | None = None, codec: str | None = None):
        settings = get_settings()
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_BASE)
        self.codec = (codec or settings.LOCAL_STORAGE_CODEC)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _trace_dir(self, trace_id: str) -> Path:
        p = self.base_path / trace_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def put(self, trace_id: str, key: str, value: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        tdir = self._trace_dir(trace_id)
        if isinstance(value, pd.DataFrame):
            fpath = tdir / f"{key}.parquet"
            value.to_parquet(fpath, compression=self.codec, index=False)
            try:
                from app.services.costs import add_io
                add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
            except Exception:
                pass
            return {"backend": self.name, "dtype": "DataFrame", "path": str(fpath)}
        else:
            # Fallback to pickle for arbitrary objects
            fpath = tdir / f"{key}.pkl"
            value.to_pickle(fpath) if hasattr(value, "to_pickle") else pd.Series([value]).to_pickle(fpath)
            try:
                from app.services.costs import add_io
                add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
            except Exception:
                pass
            return {"backend": self.name, "dtype": type(value).__name__, "path": str(fpath)}

    def get(self, trace_id: str, key: str) -> Any:
        tdir = self._trace_dir(trace_id)
        pq = tdir / f"{key}.parquet"
        if pq.exists():
            df = pd.read_parquet(pq)
            try:
                from app.services.costs import add_io
                add_io(trace_id, bytes_read=pq.stat().st_size, objects_read=1)
            except Exception:
                pass
            return df
        pkl = tdir / f"{key}.pkl"
        if pkl.exists():
            obj = pd.read_pickle(pkl)
            try:
                from app.services.costs import add_io
                add_io(trace_id, bytes_read=pkl.stat().st_size, objects_read=1)
            except Exception:
                pass
            return obj
        return None

    def delete(self, trace_id: str, key: str) -> None:
        tdir = self._trace_dir(trace_id)
        for suffix in (".parquet", ".pkl"):
            fp = tdir / f"{key}{suffix}"
            if fp.exists():
                fp.unlink()

    def clear(self, trace_id: str) -> None:
        tdir = self._trace_dir(trace_id)
        if tdir.exists():
            for f in tdir.iterdir():
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                tdir.rmdir()
            except Exception:
                pass

    def list(self, trace_id: str, limit: int = 100, cursor: str | None = None) -> Dict[str, Any]:
        tdir = self._trace_dir(trace_id)
        items = []
        entries = sorted([p for p in tdir.iterdir() if p.is_file()], key=lambda p: p.name)
        start = 0
        if cursor:
            try:
                start = next(i for i, p in enumerate(entries) if p.name > cursor)
            except StopIteration:
                start = len(entries)
        for p in entries[start:start+limit]:
            items.append({
                "key": p.stem,
                "name": p.name,
                "size": p.stat().st_size,
                "backend": self.name,
                "modified_at": p.stat().st_mtime,
            })
        next_cursor = items[-1]["name"] if items and (start + limit) < len(entries) else None
        return {"items": items, "next_cursor": next_cursor}
