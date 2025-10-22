
# Strategy Lab Backend

Enterprise-grade trading strategy development and backtesting platform backend built with FastAPI.

## 🚀 Features

### Technical Indicators
- **SMA (Simple Moving Average)**: Trend identification
- **EMA (Exponential Moving Average)**: Responsive trend analysis
- **RSI (Relative Strength Index)**: Momentum oscillator
- **MACD (Moving Average Convergence Divergence)**: Trend momentum
- **Bollinger Bands**: Volatility-based support/resistance

### Backtesting Engine
- **Vectorized Operations**: High-performance pandas-based calculations
- **Trade Simulation**: Realistic entry/exit modeling
- **Cost Modeling**: Commission and slippage simulation
- **Position Management**: Long position support (short positions coming soon)

### Performance Metrics
- **Return Metrics**: Total return, annualized return
- **Risk Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown
- **Trade Metrics**: Win rate, profit factor, average win/loss
- **Advanced Metrics**: Calmar ratio, volatility, drawdown duration

### Data Management
- **Market Data Fetcher**: yfinance integration with intelligent caching
- **Multiple Timeframes**: 1m to 1mo intervals
- **Data Validation**: Comprehensive data quality checks
- **Cache Management**: Automatic cache expiry and cleanup

### API Endpoints
- **Strategy CRUD**: Create, read, update, delete strategies
- **Backtest Execution**: Run backtests with custom parameters
- **Results Management**: Store and retrieve backtest results
- **Performance Analytics**: Comprehensive metrics calculation

## 📋 Requirements

- Python 3.11+
- SQLite (included) or PostgreSQL
- 4GB+ RAM recommended for large backtests

## 🛠️ Installation

### 1. Clone the repository
```bash
cd /home/ubuntu/strategy_lab/backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Initialize database
The database will be automatically initialized on first run.

## 🚀 Running the Application

### Development Server
```bash
# From the backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using the main module:
```bash
python -m app.main
```

### Production Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📖 API Usage

### Create a Strategy

```bash
curl -X POST "http://localhost:8000/api/v1/strategies/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SMA Crossover Strategy",
    "description": "Simple moving average crossover strategy",
    "config": {
      "indicators": [
        {"type": "SMA", "period": 20, "column": "Close"},
        {"type": "SMA", "period": 50, "column": "Close"}
      ],
      "entry_rules": {
        "condition": "SMA_20 > SMA_50"
      },
      "exit_rules": {
        "condition": "SMA_20 < SMA_50"
      }
    },
    "risk_level": "MEDIUM",
    "tags": ["trend-following", "sma"]
  }'
```

### Run a Backtest

```bash
curl -X POST "http://localhost:8000/api/v1/backtests/" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": 1,
    "symbol": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2024-01-01",
    "interval": "1d",
    "initial_capital": 100000,
    "commission_rate": 0.001,
    "slippage_rate": 0.0005
  }'
```

### List Strategies

```bash
curl "http://localhost:8000/api/v1/strategies/"
```

### Get Backtest Results

```bash
curl "http://localhost:8000/api/v1/backtests/1"
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/                    # API endpoints
│   │   ├── strategies.py       # Strategy CRUD endpoints
│   │   └── backtests.py        # Backtest endpoints
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Settings management
│   │   ├── database.py         # Database connection
│   │   └── logging.py          # Logging configuration
│   ├── models/                 # SQLAlchemy models
│   │   ├── strategy.py         # Strategy model
│   │   └── backtest.py         # Backtest model
│   ├── schemas/                # Pydantic schemas
│   │   ├── strategy.py         # Strategy schemas
│   │   └── backtest.py         # Backtest schemas
│   ├── services/               # Business logic
│   │   ├── indicators.py       # Technical indicators
│   │   ├── data_fetcher.py     # Market data fetcher
│   │   ├── backtester.py       # Backtesting engine
│   │   └── metrics.py          # Performance metrics
│   └── utils/                  # Utilities
│       ├── exceptions.py       # Custom exceptions
│       └── validators.py       # Validation utilities
├── tests/                      # Test suite
├── data/                       # Data storage
│   └── cache/                  # Cached market data
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🧪 Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## 📊 Strategy Configuration

Strategies are defined using a JSON configuration format:

```json
{
  "indicators": [
    {
      "type": "SMA",
      "period": 20,
      "column": "Close"
    },
    {
      "type": "RSI",
      "period": 14,
      "column": "Close"
    }
  ],
  "entry_rules": {
    "condition": "(SMA_20 > SMA_50) & (RSI_14 < 30)"
  },
  "exit_rules": {
    "condition": "(SMA_20 < SMA_50) | (RSI_14 > 70)"
  }
}
```

### Supported Indicators

- `SMA`: Simple Moving Average
- `EMA`: Exponential Moving Average
- `RSI`: Relative Strength Index
- `MACD`: Moving Average Convergence Divergence
- `BB` or `BOLLINGER`: Bollinger Bands

### Condition Syntax

Conditions support Python expressions with pandas operations:
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Logical: `&` (and), `|` (or), `~` (not)
- Functions: `abs()`, numpy functions via `np`
- Example: `(SMA_20 > SMA_50) & (RSI_14 < 30)`

## 🎯 Performance Optimization

### Caching
- Market data is automatically cached for 7 days
- Cache key based on symbol, date range, and interval
- Manual cache clearing available

### Vectorization
- All calculations use pandas vectorized operations
- Avoid loops for maximum performance
- Typical backtest: <1 second for 1000 data points

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Database
DATABASE_URL=sqlite:///./strategy_lab.db

# Cache
CACHE_DIR=./data/cache
CACHE_EXPIRY_DAYS=7

# Backtesting
INITIAL_CAPITAL=100000.0
COMMISSION_RATE=0.001
SLIPPAGE_RATE=0.0005
RISK_FREE_RATE=0.02

# Logging
LOG_LEVEL=INFO
```

## 🚧 Known Limitations

1. **Position Types**: Currently supports long positions only (short positions in development)
2. **Order Types**: Market orders only (limit orders coming soon)
3. **Data Source**: yfinance only (additional providers planned)
4. **Intraday Data**: Limited historical availability (API restriction)

## 🛣️ Roadmap

- [ ] Short position support
- [ ] Multi-asset portfolio backtesting
- [ ] Parameter optimization engine
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] Machine learning integration
- [ ] Real-time paper trading
- [ ] WebSocket streaming data
- [ ] Advanced order types
- [ ] Risk management rules

## 📝 License

Copyright © 2024 Strategy Lab Team

## 👥 Contributing

This is currently a private project. For questions or contributions, please contact the development team.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the logs in `logs/strategy_lab.log`
3. Contact the development team

## 🙏 Acknowledgments

Built with:
- FastAPI - Modern Python web framework
- pandas - Data analysis library
- yfinance - Yahoo Finance data
- SQLAlchemy - SQL toolkit and ORM
- NumPy - Numerical computing

---

**Strategy Lab** - Building the future of autonomous trading 🚀
