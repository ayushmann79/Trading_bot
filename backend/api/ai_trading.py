import numpy as np
from backend.api.market_data import get_historical_prices, calculate_z_score, predict_price

def mean_reversion_strategy(token_id="tether", use_ai=True):
    """
    Compute Z-score & decide trade action based on Mean Reversion Strategy.
    Optionally integrates AI-based price prediction.
    
    :param token_id: Cryptocurrency token ID.
    :param use_ai: Whether to use AI for enhanced decision-making.
    :return: Trading action ("Buy", "Sell", "Hold").
    """
    df = get_historical_prices(token_id)

    if df.empty or len(df) < 20:
        print("Not enough data for Mean Reversion strategy.")
        return "Hold"

    z_score = calculate_z_score(df)

    # AI-Powered Prediction (Optional)
    if use_ai:
        ai_prediction = predict_price(token_id)
        if "predicted_price" in ai_prediction:
            predicted_price = ai_prediction["predicted_price"]
            last_price = df["price"].iloc[-1]
            price_diff = (predicted_price - last_price) / last_price

            # Adjust buy/sell signals based on AI forecast
            if price_diff > 0.05:  # AI predicts 5%+ growth
                return "Buy"
            elif price_diff < -0.05:  # AI predicts 5%+ drop
                return "Sell"

    # Classic Mean Reversion Decision
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
