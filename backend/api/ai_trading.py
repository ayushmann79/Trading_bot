import numpy as np
from backend.api.market_data import get_historical_prices, calculate_z_score, fetch_market_data

def mean_reversion_strategy(token_id="tether"):
    """
    Compute Z-score & decide trade action based on Mean Reversion Strategy.
    """
    df = get_historical_prices(token_id)

    if df.empty or len(df) < 20:
        print("Not enough data for Mean Reversion strategy.")
        return "Hold"

    z_score = calculate_z_score(df)

    if z_score > 1.5:
        return "Sell"
    elif z_score < -1.5:
        return "Buy"
    else:
        return "Hold"

if __name__ == "__main__":
    token_id = "tether"  # Example: USDT
    decision = mean_reversion_strategy(token_id)
    print(f"Mean Reversion Trading Decision for {token_id}: {decision}")

    # Debugging: Show the last few rows
    df = fetch_market_data(token_id)
    if not df.empty:
        print(df.tail())  
    else:
        print("No market data available.")
