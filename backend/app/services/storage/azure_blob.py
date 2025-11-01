from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path
import tempfile

import pandas as pd

try:
    from azure.storage.blob import BlobServiceClient  # type: ignore
except Exception:  # pragma: no cover
    BlobServiceClient = None

from app.core.config import get_settings


class AzureBlobBackend:
    name = "azure"

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.AZURE_ENABLED:
            raise RuntimeError("Azure backend is not enabled in settings")
        if BlobServiceClient is None:
            raise RuntimeError("azure-storage-blob is required for Azure backend")
        if self.settings.AZURE_CONNECTION_STRING:
            self.client = BlobServiceClient.from_connection_string(self.settings.AZURE_CONNECTION_STRING)
        else:
            self.client = BlobServiceClient(account_url=None)  # Will fail without MSI/environment; placeholder
        self.container = self.client.get_container_client(self.settings.AZURE_CONTAINER)
        self.prefix = self.settings.AZURE_PREFIX.strip("/")

    def _key(self, trace_id: str, key: str, ext: str) -> str:
        return f"{self.prefix}/{trace_id}/{key}{ext}"

    def put(self, trace_id: str, key: str, value: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if isinstance(value, pd.DataFrame):
            with tempfile.TemporaryDirectory() as td:
                fpath = Path(td) / f"{key}.parquet"
                value.to_parquet(fpath, compression="snappy", index=False)
                blob_name = self._key(trace_id, key, ".parquet")
                with open(fpath, "rb") as fh:
                    self.container.upload_blob(name=blob_name, data=fh, overwrite=True)
                try:
                    from app.services.costs import add_io
                    add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
                except Exception:
                    pass
                return {"backend": self.name, "dtype": "DataFrame", "key": blob_name}
        else:
            with tempfile.TemporaryDirectory() as td:
                fpath = Path(td) / f"{key}.pkl"
                value.to_pickle(fpath) if hasattr(value, "to_pickle") else pd.Series([value]).to_pickle(fpath)
                blob_name = self._key(trace_id, key, ".pkl")
                with open(fpath, "rb") as fh:
                    self.container.upload_blob(name=blob_name, data=fh, overwrite=True)
                try:
                    from app.services.costs import add_io
                    add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
                except Exception:
                    pass
                return {"backend": self.name, "dtype": type(value).__name__, "key": blob_name}

    def get(self, trace_id: str, key: str) -> Any:
        for ext, reader in ((".parquet", pd.read_parquet), (".pkl", pd.read_pickle)):
            blob_name = self._key(trace_id, key, ext)
            blob = self.container.get_blob_client(blob_name)
            try:
                with tempfile.TemporaryDirectory() as td:
                    fpath = Path(td) / f"{key}{ext}"
                    with open(fpath, "wb") as fh:
                        stream = blob.download_blob()
                        fh.write(stream.readall())
                    try:
                        from app.services.costs import add_io
                        add_io(trace_id, bytes_read=Path(fpath).stat().st_size, objects_read=1)
                    except Exception:
                        pass
                    return reader(fpath)
            except Exception:
                continue
        return None

    def delete(self, trace_id: str, key: str) -> None:
        for ext in (".parquet", ".pkl"):
            blob_name = self._key(trace_id, key, ext)
            try:
                self.container.delete_blob(blob_name)
            except Exception:
                pass

    def clear(self, trace_id: str) -> None:
        prefix = f"{self.prefix}/{trace_id}/"
        try:
            blobs = self.container.list_blobs(name_starts_with=prefix)
            for b in blobs:
                try:
                    self.container.delete_blob(b.name)
                except Exception:
                    pass
        except Exception:
            pass

