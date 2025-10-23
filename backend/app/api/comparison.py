"""
Strategy comparison and summary endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.core.database import get_db
from app.models.backtest import Backtest
from app.models.strategy import Strategy

router = APIRouter(prefix="/compare", tags=["Comparison"])
logger = logging.getLogger(__name__)


@router.get("/strategies")
def compare_strategies(strategy_ids: List[int], db: Session = Depends(get_db)) -> Dict:
    """Compare strategies by their latest backtest summary metrics."""
    try:
        results = []
        for sid in strategy_ids:
            strat = db.query(Strategy).filter(Strategy.id == sid).first()
            if not strat:
                continue
            bt = (
                db.query(Backtest)
                .filter(Backtest.strategy_id == sid)
                .order_by(Backtest.executed_at.desc())
                .first()
            )
            summary = {
                'strategy_id': sid,
                'name': strat.name,
                'risk_level': strat.risk_level,
                'timeframe': strat.timeframe,
                'version': strat.version,
                'metrics': bt.metrics_dict if bt else {},
            }
            results.append(summary)
        return {'count': len(results), 'results': results}
    except Exception as e:
        logger.error(f"Error comparing strategies: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/strategy-card/{strategy_id}")
def strategy_card(strategy_id: int, db: Session = Depends(get_db)) -> Dict:
    """Return a concise card-style summary for a strategy."""
    strat = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strat:
        raise HTTPException(status_code=404, detail="Strategy not found")
    bt = (
        db.query(Backtest)
        .filter(Backtest.strategy_id == strategy_id)
        .order_by(Backtest.executed_at.desc())
        .first()
    )
    metrics = bt.metrics_dict if bt else {}
    card = {
        'id': strat.id,
        'name': strat.name,
        'description': strat.description,
        'risk_level': strat.risk_level,
        'timeframe': strat.timeframe,
        'version': strat.version,
        'tags': strat.tags_list,
        'last_run': bt.executed_at.isoformat() if bt else None,
        'highlights': {
            'total_return': metrics.get('total_return'),
            'sharpe_ratio': metrics.get('sharpe_ratio'),
            'maximum_drawdown': metrics.get('maximum_drawdown'),
            'win_rate': metrics.get('win_rate'),
            'turnover': metrics.get('turnover'),
            'avg_trade_duration_seconds': metrics.get('avg_trade_duration_seconds'),
            'rolling_sharpe_30': metrics.get('rolling_sharpe_30'),
        },
    }
    return card

