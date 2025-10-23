
"""
Strategy Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class IndicatorConfig(BaseModel):
    """Indicator configuration schema"""
    type: str = Field(..., description="Indicator type (SMA, EMA, RSI, MACD, BB)")
    period: Optional[int] = Field(20, description="Period for calculation")
    column: Optional[str] = Field("Close", description="Column to apply indicator to")
    fast_period: Optional[int] = Field(None, description="Fast period for MACD")
    slow_period: Optional[int] = Field(None, description="Slow period for MACD")
    signal_period: Optional[int] = Field(None, description="Signal period for MACD")
    num_std: Optional[float] = Field(None, description="Number of std devs for Bollinger Bands")
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['SMA', 'EMA', 'RSI', 'MACD', 'BB', 'BOLLINGER']
        if v.upper() not in valid_types:
            raise ValueError(f"Invalid indicator type. Must be one of: {valid_types}")
        return v.upper()


class RulesConfig(BaseModel):
    """Entry/Exit rules configuration schema"""
    condition: str = Field(..., description="Condition string (e.g., 'SMA_20 > SMA_50')")
    
    @validator('condition')
    def validate_condition(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Condition must be a non-empty string")
        return v


class StrategyConfig(BaseModel):
    """Strategy configuration schema"""
    indicators: List[IndicatorConfig] = Field(..., description="List of indicators")
    entry_rules: RulesConfig = Field(..., description="Entry rules")
    exit_rules: RulesConfig = Field(..., description="Exit rules")
    
    @validator('indicators')
    def validate_indicators(cls, v):
        if len(v) == 0:
            raise ValueError("At least one indicator is required")
        return v


class StrategyBase(BaseModel):
    """Base strategy schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    config: StrategyConfig = Field(..., description="Strategy configuration")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    risk_level: Optional[str] = Field(None, description="Risk level (LOW, MEDIUM, HIGH)")
    timeframe: Optional[str] = Field(
        None,
        description="Timeframe hint (1m,3m,5m,15m,30m,45m,1h,2h,4h,6h,8h,12h,1d,3d,1w,2w,1mo)"
    )
    version: Optional[str] = Field(None, description="Strategy version semantic")
    is_active: Optional[bool] = Field(True, description="Whether strategy is active")
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v is not None:
            valid_levels = ['LOW', 'MEDIUM', 'HIGH']
            if v.upper() not in valid_levels:
                raise ValueError(f"Risk level must be one of: {valid_levels}")
            return v.upper()
        return v

    @validator('timeframe')
    def validate_timeframe(cls, v):
        if v is not None:
            valid = {'1m','3m','5m','15m','30m','45m','1h','2h','4h','6h','8h','12h','1d','3d','1w','2w','1mo'}
            if v not in valid:
                raise ValueError(f"Timeframe must be one of: {sorted(valid)}")
        return v


class StrategyCreate(StrategyBase):
    """Schema for creating a strategy"""
    pass


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    config: Optional[StrategyConfig] = None
    tags: Optional[List[str]] = None
    risk_level: Optional[str] = None
    timeframe: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None


class StrategyResponse(StrategyBase):
    """Schema for strategy response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    """Schema for list of strategies"""
    strategies: List[StrategyResponse]
    total: int
