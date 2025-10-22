
"""
Configuration management for Strategy Lab backend
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Settings
    API_TITLE: str = "Strategy Lab API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Enterprise-grade trading strategy development and backtesting platform"
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./strategy_lab.db"
    
    # Cache Settings
    CACHE_DIR: str = "./data/cache"
    CACHE_EXPIRY_DAYS: int = 7
    
    # Data Settings
    DEFAULT_START_DATE: str = "2020-01-01"
    DEFAULT_END_DATE: str = "2024-12-31"
    MAX_DATA_POINTS: int = 10000
    
    # Backtesting Settings
    INITIAL_CAPITAL: float = 100000.0
    COMMISSION_RATE: float = 0.001  # 0.1%
    SLIPPAGE_RATE: float = 0.0005   # 0.05%
    RISK_FREE_RATE: float = 0.02     # 2% annual
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
