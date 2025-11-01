from __future__ import annotations
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

from app.core.config import get_settings


def _catalog_dir() -> Path:
    s = get_settings()
    p = Path(s.LOCAL_STORAGE_BASE) / "catalog"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _dataset_path(kind: str, symbol: str, timeframe: str) -> Path:
    symbol_sanitized = symbol.replace("/", "-")
    return _catalog_dir() / f"{kind}__{symbol_sanitized}__{timeframe}.json"


def register_partitions(kind: str, symbol: str, timeframe: str, partitions: List[str]) -> Dict[str, Any]:
    path = _dataset_path(kind, symbol, timeframe)
    entry = {"kind": kind, "symbol": symbol, "timeframe": timeframe, "partitions": partitions, "updated_at": datetime.utcnow().isoformat()}
    if path.exists():
        try:
            old = json.loads(path.read_text())
            # merge unique partitions
            plist = list(dict.fromkeys((old.get("partitions", []) + partitions)))
            entry["partitions"] = plist
        except Exception:
            pass
    path.write_text(json.dumps(entry))
    return entry


def get_dataset(kind: str, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
    path = _dataset_path(kind, symbol, timeframe)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def list_datasets(kind: Optional[str] = None) -> List[Dict[str, Any]]:
    datasets: List[Dict[str, Any]] = []
    for f in _catalog_dir().glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if not kind or data.get("kind") == kind:
                datasets.append(data)
        except Exception:
            continue
    return datasets

