
"""
Custom exceptions for Strategy Lab
"""


class StrategyLabException(Exception):
    """Base exception for Strategy Lab"""
    pass


class DataFetchError(StrategyLabException):
    """Error fetching market data"""
    pass


class InvalidStrategyError(StrategyLabException):
    """Invalid strategy configuration"""
    pass


class BacktestError(StrategyLabException):
    """Error during backtesting"""
    pass


class InsufficientDataError(StrategyLabException):
    """Insufficient data for analysis"""
    pass


class IndicatorCalculationError(StrategyLabException):
    """Error calculating technical indicator"""
    pass
