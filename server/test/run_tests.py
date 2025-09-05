#!/usr/bin/env python3
"""
Test runner script for trading agent tests.
Sets up proper PYTHONPATH and runs tests from the correct location.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the server directory to Python path so imports work correctly
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

def run_test_file(test_file_path, description=""):
    """Run a single test file with proper environment setup."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file_path}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        # Set PYTHONPATH environment variable
        env = os.environ.copy()
        env['PYTHONPATH'] = str(server_dir)
        
        result = subprocess.run([
            sys.executable, test_file_path
        ], env=env, capture_output=True, text=True, cwd=str(server_dir))
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
                
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERROR running test: {e}")
        return False

def main():
    """Run all tests in the test directory."""
    test_dir = Path(__file__).parent
    
    # List of test files to run
    test_files = [
        (test_dir / "trader_agent" / "agents" / "utils" / "test_indicators.py", "Technical indicators unit tests"),
        (test_dir / "trader_agent" / "agents" / "utils" / "test_scoring.py", "Scoring module tests"),
        (test_dir / "trader_agent" / "agents" / "utils" / "test_historical.py", "Historical data integration test"),
        (test_dir / "trader_agent" / "agents" / "utils" / "test_ticker_resolution.py", "Ticker resolution tests"),
        (test_dir / "trader_agent" / "agents" / "utils" / "test_integration.py", "Full integration tests"),
    ]
    
    print("🚀 Starting Trading Agent Test Suite")
    print(f"Server directory: {server_dir}")
    print(f"Test directory: {test_dir}")
    
    passed = 0
    failed = 0
    
    for test_file, description in test_files:
        if test_file.exists():
            if run_test_file(str(test_file), description):
                passed += 1
            else:
                failed += 1
        else:
            print(f"\n⚠️  Test file not found: {test_file}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n💥 {failed} test(s) failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
