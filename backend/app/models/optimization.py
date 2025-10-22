
"""
Optimization database model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import json

from app.core.database import Base


class OptimizationRun(Base):
    """
    Optimization run model
    
    Stores optimization attempts and results
    """
    __tablename__ = "optimization_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='CASCADE'), nullable=False)
    
    # Optimization configuration
    optimization_metric = Column(String(100), nullable=False, default='sharpe_ratio')
    max_iterations = Column(Integer, nullable=False)
    
    # Results
    total_tested = Column(Integer, nullable=True)
    best_parameters = Column(Text, nullable=True)  # JSON
    best_metrics = Column(Text, nullable=True)  # JSON
    
    # Statistics
    improvement_percentage = Column(Float, nullable=True)
    execution_time = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='PENDING')  # PENDING, RUNNING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    strategy = relationship("Strategy", backref="optimization_runs")
    
    def __repr__(self):
        return f"<OptimizationRun(id={self.id}, strategy_id={self.strategy_id}, status='{self.status}')>"
    
    @property
    def best_parameters_dict(self):
        """Get best parameters as dictionary"""
        try:
            return json.loads(self.best_parameters) if self.best_parameters else {}
        except:
            return {}
    
    @property
    def best_metrics_dict(self):
        """Get best metrics as dictionary"""
        try:
            return json.loads(self.best_metrics) if self.best_metrics else {}
        except:
            return {}
