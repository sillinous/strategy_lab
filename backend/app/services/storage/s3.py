from __future__ import annotations
from typing import Any, Dict, Optional
from pathlib import Path
import tempfile

import pandas as pd

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover - boto3 may not be installed in all envs
    boto3 = None

from app.core.config import get_settings


class S3Backend:
    name = "s3"

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.S3_ENABLED:
            raise RuntimeError("S3 backend is not enabled in settings")
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3 backend")
        self.s3 = boto3.client("s3", region_name=self.settings.S3_REGION)
        self.bucket = self.settings.S3_BUCKET
        self.prefix = self.settings.S3_PREFIX.strip("/")

    def _key(self, trace_id: str, key: str, ext: str) -> str:
        return f"{self.prefix}/{trace_id}/{key}{ext}"

    def _extra_args(self) -> Dict[str, Any]:
        extra: Dict[str, Any] = {}
        if self.settings.S3_SSE:
            extra["ServerSideEncryption"] = self.settings.S3_SSE
            if self.settings.S3_SSE == "aws:kms" and self.settings.S3_KMS_KEY_ID:
                extra["SSEKMSKeyId"] = self.settings.S3_KMS_KEY_ID
        return extra

    def put(self, trace_id: str, key: str, value: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if isinstance(value, pd.DataFrame):
            with tempfile.TemporaryDirectory() as td:
                fpath = Path(td) / f"{key}.parquet"
                value.to_parquet(fpath, compression="snappy", index=False)
                s3_key = self._key(trace_id, key, ".parquet")
                self.s3.upload_file(str(fpath), self.bucket, s3_key, ExtraArgs=self._extra_args())
                try:
                    from app.services.costs import add_io
                    add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
                except Exception:
                    pass
                return {"backend": self.name, "dtype": "DataFrame", "key": s3_key}
        else:
            # For simplicity, serialize non-DF as pickle via pandas
            with tempfile.TemporaryDirectory() as td:
                fpath = Path(td) / f"{key}.pkl"
                value.to_pickle(fpath) if hasattr(value, "to_pickle") else pd.Series([value]).to_pickle(fpath)
                s3_key = self._key(trace_id, key, ".pkl")
                self.s3.upload_file(str(fpath), self.bucket, s3_key, ExtraArgs=self._extra_args())
                try:
                    from app.services.costs import add_io
                    add_io(trace_id, bytes_written=fpath.stat().st_size, objects_written=1)
                except Exception:
                    pass
                return {"backend": self.name, "dtype": type(value).__name__, "key": s3_key}

    def get(self, trace_id: str, key: str) -> Any:
        # Try parquet, then pickle
        for ext, reader in ((".parquet", pd.read_parquet), (".pkl", pd.read_pickle)):
            s3_key = self._key(trace_id, key, ext)
            try:
                with tempfile.TemporaryDirectory() as td:
                    fpath = Path(td) / f"{key}{ext}"
                    self.s3.download_file(self.bucket, s3_key, str(fpath))
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
            s3_key = self._key(trace_id, key, ext)
            try:
                self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
            except Exception:
                pass

    def clear(self, trace_id: str) -> None:
        paginator = self.s3.get_paginator('list_objects_v2')
        prefix = f"{self.prefix}/{trace_id}/"
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get('Contents', []) or []:
                try:
                    self.s3.delete_object(Bucket=self.bucket, Key=obj['Key'])
                except Exception:
                    pass
