"""
Backtest API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import json
from datetime import datetime

from app.core.database import get_db
from app.models.strategy import Strategy
from app.models.backtest import Backtest
from app.schemas.backtest import (
    BacktestCreate,
    BacktestResponse,
    BacktestDetailResponse,
    BacktestListResponse,
    BacktestMetrics,
    Trade
)
from app.services.data_fetcher import MarketDataFetcher
from app.services.backtester import VectorizedBacktester
from app.utils.exceptions import DataFetchError, BacktestError

router = APIRouter(prefix="/backtests", tags=["Backtests"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=BacktestDetailResponse, status_code=status.HTTP_201_CREATED)
def run_backtest(
    backtest_data: BacktestCreate,
    db: Session = Depends(get_db)
):
    """
    Run a backtest for a strategy
    
    Args:
        backtest_data: Backtest parameters
        db: Database session
        
    Returns:
        Backtest results with metrics and trades
    """
    try:
        logger.info(f"Starting backtest for strategy {backtest_data.strategy_id} on {backtest_data.symbol}")
        
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == backtest_data.strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy with ID {backtest_data.strategy_id} not found"
            )
        
        # Fetch market data
        data_fetcher = MarketDataFetcher()
        try:
            market_data = data_fetcher.fetch_data(
                symbol=backtest_data.symbol,
                start_date=backtest_data.start_date,
                end_date=backtest_data.end_date,
                interval=backtest_data.interval,
                force_refresh=backtest_data.force_refresh
            )
        except DataFetchError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error fetching market data: {str(e)}"
            )
        
        # Run backtest
        backtester = VectorizedBacktester(
            data=market_data,
            initial_capital=backtest_data.initial_capital,
            commission_rate=backtest_data.commission_rate,
            slippage_rate=backtest_data.slippage_rate
        )
        
        strategy_config = json.loads(strategy.config)
        
        try:
            results = backtester.run_backtest(strategy_config)
        except BacktestError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Backtest error: {str(e)}"
            )
        
        # Save backtest to database
        backtest = Backtest(
            strategy_id=backtest_data.strategy_id,
            symbol=backtest_data.symbol,
            start_date=datetime.strptime(backtest_data.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(
                backtest_data.end_date if backtest_data.end_date else datetime.now().strftime("%Y-%m-%d"),
                "%Y-%m-%d"
            ),
            interval=backtest_data.interval,
            initial_capital=backtest_data.initial_capital,
            execution_time=results['execution_time'],
            metrics=json.dumps(results['metrics']),
            trades=json.dumps(results['trades']),
            equity_curve=json.dumps(results['equity_curve']),
            total_return=results['metrics']['total_return'],
            sharpe_ratio=results['metrics']['sharpe_ratio'],
            max_drawdown=results['metrics']['maximum_drawdown'],
            win_rate=results['metrics']['win_rate'],
            num_trades=results['num_trades']
        )
        
        db.add(backtest)
        db.commit()
        db.refresh(backtest)
        
        logger.info(f"Backtest completed and saved with ID: {backtest.id}")
        
        # Convert trades to Trade schema
        trades = [
            Trade(
                entry_date=t['entry_date'],
                exit_date=t['exit_date'],
                entry_price=t['entry_price'],
                exit_price=t['exit_price'],
                return_value=t['return'],
                profit_loss=t['profit_loss'],
                duration=t['duration'],
                type=t['type']
            )
            for t in results['trades']
        ]
        
        # Prepare response
        response = BacktestDetailResponse(
            id=backtest.id,
            strategy_id=backtest.strategy_id,
            symbol=backtest.symbol,
            start_date=backtest.start_date,
            end_date=backtest.end_date,
            interval=backtest.interval,
            initial_capital=backtest.initial_capital,
            executed_at=backtest.executed_at,
            execution_time=backtest.execution_time,
            metrics=BacktestMetrics(**results['metrics']),
            num_trades=backtest.num_trades,
            total_return=backtest.total_return,
            sharpe_ratio=backtest.sharpe_ratio,
            max_drawdown=backtest.max_drawdown,
            win_rate=backtest.win_rate,
            trades=trades,
            equity_curve=results['equity_curve']
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during backtest: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/", response_model=BacktestListResponse)
def list_backtests(
    strategy_id: int = None,
    symbol: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List backtests with optional filtering
    
    Args:
        strategy_id: Filter by strategy ID
        symbol: Filter by symbol
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of backtests
    """
    try:
        query = db.query(Backtest)
        
        if strategy_id is not None:
            query = query.filter(Backtest.strategy_id == strategy_id)
        
        if symbol is not None:
            query = query.filter(Backtest.symbol == symbol.upper())
        
        total = query.count()
        backtests = query.order_by(Backtest.executed_at.desc()).offset(skip).limit(limit).all()
        
        # Convert to response format
        backtest_responses = []
        for bt in backtests:
            backtest_responses.append(
                BacktestResponse(
                    id=bt.id,
                    strategy_id=bt.strategy_id,
                    symbol=bt.symbol,
                    start_date=bt.start_date,
                    end_date=bt.end_date,
                    interval=bt.interval,
                    initial_capital=bt.initial_capital,
                    executed_at=bt.executed_at,
                    execution_time=bt.execution_time,
                    metrics=BacktestMetrics(**json.loads(bt.metrics)),
                    num_trades=bt.num_trades,
                    total_return=bt.total_return,
                    sharpe_ratio=bt.sharpe_ratio,
                    max_drawdown=bt.max_drawdown,
                    win_rate=bt.win_rate
                )
            )
        
        return BacktestListResponse(backtests=backtest_responses, total=total)
        
    except Exception as e:
        logger.error(f"Error listing backtests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing backtests: {str(e)}"
        )


