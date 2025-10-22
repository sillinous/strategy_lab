
export interface Strategy {
  id: string;
  name: string;
  description?: string;
  indicators: Indicator[];
  buy_conditions: Condition[];
  sell_conditions: Condition[];
  created_at: string;
}

export interface Indicator {
  type: string;
  parameters: Record<string, any>;
}

export interface Condition {
  indicator: string;
  operator: string;
  value: number;
  logic?: 'and' | 'or';
}

export interface BacktestRequest {
  strategy_id: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital?: number;
}

export interface BacktestResult {
  id: string;
  strategy_id: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  total_return_percentage: number;
  max_drawdown: number;
  sharpe_ratio: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  equity_curve: EquityPoint[];
  trades: Trade[];
  created_at: string;
}

export interface EquityPoint {
  date: string;
  equity: number;
}

export interface Trade {
  id: string;
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  profit_loss: number;
  profit_loss_percentage: number;
  type: 'buy' | 'sell';
}

export interface FormData {
  name: string;
  description: string;
  indicators: Indicator[];
  buy_conditions: Condition[];
  sell_conditions: Condition[];
}

// Common indicator types
export const INDICATOR_TYPES = [
  { value: 'sma', label: 'Simple Moving Average (SMA)' },
  { value: 'ema', label: 'Exponential Moving Average (EMA)' },
  { value: 'rsi', label: 'Relative Strength Index (RSI)' },
  { value: 'macd', label: 'MACD' },
  { value: 'bollinger_bands', label: 'Bollinger Bands' },
  { value: 'stochastic', label: 'Stochastic Oscillator' },
] as const;

// Common operators
export const OPERATORS = [
  { value: 'greater_than', label: '>' },
  { value: 'less_than', label: '<' },
  { value: 'equals', label: '=' },
  { value: 'crosses_above', label: 'Crosses Above' },
  { value: 'crosses_below', label: 'Crosses Below' },
] as const;
