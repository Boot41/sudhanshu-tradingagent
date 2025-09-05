import unittest
import logging
import sys
import os

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

try:
    import pandas as pd
    from trader_agent.agents.utils.indicators import (
        sma,
        ema,
        rsi,
        macd,
        validate_price_data,
        extract_closing_prices
    )
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False
    
    # Create dummy functions for testing structure
    def sma(*args): return None
    def ema(*args): return None  
    def rsi(*args): return None
    def macd(*args): return None
    def validate_price_data(*args): return None
    def extract_closing_prices(*args): return None


# Suppress logging during tests to keep the output clean
logging.disable(logging.CRITICAL)



class TestIndicators(unittest.TestCase):
    """
    Unit test suite for the technical indicators module.
    """


    def setUp(self):
        """
        Set up common test data before each test method.
        This method is called before each test.
        """
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available")
            
        self.prices_short = [10, 11, 12]
        self.prices_long = [
            100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
            110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
            120, 121, 122, 123, 124, 125, 126, 127, 128, 129
        ]
        # Add more data points for the MACD test to pass
        self.prices_extra_long = self.prices_long + [130, 131, 132, 133, 134, 135]
        self.mock_df = pd.DataFrame({'Close': self.prices_long})
        self.mock_df_no_close = pd.DataFrame({'Open': self.prices_long})
        self.invalid_prices = [10, 11, 'bad_data', 13]
        self.non_positive_prices = [10, 11, 0, 13]



    # --- Tests for sma() ---


    def test_sma_valid(self):
        """Test SMA calculation with valid data."""
        result = sma(self.prices_long, 5)
        self.assertAlmostEqual(result, 127.0) # (125+126+127+128+129)/5


    def test_sma_insufficient_data(self):
        """Test SMA with not enough prices for the window."""
        result = sma(self.prices_short, 5)
        self.assertIsNone(result)


    def test_sma_invalid_input(self):
        """Test SMA with invalid input types."""
        self.assertIsNone(sma(None, 5))
        self.assertIsNone(sma(self.invalid_prices, 3))



    # --- Tests for ema() ---


    def test_ema_valid(self):
        """Test EMA calculation with valid data."""
        result = ema(self.prices_long, 10)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)


    def test_ema_insufficient_data(self):
        """Test EMA with not enough prices for the window."""
        result = ema(self.prices_short, 10)
        self.assertIsNone(result)


    def test_ema_invalid_input(self):
        """Test EMA with invalid input types."""
        self.assertIsNone(ema(None, 10))
        self.assertIsNone(ema(self.invalid_prices, 3))



    # --- Tests for rsi() ---


    def test_rsi_valid(self):
        """Test RSI calculation with valid data."""
        prices = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28]
        result = rsi(prices, window=14)
        self.assertIsInstance(result, float)
        self.assertTrue(0 <= result <= 100)


    def test_rsi_all_gains(self):
        """Test RSI where all price movements are gains."""
        prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        result = rsi(prices, window=14)
        self.assertEqual(result, 100.0)


    def test_rsi_insufficient_data(self):
        """Test RSI with not enough data."""
        result = rsi(self.prices_short, 14)
        self.assertIsNone(result)



    # --- Tests for macd() ---


    def test_macd_valid(self):
        """Test MACD calculation with valid data."""
        # Use the extra long price list to ensure enough data
        result = macd(self.prices_extra_long, short_win=12, long_win=26, signal=9)
        self.assertIsInstance(result, dict)
        self.assertIn('macd_line', result)
        self.assertIn('signal_line', result)
        self.assertIn('histogram', result)
        self.assertIsInstance(result['macd_line'], float)
        self.assertIsInstance(result['signal_line'], float)
        self.assertIsInstance(result['histogram'], float)


    def test_macd_insufficient_data(self):
        """Test MACD with not enough data for the long window."""
        result = macd(self.prices_long, short_win=12, long_win=40, signal=9)
        self.assertEqual(result['macd_line'], None)
        self.assertEqual(result['signal_line'], None)
        self.assertEqual(result['histogram'], None)


    def test_macd_invalid_windows(self):
        """Test MACD with invalid window configuration."""
        result = macd(self.prices_long, short_win=26, long_win=12, signal=9)
        self.assertEqual(result['macd_line'], None)



    # --- Tests for validate_price_data() ---


    def test_validate_price_data_valid(self):
        """Test validation with a valid list of prices."""
        self.assertTrue(validate_price_data(self.prices_long))


    def test_validate_price_data_with_string(self):
        """Test validation with non-numeric data."""
        self.assertFalse(validate_price_data(self.invalid_prices))


    def test_validate_price_data_with_zero(self):
        """Test validation with a non-positive price."""
        self.assertFalse(validate_price_data(self.non_positive_prices))


    def test_validate_price_data_empty(self):
        """Test validation with an empty list."""
        self.assertFalse(validate_price_data([]))


    def test_validate_price_data_none(self):
        """Test validation with None input."""
        self.assertFalse(validate_price_data(None))



    # --- Tests for extract_closing_prices() ---


    def test_extract_closing_prices_valid_df(self):
        """Test extracting prices from a valid DataFrame."""
        result = extract_closing_prices(self.mock_df)
        self.assertEqual(result, self.prices_long)


    def test_extract_closing_prices_no_close_column(self):
        """Test extracting from a DataFrame without a 'Close' column."""
        result = extract_closing_prices(self.mock_df_no_close)
        self.assertEqual(result, [])


    def test_extract_closing_prices_empty_df(self):
        """Test extracting from an empty DataFrame."""
        result = extract_closing_prices(pd.DataFrame())
        self.assertEqual(result, [])


    def test_extract_closing_prices_df_with_nan(self):
        """Test extracting from a DataFrame containing NaN values."""
        prices_with_nan = self.prices_long + [pd.NA]
        df = pd.DataFrame({'Close': prices_with_nan})
        result = extract_closing_prices(df)
        self.assertEqual(result, self.prices_long) # Should drop NaN



if __name__ == '__main__':
    unittest.main(verbosity=2)
