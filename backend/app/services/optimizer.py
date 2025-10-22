
"""
Autonomous Strategy Optimizer
Automatically tweaks and improves trading strategies through systematic parameter optimization
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import itertools
import json

from app.services.backtester import VectorizedBacktester
from app.services.data_fetcher import MarketDataFetcher
from app.services.prebuilt_strategies import PrebuiltStrategies
from app.utils.exceptions import BacktestError

logger = logging.getLogger(__name__)


class StrategyOptimizer:
    """
    Autonomous strategy optimizer that:
    1. Takes a base strategy
    2. Generates parameter variations
    3. Backtests all variations
    4. Identifies best performing strategies
    5. Creates evolved strategies
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005
    ):
        """
        Initialize optimizer
        
        Args:
            initial_capital: Starting capital for backtests
            commission_rate: Commission per trade
            slippage_rate: Slippage per trade
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
    def optimize_strategy(
        self,
        strategy_config: Dict,
        market_data: pd.DataFrame,
        optimization_metric: str = 'sharpe_ratio',
        max_iterations: int = 50,
        top_n: int = 5
    ) -> Dict:
        """
        Optimize a strategy by testing parameter variations
        
        Args:
            strategy_config: Base strategy configuration
            market_data: Historical market data
            optimization_metric: Metric to optimize ('sharpe_ratio', 'total_return', 'win_rate')
            max_iterations: Maximum number of variations to test
            top_n: Number of top strategies to return
            
        Returns:
            Dictionary with optimization results
        """
        try:
            logger.info(f"Starting strategy optimization (max iterations: {max_iterations})")
            start_time = datetime.now()
            
            # Get optimizable parameters
            optimizable_params = strategy_config.get('optimizable_params', {})
            
            if not optimizable_params:
                logger.warning("No optimizable parameters found - using original strategy")
                return self._optimize_without_params(strategy_config, market_data)
            
            # Generate parameter combinations
            param_combinations = self._generate_parameter_combinations(
                optimizable_params,
                max_combinations=max_iterations
            )
            
            logger.info(f"Generated {len(param_combinations)} parameter combinations")
            
            # Test each combination
            results = []
            for i, params in enumerate(param_combinations):
                try:
                    # Create modified strategy config
                    modified_config = self._apply_parameters(strategy_config, params)
                    
                    # Run backtest
                    backtester = VectorizedBacktester(
                        market_data,
                        self.initial_capital,
                        self.commission_rate,
                        self.slippage_rate
                    )
                    
                    backtest_result = backtester.run_backtest(modified_config['config'])
                    
                    # Store results
                    if backtest_result['success']:
                        results.append({
                            'parameters': params,
                            'metrics': backtest_result['metrics'],
                            'num_trades': backtest_result['num_trades'],
                            'config': modified_config['config']
                        })
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Completed {i + 1}/{len(param_combinations)} backtests")
                        
                except Exception as e:
                    logger.warning(f"Backtest failed for params {params}: {str(e)}")
                    continue
            
            # Sort by optimization metric
            results.sort(
                key=lambda x: x['metrics'].get(optimization_metric, -float('inf')),
                reverse=True
            )
            
            # Get top N results
            top_results = results[:top_n]
            
            # Calculate statistics
            optimization_stats = self._calculate_optimization_stats(
                results,
                optimization_metric
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Optimization completed in {execution_time:.2f}s - "
                       f"Best {optimization_metric}: {top_results[0]['metrics'][optimization_metric]:.4f}")
            
            return {
                'success': True,
                'base_strategy': strategy_config.get('name', 'Custom Strategy'),
                'optimization_metric': optimization_metric,
                'total_tested': len(results),
                'top_strategies': top_results,
                'statistics': optimization_stats,
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_parameter_combinations(
        self,
        optimizable_params: Dict,
        max_combinations: int = 50
    ) -> List[Dict]:
        """
        Generate parameter combinations for testing
        
        Args:
            optimizable_params: Dictionary of parameter ranges
            max_combinations: Maximum number of combinations to generate
            
        Returns:
            List of parameter dictionaries
        """
        # Create parameter ranges
        param_ranges = {}
        for param_name, param_config in optimizable_params.items():
            min_val = param_config['min']
            max_val = param_config['max']
            step = param_config.get('step', 1)
            
            # Generate range
            if isinstance(min_val, float) or isinstance(step, float):
                param_ranges[param_name] = np.arange(min_val, max_val + step, step).tolist()
            else:
                param_ranges[param_name] = list(range(min_val, max_val + step, step))
        
        # Generate all combinations
        param_names = list(param_ranges.keys())
        param_values = [param_ranges[name] for name in param_names]
        
        all_combinations = list(itertools.product(*param_values))
        
        # Limit combinations
        if len(all_combinations) > max_combinations:
            # Sample randomly
            indices = np.random.choice(
                len(all_combinations),
                size=max_combinations,
                replace=False
            )
            all_combinations = [all_combinations[i] for i in indices]
        
        # Convert to list of dictionaries
        combinations = []
        for combo in all_combinations:
            combinations.append(dict(zip(param_names, combo)))
        
        return combinations
    
    def _apply_parameters(self, strategy_config: Dict, parameters: Dict) -> Dict:
        """
        Apply parameter values to strategy configuration
        
        Args:
            strategy_config: Base strategy configuration
            parameters: Parameter values to apply
            
        Returns:
            Modified strategy configuration
        """
        modified_config = json.loads(json.dumps(strategy_config))  # Deep copy
        
        # Update indicator parameters
        for indicator in modified_config['config']['indicators']:
            indicator_type = indicator['type']
            
            # Handle different parameter naming patterns
            for param_name, param_value in parameters.items():
                # SMA/EMA parameters
                if 'SMA_fast_period' in param_name and indicator_type == 'SMA':
                    if indicator.get('period', 0) < 30:  # Assume this is fast SMA
                        indicator['period'] = int(param_value)
                elif 'SMA_slow_period' in param_name and indicator_type == 'SMA':
                    if indicator.get('period', 0) >= 30:  # Assume this is slow SMA
                        indicator['period'] = int(param_value)
                
                # RSI parameters
                elif 'RSI_period' in param_name and indicator_type == 'RSI':
                    indicator['period'] = int(param_value)
                
                # MACD parameters
                elif 'MACD_fast' in param_name and indicator_type == 'MACD':
                    indicator['fast_period'] = int(param_value)
                elif 'MACD_slow' in param_name and indicator_type == 'MACD':
                    indicator['slow_period'] = int(param_value)
                elif 'MACD_signal' in param_name and indicator_type == 'MACD':
                    indicator['signal_period'] = int(param_value)
                
                # Bollinger Bands parameters
                elif 'BB_period' in param_name and indicator_type in ['BOLLINGER', 'BB']:
                    indicator['period'] = int(param_value)
                elif 'BB_std_dev' in param_name and indicator_type in ['BOLLINGER', 'BB']:
                    indicator['num_std'] = float(param_value)
                
                # EMA parameters
                elif 'EMA_short' in param_name and indicator_type == 'EMA':
                    if indicator.get('period', 0) < 20:
                        indicator['period'] = int(param_value)
                elif 'EMA_medium' in param_name and indicator_type == 'EMA':
                    if 15 <= indicator.get('period', 0) < 35:
                        indicator['period'] = int(param_value)
                elif 'EMA_long' in param_name and indicator_type == 'EMA':
                    if indicator.get('period', 0) >= 35:
                        indicator['period'] = int(param_value)
        
        # Update entry/exit rule thresholds if applicable
        for param_name, param_value in parameters.items():
            if 'threshold' in param_name.lower():
                # Update condition strings with new thresholds
                entry_condition = modified_config['config']['entry_rules']['condition']
                exit_condition = modified_config['config']['exit_rules']['condition']
                
                if 'oversold' in param_name.lower():
                    entry_condition = entry_condition.replace('30', str(int(param_value)))
                    modified_config['config']['entry_rules']['condition'] = entry_condition
                elif 'overbought' in param_name.lower():
                    exit_condition = exit_condition.replace('70', str(int(param_value)))
                    modified_config['config']['exit_rules']['condition'] = exit_condition
        
        return modified_config
    
    def _calculate_optimization_stats(
        self,
        results: List[Dict],
        optimization_metric: str
    ) -> Dict:
        """
        Calculate statistics about optimization results
        
        Args:
            results: List of backtest results
            optimization_metric: Metric being optimized
            
        Returns:
            Statistics dictionary
        """
        if not results:
            return {}
        
        metric_values = [r['metrics'].get(optimization_metric, 0) for r in results]
        
        return {
            'mean': float(np.mean(metric_values)),
            'median': float(np.median(metric_values)),
            'std': float(np.std(metric_values)),
            'min': float(np.min(metric_values)),
            'max': float(np.max(metric_values)),
            'improvement': float(np.max(metric_values) - np.mean(metric_values))
        }
    
    def _optimize_without_params(
        self,
        strategy_config: Dict,
        market_data: pd.DataFrame
    ) -> Dict:
        """
        Handle optimization when no parameters are available
        Just runs single backtest and returns result
        """
        backtester = VectorizedBacktester(
            market_data,
            self.initial_capital,
            self.commission_rate,
            self.slippage_rate
        )
        
        result = backtester.run_backtest(strategy_config['config'])
        
        return {
            'success': True,
            'base_strategy': strategy_config.get('name', 'Custom Strategy'),
            'optimization_metric': 'sharpe_ratio',
            'total_tested': 1,
            'top_strategies': [{
                'parameters': {},
                'metrics': result['metrics'],
                'num_trades': result['num_trades'],
                'config': strategy_config['config']
            }],
            'statistics': {},
            'execution_time': result.get('execution_time', 0)
        }
    
    def create_evolved_strategy(
        self,
        base_strategy_name: str,
        optimized_config: Dict,
        performance_metrics: Dict,
        generation: int = 1
    ) -> Dict:
        """
        Create a new evolved strategy from optimization results
        
        Args:
            base_strategy_name: Original strategy name
            optimized_config: Optimized configuration
            performance_metrics: Performance metrics of optimized strategy
            generation: Generation number
            
        Returns:
            New strategy dictionary
        """
        evolved_name = f"{base_strategy_name} (Gen {generation})"
        
        return {
            'name': evolved_name,
            'description': f"Autonomous evolution of {base_strategy_name}. "
                          f"Optimized for Sharpe Ratio: {performance_metrics.get('sharpe_ratio', 0):.2f}",
            'config': optimized_config,
            'tags': ['evolved', 'optimized', f'gen{generation}'],
            'risk_level': 'MEDIUM',
            'is_active': True,
            'parent_strategy': base_strategy_name,
            'generation': generation,
            'performance_snapshot': performance_metrics
        }
    
    def autonomous_improve(
        self,
        strategy_id: int,
        db_session,
        symbol: str = 'AAPL',
        period: str = '1y',
        max_generations: int = 3
    ) -> Dict:
        """
        Autonomously improve a strategy over multiple generations
        
        Args:
            strategy_id: Strategy ID to improve
            db_session: Database session
            symbol: Symbol to test on
            period: Time period for testing
            max_generations: Number of evolution cycles
            
        Returns:
            Results of autonomous improvement
        """
        from app.models.strategy import Strategy
        
        try:
            # Get base strategy
            strategy = db_session.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            # Fetch market data
            data_fetcher = MarketDataFetcher()
            market_data = data_fetcher.fetch_data(symbol, period=period)
            
            base_config = {
                'name': strategy.name,
                'config': strategy.config_dict,
                'optimizable_params': {}
            }
            
            # Try to get optimizable params from prebuilt strategies
            prebuilt = PrebuiltStrategies.get_by_name(strategy.name)
            if prebuilt:
                base_config['optimizable_params'] = prebuilt['optimizable_params']
            
            generations = []
            current_config = base_config
            
            for gen in range(1, max_generations + 1):
                logger.info(f"Running optimization generation {gen}")
                
                # Optimize current strategy
                optimization_result = self.optimize_strategy(
                    current_config,
                    market_data,
                    optimization_metric='sharpe_ratio',
                    max_iterations=30,
                    top_n=3
                )
                
                if not optimization_result['success'] or not optimization_result['top_strategies']:
                    logger.warning(f"Generation {gen} failed")
                    break
                
                # Get best result
                best_result = optimization_result['top_strategies'][0]
                
                # Create evolved strategy
                evolved_strategy = self.create_evolved_strategy(
                    strategy.name,
                    best_result['config'],
                    best_result['metrics'],
                    generation=gen
                )
                
                # Save to database
                new_strategy = Strategy(
                    name=evolved_strategy['name'],
                    description=evolved_strategy['description'],
                    config=json.dumps(evolved_strategy['config']),
                    tags=','.join(evolved_strategy['tags']),
                    risk_level=evolved_strategy['risk_level'],
                    is_active=True
                )
                db_session.add(new_strategy)
                db_session.flush()
                
                generations.append({
                    'generation': gen,
                    'strategy_id': new_strategy.id,
                    'strategy_name': evolved_strategy['name'],
                    'metrics': best_result['metrics'],
                    'parameters': best_result['parameters']
                })
                
                # Use best strategy as base for next generation
                current_config = {
                    'name': evolved_strategy['name'],
                    'config': best_result['config'],
                    'optimizable_params': current_config['optimizable_params']
                }
                
                logger.info(f"Generation {gen} complete - "
                           f"Sharpe: {best_result['metrics']['sharpe_ratio']:.2f}")
            
            db_session.commit()
            
            return {
                'success': True,
                'base_strategy': strategy.name,
                'base_strategy_id': strategy_id,
                'generations': generations,
                'total_generations': len(generations)
            }
            
        except Exception as e:
            logger.error(f"Autonomous improvement error: {str(e)}", exc_info=True)
            db_session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
