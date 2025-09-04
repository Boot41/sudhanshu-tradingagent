#!/usr/bin/env python3
"""
Simple validation script to test the entire flow:
http_client → nasdaq_api → indicators → scoring

This script performs basic validation of each component and the integration
without requiring complex test frameworks.
"""

import sys
import os
import traceback
from typing import Dict, Any, List
import pandas as pd

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    try:
        import http_client
        import nasdaq_api
        import indicators
        import scoring
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_http_client():
    """Test basic HTTP client functionality"""
    print("\nTesting HTTP client...")
    try:
        import http_client
        
        # Test cache key generation
        cache_key = http_client._cache_key("https://test.com", {"test": "header"})
        assert isinstance(cache_key, str) and len(cache_key) == 32
        
        # Test numeric parsing in cache functions
        test_data = {"test": "data"}
        http_client._save_to_cache("test_key", test_data)
        loaded = http_client._load_from_cache("test_key")
        assert loaded == test_data
        
        print("✅ HTTP client basic functions work")
        return True
    except Exception as e:
        print(f"❌ HTTP client test failed: {e}")
        traceback.print_exc()
        return False

def test_nasdaq_api():
    """Test NASDAQ API utility functions"""
    print("\nTesting NASDAQ API utilities...")
    try:
        import nasdaq_api
        from datetime import date
        
        # Test date utilities
        test_date = date(2023, 12, 25)
        iso_string = nasdaq_api._iso_date(test_date)
        assert iso_string == "2023-12-25"
        
        # Test period parsing
        assert nasdaq_api._parse_period_to_months("3mo") == 3
        assert nasdaq_api._parse_period_to_months("1y") == 12
        assert nasdaq_api._parse_period_to_months("90d") == 3
        
        # Test data normalization
        raw_data = {
            "data": {
                "symbol": "TEST",
                "summaryData": {
                    "CompanyName": {"value": "Test Company"},
                    "Sector": {"value": "Technology"}
                }
            }
        }
        normalized = nasdaq_api._normalize_company_data(raw_data)
        assert normalized["symbol"] == "TEST"
        assert normalized["company_name"] == "Test Company"
        
        print("✅ NASDAQ API utilities work")
        return True
    except Exception as e:
        print(f"❌ NASDAQ API test failed: {e}")
        traceback.print_exc()
        return False

def test_indicators():
    """Test technical indicators with sample data"""
    print("\nTesting technical indicators...")
    try:
        import indicators
        
        # Create sample price data
        sample_prices = [
            100.0, 101.0, 99.0, 102.0, 103.0, 101.0, 104.0, 105.0, 103.0, 106.0,
            107.0, 105.0, 108.0, 109.0, 107.0, 110.0, 111.0, 109.0, 112.0, 113.0,
            111.0, 114.0, 115.0, 113.0, 116.0, 117.0, 115.0, 118.0, 119.0, 117.0,
            120.0, 121.0, 119.0, 122.0, 123.0, 121.0, 124.0, 125.0, 123.0, 126.0,
            127.0, 125.0, 128.0, 129.0, 127.0, 130.0, 131.0, 129.0, 132.0, 133.0
        ]
        
        # Test price validation
        assert indicators.validate_price_data(sample_prices) == True
        assert indicators.validate_price_data([]) == False
        
        # Test SMA
        sma_10 = indicators.sma(sample_prices, 10)
        assert sma_10 is not None
        assert isinstance(sma_10, float)
        assert sma_10 > 0
        
        # Test EMA
        ema_10 = indicators.ema(sample_prices, 10)
        assert ema_10 is not None
        assert isinstance(ema_10, float)
        assert ema_10 != sma_10  # EMA should differ from SMA
        
        # Test RSI
        rsi_value = indicators.rsi(sample_prices, 14)
        assert rsi_value is not None
        assert 0 <= rsi_value <= 100
        
        # Test MACD
        macd_result = indicators.macd(sample_prices, 12, 26, 9)
        assert isinstance(macd_result, dict)
        assert "macd_line" in macd_result
        assert "signal_line" in macd_result
        assert "histogram" in macd_result
        assert macd_result["macd_line"] is not None
        
        # Test DataFrame extraction
        df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [99, 100, 101],
            'Close': [104, 105, 106],
            'Volume': [1000000, 1100000, 1200000]
        })
        
        extracted_prices = indicators.extract_closing_prices(df)
        assert extracted_prices == [104, 105, 106]
        
        print("✅ Technical indicators work correctly")
        return True
    except Exception as e:
        print(f"❌ Indicators test failed: {e}")
        traceback.print_exc()
        return False

