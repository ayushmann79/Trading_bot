from sqlalchemy.orm import Session
from database.db_setup import SessionLocal
from database.models import MarketData
import requests
import pandas as pd
import numpy as np
from scipy.stats import zscore

# CoinGecko API URL
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"

def get_historical_prices(token_id: str, days: int = 90) -> pd.DataFrame:
    """
    Fetch historical token prices from CoinGecko.
    :param token_id: Token ID (e.g., 'tether' for USDT).
    :param days: Number of days of historical data.
    :return: DataFrame with timestamps and prices.
    """
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    try:
        response = requests.get(COINGECKO_API_URL.format(token_id=token_id), params=params)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching market data: {e}")
        return pd.DataFrame()

    prices = data.get("prices", [])
    if not prices:
        print("No price data found.")
        return pd.DataFrame()

    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # Debugging Output: Print last 10 prices
    print("Latest Market Data:")
    print(df.tail(10))

    return df

def save_market_data(token_id: str, df: pd.DataFrame):
    """
    Save historical market data into the database efficiently.
    """
    if df.empty:
        print("No data to save.")
        return

    db: Session = SessionLocal()
    try:
        market_entries = [
            MarketData(token_id=token_id, timestamp=row["timestamp"], price=row["price"])
            for _, row in df.iterrows()
        ]
        db.bulk_save_objects(market_entries)  # Efficient batch insert
        db.commit()
        print(f"Market data saved for {token_id}")
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
    finally:
        db.close()

def calculate_z_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute Z-score for Mean Reversion strategy.
    :param df: DataFrame with historical prices.
    :return: Full series of Z-score values.
    """
    if len(df) < 20:
        print("Not enough data for Z-score calculation.")
        return pd.Series([0] * len(df))  # Return zero values

    df["Z-score"] = zscore(df["price"].astype(float), nan_policy='omit')  # Convert to float & handle NaNs

    # Debugging Output: Print last 10 Z-scores
    print("Latest Z-score Data:")
    print(df[["timestamp", "price", "Z-score"]].tail(10))

    return df["Z-score"]

def fetch_market_data(token_id: str, days: int = 90) -> pd.DataFrame:
    """
    Wrapper function to fetch historical market data.
    :param token_id: Token ID (e.g., 'tether' for USDT).
    :param days: Number of days of historical data.
    :return: DataFrame with timestamps and prices.
    """
    return get_historical_prices(token_id, days)

if __name__ == "__main__":
    token_id = "tether"  # Example: USDT token ID on CoinGecko
    
    # Fetch and save market data
    df = get_historical_prices(token_id)
    
    if not df.empty:
        save_market_data(token_id, df)
        
        # Calculate Z-score for Mean Reversion
        z_score = calculate_z_score(df)
        print(f"Latest Z-score for {token_id}: {z_score.iloc[-1]:.2f}")
    else:
        print("Failed to fetch token price data.")
