
"""
Backtest database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.core.database import Base


class Backtest(Base):
    """
    Backtest results model
    
    Stores backtest execution results, metrics, and trade history
    """
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, index=True)
    
    # Backtest parameters
    symbol = Column(String(50), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    interval = Column(String(10), nullable=False)  # 1d, 1h, etc.
    initial_capital = Column(Float, nullable=False)
    
    # Execution metadata
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_time = Column(Float, nullable=True)  # seconds
    
    # Performance metrics (JSON)
    metrics = Column(Text, nullable=False)
    
    # Trade history (JSON)
    trades = Column(Text, nullable=True)
    
    # Equity curve (JSON) - optional, can be large
    equity_curve = Column(Text, nullable=True)
    
    # Summary metrics for quick access
    total_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    num_trades = Column(Integer, nullable=True)
    
    # Relationship to strategy
    strategy = relationship("Strategy", back_populates="backtests")
    
    def __repr__(self):
        return f"<Backtest(id={self.id}, strategy_id={self.strategy_id}, symbol='{self.symbol}')>"
    
    @property
    def metrics_dict(self):
        """Get metrics as dictionary"""
        try:
            return json.loads(self.metrics)
        except:
            return {}
    
    @metrics_dict.setter
    def metrics_dict(self, value):
        """Set metrics from dictionary"""
        self.metrics = json.dumps(value)
    
    @property
    def trades_list(self):
        """Get trades as list"""
        try:
            return json.loads(self.trades) if self.trades else []
        except:
            return []
    
    @trades_list.setter
    def trades_list(self, value):
        """Set trades from list"""
        self.trades = json.dumps(value) if value else None
    
    @property
    def equity_curve_dict(self):
        """Get equity curve as dictionary"""
        try:
            return json.loads(self.equity_curve) if self.equity_curve else {}
        except:
            return {}
    
    @equity_curve_dict.setter
    def equity_curve_dict(self, value):
        """Set equity curve from dictionary"""
        self.equity_curve = json.dumps(value) if value else None
