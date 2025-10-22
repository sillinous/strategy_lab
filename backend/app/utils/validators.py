
"""
Validation utilities for Strategy Lab
"""
import pandas as pd
from datetime import datetime
from typing import Optional
from app.utils.exceptions import InvalidStrategyError, InsufficientDataError


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Validate that dataframe has required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Raises:
        InsufficientDataError: If DataFrame is empty or missing columns
    """
    if df.empty:
        raise InsufficientDataError("DataFrame is empty")
    
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise InsufficientDataError(f"Missing required columns: {missing_columns}")


def validate_date_range(start_date: str, end_date: Optional[str] = None) -> tuple[datetime, datetime]:
    """
    Validate and parse date range
    
    Args:
        start_date: Start date string
        end_date: End date string (optional)
        
    Returns:
        Tuple of (start_datetime, end_datetime)
        
    Raises:
        ValueError: If dates are invalid
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid start_date format: {start_date}. Use YYYY-MM-DD")
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid end_date format: {end_date}. Use YYYY-MM-DD")
    else:
        end = datetime.now()
    
    if start >= end:
        raise ValueError("start_date must be before end_date")
    
    return start, end


def validate_strategy_config(config: dict) -> None:
    """
    Validate strategy configuration
    
    Args:
        config: Strategy configuration dictionary
        
    Raises:
        InvalidStrategyError: If configuration is invalid
    """
    required_fields = ["indicators", "entry_rules", "exit_rules"]
    
    for field in required_fields:
        if field not in config:
            raise InvalidStrategyError(f"Missing required field: {field}")
    
    if not isinstance(config["indicators"], list):
        raise InvalidStrategyError("'indicators' must be a list")
    
    if len(config["indicators"]) == 0:
        raise InvalidStrategyError("At least one indicator is required")
