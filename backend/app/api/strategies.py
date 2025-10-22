
"""
Strategy API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import json

from app.core.database import get_db
from app.models.strategy import Strategy
from app.schemas.strategy import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyListResponse
)

router = APIRouter(prefix="/strategies", tags=["Strategies"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(
    strategy_data: StrategyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new trading strategy
    
    Args:
        strategy_data: Strategy creation data
        db: Database session
        
    Returns:
        Created strategy
    """
    try:
        logger.info(f"Creating strategy: {strategy_data.name}")
        
        # Create strategy model
        strategy = Strategy(
            name=strategy_data.name,
            description=strategy_data.description,
            config=json.dumps(strategy_data.config.dict()),
            tags=','.join(strategy_data.tags) if strategy_data.tags else None,
            risk_level=strategy_data.risk_level,
            is_active=strategy_data.is_active if strategy_data.is_active is not None else True
        )
        
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        
        logger.info(f"Strategy created with ID: {strategy.id}")
        
        # Convert to response format
        response = StrategyResponse(
            id=strategy.id,
            name=strategy.name,
            description=strategy.description,
            config=strategy_data.config,
            tags=strategy.tags_list,
            risk_level=strategy.risk_level,
            is_active=strategy.is_active,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating strategy: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating strategy: {str(e)}"
        )


@router.get("/", response_model=StrategyListResponse)
def list_strategies(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    List all strategies with optional filtering
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        db: Database session
        
    Returns:
        List of strategies
    """
    try:
        query = db.query(Strategy)
        
        if is_active is not None:
            query = query.filter(Strategy.is_active == is_active)
        
        total = query.count()
        strategies = query.order_by(Strategy.created_at.desc()).offset(skip).limit(limit).all()
        
        # Convert to response format
        strategy_responses = []
        for strategy in strategies:
            strategy_responses.append(
                StrategyResponse(
                    id=strategy.id,
                    name=strategy.name,
                    description=strategy.description,
                    config=json.loads(strategy.config),
                    tags=strategy.tags_list,
                    risk_level=strategy.risk_level,
                    is_active=strategy.is_active,
                    created_at=strategy.created_at,
                    updated_at=strategy.updated_at
                )
            )
        
        return StrategyListResponse(strategies=strategy_responses, total=total)
        
    except Exception as e:
        logger.error(f"Error listing strategies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing strategies: {str(e)}"
        )


@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific strategy by ID
    
    Args:
        strategy_id: Strategy ID
        db: Database session
        
    Returns:
        Strategy details
    """
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with ID {strategy_id} not found"
        )
    
    return StrategyResponse(
        id=strategy.id,
        name=strategy.name,
        description=strategy.description,
        config=json.loads(strategy.config),
        tags=strategy.tags_list,
        risk_level=strategy.risk_level,
        is_active=strategy.is_active,
        created_at=strategy.created_at,
        updated_at=strategy.updated_at
    )


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a strategy
    
    Args:
        strategy_id: Strategy ID
        strategy_data: Strategy update data
        db: Database session
        
    Returns:
        Updated strategy
    """
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with ID {strategy_id} not found"
        )
    
    try:
        # Update fields
        if strategy_data.name is not None:
            strategy.name = strategy_data.name
        if strategy_data.description is not None:
            strategy.description = strategy_data.description
        if strategy_data.config is not None:
            strategy.config = json.dumps(strategy_data.config.dict())
        if strategy_data.tags is not None:
            strategy.tags = ','.join(strategy_data.tags)
        if strategy_data.risk_level is not None:
            strategy.risk_level = strategy_data.risk_level
        if strategy_data.is_active is not None:
            strategy.is_active = strategy_data.is_active
        
        db.commit()
        db.refresh(strategy)
        
        logger.info(f"Strategy {strategy_id} updated")
        
        return StrategyResponse(
            id=strategy.id,
            name=strategy.name,
            description=strategy.description,
            config=json.loads(strategy.config),
            tags=strategy.tags_list,
            risk_level=strategy.risk_level,
            is_active=strategy.is_active,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error updating strategy: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating strategy: {str(e)}"
        )


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a strategy
    
    Args:
        strategy_id: Strategy ID
        db: Database session
    """
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy with ID {strategy_id} not found"
        )
    
    try:
        db.delete(strategy)
        db.commit()
        logger.info(f"Strategy {strategy_id} deleted")
        
    except Exception as e:
        logger.error(f"Error deleting strategy: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting strategy: {str(e)}"
        )
