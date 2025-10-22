
"""
Backtest Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class Trade(BaseModel):
    """Trade schema"""
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    return_value: float = Field(..., alias="return")
    profit_loss: float
    duration: int
    type: str = "LONG"
    
    class Config:
        populate_by_name = True


class BacktestMetrics(BaseModel):
    """Backtest metrics schema"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    maximum_drawdown: float
    max_drawdown_duration: int
    calmar_ratio: float
    initial_capital: float
    final_capital: float
    profit_loss: float
    num_trades: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    win_loss_ratio: float
    num_winning_trades: int
    num_losing_trades: int


class BacktestCreate(BaseModel):
    """Schema for creating a backtest"""
    strategy_id: int = Field(..., description="Strategy ID to backtest")
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, BTCUSDT)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    interval: Optional[str] = Field("1d", description="Data interval")
    initial_capital: Optional[float] = Field(100000.0, description="Initial capital")
    commission_rate: Optional[float] = Field(0.001, description="Commission rate")
    slippage_rate: Optional[float] = Field(0.0005, description="Slippage rate")
    force_refresh: Optional[bool] = Field(False, description="Force refresh data")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Symbol cannot be empty")
        return v.upper()
    
    @validator('interval')
    def validate_interval(cls, v):
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        if v not in valid_intervals:
            raise ValueError(f"Interval must be one of: {valid_intervals}")
        return v


class BacktestResponse(BaseModel):
    """Schema for backtest response"""
    id: int
    strategy_id: int
    symbol: str
    start_date: datetime
    end_date: datetime
    interval: str
    initial_capital: float
    executed_at: datetime
    execution_time: Optional[float]
    metrics: BacktestMetrics
    num_trades: int
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    
    class Config:
        from_attributes = True


class BacktestDetailResponse(BacktestResponse):
    """Schema for detailed backtest response with trades"""
    trades: List[Trade]
    equity_curve: Optional[Dict[str, Any]] = None


class BacktestListResponse(BaseModel):
    """Schema for list of backtests"""
    backtests: List[BacktestResponse]
    total: int