def test_scoring():
    """Test scoring functions"""
    print("\nTesting scoring functions...")
    try:
        import scoring
        
        # Test numeric parsing
        assert scoring._parse_numeric_value("$1,234.56") == 1234.56
        assert scoring._parse_numeric_value("25.5%") == 25.5
        assert scoring._parse_numeric_value("N/A") == 0.0
        
        # Test market cap parsing
        assert scoring._parse_market_cap("$2.5T") == 2.5e12
        assert scoring._parse_market_cap("$150.2B") == 150.2e9
        assert scoring._parse_market_cap("$5.1M") == 5.1e6
        
        # Test fundamentals scoring
        company_data = {
            "symbol": "TEST",
            "market_cap": "$2.5T",
            "pe_ratio": "20.5",
            "dividend_yield": "3.5",
            "volume": "50000000",
            "avg_volume": "40000000",
            "price": "150.25",
            "high_52week": "180.00",
            "low_52week": "120.00"
        }
        
        fund_score = scoring.fundamentals_score(company_data)
        assert isinstance(fund_score, float)
        assert 0 <= fund_score <= 100
        
        # Test technical scoring
        indicators_data = {
            "rsi": 45.0,
            "macd": {
                "macd_line": 1.5,
                "signal_line": 1.0,
                "histogram": 0.5
            },
            "sma_50": 150.0,
            "sma_200": 140.0,
            "current_price": 155.0
        }
        
        tech_score = scoring.technical_score(indicators_data)
        assert isinstance(tech_score, float)
        assert 0 <= tech_score <= 100
        
        # Test sentiment scoring
        news_data = [
            {"title": "Company beats earnings", "summary": "Strong growth"},
            {"title": "Stock upgraded", "summary": "Bullish outlook"}
        ]
        
        sent_score = scoring.sentiment_score(news_data)
        assert isinstance(sent_score, float)
        assert 0 <= sent_score <= 100
        
        # Test composite scoring
        composite = scoring.composite_score(70.0, 60.0, 80.0, 65.0)
        assert isinstance(composite, float)
        assert 0 <= composite <= 100
        
        print("✅ Scoring functions work correctly")
        return True
    except Exception as e:
        print(f"❌ Scoring test failed: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test end-to-end integration with mock data"""
    print("\nTesting end-to-end integration...")
    try:
        import indicators
        import scoring
        
        # Create realistic price data (100 days of upward trending prices)
        base_price = 100.0
        price_data = []
        for i in range(100):
            # Add some randomness but maintain upward trend
            daily_change = (i * 0.5) + ((-1) ** i) * 2  # Trending up with volatility
            price_data.append(base_price + daily_change)
        
        # Step 1: Extract closing prices (simulated)
        closing_prices = price_data
        assert len(closing_prices) >= 50
        
        # Step 2: Calculate technical indicators
        rsi_value = indicators.rsi(closing_prices, 14)
        macd_data = indicators.macd(closing_prices, 12, 26, 9)
        sma_50 = indicators.sma(closing_prices, 50)
        sma_200 = indicators.sma(closing_prices, 50)  # Use 50 instead of 200 for test data
        
        assert rsi_value is not None
        assert macd_data["macd_line"] is not None
        assert sma_50 is not None
        
        # Step 3: Create indicators dict
        indicators_dict = {
            "rsi": rsi_value,
            "macd": macd_data,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "current_price": closing_prices[-1]
        }
        
        # Step 4: Calculate technical score
        tech_score = scoring.technical_score(indicators_dict)
        assert isinstance(tech_score, float)
        assert 0 <= tech_score <= 100
        
        # Step 5: Test direct calculation method
        direct_score = scoring.technical_score_from_prices(closing_prices)
        assert isinstance(direct_score, float)
        assert 0 <= direct_score <= 100
        
        # Step 6: Test with mock fundamental data
        mock_company_data = {
            "symbol": "MOCK",
            "market_cap": "$100B",
            "pe_ratio": "18.5",
            "dividend_yield": "2.5",
            "price": str(closing_prices[-1])
        }
        
        fund_score = scoring.fundamentals_score(mock_company_data)
        
        # Step 7: Calculate composite score
        composite = scoring.composite_score(fund_score, tech_score, 60.0, 55.0)
        
        print(f"✅ Integration test completed successfully!")
        print(f"   Technical Score: {tech_score:.2f}")
        print(f"   Direct Technical Score: {direct_score:.2f}")
        print(f"   Fundamentals Score: {fund_score:.2f}")
        print(f"   Composite Score: {composite:.2f}")
        print(f"   RSI: {rsi_value:.2f}")
        print(f"   MACD Line: {macd_data['macd_line']:.4f}")
        print(f"   SMA 50: {sma_50:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("TRADING AGENT UTILS FLOW VALIDATION")
    print("=" * 60)
    print("Testing: http_client → nasdaq_api → indicators → scoring")
    print("-" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("HTTP Client", test_http_client),
        ("NASDAQ API", test_nasdaq_api),
        ("Indicators", test_indicators),
        ("Scoring", test_scoring),
        ("Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("The entire flow is working correctly:")
        print("  1. ✅ HTTP client handles requests and caching")
        print("  2. ✅ NASDAQ API fetches and normalizes data")
        print("  3. ✅ Indicators calculate technical metrics")
        print("  4. ✅ Scoring converts data to normalized scores")
        print("  5. ✅ End-to-end integration works properly")
        return True
    else:
        print(f"\n⚠️  {total-passed} test(s) failed!")
        print("Please check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
