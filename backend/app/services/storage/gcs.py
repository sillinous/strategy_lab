from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path
import tempfile

import pandas as pd

try:
    from google.cloud import storage  # type: ignore
except Exception:  # pragma: no cover
    storage = None

from app.core.config import get_settings


class GCSBackend:
    name = "gcs"

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.GCS_ENABLED:
            raise RuntimeError("GCS backend is not enabled in settings")
        if storage is None:
            raise RuntimeError("google-cloud-storage is required for GCS backend")
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.settings.GCS_BUCKET)
        self.prefix = self.settings.GCS_PREFIX.strip("/")

    def _key(self, trace_id: str, key: str, ext: str) -> str:
        return f"{self.prefix}/{trace_id}/{key}{ext}"

    def put(self, trace_id: str, key: str, value: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if isinstance(value, pd.DataFrame):
            with tempfile.TemporaryDirectory() as td:
                fpath = Path(td) / f"{key}.parquet"
                value.to_parquet(fpath, compression="snappy", index=False)
                blob = self.bucket.blob(self._key(trace_id, key, ".parquet"))
                blob.upload_from_filename(str(fpath))
                try:
                    from app.services.costs import add_io
                    add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
                except Exception:
                    pass
                return {"backend": self.name, "dtype": "DataFrame", "key": blob.name}
        else:
            with tempfile.TemporaryDirectory() as td:
                fpath = Path(td) / f"{key}.pkl"
                value.to_pickle(fpath) if hasattr(value, "to_pickle") else pd.Series([value]).to_pickle(fpath)
                blob = self.bucket.blob(self._key(trace_id, key, ".pkl"))
                blob.upload_from_filename(str(fpath))
                try:
                    from app.services.costs import add_io
                    add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
                except Exception:
                    pass
                return {"backend": self.name, "dtype": type(value).__name__, "key": blob.name}

    def get(self, trace_id: str, key: str) -> Any:
        for ext, reader in ((".parquet", pd.read_parquet), (".pkl", pd.read_pickle)):
            blob = self.bucket.blob(self._key(trace_id, key, ext))
            if blob.exists():
                with tempfile.TemporaryDirectory() as td:
                    fpath = Path(td) / f"{key}{ext}"
                    blob.download_to_filename(str(fpath))
                    try:
                        from app.services.costs import add_io
                        add_io(trace_id, bytes_read=Path(fpath).stat().st_size, objects_read=1)
                    except Exception:
                        pass
                    return reader(fpath)
        return None

    def delete(self, trace_id: str, key: str) -> None:
        for ext in (".parquet", ".pkl"):
            blob = self.bucket.blob(self._key(trace_id, key, ext))
            try:
                blob.delete()
            except Exception:
                pass

    def clear(self, trace_id: str) -> None:
        prefix = f"{self.prefix}/{trace_id}/"
        try:
            for blob in self.client.list_blobs(self.settings.GCS_BUCKET, prefix=prefix):
                try:
                    blob.delete()
                except Exception:
                    pass
        except Exception:
            pass

