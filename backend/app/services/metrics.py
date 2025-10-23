
"""
Performance Metrics Calculator
Calculates key trading strategy performance metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Calculate trading strategy performance metrics
    
    Metrics include:
    - Total Return
    - Annualized Return
    - Sharpe Ratio
    - Sortino Ratio
    - Maximum Drawdown
    - Win Rate
    - Profit Factor
    - Average Win/Loss
    - Number of Trades
    """
    
    def __init__(self, risk_free_rate: float = 0.02, periods_per_year: int = 252):
        """
        Initialize metrics calculator
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
            periods_per_year: Trading periods per year (252 for daily, 52 for weekly)
        """
        self.risk_free_rate = risk_free_rate
        self.periods_per_year = periods_per_year
    
    @staticmethod
    def total_return(returns: pd.Series) -> float:
        """
        Calculate total cumulative return
        
        Args:
            returns: Series of period returns
            
        Returns:
            Total return as decimal (e.g., 0.25 = 25%)
        """
        if len(returns) == 0:
            return 0.0
        
        cumulative_return = (1 + returns).prod() - 1
        return float(cumulative_return)
    
    @staticmethod
    def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate annualized return
        
        Args:
            returns: Series of period returns
            periods_per_year: Number of periods in a year
            
        Returns:
            Annualized return as decimal
        """
        if len(returns) == 0:
            return 0.0
        
        total_return = (1 + returns).prod()
        n_periods = len(returns)
        years = n_periods / periods_per_year
        
        if years <= 0 or total_return <= 0:
            return 0.0
        
        annualized = (total_return ** (1 / years)) - 1
        return float(annualized)
    
    def sharpe_ratio(self, returns: pd.Series) -> float:
        """
        Calculate Sharpe Ratio (risk-adjusted return)
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        
        Args:
            returns: Series of period returns
            
        Returns:
            Annualized Sharpe Ratio
        """
        if len(returns) <= 1:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / self.periods_per_year)
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = np.sqrt(self.periods_per_year) * excess_returns.mean() / excess_returns.std()
        return float(sharpe)
    
    def sortino_ratio(self, returns: pd.Series) -> float:
        """
        Calculate Sortino Ratio (downside risk-adjusted return)
        
        Similar to Sharpe but only considers downside volatility
        
        Args:
            returns: Series of period returns
            
        Returns:
            Annualized Sortino Ratio
        """
        if len(returns) <= 1:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / self.periods_per_year)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        sortino = np.sqrt(self.periods_per_year) * excess_returns.mean() / downside_returns.std()
        return float(sortino)
    
    @staticmethod
    def maximum_drawdown(returns: pd.Series) -> float:
        """
        Calculate maximum drawdown (largest peak-to-trough decline)
        
        Args:
            returns: Series of period returns
            
        Returns:
            Maximum drawdown as decimal (negative value)
        """
        if len(returns) == 0:
            return 0.0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        return float(max_dd)
    
    @staticmethod
    def max_drawdown_duration(returns: pd.Series) -> int:
        """
        Calculate maximum drawdown duration in periods
        
        Args:
            returns: Series of period returns
            
        Returns:
            Maximum number of periods in drawdown
        """
        if len(returns) == 0:
            return 0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        # Find periods in drawdown
        in_drawdown = drawdown < 0
        
        # Calculate consecutive drawdown periods
        max_duration = 0
        current_duration = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_duration += 1
                max_duration = max(max_duration, current_duration)
            else:
                current_duration = 0
        
        return int(max_duration)
    
    @staticmethod
    def win_rate(trade_returns: pd.Series) -> float:
        """
        Calculate win rate (percentage of winning trades)
        
        Args:
            trade_returns: Series of individual trade returns
            
        Returns:
            Win rate as percentage (0-100)
        """
        if len(trade_returns) == 0:
            return 0.0
        
        winning_trades = (trade_returns > 0).sum()
        total_trades = len(trade_returns)
        
        win_rate = (winning_trades / total_trades) * 100
        return float(win_rate)
    
    @staticmethod
    def profit_factor(trade_returns: pd.Series) -> float:
        """
        Calculate profit factor (gross profit / gross loss)
        
        Args:
            trade_returns: Series of individual trade returns
            
        Returns:
            Profit factor (>1 is profitable)
        """
        if len(trade_returns) == 0:
            return 0.0
        
        gross_profit = trade_returns[trade_returns > 0].sum()
        gross_loss = abs(trade_returns[trade_returns < 0].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        pf = gross_profit / gross_loss
        return float(pf)
    
    @staticmethod
    def average_win_loss(trade_returns: pd.Series) -> Dict[str, float]:
        """
        Calculate average winning and losing trade amounts
        
        Args:
            trade_returns: Series of individual trade returns
            
        Returns:
            Dictionary with avg_win and avg_loss
        """
        winning_trades = trade_returns[trade_returns > 0]
        losing_trades = trade_returns[trade_returns < 0]
        
        avg_win = float(winning_trades.mean()) if len(winning_trades) > 0 else 0.0
        avg_loss = float(losing_trades.mean()) if len(losing_trades) > 0 else 0.0
        
        return {
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': abs(avg_win / avg_loss) if avg_loss != 0 else 0.0
        }
    
    @staticmethod
    def volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate annualized volatility (standard deviation)
        
        Args:
            returns: Series of period returns
            periods_per_year: Number of periods in a year
            
        Returns:
            Annualized volatility
        """
        if len(returns) <= 1:
            return 0.0
        
        vol = returns.std() * np.sqrt(periods_per_year)
        return float(vol)
    
    @staticmethod
    def calmar_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        Calculate Calmar Ratio (annualized return / maximum drawdown)
        
        Args:
            returns: Series of period returns
            periods_per_year: Number of periods in a year
            
        Returns:
            Calmar ratio
        """
        if len(returns) == 0:
            return 0.0
        
        annual_return = PerformanceMetrics.annualized_return(returns, periods_per_year)
        max_dd = abs(PerformanceMetrics.maximum_drawdown(returns))
        
        if max_dd == 0:
            return 0.0
        
        calmar = annual_return / max_dd
        return float(calmar)
    
    def calculate_all_metrics(
        self,
        returns: pd.Series,
        trade_returns: Optional[pd.Series] = None,
        initial_capital: float = 100000.0
    ) -> Dict[str, float]:
        """
        Calculate all performance metrics
        
        Args:
            returns: Series of period returns (e.g., daily)
            trade_returns: Series of individual trade returns (optional)
            initial_capital: Initial capital amount
            
        Returns:
            Dictionary containing all metrics
        """
        logger.info(f"Calculating performance metrics for {len(returns)} periods")
        
        # Basic returns metrics
        metrics = {
            'total_return': self.total_return(returns),
            'annualized_return': self.annualized_return(returns, self.periods_per_year),
            'volatility': self.volatility(returns, self.periods_per_year),
            'sharpe_ratio': self.sharpe_ratio(returns),
            'sortino_ratio': self.sortino_ratio(returns),
            'maximum_drawdown': self.maximum_drawdown(returns),
            'max_drawdown_duration': self.max_drawdown_duration(returns),
            'calmar_ratio': self.calmar_ratio(returns, self.periods_per_year),
        }
        
        # Calculate final capital
        final_capital = initial_capital * (1 + metrics['total_return'])
        metrics['initial_capital'] = initial_capital
        metrics['final_capital'] = final_capital
        metrics['profit_loss'] = final_capital - initial_capital
        
        # Trade-level metrics if provided
        if trade_returns is not None and len(trade_returns) > 0:
            metrics['num_trades'] = len(trade_returns)
            metrics['win_rate'] = self.win_rate(trade_returns)
            metrics['profit_factor'] = self.profit_factor(trade_returns)
            
            avg_metrics = self.average_win_loss(trade_returns)
            metrics.update(avg_metrics)
            
            # Additional trade stats
            metrics['num_winning_trades'] = int((trade_returns > 0).sum())
            metrics['num_losing_trades'] = int((trade_returns < 0).sum())
        else:
            # Set default values
            metrics['num_trades'] = 0
            metrics['win_rate'] = 0.0
            metrics['profit_factor'] = 0.0
            metrics['avg_win'] = 0.0
            metrics['avg_loss'] = 0.0
            metrics['win_loss_ratio'] = 0.0
            metrics['num_winning_trades'] = 0
            metrics['num_losing_trades'] = 0
        
        # Rolling Sharpe (30 periods) if enough data
        try:
            if len(returns) >= 30:
                roll = returns.rolling(30)
                roll_sharpe = (roll.mean() / (roll.std() + 1e-12)) * np.sqrt(self.periods_per_year)
                metrics['rolling_sharpe_30'] = float(roll_sharpe.iloc[-1]) if not np.isnan(roll_sharpe.iloc[-1]) else 0.0
        except Exception:
            metrics['rolling_sharpe_30'] = 0.0

        logger.info(
            f"Calculated metrics - Total Return: {metrics['total_return']:.2%}, "
            f"Sharpe: {metrics['sharpe_ratio']:.2f}, Max DD: {metrics['maximum_drawdown']:.2%}"
        )

        return metrics
