from __future__ import annotations
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from app.services.catalog import list_datasets, get_dataset


router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("/datasets")
def list_catalog(kind: Optional[str] = None) -> Dict[str, Any]:
    items = list_datasets(kind)
    return {"items": items, "count": len(items)}


@router.get("/dataset/{kind}/{symbol}/{timeframe}")
def get_catalog_entry(kind: str, symbol: str, timeframe: str) -> Dict[str, Any]:
    ds = get_dataset(kind, symbol, timeframe)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds

