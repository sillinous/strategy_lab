
"""
Pre-built Trading Strategies
Collection of proven trading strategies that users can use immediately
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PrebuiltStrategies:
    """
    Collection of pre-configured trading strategies
    Each strategy includes indicators, entry/exit rules, and metadata
    """
    
    @staticmethod
    def get_all_strategies() -> List[Dict]:
        """
        Get all pre-built strategies
        
        Returns:
            List of strategy configurations
        """
        return [
            PrebuiltStrategies.sma_crossover(),
            PrebuiltStrategies.rsi_oversold_overbought(),
            PrebuiltStrategies.macd_momentum(),
            PrebuiltStrategies.bollinger_bands_mean_reversion(),
            PrebuiltStrategies.triple_ema_trend(),
            PrebuiltStrategies.rsi_bollinger_combo()
        ]
    
    @staticmethod
    def get_by_name(name: str) -> Dict:
        """
        Get a specific pre-built strategy by name
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy configuration or None
        """
        strategies = PrebuiltStrategies.get_all_strategies()
        for strategy in strategies:
            if strategy['name'].lower() == name.lower():
                return strategy
        return None
    
    @staticmethod
    def sma_crossover() -> Dict:
        """
        Simple Moving Average Crossover Strategy
        
        Classic trend-following strategy where:
        - Buy when fast SMA crosses above slow SMA
        - Sell when fast SMA crosses below slow SMA
        
        Parameters optimizable: fast_period (10-30), slow_period (30-100)
        """
        return {
            'name': 'SMA Crossover',
            'description': 'Classic trend-following strategy using two moving averages. ' \
                          'Buys when fast SMA crosses above slow SMA, sells when it crosses below.',
            'category': 'Trend Following',
            'risk_level': 'MEDIUM',
            'tags': ['trend', 'crossover', 'beginner-friendly'],
            'config': {
                'indicators': [
                    {'type': 'SMA', 'period': 20, 'column': 'Close'},
                    {'type': 'SMA', 'period': 50, 'column': 'Close'}
                ],
                'entry_rules': {
                    'condition': '(SMA_20 > SMA_50) & (SMA_20.shift(1) <= SMA_50.shift(1))',
                    'description': 'Fast SMA crosses above slow SMA'
                },
                'exit_rules': {
                    'condition': '(SMA_20 < SMA_50) & (SMA_20.shift(1) >= SMA_50.shift(1))',
                    'description': 'Fast SMA crosses below slow SMA'
                }
            },
            'optimizable_params': {
                'SMA_fast_period': {'min': 10, 'max': 30, 'step': 5, 'default': 20},
                'SMA_slow_period': {'min': 30, 'max': 100, 'step': 10, 'default': 50}
            },
            'expected_win_rate': 0.45,
            'expected_sharpe': 0.8
        }
    
    @staticmethod
    def rsi_oversold_overbought() -> Dict:
        """
        RSI Oversold/Overbought Strategy
        
        Mean reversion strategy:
        - Buy when RSI crosses above oversold threshold (30)
        - Sell when RSI crosses below overbought threshold (70)
        
        Parameters optimizable: period (10-20), oversold (20-35), overbought (65-80)
        """
        return {
            'name': 'RSI Mean Reversion',
            'description': 'Mean reversion strategy that buys oversold conditions (RSI < 30) ' \
                          'and sells overbought conditions (RSI > 70).',
            'category': 'Mean Reversion',
            'risk_level': 'MEDIUM',
            'tags': ['rsi', 'mean-reversion', 'oscillator'],
            'config': {
                'indicators': [
                    {'type': 'RSI', 'period': 14, 'column': 'Close'}
                ],
                'entry_rules': {
                    'condition': '(RSI_14 > 30) & (RSI_14.shift(1) <= 30)',
                    'description': 'RSI crosses above 30 (oversold recovery)'
                },
                'exit_rules': {
                    'condition': '(RSI_14 > 70)',
                    'description': 'RSI reaches overbought level (70)'
                }
            },
            'optimizable_params': {
                'RSI_period': {'min': 10, 'max': 20, 'step': 2, 'default': 14},
                'oversold_threshold': {'min': 20, 'max': 35, 'step': 5, 'default': 30},
                'overbought_threshold': {'min': 65, 'max': 80, 'step': 5, 'default': 70}
            },
            'expected_win_rate': 0.55,
            'expected_sharpe': 1.0
        }
    
    @staticmethod
    def macd_momentum() -> Dict:
        """
        MACD Momentum Strategy
        
        Momentum strategy:
        - Buy when MACD line crosses above signal line
        - Sell when MACD line crosses below signal line
        
        Parameters optimizable: fast (8-15), slow (20-30), signal (7-11)
        """
        return {
            'name': 'MACD Momentum',
            'description': 'Momentum strategy using MACD crossovers. ' \
                          'Enters when MACD crosses above signal, exits when it crosses below.',
            'category': 'Momentum',
            'risk_level': 'MEDIUM',
            'tags': ['macd', 'momentum', 'trending'],
            'config': {
                'indicators': [
                    {
                        'type': 'MACD',
                        'fast_period': 12,
                        'slow_period': 26,
                        'signal_period': 9,
                        'column': 'Close'
                    }
                ],
                'entry_rules': {
                    'condition': '(MACD_Line > MACD_Signal) & (MACD_Line.shift(1) <= MACD_Signal.shift(1))',
                    'description': 'MACD line crosses above signal line'
                },
                'exit_rules': {
                    'condition': '(MACD_Line < MACD_Signal) & (MACD_Line.shift(1) >= MACD_Signal.shift(1))',
                    'description': 'MACD line crosses below signal line'
                }
            },
            'optimizable_params': {
                'MACD_fast': {'min': 8, 'max': 15, 'step': 1, 'default': 12},
                'MACD_slow': {'min': 20, 'max': 30, 'step': 2, 'default': 26},
                'MACD_signal': {'min': 7, 'max': 11, 'step': 1, 'default': 9}
            },
            'expected_win_rate': 0.48,
            'expected_sharpe': 0.9
        }
    
    @staticmethod
    def bollinger_bands_mean_reversion() -> Dict:
        """
        Bollinger Bands Mean Reversion Strategy
        
        Mean reversion strategy:
        - Buy when price touches lower band
        - Sell when price touches upper band
        
        Parameters optimizable: period (15-25), num_std (1.5-2.5)
        """
        return {
            'name': 'Bollinger Bands Mean Reversion',
            'description': 'Mean reversion strategy that buys at lower Bollinger Band ' \
                          'and sells at upper band, betting on price returning to mean.',
            'category': 'Mean Reversion',
            'risk_level': 'MEDIUM',
            'tags': ['bollinger', 'mean-reversion', 'volatility'],
            'config': {
                'indicators': [
                    {'type': 'BOLLINGER', 'period': 20, 'num_std': 2.0, 'column': 'Close'}
                ],
                'entry_rules': {
                    'condition': '(Close <= BB_Lower)',
                    'description': 'Price touches or goes below lower Bollinger Band'
                },
                'exit_rules': {
                    'condition': '(Close >= BB_Upper)',
                    'description': 'Price touches or goes above upper Bollinger Band'
                }
            },
            'optimizable_params': {
                'BB_period': {'min': 15, 'max': 25, 'step': 5, 'default': 20},
                'BB_std_dev': {'min': 1.5, 'max': 2.5, 'step': 0.25, 'default': 2.0}
            },
            'expected_win_rate': 0.58,
            'expected_sharpe': 1.1
        }
    
    @staticmethod
    def triple_ema_trend() -> Dict:
        """
        Triple EMA Trend Strategy
        
        Advanced trend-following using three EMAs:
        - Buy when short > medium > long (uptrend alignment)
        - Sell when short < medium < long (downtrend alignment)
        
        Parameters optimizable: short (5-15), medium (15-30), long (30-60)
        """
        return {
            'name': 'Triple EMA Trend',
            'description': 'Advanced trend strategy using three EMAs. ' \
                          'Enters when all EMAs align in trend direction.',
            'category': 'Trend Following',
            'risk_level': 'LOW',
            'tags': ['ema', 'trend', 'multi-timeframe'],
            'config': {
                'indicators': [
                    {'type': 'EMA', 'period': 8, 'column': 'Close'},
                    {'type': 'EMA', 'period': 21, 'column': 'Close'},
                    {'type': 'EMA', 'period': 50, 'column': 'Close'}
                ],
                'entry_rules': {
                    'condition': '(EMA_8 > EMA_21) & (EMA_21 > EMA_50)',
                    'description': 'All EMAs aligned bullish (fast > medium > slow)'
                },
                'exit_rules': {
                    'condition': '(EMA_8 < EMA_21) & (EMA_21 < EMA_50)',
                    'description': 'All EMAs aligned bearish (fast < medium < slow)'
                }
            },
            'optimizable_params': {
                'EMA_short': {'min': 5, 'max': 15, 'step': 2, 'default': 8},
                'EMA_medium': {'min': 15, 'max': 30, 'step': 3, 'default': 21},
                'EMA_long': {'min': 30, 'max': 60, 'step': 10, 'default': 50}
            },
            'expected_win_rate': 0.42,
            'expected_sharpe': 0.75
        }
    
    @staticmethod
    def rsi_bollinger_combo() -> Dict:
        """
        RSI + Bollinger Bands Combo Strategy
        
        Combined mean reversion strategy:
        - Buy when RSI < 30 AND price < lower Bollinger Band
        - Sell when RSI > 70 OR price > upper Bollinger Band
        
        Parameters optimizable: rsi_period (10-20), bb_period (15-25), rsi_oversold (20-35)
        """
        return {
            'name': 'RSI + Bollinger Combo',
            'description': 'Powerful mean reversion strategy combining RSI and Bollinger Bands. ' \
                          'Buys only when both indicators show oversold conditions.',
            'category': 'Mean Reversion',
            'risk_level': 'LOW',
            'tags': ['rsi', 'bollinger', 'combo', 'mean-reversion'],
            'config': {
                'indicators': [
                    {'type': 'RSI', 'period': 14, 'column': 'Close'},
                    {'type': 'BOLLINGER', 'period': 20, 'num_std': 2.0, 'column': 'Close'}
                ],
                'entry_rules': {
                    'condition': '(RSI_14 < 30) & (Close <= BB_Lower)',
                    'description': 'RSI oversold AND price at lower Bollinger Band'
                },
                'exit_rules': {
                    'condition': '(RSI_14 > 70) | (Close >= BB_Upper)',
                    'description': 'RSI overbought OR price at upper Bollinger Band'
                }
            },
            'optimizable_params': {
                'RSI_period': {'min': 10, 'max': 20, 'step': 2, 'default': 14},
                'BB_period': {'min': 15, 'max': 25, 'step': 5, 'default': 20},
                'RSI_oversold': {'min': 20, 'max': 35, 'step': 5, 'default': 30},
                'RSI_overbought': {'min': 65, 'max': 80, 'step': 5, 'default': 70}
            },
            'expected_win_rate': 0.62,
            'expected_sharpe': 1.3
        }


def initialize_prebuilt_strategies(db_session) -> List:
    """
    Initialize database with pre-built strategies if they don't exist
    
    Args:
        db_session: Database session
        
    Returns:
        List of created strategy IDs
    """
    from app.models.strategy import Strategy
    import json
    
    strategies = PrebuiltStrategies.get_all_strategies()
    created_ids = []
    
    for strategy_data in strategies:
        # Check if strategy already exists
        existing = db_session.query(Strategy).filter(
            Strategy.name == strategy_data['name']
        ).first()
        
        if not existing:
            strategy = Strategy(
                name=strategy_data['name'],
                description=strategy_data['description'],
                config=json.dumps(strategy_data['config']),
                tags=','.join(strategy_data['tags']),
                risk_level=strategy_data['risk_level'],
                is_active=True
            )
            db_session.add(strategy)
            db_session.flush()
            created_ids.append(strategy.id)
            logger.info(f"Created pre-built strategy: {strategy_data['name']}")
        else:
            logger.info(f"Pre-built strategy already exists: {strategy_data['name']}")
    
    db_session.commit()
    return created_ids
