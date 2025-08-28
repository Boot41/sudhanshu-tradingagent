#!/usr/bin/env python3
"""Script to populate the stocks table with initial data."""

from sqlalchemy.orm import sessionmaker
from db.db import engine, Base
from model.model import Stock

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Sample stock data
stocks_data = [
    # Technology stocks
    {"ticker": "INFY", "name": "Infosys", "industry": "technology", "current_price": 1450.50, "performance": "+6.3%", "volume": "2.1M"},
    {"ticker": "TCS", "name": "Tata Consultancy Services", "industry": "technology", "current_price": 3890.75, "performance": "+5.9%", "volume": "1.8M"},
    {"ticker": "WIPRO", "name": "Wipro", "industry": "technology", "current_price": 425.30, "performance": "+4.5%", "volume": "3.2M"},
    {"ticker": "HCLT", "name": "HCL Technologies", "industry": "technology", "current_price": 1180.25, "performance": "+4.2%", "volume": "1.5M"},
    {"ticker": "TECHM", "name": "Tech Mahindra", "industry": "technology", "current_price": 1095.80, "performance": "+3.8%", "volume": "2.0M"},
    
    # Automotive stocks
    {"ticker": "TM", "name": "Tata Motors", "industry": "automotive", "current_price": 485.60, "performance": "+5.2%", "volume": "4.5M"},
    {"ticker": "M&M", "name": "Mahindra & Mahindra", "industry": "automotive", "current_price": 1520.40, "performance": "+4.8%", "volume": "2.8M"},
    {"ticker": "MSIL", "name": "Maruti Suzuki", "industry": "automotive", "current_price": 10850.90, "performance": "+3.1%", "volume": "1.2M"},
    {"ticker": "BJAUT", "name": "Bajaj Auto", "industry": "automotive", "current_price": 6890.25, "performance": "+2.5%", "volume": "0.8M"},
    {"ticker": "EIM", "name": "Eicher Motors", "industry": "automotive", "current_price": 3450.75, "performance": "+2.1%", "volume": "0.6M"},
]

try:
    # Clear existing data
    session.query(Stock).delete()
    
    # Add new stock data
    for stock_info in stocks_data:
        stock = Stock(**stock_info)
        session.add(stock)
    
    session.commit()
    print(f"Successfully populated {len(stocks_data)} stocks in the database")
    
    # Verify data
    count = session.query(Stock).count()
    print(f"Total stocks in database: {count}")
    
except Exception as e:
    session.rollback()
    print(f"Error populating stocks: {e}")
finally:
    session.close()
