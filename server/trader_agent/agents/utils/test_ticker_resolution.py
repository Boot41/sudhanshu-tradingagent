#!/usr/bin/env python3
"""
Test script for resolve_ticker functionality in nasdaq_api.py

This script tests the external yfinance search functionality by calling
the resolve_ticker method with various company names and displaying results.
"""

import sys
import os
import logging
from typing import List, Tuple

# Add the current directory to Python path so we can import nasdaq_api
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nasdaq_api import resolve_ticker

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_ticker_resolution():
    """Test resolve_ticker with various company names."""
    
    # Test cases: (company_name, expected_ticker_or_description)
    test_cases = [
        ("Apple Inc", "AAPL"),
       # ("Microsoft Corporation", "MSFT"),
       # ("Google", "GOOGL or GOOG"),
       # ("Amazon", "AMZN"),
       # ("Tesla", "TSLA"),
       # ("Meta", "META"),
       # ("Netflix", "NFLX"),
       # ("NVIDIA", "NVDA"),
       # ("Coca Cola", "KO"),
       # ("Johnson & Johnson", "JNJ"),
       # ("Walmart", "WMT"),
       # ("Disney", "DIS"),
       # ("Invalid Company XYZ123", "None (should not be found)"),
       # ("", "None (empty input)"),
       # ("A", "None or some ticker (very short input)"),
    ]
    
    print("=" * 80)
    print("TESTING TICKER RESOLUTION WITH YFINANCE SEARCH")
    print("=" * 80)
    print()
    
    results = []
    
    for i, (company_name, expected) in enumerate(test_cases, 1):
        print(f"Test {i:2d}: '{company_name}'")
        print(f"Expected: {expected}")
        
        try:
            # Test with cache enabled
            ticker = resolve_ticker(company_name, use_cache=True)
            print(f"Result:   {ticker}")
            
            # Store result for summary
            results.append((company_name, ticker, expected))
            
            if ticker:
                print(f"✅ SUCCESS - Found ticker: {ticker}")
            else:
                print(f"❌ NO RESULT - Could not resolve ticker")
                
        except Exception as e:
            print(f"🔥 ERROR - Exception occurred: {e}")
            results.append((company_name, f"ERROR: {e}", expected))
        
        print("-" * 40)
        print()
    
    # Print summary
    print("=" * 80)
    print("SUMMARY OF RESULTS")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for company_name, result, expected in results:
        status = "✅" if result and not str(result).startswith("ERROR") else "❌"
        if result and not str(result).startswith("ERROR"):
            successful += 1
        else:
            failed += 1
            
        print(f"{status} {company_name:<25} -> {result}")
    
    print()
    print(f"Total tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful/len(results)*100:.1f}%")


def test_edge_cases():
    """Test edge cases and error handling."""
    
    print("\n" + "=" * 80)
    print("TESTING EDGE CASES")
    print("=" * 80)
    
    edge_cases = [
        None,
        123,
        [],
        {},
        "   ",  # whitespace only
        "a" * 100,  # very long string
    ]
    
    for i, test_input in enumerate(edge_cases, 1):
        print(f"Edge case {i}: {repr(test_input)}")
        try:
            result = resolve_ticker(test_input)
            print(f"Result: {result}")
            print("✅ Handled gracefully")
        except Exception as e:
            print(f"🔥 Exception: {e}")
        print("-" * 40)


def test_cache_behavior():
    """Test caching behavior by making the same request twice."""
    
    print("\n" + "=" * 80)
    print("TESTING CACHE BEHAVIOR")
    print("=" * 80)
    
    test_company = "Apple Inc"
    
    print(f"First call (cache=True): {test_company}")
    start_time = __import__('time').time()
    result1 = resolve_ticker(test_company, use_cache=True)
    time1 = __import__('time').time() - start_time
    print(f"Result: {result1}, Time: {time1:.3f}s")
    
    print(f"Second call (cache=True): {test_company}")
    start_time = __import__('time').time()
    result2 = resolve_ticker(test_company, use_cache=True)
    time2 = __import__('time').time() - start_time
    print(f"Result: {result2}, Time: {time2:.3f}s")
    
    print(f"Third call (cache=False): {test_company}")
    start_time = __import__('time').time()
    result3 = resolve_ticker(test_company, use_cache=False)
    time3 = __import__('time').time() - start_time
    print(f"Result: {result3}, Time: {time3:.3f}s")
    
    print(f"\nCache analysis:")
    print(f"Results consistent: {result1 == result2 == result3}")
    print(f"Second call faster: {time2 < time1}")


if __name__ == "__main__":
    print("Starting ticker resolution tests...")
    print(f"Python path: {sys.path[0]}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    try:
        # Run all tests
        test_ticker_resolution()
        test_edge_cases()
        test_cache_behavior()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
