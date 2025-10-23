
"""
Pre-built Strategies API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import json

from app.core.database import get_db
from app.models.strategy import Strategy
from app.services.prebuilt_strategies import PrebuiltStrategies, initialize_prebuilt_strategies
from app.schemas.strategy import StrategyResponse

router = APIRouter(prefix="/prebuilt", tags=["Pre-built Strategies"])
logger = logging.getLogger(__name__)


@router.get("/strategies", response_model=List[dict])
def get_prebuilt_strategies():
    """
    Get all available pre-built strategies
    
    Returns:
        List of pre-built strategy configurations
    """
    try:
        strategies = PrebuiltStrategies.get_all_strategies()
        return strategies
        
    except Exception as e:
        logger.error(f"Error getting prebuilt strategies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting prebuilt strategies: {str(e)}"
        )


@router.get("/strategies/{name}")
def get_prebuilt_strategy(name: str):
    """
    Get a specific pre-built strategy by name
    
    Args:
        name: Strategy name
        
    Returns:
        Strategy configuration
    """
    strategy = PrebuiltStrategies.get_by_name(name)
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pre-built strategy '{name}' not found"
        )
    
    return strategy


@router.post("/initialize", status_code=status.HTTP_201_CREATED)
def initialize_strategies(db: Session = Depends(get_db)):
    """
    Initialize database with all pre-built strategies
    
    Args:
        db: Database session
        
    Returns:
        Number of strategies created
    """
    try:
        created_ids = initialize_prebuilt_strategies(db)
        
        return {
            'success': True,
            'message': f'Initialized {len(created_ids)} pre-built strategies',
            'strategy_ids': created_ids
        }
        
    except Exception as e:
        logger.error(f"Error initializing prebuilt strategies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing prebuilt strategies: {str(e)}"
        )


@router.post("/import/{name}", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def import_prebuilt_strategy(name: str, db: Session = Depends(get_db)):
    """
    Import a specific pre-built strategy into user's strategies
    
    Args:
        name: Strategy name to import
        db: Database session
        
    Returns:
        Created strategy
    """
    # Get pre-built strategy
    prebuilt = PrebuiltStrategies.get_by_name(name)
    
    if not prebuilt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pre-built strategy '{name}' not found"
        )
    
    try:
        # Check if already exists
        existing = db.query(Strategy).filter(Strategy.name == prebuilt['name']).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Strategy '{name}' already exists in your library"
            )
        
        # Create strategy
        strategy = Strategy(
            name=prebuilt['name'],
            description=prebuilt['description'],
            config=json.dumps(prebuilt['config']),
            tags=','.join(prebuilt['tags']),
            risk_level=prebuilt['risk_level'],
            timeframe=prebuilt.get('timeframe'),
            version=prebuilt.get('version', '1.0.0'),
            is_active=True
        )
        
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        
        logger.info(f"Imported pre-built strategy: {name}")
        
        # Convert to response
        return StrategyResponse(
            id=strategy.id,
            name=strategy.name,
            description=strategy.description,
            config=strategy.config_dict,
            tags=strategy.tags_list,
            risk_level=strategy.risk_level,
            timeframe=strategy.timeframe,
            version=strategy.version,
            is_active=strategy.is_active,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing prebuilt strategy: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing strategy: {str(e)}"
        )
