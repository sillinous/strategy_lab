
"""
Technical indicators tests
"""
import pytest
import pandas as pd
import numpy as np
from app.services.indicators import TechnicalIndicators
from app.utils.exceptions import IndicatorCalculationError, InsufficientDataError


@pytest.fixture
def sample_data():
    """Create sample price data for testing"""
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    return pd.Series(prices, index=dates, name='Close')


def test_sma_calculation(sample_data):
    """Test SMA calculation"""
    sma = TechnicalIndicators.sma(sample_data, period=20)
    
    assert len(sma) == len(sample_data)
    assert sma.name == 'SMA_20'
    assert not sma.iloc[19:].isna().any()  # No NaN after period


def test_ema_calculation(sample_data):
    """Test EMA calculation"""
    ema = TechnicalIndicators.ema(sample_data, period=20)
    
    assert len(ema) == len(sample_data)
    assert ema.name == 'EMA_20'
    assert not ema.iloc[19:].isna().any()


def test_rsi_calculation(sample_data):
    """Test RSI calculation"""
    rsi = TechnicalIndicators.rsi(sample_data, period=14)
    
    assert len(rsi) == len(sample_data)
    assert rsi.name == 'RSI_14'
    assert (rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all()


def test_macd_calculation(sample_data):
    """Test MACD calculation"""
    macd_line, signal_line, histogram = TechnicalIndicators.macd(sample_data)
    
    assert len(macd_line) == len(sample_data)
    assert len(signal_line) == len(sample_data)
    assert len(histogram) == len(sample_data)
    assert macd_line.name == 'MACD_Line'


def test_bollinger_bands_calculation(sample_data):
    """Test Bollinger Bands calculation"""
    upper, middle, lower = TechnicalIndicators.bollinger_bands(sample_data)
    
    assert len(upper) == len(sample_data)
    assert len(middle) == len(sample_data)
    assert len(lower) == len(sample_data)
    
    # Upper should be above middle, middle above lower
    valid_data = ~upper.isna()
    assert (upper[valid_data] >= middle[valid_data]).all()
    assert (middle[valid_data] >= lower[valid_data]).all()


def test_insufficient_data_error():
    """Test that insufficient data raises error"""
    short_data = pd.Series([1, 2, 3, 4, 5])
    
    with pytest.raises(InsufficientDataError):
        TechnicalIndicators.sma(short_data, period=20)


def test_calculate_all_indicators():
    """Test calculating all indicators at once"""
    df = pd.DataFrame({
        'Open': np.random.rand(100) * 100,
        'High': np.random.rand(100) * 100,
        'Low': np.random.rand(100) * 100,
        'Close': np.random.rand(100) * 100,
        'Volume': np.random.randint(1000, 10000, 100)
    })
    
    result = TechnicalIndicators.calculate_all_indicators(df)
    
    # Check that all indicators were added
    assert 'SMA_20' in result.columns
    assert 'EMA_12' in result.columns
    assert 'RSI_14' in result.columns
    assert 'MACD_Line' in result.columns
    assert 'BB_Upper' in result.columns
