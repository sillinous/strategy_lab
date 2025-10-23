"""
Vectorized Backtesting Engine
High-performance backtesting using pandas vectorization
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
import logging
from datetime import datetime

from app.services.indicators import TechnicalIndicators
from app.services.metrics import PerformanceMetrics
from app.utils.exceptions import BacktestError, InvalidStrategyError, InsufficientDataError
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class VectorizedBacktester:
    """
    Vectorized backtesting engine for trading strategies
    
    Features:
    - High-speed vectorized operations
    - Support for long and short positions
    - Commission and slippage modeling
    - Trade-level analysis
    - Performance metrics calculation
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005
    ):
        """
        Initialize backtester
        
        Args:
            data: DataFrame with OHLCV data
            initial_capital: Starting capital
            commission_rate: Commission per trade (default: 0.1%)
            slippage_rate: Slippage per trade (default: 0.05%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        # Results storage
        self.results = None
        self.trades = []
        self.equity_curve = None
        self.turnover = 0.0
        self.avg_trade_duration_seconds = 0.0
        
        logger.info(f"Initialized VectorizedBacktester with {len(data)} data points")
    
    def _evaluate_condition(self, condition_str: str, data: pd.DataFrame) -> pd.Series:
        """
        Evaluate a condition string against data
        
        Args:
            condition_str: Condition string (e.g., "SMA_20 > SMA_50")
            data: DataFrame with indicator values
            
        Returns:
            Boolean series representing condition results
        """
        try:
            # Create safe evaluation environment with only data columns
            eval_namespace = {col: data[col] for col in data.columns}
            eval_namespace['np'] = np
            eval_namespace['abs'] = abs
            
            # Evaluate condition
            result = eval(condition_str, {"__builtins__": {}}, eval_namespace)
            
            # Ensure result is boolean series
            if not isinstance(result, pd.Series):
                result = pd.Series(result, index=data.index)
            
            return result.fillna(False)
            
        except Exception as e:
            raise InvalidStrategyError(f"Error evaluating condition '{condition_str}': {str(e)}")
    
    def _generate_signals(
        self,
        entry_condition: str,
        exit_condition: str,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Generate entry and exit signals
        
        Args:
            entry_condition: Entry condition string
            exit_condition: Exit condition string
            data: DataFrame with indicator values
            
        Returns:
            DataFrame with Signal and Position columns
        """
        df = data.copy()
        
        # Evaluate conditions
        entry_signal = self._evaluate_condition(entry_condition, df)
        exit_signal = self._evaluate_condition(exit_condition, df)
        
        # Generate signals (1 = long, 0 = flat)
        df['Entry_Signal'] = entry_signal.astype(int)
        df['Exit_Signal'] = exit_signal.astype(int)
        
        # Generate position (maintain position until exit)
        df['Signal'] = 0
        position = 0
        
        signals = []
        for i in range(len(df)):
            if df['Entry_Signal'].iloc[i] == 1 and position == 0:
                position = 1  # Enter long
            elif df['Exit_Signal'].iloc[i] == 1 and position == 1:
                position = 0  # Exit position
            
            signals.append(position)
        
        df['Signal'] = signals
        
        return df
    
    def _calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate strategy returns with commission and slippage
        
        Args:
            data: DataFrame with Signal column
            
        Returns:
            DataFrame with returns and equity curve
        """
        df = data.copy()
        
        # Calculate market returns
        df['Market_Returns'] = df['Close'].pct_change()
        
        # Calculate position changes (trades)
        df['Position_Change'] = df['Signal'].diff()
        
        # Calculate strategy returns (before costs)
        df['Strategy_Returns'] = df['Market_Returns'] * df['Signal'].shift(1)
        
        # Calculate trading costs (commission + slippage)
        df['Trading_Costs'] = 0.0
        df.loc[df['Position_Change'] != 0, 'Trading_Costs'] = self.commission_rate + self.slippage_rate
        
        # Apply trading costs
        df['Net_Returns'] = df['Strategy_Returns'] - df['Trading_Costs']
        
        # Calculate cumulative returns
        df['Cumulative_Returns'] = (1 + df['Net_Returns']).cumprod()
        df['Cumulative_Market_Returns'] = (1 + df['Market_Returns']).cumprod()
        
        # Calculate equity curve
        df['Equity'] = self.initial_capital * df['Cumulative_Returns']
        df['Market_Equity'] = self.initial_capital * df['Cumulative_Market_Returns']
        
        return df
    
    def _extract_trades(self, data: pd.DataFrame) -> List[Dict]:
        """
        Extract individual trades from backtest results
        
        Args:
            data: DataFrame with backtest results
            
        Returns:
            List of trade dictionaries
        """
        trades = []
        in_position = False
        entry_idx = None
        entry_price = None
        
        for idx in range(len(data)):
            position = data['Signal'].iloc[idx]
            position_change = data['Position_Change'].iloc[idx]
            
            # Entry
            if position_change == 1 and not in_position:
                in_position = True
                entry_idx = idx
                entry_price = data['Close'].iloc[idx]
            
            # Exit
            elif position_change == -1 and in_position:
                exit_idx = idx
                exit_price = data['Close'].iloc[idx]
                
                # Calculate trade return
                trade_return = (exit_price - entry_price) / entry_price
                
                # Apply costs
                trade_return -= (self.commission_rate + self.slippage_rate) * 2  # Entry and exit
                
                trades.append({
                    'entry_date': data.index[entry_idx],
                    'exit_date': data.index[exit_idx],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return': trade_return,
                    'profit_loss': trade_return * self.initial_capital,
                    'duration': exit_idx - entry_idx,
                    'type': 'LONG'
                })
                
                in_position = False
        
        return trades
    
    def run_backtest(
        self,
        strategy_config: Dict,
        calculate_indicators: bool = True
    ) -> Dict:
        """
        Run backtest for a strategy configuration
        
        Args:
            strategy_config: Strategy configuration dictionary with:
                - indicators: List of indicator configs
                - entry_rules: Dict with entry condition
                - exit_rules: Dict with exit condition
            calculate_indicators: Whether to calculate indicators (default: True)
            
        Returns:
            Dictionary with backtest results and metrics
            
        Raises:
            BacktestError: If backtest fails
        """
        try:
            logger.info("Starting backtest execution")
            start_time = datetime.now()
            
            # Prepare data
            df = self.data.copy()
            
            if len(df) < 50:
                raise InsufficientDataError("Insufficient data for backtesting (minimum 50 periods)")
            
            # Calculate indicators if requested
            if calculate_indicators:
                df = self._calculate_indicators(df, strategy_config.get('indicators', []))
            
            # Generate signals
            entry_condition = strategy_config['entry_rules'].get('condition')
            exit_condition = strategy_config['exit_rules'].get('condition')
            
            if not entry_condition or not exit_condition:
                raise InvalidStrategyError("Missing entry or exit conditions")
            
            df = self._generate_signals(entry_condition, exit_condition, df)
            
            # Calculate returns
            df = self._calculate_returns(df)
            
            # Extract trades
            self.trades = self._extract_trades(df)
            # Compute turnover and avg trade duration
            try:
                gross_turnover = 0.0
                durations = []
                for t in self.trades:
                    qty = float(t.get('quantity', 0) or 0)
                    ep = float(t.get('entry_price', 0) or 0)
                    xp = float(t.get('exit_price', 0) or 0)
                    if qty and ep:
                        gross_turnover += abs(ep * qty)
                    if qty and xp:
                        gross_turnover += abs(xp * qty)
                    et = t.get('entry_time')
                    xt = t.get('exit_time')
                    if et and xt:
                        durations.append((pd.to_datetime(xt) - pd.to_datetime(et)).total_seconds())
                self.turnover = float(gross_turnover)
                if durations:
                    self.avg_trade_duration_seconds = float(pd.Series(durations).mean())
            except Exception:
                pass
            
            # Calculate metrics
            metrics_calculator = PerformanceMetrics(
                risk_free_rate=settings.RISK_FREE_RATE,
                periods_per_year=252
            )
            
            # Get returns series (drop NaN values)
            returns = df['Net_Returns'].dropna()
            
            # Get trade returns
            trade_returns = pd.Series([t['return'] for t in self.trades]) if self.trades else None
            
            # Calculate all metrics
            metrics = metrics_calculator.calculate_all_metrics(
                returns=returns,
                trade_returns=trade_returns,
                initial_capital=self.initial_capital
            )
            # Attach additional metrics
            metrics['turnover'] = self.turnover
            metrics['avg_trade_duration_seconds'] = self.avg_trade_duration_seconds
            
            # Store results
            self.results = df
            self.equity_curve = df[['Equity', 'Market_Equity']].copy()
            
            # Prepare result dictionary
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'metrics': metrics,
                'num_trades': len(self.trades),
                'trades': self.trades,
                'equity_curve': self.equity_curve.to_dict('index'),
                'execution_time': execution_time,
                'data_points': len(df),
                'date_range': {
                    'start': str(df.index[0]),
                    'end': str(df.index[-1])
                }
            }
            
            logger.info(f"Backtest completed in {execution_time:.2f}s - "
                       f"Return: {metrics['total_return']:.2%}, Trades: {len(self.trades)}")
            
            return result
            
        except (InvalidStrategyError, InsufficientDataError) as e:
            raise BacktestError(str(e))
        except Exception as e:
            logger.error(f"Backtest error: {str(e)}", exc_info=True)
            raise BacktestError(f"Unexpected error during backtest: {str(e)}")
    
    def _calculate_indicators(self, data: pd.DataFrame, indicators_config: List[Dict]) -> pd.DataFrame:
        """
        Calculate indicators based on configuration
        
        Args:
            data: DataFrame with OHLCV data
            indicators_config: List of indicator configurations
            
        Returns:
            DataFrame with calculated indicators
        """
        df = data.copy()
        indicators = TechnicalIndicators()
        
        for config in indicators_config:
            indicator_type = config.get('type', '').upper()
            period = config.get('period', 20)
            column = config.get('column', 'Close')
            
            try:
                if indicator_type == 'SMA':
                    df[f'SMA_{period}'] = indicators.sma(df[column], period)
                
                elif indicator_type == 'EMA':
                    df[f'EMA_{period}'] = indicators.ema(df[column], period)
                
                elif indicator_type == 'RSI':
                    df[f'RSI_{period}'] = indicators.rsi(df[column], period)
                
                elif indicator_type == 'MACD':
                    fast = config.get('fast_period', 12)
                    slow = config.get('slow_period', 26)
                    signal = config.get('signal_period', 9)
                    df['MACD_Line'], df['MACD_Signal'], df['MACD_Histogram'] = \
                        indicators.macd(df[column], fast, slow, signal)
                
                elif indicator_type == 'BOLLINGER' or indicator_type == 'BB':
                    num_std = config.get('num_std', 2.0)
                    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = \
                        indicators.bollinger_bands(df[column], period, num_std)
                
                else:
                    logger.warning(f"Unknown indicator type: {indicator_type}")
            
            except Exception as e:
                logger.error(f"Error calculating {indicator_type}: {str(e)}")
                raise
        
        return df
    
    def get_results_dataframe(self) -> Optional[pd.DataFrame]:
        """Get full backtest results as DataFrame"""
        return self.results
    
    def get_equity_curve(self) -> Optional[pd.DataFrame]:
        """Get equity curve DataFrame"""
        return self.equity_curve
    
    def get_trades(self) -> List[Dict]:
        """Get list of trades"""
        return self.trades
