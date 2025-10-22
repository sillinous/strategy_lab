
"""
Technical Indicators Module
Implements SMA, EMA, RSI, MACD, and Bollinger Bands
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging
from app.utils.exceptions import IndicatorCalculationError, InsufficientDataError

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Technical indicators calculator for trading strategies
    All indicators are vectorized using pandas/numpy for optimal performance
    """
    
    @staticmethod
    def sma(data: pd.Series, period: int = 20, column_name: Optional[str] = None) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            data: Price series (typically Close price)
            period: Lookback period for moving average
            column_name: Optional name for the output series
            
        Returns:
            Series containing SMA values
            
        Raises:
            IndicatorCalculationError: If calculation fails
            InsufficientDataError: If insufficient data points
        """
        try:
            if len(data) < period:
                raise InsufficientDataError(
                    f"Insufficient data for SMA calculation. Need at least {period} points, got {len(data)}"
                )
            
            sma_values = data.rolling(window=period, min_periods=period).mean()
            
            if column_name:
                sma_values.name = column_name
            else:
                sma_values.name = f'SMA_{period}'
            
            logger.debug(f"Calculated SMA with period {period}")
            return sma_values
            
        except Exception as e:
            raise IndicatorCalculationError(f"Error calculating SMA: {str(e)}")
    
    @staticmethod
    def ema(data: pd.Series, period: int = 20, column_name: Optional[str] = None) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        EMA applies greater weight to recent prices, making it more responsive
        to new information than SMA.
        
        Args:
            data: Price series (typically Close price)
            period: Lookback period for moving average
            column_name: Optional name for the output series
            
        Returns:
            Series containing EMA values
            
        Raises:
            IndicatorCalculationError: If calculation fails
            InsufficientDataError: If insufficient data points
        """
        try:
            if len(data) < period:
                raise InsufficientDataError(
                    f"Insufficient data for EMA calculation. Need at least {period} points, got {len(data)}"
                )
            
            ema_values = data.ewm(span=period, adjust=False, min_periods=period).mean()
            
            if column_name:
                ema_values.name = column_name
            else:
                ema_values.name = f'EMA_{period}'
            
            logger.debug(f"Calculated EMA with period {period}")
            return ema_values
            
        except Exception as e:
            raise IndicatorCalculationError(f"Error calculating EMA: {str(e)}")
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14, column_name: Optional[str] = None) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        RSI is a momentum oscillator measuring speed and magnitude of price movements.
        Values range from 0 to 100:
        - Above 70: Overbought condition
        - Below 30: Oversold condition
        
        Args:
            data: Price series (typically Close price)
            period: Lookback period (typically 14)
            column_name: Optional name for the output series
            
        Returns:
            Series containing RSI values (0-100)
            
        Raises:
            IndicatorCalculationError: If calculation fails
            InsufficientDataError: If insufficient data points
        """
        try:
            if len(data) < period + 1:
                raise InsufficientDataError(
                    f"Insufficient data for RSI calculation. Need at least {period + 1} points, got {len(data)}"
                )
            
            # Calculate price changes
            delta = data.diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0.0)
            losses = -delta.where(delta < 0, 0.0)
            
            # Calculate average gains and losses using EMA (Wilder's smoothing)
            avg_gains = gains.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
            avg_losses = losses.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
            
            # Calculate RS and RSI
            rs = avg_gains / avg_losses
            rsi_values = 100 - (100 / (1 + rs))
            
            # Handle division by zero (when avg_losses = 0)
            rsi_values = rsi_values.fillna(100)
            
            if column_name:
                rsi_values.name = column_name
            else:
                rsi_values.name = f'RSI_{period}'
            
            logger.debug(f"Calculated RSI with period {period}")
            return rsi_values
            
        except Exception as e:
            raise IndicatorCalculationError(f"Error calculating RSI: {str(e)}")
    
    @staticmethod
    def macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        column_prefix: Optional[str] = None
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Moving Average Convergence Divergence (MACD)
        
        MACD reveals changes in trend strength, direction, momentum, and duration.
        
        Components:
        - MACD Line: Fast EMA - Slow EMA
        - Signal Line: EMA of MACD Line
        - Histogram: MACD Line - Signal Line
        
        Args:
            data: Price series (typically Close price)
            fast_period: Fast EMA period (typically 12)
            slow_period: Slow EMA period (typically 26)
            signal_period: Signal line EMA period (typically 9)
            column_prefix: Optional prefix for column names
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
            
        Raises:
            IndicatorCalculationError: If calculation fails
            InsufficientDataError: If insufficient data points
        """
        try:
            min_required = slow_period + signal_period
            if len(data) < min_required:
                raise InsufficientDataError(
                    f"Insufficient data for MACD calculation. Need at least {min_required} points, got {len(data)}"
                )
            
            # Calculate fast and slow EMAs
            ema_fast = data.ewm(span=fast_period, adjust=False, min_periods=fast_period).mean()
            ema_slow = data.ewm(span=slow_period, adjust=False, min_periods=slow_period).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line
            signal_line = macd_line.ewm(span=signal_period, adjust=False, min_periods=signal_period).mean()
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            # Set names
            prefix = column_prefix if column_prefix else ""
            macd_line.name = f'{prefix}MACD_Line' if prefix else 'MACD_Line'
            signal_line.name = f'{prefix}MACD_Signal' if prefix else 'MACD_Signal'
            histogram.name = f'{prefix}MACD_Histogram' if prefix else 'MACD_Histogram'
            
            logger.debug(f"Calculated MACD with periods {fast_period}/{slow_period}/{signal_period}")
            return macd_line, signal_line, histogram
            
        except Exception as e:
            raise IndicatorCalculationError(f"Error calculating MACD: {str(e)}")
    
    @staticmethod
    def bollinger_bands(
        data: pd.Series,
        period: int = 20,
        num_std: float = 2.0,
        column_prefix: Optional[str] = None
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Bollinger Bands consist of three lines that adapt to volatility,
        providing dynamic support and resistance levels.
        
        Components:
        - Middle Band: SMA
        - Upper Band: Middle Band + (Standard Deviation × num_std)
        - Lower Band: Middle Band - (Standard Deviation × num_std)
        
        Args:
            data: Price series (typically Close price)
            period: Lookback period for SMA and standard deviation (typically 20)
            num_std: Number of standard deviations (typically 2)
            column_prefix: Optional prefix for column names
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
            
        Raises:
            IndicatorCalculationError: If calculation fails
            InsufficientDataError: If insufficient data points
        """
        try:
            if len(data) < period:
                raise InsufficientDataError(
                    f"Insufficient data for Bollinger Bands calculation. Need at least {period} points, got {len(data)}"
                )
            
            # Calculate middle band (SMA)
            middle_band = data.rolling(window=period, min_periods=period).mean()
            
            # Calculate standard deviation
            std_dev = data.rolling(window=period, min_periods=period).std()
            
            # Calculate upper and lower bands
            upper_band = middle_band + (std_dev * num_std)
            lower_band = middle_band - (std_dev * num_std)
            
            # Set names
            prefix = column_prefix if column_prefix else ""
            upper_band.name = f'{prefix}BB_Upper' if prefix else 'BB_Upper'
            middle_band.name = f'{prefix}BB_Middle' if prefix else 'BB_Middle'
            lower_band.name = f'{prefix}BB_Lower' if prefix else 'BB_Lower'
            
            logger.debug(f"Calculated Bollinger Bands with period {period} and {num_std} std devs")
            return upper_band, middle_band, lower_band
            
        except Exception as e:
            raise IndicatorCalculationError(f"Error calculating Bollinger Bands: {str(e)}")
    
    @classmethod
    def calculate_all_indicators(
        cls,
        data: pd.DataFrame,
        price_column: str = 'Close'
    ) -> pd.DataFrame:
        """
        Calculate all available indicators on a dataframe
        
        Args:
            data: DataFrame with OHLCV data
            price_column: Column to use for calculations (default: 'Close')
            
        Returns:
            DataFrame with all indicators added
            
        Raises:
            IndicatorCalculationError: If calculation fails
        """
        try:
            df = data.copy()
            prices = df[price_column]
            
            # SMA indicators
            df['SMA_20'] = cls.sma(prices, period=20)
            df['SMA_50'] = cls.sma(prices, period=50)
            df['SMA_200'] = cls.sma(prices, period=200)
            
            # EMA indicators
            df['EMA_12'] = cls.ema(prices, period=12)
            df['EMA_26'] = cls.ema(prices, period=26)
            df['EMA_50'] = cls.ema(prices, period=50)
            
            # RSI
            df['RSI_14'] = cls.rsi(prices, period=14)
            
            # MACD
            df['MACD_Line'], df['MACD_Signal'], df['MACD_Histogram'] = cls.macd(prices)
            
            # Bollinger Bands
            df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = cls.bollinger_bands(prices)
            
            logger.info(f"Calculated all indicators for {len(df)} data points")
            return df
            
        except Exception as e:
            raise IndicatorCalculationError(f"Error calculating all indicators: {str(e)}")
