import logging
import pandas as pd
from dotenv import load_dotenv

# Import the function from your module
from nasdaq_api import get_historical_data

# Set up basic logging to see output from the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_test():
    """
    Runs a test of the get_historical_data function and prints the full results.
    """
    # Load environment variables from your .env file
    load_dotenv()
    
    print("--- Starting Historical Data Test ---")
    
    # Define test parameters
    ticker = "AAPL"
    period = "1mo"
    
    # Call the function
    historical_df = get_historical_data(ticker, period)
    
    # Check the result
    if isinstance(historical_df, pd.DataFrame) and not historical_df.empty:
        print(f"\n✅ SUCCESS: Retrieved {len(historical_df)} data points for {ticker}.")
        print("--- Complete Fetched Data ---")
        
        # Use pandas option_context to temporarily display all rows and columns
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(historical_df)
            
        print("---------------------------")
    else:
        print("\n❌ FAILED: Did not retrieve valid data. Check logs for errors.")
    
    print("\n--- Test Finished ---")

if __name__ == "__main__":
    run_test()
