
"""
Strategy database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.core.database import Base


class Strategy(Base):
    """
    Trading strategy model
    
    Stores strategy configurations, indicators, entry/exit rules
    """
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Strategy configuration stored as JSON
    config = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Strategy status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Tags for categorization
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Risk parameters
    risk_level = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH
    timeframe = Column(String(20), nullable=True)  # e.g., 1m,5m,15m,1h,4h,1d,1w,1mo
    version = Column(String(20), nullable=True, default="1.0.0")
    
    # Relationship to backtests
    backtests = relationship("Backtest", back_populates="strategy", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, name='{self.name}')>"
    
    @property
    def config_dict(self):
        """Get config as dictionary"""
        try:
            return json.loads(self.config)
        except:
            return {}
    
    @config_dict.setter
    def config_dict(self, value):
        """Set config from dictionary"""
        self.config = json.dumps(value)
    
    @property
    def tags_list(self):
        """Get tags as list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    @tags_list.setter
    def tags_list(self, value):
        """Set tags from list"""
        if isinstance(value, list):
            self.tags = ','.join(value)
        else:
            self.tags = value
