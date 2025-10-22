
"""
Market Data Fetcher with Caching
Uses yfinance for data retrieval with intelligent caching mechanism
"""
import yfinance as yf
import pandas as pd
import pickle
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging
from app.core.config import get_settings
from app.utils.exceptions import DataFetchError, InsufficientDataError
from app.utils.validators import validate_date_range

settings = get_settings()
logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """
    Market data fetcher with intelligent caching
    
    Features:
    - Automatic caching of market data
    - Cache expiry management
    - Support for multiple timeframes
    - Data validation and cleaning
    """
    
    def __init__(self, cache_dir: Optional[str] = None, cache_expiry_days: int = 7):
        """
        Initialize market data fetcher
        
        Args:
            cache_dir: Directory for cache storage
            cache_expiry_days: Number of days before cache expires
        """
        self.cache_dir = Path(cache_dir or settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry_days = cache_expiry_days
        logger.info(f"Initialized MarketDataFetcher with cache dir: {self.cache_dir}")
    
    def _generate_cache_key(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str
    ) -> str:
        """
        Generate unique cache key for data request
        
        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
            
        Returns:
            Cache key string
        """
        key_string = f"{symbol}_{start_date}_{end_date}_{interval}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get full path for cache file"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Check if cache file is valid and not expired
        
        Args:
            cache_path: Path to cache file
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False
        
        # Check cache age
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if cache_age > timedelta(days=self.cache_expiry_days):
            logger.debug(f"Cache expired: {cache_path.name}")
            return False
        
        return True
    
    def _load_from_cache(self, cache_path: Path) -> Optional[pd.DataFrame]:
        """
        Load data from cache file
        
        Args:
            cache_path: Path to cache file
            
        Returns:
            DataFrame if successful, None otherwise
        """
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"Loaded data from cache: {cache_path.name}")
            return data
        except Exception as e:
            logger.warning(f"Error loading cache {cache_path.name}: {str(e)}")
            return None
    
    def _save_to_cache(self, data: pd.DataFrame, cache_path: Path) -> None:
        """
        Save data to cache file
        
        Args:
            data: DataFrame to cache
            cache_path: Path to cache file
        """
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Saved data to cache: {cache_path.name}")
        except Exception as e:
            logger.warning(f"Error saving cache {cache_path.name}: {str(e)}")
    
    def _validate_and_clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean market data
        
        Args:
            data: Raw market data DataFrame
            
        Returns:
            Cleaned DataFrame
            
        Raises:
            InsufficientDataError: If data is invalid or insufficient
        """
        if data.empty:
            raise InsufficientDataError("No data returned from yfinance")
        
        # Remove rows with NaN values
        initial_len = len(data)
        data = data.dropna()
        
        if len(data) == 0:
            raise InsufficientDataError("All data rows contain NaN values")
        
        if len(data) < initial_len:
            logger.warning(f"Removed {initial_len - len(data)} rows with NaN values")
        
        # Ensure required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = set(required_columns) - set(data.columns)
        
        if missing_columns:
            raise InsufficientDataError(f"Missing required columns: {missing_columns}")
        
        # Ensure index is datetime
        if not isinstance(data.index, pd.DatetimeIndex):
            try:
                data.index = pd.to_datetime(data.index)
            except Exception as e:
                raise DataFetchError(f"Error converting index to datetime: {str(e)}")
        
        # Sort by date
        data = data.sort_index()
        
        logger.info(f"Validated and cleaned data: {len(data)} rows")
        return data
    
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        interval: str = '1d',
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Fetch market data with caching
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'BTCUSDT')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (default: today)
            interval: Data interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            force_refresh: Force refresh from API, ignore cache
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            DataFetchError: If data fetch fails
            InsufficientDataError: If insufficient data returned
        """
        try:
            # Validate dates
            start_dt, end_dt = validate_date_range(start_date, end_date)
            end_date_str = end_dt.strftime("%Y-%m-%d")
            
            logger.info(f"Fetching data for {symbol} from {start_date} to {end_date_str}, interval: {interval}")
            
            # Check cache if not forcing refresh
            if not force_refresh:
                cache_key = self._generate_cache_key(symbol, start_date, end_date_str, interval)
                cache_path = self._get_cache_path(cache_key)
                
                if self._is_cache_valid(cache_path):
                    cached_data = self._load_from_cache(cache_path)
                    if cached_data is not None:
                        return cached_data
            
            # Fetch from yfinance
            logger.info(f"Fetching fresh data from yfinance for {symbol}")
            ticker = yf.Ticker(symbol)
            
            try:
                data = ticker.history(
                    start=start_date,
                    end=end_date_str,
                    interval=interval,
                    auto_adjust=True  # Use adjusted close prices
                )
            except Exception as e:
                raise DataFetchError(f"yfinance error for {symbol}: {str(e)}")
            
            # Validate and clean data
            data = self._validate_and_clean_data(data)
            
            # Check minimum data points
            if len(data) < 50:
                logger.warning(f"Limited data available for {symbol}: {len(data)} rows")
            
            # Save to cache
            if not force_refresh:
                cache_key = self._generate_cache_key(symbol, start_date, end_date_str, interval)
                cache_path = self._get_cache_path(cache_key)
                self._save_to_cache(data, cache_path)
            
            logger.info(f"Successfully fetched {len(data)} rows for {symbol}")
            return data
            
        except (DataFetchError, InsufficientDataError):
            raise
        except Exception as e:
            raise DataFetchError(f"Unexpected error fetching data for {symbol}: {str(e)}")
    
    def fetch_multiple(
        self,
        symbols: list[str],
        start_date: str,
        end_date: Optional[str] = None,
        interval: str = '1d'
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data interval
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.fetch_data(symbol, start_date, end_date, interval)
                results[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                results[symbol] = None
        
        return results
    
    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear cache files
        
        Args:
            older_than_days: Only clear files older than this many days (None = all)
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                if older_than_days is None:
                    cache_file.unlink()
                    deleted_count += 1
                else:
                    cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                    if cache_age > timedelta(days=older_than_days):
                        cache_file.unlink()
                        deleted_count += 1
            except Exception as e:
                logger.warning(f"Error deleting cache file {cache_file.name}: {str(e)}")
        
        logger.info(f"Cleared {deleted_count} cache files")
        return deleted_count
    
    def get_ticker_info(self, symbol: str) -> dict:
        """
        Get ticker information
        
        Args:
            symbol: Ticker symbol
            
        Returns:
            Dictionary with ticker information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'symbol': symbol,
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }
        except Exception as e:
            logger.error(f"Error fetching ticker info for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
