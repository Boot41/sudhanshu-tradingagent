"""
Test script for scoring module functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scoring import (
    fundamentals_score, 
    technical_score, 
    sentiment_score, 
    news_score,
    technical_score_from_prices,
    composite_score
)

def test_fundamentals_score():
    """Test fundamentals scoring with sample company data."""
    print("Testing fundamentals_score()...")
    
    # Sample company data (similar to nasdaq_api output)
    sample_company = {
        "symbol": "AAPL",
        "market_cap": "$2.5T",
        "pe_ratio": "18.5",
        "dividend_yield": "0.5%",
        "volume": "50000000",
        "avg_volume": "45000000",
        "price": "150.00",
        "high_52week": "180.00",
        "low_52week": "120.00"
    }
    
    score = fundamentals_score(sample_company)
    print(f"Fundamentals score for AAPL: {score:.2f}")
    assert 0 <= score <= 100, "Score should be between 0-100"
    
    # Test with empty data
    empty_score = fundamentals_score({})
    print(f"Empty data score: {empty_score:.2f}")
    assert empty_score == 50.0, "Empty data should return neutral score"
    
    print("✓ fundamentals_score() tests passed\n")


def test_technical_score():
    """Test technical scoring with sample indicators."""
    print("Testing technical_score()...")
    
    # Sample indicators data
    sample_indicators = {
        "rsi": 45.0,  # Neutral
        "macd": {
            "macd_line": 1.2,
            "signal_line": 0.8,
            "histogram": 0.4
        },
        "sma_50": 145.0,
        "sma_200": 140.0,
        "current_price": 150.0
    }
    
    score = technical_score(sample_indicators)
    print(f"Technical score: {score:.2f}")
    assert 0 <= score <= 100, "Score should be between 0-100"
    
    # Test with oversold RSI
    oversold_indicators = sample_indicators.copy()
    oversold_indicators["rsi"] = 25.0
    oversold_score = technical_score(oversold_indicators)
    print(f"Oversold RSI score: {oversold_score:.2f}")
    
    print("✓ technical_score() tests passed\n")


def test_sentiment_score():
    """Test sentiment scoring with sample news data."""
    print("Testing sentiment_score()...")
    
    # Sample news data
    positive_news = [
        {"title": "Company beats earnings expectations", "summary": "Strong growth reported"},
        {"title": "Stock upgraded by analysts", "summary": "Bullish outlook for next quarter"}
    ]
    
    negative_news = [
        {"title": "Company misses earnings", "summary": "Weak performance disappoints"},
        {"title": "Stock downgraded due to concerns", "summary": "Bearish sentiment prevails"}
    ]
    
    mixed_news = positive_news + negative_news
    
    pos_score = sentiment_score(positive_news)
    neg_score = sentiment_score(negative_news)
    mixed_score = sentiment_score(mixed_news)
    
    print(f"Positive news score: {pos_score:.2f}")
    print(f"Negative news score: {neg_score:.2f}")
    print(f"Mixed news score: {mixed_score:.2f}")
    
    assert pos_score > 50, "Positive news should score above neutral"
    assert neg_score < 50, "Negative news should score below neutral"
    assert 0 <= mixed_score <= 100, "Mixed score should be between 0-100"
    
    print("✓ sentiment_score() tests passed\n")


def test_news_score():
    """Test news impact scoring."""
    print("Testing news_score()...")
    
    high_impact_news = [
        {"title": "Company announces major acquisition deal", "summary": "Strategic partnership formed"},
        {"title": "Earnings beat expectations significantly", "summary": "Record revenue reported"}
    ]
    
    score = news_score(high_impact_news)
    print(f"High impact news score: {score:.2f}")
    assert score > 50, "High impact positive news should score above neutral"
    
    print("✓ news_score() tests passed\n")


def test_technical_score_from_prices():
    """Test technical scoring from price data."""
    print("Testing technical_score_from_prices()...")
    
    # Generate sample price data (uptrend)
    base_price = 100.0
    sample_prices = [base_price + i * 0.5 + (i % 10) * 0.2 for i in range(100)]
    
    score = technical_score_from_prices(sample_prices)
    print(f"Uptrend price score: {score:.2f}")
    assert 0 <= score <= 100, "Score should be between 0-100"
    
    # Test with insufficient data
    short_prices = [100, 101, 102]
    short_score = technical_score_from_prices(short_prices)
    print(f"Insufficient data score: {short_score:.2f}")
    assert short_score == 50.0, "Insufficient data should return neutral score"
    
    print("✓ technical_score_from_prices() tests passed\n")


def test_composite_score():
    """Test composite scoring."""
    print("Testing composite_score()...")
    
    # Sample individual scores
    fund_score = 75.0
    tech_score = 60.0
    sent_score = 80.0
    news_score_val = 70.0
    
    composite = composite_score(fund_score, tech_score, sent_score, news_score_val)
    print(f"Composite score: {composite:.2f}")
    assert 0 <= composite <= 100, "Composite score should be between 0-100"
    
    # Test with custom weights
    custom_weights = {"fundamentals": 0.5, "technical": 0.3, "sentiment": 0.1, "news": 0.1}
    weighted_composite = composite_score(fund_score, tech_score, sent_score, news_score_val, custom_weights)
    print(f"Weighted composite score: {weighted_composite:.2f}")
    
    print("✓ composite_score() tests passed\n")


def main():
    """Run all tests."""
    print("Running scoring module tests...\n")
    
    try:
        test_fundamentals_score()
        test_technical_score()
        test_sentiment_score()
        test_news_score()
        test_technical_score_from_prices()
        test_composite_score()
        
        print("🎉 All scoring tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