@router.get("/{backtest_id}", response_model=BacktestDetailResponse)
def get_backtest(
    backtest_id: int,
    include_equity_curve: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get detailed backtest results
    
    Args:
        backtest_id: Backtest ID
        include_equity_curve: Whether to include equity curve data
        db: Database session
        
    Returns:
        Detailed backtest results
    """
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest with ID {backtest_id} not found"
        )
    
    # Convert trades to Trade schema
    trades_data = json.loads(backtest.trades) if backtest.trades else []
    trades = [
        Trade(
            entry_date=t['entry_date'],
            exit_date=t['exit_date'],
            entry_price=t['entry_price'],
            exit_price=t['exit_price'],
            return_value=t['return'],
            profit_loss=t['profit_loss'],
            duration=t['duration'],
            type=t['type']
        )
        for t in trades_data
    ]
    
    # Get equity curve if requested
    equity_curve = None
    if include_equity_curve and backtest.equity_curve:
        equity_curve = json.loads(backtest.equity_curve)
    
    return BacktestDetailResponse(
        id=backtest.id,
        strategy_id=backtest.strategy_id,
        symbol=backtest.symbol,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        interval=backtest.interval,
        initial_capital=backtest.initial_capital,
        executed_at=backtest.executed_at,
        execution_time=backtest.execution_time,
        metrics=BacktestMetrics(**json.loads(backtest.metrics)),
        num_trades=backtest.num_trades,
        total_return=backtest.total_return,
        sharpe_ratio=backtest.sharpe_ratio,
        max_drawdown=backtest.max_drawdown,
        win_rate=backtest.win_rate,
        trades=trades,
        equity_curve=equity_curve
    )


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backtest(
    backtest_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a backtest
    
    Args:
        backtest_id: Backtest ID
        db: Database session
    """
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest with ID {backtest_id} not found"
        )
    
    try:
        db.delete(backtest)
        db.commit()
        logger.info(f"Backtest {backtest_id} deleted")
        
    except Exception as e:
        logger.error(f"Error deleting backtest: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting backtest: {str(e)}"
        )
