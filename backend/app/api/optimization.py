
"""
Strategy Optimization API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import json

from app.core.database import get_db
from app.models.strategy import Strategy
from app.models.optimization import OptimizationRun
from app.services.optimizer import StrategyOptimizer
from app.services.data_fetcher import MarketDataFetcher
from app.services.prebuilt_strategies import PrebuiltStrategies

router = APIRouter(prefix="/optimization", tags=["Optimization"])
logger = logging.getLogger(__name__)


@router.post("/optimize/{strategy_id}")
def optimize_strategy(
    strategy_id: int,
    symbol: str = 'AAPL',
    period: str = '1y',
    optimization_metric: str = 'sharpe_ratio',
    max_iterations: int = 50,
    db: Session = Depends(get_db)
):
    """
    Optimize a strategy by testing parameter variations
    
    Args:
        strategy_id: Strategy ID to optimize
        symbol: Symbol to test on (default: AAPL)
        period: Time period for testing (default: 1y)
        optimization_metric: Metric to optimize (default: sharpe_ratio)
        max_iterations: Maximum number of variations to test (default: 50)
        db: Database session
        
    Returns:
        Optimization results
    """
    try:
        # Get strategy
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_id} not found"
            )
        
        logger.info(f"Starting optimization for strategy {strategy_id}: {strategy.name}")
        
        # Create optimization run record
        opt_run = OptimizationRun(
            strategy_id=strategy_id,
            optimization_metric=optimization_metric,
            max_iterations=max_iterations,
            status='RUNNING'
        )
        db.add(opt_run)
        db.commit()
        db.refresh(opt_run)
        
        # Fetch market data
        data_fetcher = MarketDataFetcher()
        market_data = data_fetcher.fetch_data(symbol, period=period)
        
        # Prepare strategy config
        strategy_config = {
            'name': strategy.name,
            'config': strategy.config_dict,
            'optimizable_params': {}
        }
        
        # Try to get optimizable params from prebuilt strategies
        prebuilt = PrebuiltStrategies.get_by_name(strategy.name)
        if prebuilt:
            strategy_config['optimizable_params'] = prebuilt['optimizable_params']
        
        # Run optimization
        optimizer = StrategyOptimizer()
        optimization_result = optimizer.optimize_strategy(
            strategy_config,
            market_data,
            optimization_metric=optimization_metric,
            max_iterations=max_iterations,
            top_n=5
        )
        
        if optimization_result['success']:
            # Update optimization run record
            best_strategy = optimization_result['top_strategies'][0]
            
            opt_run.status = 'COMPLETED'
            opt_run.total_tested = optimization_result['total_tested']
            opt_run.best_parameters = json.dumps(best_strategy['parameters'])
            opt_run.best_metrics = json.dumps(best_strategy['metrics'])
            opt_run.execution_time = optimization_result['execution_time']
            opt_run.completed_at = datetime.utcnow()
            
            # Calculate improvement
            if optimization_result['statistics']:
                opt_run.improvement_percentage = (
                    optimization_result['statistics'].get('improvement', 0) * 100
                )
            
            db.commit()
            
            logger.info(f"Optimization completed for strategy {strategy_id}")
            
            return {
                'success': True,
                'optimization_run_id': opt_run.id,
                'strategy_id': strategy_id,
                'strategy_name': strategy.name,
                'results': optimization_result
            }
        else:
            # Update optimization run as failed
            opt_run.status = 'FAILED'
            opt_run.error_message = optimization_result.get('error', 'Unknown error')
            opt_run.completed_at = datetime.utcnow()
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=optimization_result.get('error', 'Optimization failed')
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Optimization error: {str(e)}", exc_info=True)
        
        # Update optimization run as failed if it exists
        if 'opt_run' in locals():
            opt_run.status = 'FAILED'
            opt_run.error_message = str(e)
            opt_run.completed_at = datetime.utcnow()
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization error: {str(e)}"
        )


@router.post("/autonomous-improve/{strategy_id}")
def autonomous_improve_strategy(
    strategy_id: int,
    symbol: str = 'AAPL',
    period: str = '1y',
    max_generations: int = 3,
    db: Session = Depends(get_db)
):
    """
    Autonomously improve a strategy over multiple generations
    
    Args:
        strategy_id: Strategy ID to improve
        symbol: Symbol to test on
        period: Time period for testing
        max_generations: Number of evolution cycles
        db: Database session
        
    Returns:
        Results of autonomous improvement
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_id} not found"
            )
        
        logger.info(f"Starting autonomous improvement for strategy {strategy_id}")
        
        # Run autonomous improvement
        optimizer = StrategyOptimizer()
        result = optimizer.autonomous_improve(
            strategy_id,
            db,
            symbol=symbol,
            period=period,
            max_generations=max_generations
        )
        
        if result['success']:
            logger.info(f"Autonomous improvement completed - {result['total_generations']} generations")
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Autonomous improvement failed')
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Autonomous improvement error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/runs/{strategy_id}")
def get_optimization_runs(
    strategy_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get optimization runs for a strategy
    
    Args:
        strategy_id: Strategy ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of optimization runs
    """
    try:
        runs = db.query(OptimizationRun).filter(
            OptimizationRun.strategy_id == strategy_id
        ).order_by(
            OptimizationRun.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            'strategy_id': strategy_id,
            'runs': [
                {
                    'id': run.id,
                    'optimization_metric': run.optimization_metric,
                    'status': run.status,
                    'total_tested': run.total_tested,
                    'best_parameters': run.best_parameters_dict,
                    'best_metrics': run.best_metrics_dict,
                    'improvement_percentage': run.improvement_percentage,
                    'execution_time': run.execution_time,
                    'created_at': run.created_at.isoformat(),
                    'completed_at': run.completed_at.isoformat() if run.completed_at else None,
                    'error_message': run.error_message
                }
                for run in runs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization runs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting optimization runs: {str(e)}"
        )


@router.get("/run/{run_id}")
def get_optimization_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific optimization run
    
    Args:
        run_id: Optimization run ID
        db: Database session
        
    Returns:
        Optimization run details
    """
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization run {run_id} not found"
        )
    
    return {
        'id': run.id,
        'strategy_id': run.strategy_id,
        'strategy_name': run.strategy.name,
        'optimization_metric': run.optimization_metric,
        'status': run.status,
        'max_iterations': run.max_iterations,
        'total_tested': run.total_tested,
        'best_parameters': run.best_parameters_dict,
        'best_metrics': run.best_metrics_dict,
        'improvement_percentage': run.improvement_percentage,
        'execution_time': run.execution_time,
        'created_at': run.created_at.isoformat(),
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'error_message': run.error_message
    }
