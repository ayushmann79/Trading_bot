import pandas as pd
import numpy as np
from backend.api.market_data import get_historical_prices, calculate_z_score

def backtest_mean_reversion(
    token_id="solana", 
    initial_balance=10000, 
    z_threshold=1.0, 
    days=90, 
    stop_loss_pct=0.05,   # 5% Stop-Loss
    take_profit_pct=0.10   # 10% Take-Profit
):
    """
    Backtest the Mean Reversion Strategy using historical price data with Stop-Loss & Take-Profit.
    
    :param token_id: Cryptocurrency token ID.
    :param initial_balance: Starting balance in USD.
    :param z_threshold: Z-score threshold for buy/sell signals.
    :param days: Number of days of historical price data.
    :param stop_loss_pct: Stop-loss percentage (e.g., 0.05 = 5% drop).
    :param take_profit_pct: Take-profit percentage (e.g., 0.10 = 10% gain).
    """
    df = get_historical_prices(token_id, days=days)

    if df.empty or len(df) < 20:
        print("Not enough data for backtesting.")
        return

    df["Z-score"] = calculate_z_score(df)

    balance = initial_balance
    position = 0  # Number of tokens held
    buy_price = 0
    trade_log = []

    for i in range(20, len(df)):
        z_score = df["Z-score"].iloc[i]
        price = df["price"].iloc[i]

        if z_score < -z_threshold and position == 0:
            # Buy Signal
            position = balance / price
            buy_price = price
            balance = 0
            trade_log.append(f"BUY at ${price:.2f} on {df['timestamp'].iloc[i]}")
            print(trade_log[-1])

        elif position > 0:
            # Stop-Loss Check
            if price <= buy_price * (1 - stop_loss_pct):
                balance = position * price  # Sell all
                position = 0
                trade_log.append(f"STOP-LOSS triggered! SELL at ${price:.2f} on {df['timestamp'].iloc[i]}")
                print(trade_log[-1])

            # Take-Profit Check
            elif price >= buy_price * (1 + take_profit_pct):
                balance = position * price  # Sell all
                position = 0
                trade_log.append(f"TAKE-PROFIT triggered! SELL at ${price:.2f} on {df['timestamp'].iloc[i]}")
                print(trade_log[-1])

            # Normal Sell Condition (Mean Reversion Exit)
            elif z_score > z_threshold:
                balance = position * price  # Sell all
                position = 0
                trade_log.append(f"SELL at ${price:.2f} on {df['timestamp'].iloc[i]}")
                print(trade_log[-1])

    # Final balance (if still holding tokens)
    if position > 0:
        balance = position * df["price"].iloc[-1]

    print(f"Final Balance: ${balance:.2f} | Net Profit: ${balance - initial_balance:.2f}")

if __name__ == "__main__":
    token_id = "solana"  
    print(token_id)
    backtest_mean_reversion(token_id)
