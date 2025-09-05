# Trading Agent Test Suite

This directory contains all test files for the trading agent system, organized in a proper directory structure.

## Directory Structure

```
server/test/
├── __init__.py
├── README.md
├── run_tests.py                    # Test runner script
└── trader_agent/
    └── agents/
        └── utils/
            ├── test_historical.py      # Historical data integration test
            ├── test_indicators.py      # Technical indicators unit tests
            ├── test_integration.py     # Full integration tests
            ├── test_scoring.py         # Scoring module tests
            └── test_ticker_resolution.py # Ticker resolution tests
```

## Running Tests

### Option 1: Use the Test Runner (Recommended)
```bash
cd /home/sudhanshu/tradingagent/server
python3 test/run_tests.py
```

### Option 2: Run Individual Tests
```bash
cd /home/sudhanshu/tradingagent/server
PYTHONPATH=/home/sudhanshu/tradingagent/server python3 test/test_indicators.py
PYTHONPATH=/home/sudhanshu/tradingagent/server python3 test/trader_agent/agents/utils/test_scoring.py
```

## Test Categories

1. **Unit Tests**: `test_indicators.py` - Tests individual technical indicator functions
2. **Module Tests**: `test_scoring.py` - Tests scoring algorithms and calculations
3. **Integration Tests**: `test_integration.py` - Tests complete workflow integration
4. **API Tests**: `test_historical.py`, `test_ticker_resolution.py` - Tests external API interactions

## Requirements

The tests require the following dependencies to be installed:
- pandas
- yfinance (for API tests)
- python-dotenv (for environment variable tests)

## Notes

- All test files have been moved from `trader_agent/agents/utils/` to maintain proper separation of concerns
- Import paths have been updated to use absolute imports from the server root
- The test runner automatically sets up the correct PYTHONPATH for module resolution
