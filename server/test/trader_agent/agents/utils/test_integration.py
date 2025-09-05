"""
Integration Test Suite for Trading Agent Utils

Tests the complete flow:
http_client → nasdaq_api → indicators → scoring

This test verifies that:
1. HTTP client can make requests and handle responses
2. NASDAQ API can fetch and normalize data
3. Indicators can calculate technical metrics from price data
4. Scoring can convert raw data into normalized scores
5. The entire pipeline works end-to-end
"""

import unittest
import logging
import json
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock, mock_open
from typing import Dict, List, Any

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

try:
    import pandas as pd
    from trader_agent.agents.utils import http_client
    from trader_agent.agents.utils import nasdaq_api
    from trader_agent.agents.utils import indicators
    from trader_agent.agents.utils import scoring
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestHTTPClient(unittest.TestCase):
    """Test HTTP client functionality"""
    
    def setUp(self):
        """Set up test environment"""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available")
            
        # Create temporary cache directory for testing
        self.temp_cache_dir = tempfile.mkdtemp()
        self.original_cache_dir = http_client.CACHE_DIR
        http_client.CACHE_DIR = self.temp_cache_dir
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original cache directory and clean up
        http_client.CACHE_DIR = self.original_cache_dir
        shutil.rmtree(self.temp_cache_dir, ignore_errors=True)
    
    @patch('trader_agent.agents.utils.http_client.requests.get')
    def test_get_json_success(self, mock_get):
        """Test successful JSON GET request"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data", "value": 123}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = http_client.get_json("https://test.com/api")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["test"], "data")
        self.assertEqual(result["value"], 123)
        mock_get.assert_called_once()
    
    @patch('trader_agent.agents.utils.http_client.requests.get')
    def test_get_json_retry_on_failure(self, mock_get):
        """Test retry mechanism on request failure"""
        import requests
    
        # Create a proper mock response for the successful attempt
        mock_success_response = MagicMock()
        mock_success_response.json.return_value = {"retry": "success"}
        mock_success_response.raise_for_status.return_value = None
    
        # Configure side_effect: fail twice, then succeed
        mock_get.side_effect = [
            requests.exceptions.RequestException("Connection error"),
            requests.exceptions.RequestException("Timeout"), 
            mock_success_response
        ]
    
        result = http_client.get_json("https://test.com/api", retries=3)
    
        self.assertIsNotNone(result)
        self.assertEqual(result["retry"], "success")
        self.assertEqual(mock_get.call_count, 3)


    
    def test_cache_functionality(self):
        """Test caching mechanism"""
        # Test cache key generation
        cache_key = http_client._cache_key("https://test.com", {"header": "value"})
        self.assertIsInstance(cache_key, str)
        self.assertEqual(len(cache_key), 32)  # MD5 hash length
        
        # Test cache save and load
        test_data = {"cached": "data", "timestamp": 123456}
        http_client._save_to_cache(cache_key, test_data)
        
        loaded_data = http_client._load_from_cache(cache_key)
        self.assertEqual(loaded_data, test_data)
    
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        # Create some cache files
        cache_key1 = "test1"
        cache_key2 = "test2"
        http_client._save_to_cache(cache_key1, {"data": 1})
        http_client._save_to_cache(cache_key2, {"data": 2})
        
        # Verify files exist
        self.assertTrue(os.path.exists(http_client._cache_path(cache_key1)))
        self.assertTrue(os.path.exists(http_client._cache_path(cache_key2)))
        
        # Clear cache
        http_client.clear_cache()
        
        # Verify files are removed
        self.assertFalse(os.path.exists(http_client._cache_path(cache_key1)))
        self.assertFalse(os.path.exists(http_client._cache_path(cache_key2)))


class TestNASDAQAPI(unittest.TestCase):
    """Test NASDAQ API functionality"""
    
    def setUp(self):
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available")
    
    def test_date_utilities(self):
        """Test date utility functions"""
        from datetime import date
        
        # Test ISO date conversion
        test_date = date(2023, 12, 25)
        iso_string = nasdaq_api._iso_date(test_date)
        self.assertEqual(iso_string, "2023-12-25")
        
        # Test default date range
        start_date, end_date = nasdaq_api._default_date_range(3)
        self.assertIsInstance(start_date, str)
        self.assertIsInstance(end_date, str)
        self.assertTrue(start_date < end_date)
    
    def test_period_parsing(self):
        """Test period string parsing"""
        test_cases = [
            ("3mo", 3),
            ("6m", 6),
            ("1y", 12),
            ("90d", 3),
            ("2y", 24),
            ("invalid", 3),  # Should default to 3, not raise exception
            ("", 3),         # Empty string should default to 3
            ("10x", 3),      # Unknown suffix should default to 3
            (None, 3)        # None input should default to 3
        ]
    
        for period_str, expected_months in test_cases:
            with self.subTest(period=period_str):
                result = nasdaq_api._parse_period_to_months(period_str)
                self.assertEqual(result, expected_months, 
                               f"Period '{period_str}' should return {expected_months} months, got {result}")

    
    @patch('trader_agent.agents.utils.nasdaq_api.yf.Ticker')
    def test_get_historical_data_success(self, mock_ticker_class):
        """Test successful historical data fetching"""
        # Create mock data
        mock_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        # Mock ticker instance
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker
        
        result = nasdaq_api.get_historical_data("AAPL", "3mo")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 3)
        self.assertIn('Close', result.columns)
    
    @patch('trader_agent.agents.utils.nasdaq_api.yf.Ticker')
    def test_get_historical_data_empty_response(self, mock_ticker_class):
        """Test handling of empty historical data response"""
        # Mock empty response
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_ticker_class.return_value = mock_ticker
        
        result = nasdaq_api.get_historical_data("INVALID", "3mo")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_normalize_company_data(self):
        """Test company data normalization"""
        raw_data = {
            "data": {
                "symbol": "AAPL",
                "summaryData": {
                    "CompanyName": {"value": "Apple Inc."},
                    "Sector": {"value": "Technology"},
                    "MarketCap": {"value": "$2.5T"},
                    "PERatio": {"value": "25.5"},
                    "LastSale": {"value": "$150.25"}
                }
            }
        }
        
        result = nasdaq_api._normalize_company_data(raw_data)
        
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["company_name"], "Apple Inc.")
        self.assertEqual(result["sector"], "Technology")
        self.assertEqual(result["market_cap"], "$2.5T")
        self.assertEqual(result["pe_ratio"], "25.5")
    
    def test_normalize_news_data(self):
        """Test news data normalization"""
        raw_data = {
            "data": {
                "rows": [
                    {
                        "title": "Apple Reports Strong Earnings",
                        "summary": "Apple beats expectations",
                        "url": "https://example.com/news1",
                        "published_date": "2023-12-01",
                        "source": "Reuters"
                    },
                    {
                        "title": "Tech Stocks Rally",
                        "summary": "Market surge continues",
                        "url": "https://example.com/news2",
                        "published_date": "2023-12-02",
                        "source": "Bloomberg"
                    }
                ]
            }
        }
        
        result = nasdaq_api._normalize_news_data(raw_data)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Apple Reports Strong Earnings")
        self.assertEqual(result[1]["source"], "Bloomberg")


class TestIndicators(unittest.TestCase):
    """Test technical indicators functionality"""
    
    def setUp(self):
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available")
            
        """Set up test data"""
        # Create sample price data for testing
        self.sample_prices = [
            100.0, 101.0, 99.0, 102.0, 103.0, 101.0, 104.0, 105.0, 103.0, 106.0,
            107.0, 105.0, 108.0, 109.0, 107.0, 110.0, 111.0, 109.0, 112.0, 113.0,
            111.0, 114.0, 115.0, 113.0, 116.0, 117.0, 115.0, 118.0, 119.0, 117.0,
            120.0, 121.0, 119.0, 122.0, 123.0, 121.0, 124.0, 125.0, 123.0, 126.0,
            127.0, 125.0, 128.0, 129.0, 127.0, 130.0, 131.0, 129.0, 132.0, 133.0
        ]
    
    def test_validate_price_data(self):
        """Test price data validation"""
        # Valid data
        self.assertTrue(indicators.validate_price_data(self.sample_prices))
        
        # Invalid data cases
        self.assertFalse(indicators.validate_price_data([]))
        self.assertFalse(indicators.validate_price_data(None))
        self.assertFalse(indicators.validate_price_data([100, "invalid", 102]))
        self.assertFalse(indicators.validate_price_data([100, -50, 102]))
    
    def test_sma_calculation(self):
        """Test Simple Moving Average calculation"""
        # Test with sufficient data
        sma_10 = indicators.sma(self.sample_prices, 10)
        self.assertIsNotNone(sma_10)
        self.assertIsInstance(sma_10, float)
        self.assertGreater(sma_10, 0)
        
        # Test with insufficient data
        sma_100 = indicators.sma(self.sample_prices, 100)
        self.assertIsNone(sma_100)
        
        # Test with invalid inputs
        self.assertIsNone(indicators.sma([], 10))
        self.assertIsNone(indicators.sma(self.sample_prices, 0))
    
    def test_ema_calculation(self):
        """Test Exponential Moving Average calculation"""
        # Test with sufficient data
        ema_10 = indicators.ema(self.sample_prices, 10)
        self.assertIsNotNone(ema_10)
        self.assertIsInstance(ema_10, float)
        self.assertGreater(ema_10, 0)
        
        # Test with insufficient data
        ema_100 = indicators.ema(self.sample_prices, 100)
        self.assertIsNone(ema_100)
        
        # EMA should be different from SMA
        sma_10 = indicators.sma(self.sample_prices, 10)
        self.assertNotEqual(ema_10, sma_10)
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        # Test with sufficient data
        rsi_value = indicators.rsi(self.sample_prices, 14)
        self.assertIsNotNone(rsi_value)
        self.assertIsInstance(rsi_value, float)
        self.assertGreaterEqual(rsi_value, 0)
        self.assertLessEqual(rsi_value, 100)
        
        # Test with insufficient data
        rsi_insufficient = indicators.rsi(self.sample_prices[:10], 14)
        self.assertIsNone(rsi_insufficient)
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        # Test with sufficient data
        macd_result = indicators.macd(self.sample_prices, 12, 26, 9)
        self.assertIsInstance(macd_result, dict)
        self.assertIn("macd_line", macd_result)
        self.assertIn("signal_line", macd_result)
        self.assertIn("histogram", macd_result)
        
        # All values should be present with sufficient data
        self.assertIsNotNone(macd_result["macd_line"])
        self.assertIsNotNone(macd_result["signal_line"])
        self.assertIsNotNone(macd_result["histogram"])
        
        # Test with insufficient data
        macd_insufficient = indicators.macd(self.sample_prices[:20], 12, 26, 9)
        self.assertEqual(macd_insufficient["macd_line"], None)
    
    def test_extract_closing_prices(self):
        """Test closing price extraction from DataFrame"""
        # Create test DataFrame
        df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        })
        
        prices = indicators.extract_closing_prices(df)
        self.assertEqual(len(prices), 3)
        self.assertEqual(prices, [104, 105, 106])
        
        # Test with empty DataFrame
        empty_prices = indicators.extract_closing_prices(pd.DataFrame())
        self.assertEqual(empty_prices, [])
        
        # Test with None
        none_prices = indicators.extract_closing_prices(None)
        self.assertEqual(none_prices, [])


class TestScoring(unittest.TestCase):
    """Test scoring functionality"""
    
    def setUp(self):
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available")
    
    def test_parse_numeric_value(self):
        """Test numeric value parsing"""
        test_cases = [
            ("$1,234.56", 1234.56),
            ("25.5%", 25.5),
            ("1,000,000", 1000000.0),
            ("N/A", 0.0),
            ("--", 0.0),
            ("invalid", 0.0),
            ("", 0.0)
        ]
        
        for input_str, expected in test_cases:
            result = scoring._parse_numeric_value(input_str)
            self.assertEqual(result, expected)
    
    def test_parse_market_cap(self):
        """Test market cap parsing"""
        test_cases = [
            ("$2.5T", 2.5e12),
            ("$150.2B", 150.2e9),
            ("$5.1M", 5.1e6),
            ("$1.5K", 1.5e3),
            ("$1000", 1000.0),
            ("invalid", 0.0)
        ]
        
        for input_str, expected in test_cases:
            result = scoring._parse_market_cap(input_str)
            self.assertEqual(result, expected)
    
    def test_fundamentals_score(self):
        """Test fundamentals scoring"""
        # Test with good fundamental data
        good_company_data = {
            "symbol": "AAPL",
            "market_cap": "$2.5T",
            "pe_ratio": "20.5",
            "dividend_yield": "3.5",
            "volume": "50000000",
            "avg_volume": "40000000",
            "price": "150.25",
            "high_52week": "180.00",
            "low_52week": "120.00"
        }
        
        score = scoring.fundamentals_score(good_company_data)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        self.assertGreater(score, 50.0)  # Should be above neutral for good data
        
        # Test with empty data
        empty_score = scoring.fundamentals_score({})
        self.assertEqual(empty_score, 50.0)  # Neutral score
    
    def test_technical_score(self):
        """Test technical scoring"""
        # Test with bullish indicators
        bullish_indicators = {
            "rsi": 25.0,  # Oversold - bullish
            "macd": {
                "macd_line": 1.5,
                "signal_line": 1.0,
                "histogram": 0.5
            },
            "sma_50": 150.0,
            "sma_200": 140.0,  # Golden cross
            "current_price": 155.0  # Above SMA50
        }
        
        score = scoring.technical_score(bullish_indicators)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        self.assertGreater(score, 50.0)  # Should be bullish
        
        # Test with bearish indicators
        bearish_indicators = {
            "rsi": 80.0,  # Overbought - bearish
            "macd": {
                "macd_line": 1.0,
                "signal_line": 1.5,
                "histogram": -0.5
            },
            "sma_50": 140.0,
            "sma_200": 150.0,  # Death cross
            "current_price": 135.0  # Below SMA50
        }
        
        bearish_score = scoring.technical_score(bearish_indicators)
        self.assertLess(bearish_score, 50.0)  # Should be bearish
    
    def test_sentiment_score(self):
        """Test sentiment scoring"""
        # Test with positive news
        positive_news = [
            {"title": "Company beats earnings expectations", "summary": "Strong growth reported"},
            {"title": "Stock upgraded by analysts", "summary": "Bullish outlook maintained"}
        ]
        
        pos_score = scoring.sentiment_score(positive_news)
        self.assertGreater(pos_score, 50.0)
        
        # Test with negative news
        negative_news = [
            {"title": "Company misses earnings", "summary": "Weak performance reported"},
            {"title": "Stock downgraded", "summary": "Bearish outlook"}
        ]
        
        neg_score = scoring.sentiment_score(negative_news)
        self.assertLess(neg_score, 50.0)
        
        # Test with empty news
        empty_score = scoring.sentiment_score([])
        self.assertEqual(empty_score, 50.0)
    
    def test_technical_score_from_prices(self):
        """Test technical score calculation from price data"""
        # Create sufficient price data
        prices = list(range(100, 300))  # 200 data points
        
        score = scoring.technical_score_from_prices(prices)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        
        # Test with insufficient data
        insufficient_score = scoring.technical_score_from_prices([100, 101, 102])
        self.assertEqual(insufficient_score, 50.0)
    
    def test_composite_score(self):
        """Test composite score calculation"""
        # Test with default weights
        composite = scoring.composite_score(70.0, 60.0, 80.0, 65.0)
        self.assertIsInstance(composite, float)
        self.assertGreaterEqual(composite, 0.0)
        self.assertLessEqual(composite, 100.0)
        
        # Test with custom weights
        custom_weights = {
            "fundamentals": 0.5,
            "technical": 0.3,
            "sentiment": 0.1,
            "news": 0.1
        }
        
        custom_composite = scoring.composite_score(70.0, 60.0, 80.0, 65.0, custom_weights)
        self.assertNotEqual(composite, custom_composite)


class TestIntegration(unittest.TestCase):
    """Test end-to-end integration"""
    
    def setUp(self):
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Dependencies not available")
    
    @patch('trader_agent.agents.utils.nasdaq_api.yf.Ticker')
    def test_end_to_end_flow(self, mock_ticker_class):
        """Test complete flow from data fetching to scoring"""
        # Mock historical data
        mock_data = pd.DataFrame({
            'Open': list(range(100, 200)),
            'High': list(range(105, 205)),
            'Low': list(range(95, 195)),
            'Close': list(range(102, 202)),
            'Volume': [1000000] * 100
        }, index=pd.date_range('2023-01-01', periods=100))
        
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker
        
        # Step 1: Fetch historical data
        ticker = "AAPL"
        historical_data = nasdaq_api.get_historical_data(ticker, "3mo")
        self.assertFalse(historical_data.empty)
        
        # Step 2: Extract closing prices
        closing_prices = indicators.extract_closing_prices(historical_data)
        self.assertGreater(len(closing_prices), 50)
        
        # Step 3: Calculate technical indicators
        rsi_value = indicators.rsi(closing_prices, 14)
        macd_data = indicators.macd(closing_prices, 12, 26, 9)
        sma_50 = indicators.sma(closing_prices, 50)
        
        self.assertIsNotNone(rsi_value)
        self.assertIsNotNone(macd_data["macd_line"])
        self.assertIsNotNone(sma_50)
        
        # Step 4: Calculate technical score
        indicators_dict = {
            "rsi": rsi_value,
            "macd": macd_data,
            "sma_50": sma_50,
            "current_price": closing_prices[-1]
        }
        
        tech_score = scoring.technical_score(indicators_dict)
        self.assertIsInstance(tech_score, float)
        self.assertGreaterEqual(tech_score, 0.0)
        self.assertLessEqual(tech_score, 100.0)
        
        # Step 5: Test alternative method
        direct_tech_score = scoring.technical_score_from_prices(closing_prices)
        self.assertIsInstance(direct_tech_score, float)
        
        logger.info(f"End-to-end test completed successfully for {ticker}")
        logger.info(f"Technical score: {tech_score:.2f}")
        logger.info(f"Direct technical score: {direct_tech_score:.2f}")
    
    def test_error_handling_integration(self):
        """Test error handling throughout the pipeline"""
        # Test with invalid ticker
        invalid_data = nasdaq_api.get_historical_data("", "3mo")
        self.assertTrue(invalid_data.empty)
        
        # Test indicators with empty data
        empty_prices = indicators.extract_closing_prices(invalid_data)
        self.assertEqual(empty_prices, [])
        
        # Test scoring with empty indicators
        empty_score = scoring.technical_score_from_prices(empty_prices)
        self.assertEqual(empty_score, 50.0)
        
        # Test composite score with edge cases
        edge_composite = scoring.composite_score(0.0, 100.0, 50.0, 50.0)
        self.assertGreaterEqual(edge_composite, 0.0)
        self.assertLessEqual(edge_composite, 100.0)


def run_integration_tests():
    """Run all integration tests and return results"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestHTTPClient,
        TestNASDAQAPI,
        TestIndicators,
        TestScoring,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    """Run integration tests when executed directly"""
    print("Starting Trading Agent Utils Integration Tests...")
    print("Testing flow: http_client → nasdaq_api → indicators → scoring")
    print("-" * 60)
    
    success = run_integration_tests()
    
    if success:
        print("\n✅ All integration tests passed!")
        print("The entire flow is working correctly.")
    else:
        print("\n❌ Some tests failed!")
        print("Please check the output above for details.")
    
    exit(0 if success else 1)
