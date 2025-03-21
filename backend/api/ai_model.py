import os
import time
import numpy as np
import pandas as pd
import requests
import joblib
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CoinGecko API for fetching historical price data
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/{}/market_chart"
DEFAULT_TOKEN = "bitcoin"
MAX_RETRIES = 3  # ✅ Prevent infinite recursion

# File paths for saving models and scalers
MODEL_DIR = "backend/models/"
SCALER_FILE = os.path.join(MODEL_DIR, "scaler.pkl")
MODEL_FILE = os.path.join(MODEL_DIR, "lstm_model.pth")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# ✅ Fetch Historical Prices (Fixed Recursion & SSL Issue)
def fetch_historical_prices(token_id, days=365, retries=0):
    """Fetch historical price data for a token."""
    url = COINGECKO_API_URL.format(token_id)
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}

    try:
        response = requests.get(url, params=params, verify=True, timeout=10)  # ✅ Added timeout
        response.raise_for_status()
        data = response.json()

        if "prices" not in data:
            raise ValueError("Invalid response format")

        return pd.DataFrame(data["prices"], columns=["timestamp", "price"]).set_index("timestamp")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching data for {token_id}: {e}")

        if retries < MAX_RETRIES:
            print(f"🔄 Retrying... Attempt {retries + 1}/{MAX_RETRIES}")
            time.sleep(2)  # ✅ Prevent API rate limit issues
            return fetch_historical_prices(DEFAULT_TOKEN, days, retries + 1)
        else:
            print(f"❌ Failed after {MAX_RETRIES} attempts. Check network or API status.")
            return None

# ✅ Preprocessing Data
def preprocess_data(df, lookback=30):
    """Normalize and prepare data for LSTM model."""
    scaler = MinMaxScaler(feature_range=(0, 1))
    df["scaled_price"] = scaler.fit_transform(df["price"].values.reshape(-1, 1))

    # Save scaler for later use
    joblib.dump(scaler, SCALER_FILE)

    X, y = [], []
    for i in range(lookback, len(df)):
        X.append(df["scaled_price"].values[i-lookback:i])
        y.append(df["scaled_price"].values[i])

    return np.array(X), np.array(y), scaler

# ✅ Define PyTorch LSTM Model
class LSTMModel(nn.Module):
    def __init__(self):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=50, num_layers=2, batch_first=True)
        self.fc = nn.Linear(50, 1)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1])

# ✅ Training Function
def train_model(token_id="bitcoin", epochs=50, batch_size=16):
    """Train LSTM model using historical data."""
    df = fetch_historical_prices(token_id)
    if df is None or len(df) < 30:
        print("⚠️ Not enough data to train model.")
        return

    X, y, _ = preprocess_data(df)

    # Convert data to PyTorch tensors
    X_train = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)  # Add channel dimension
    y_train = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)

    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss = criterion(output, y_train)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.6f}")

    torch.save(model.state_dict(), MODEL_FILE)
    print(f"✅ Model trained & saved: {MODEL_FILE}")

# ✅ Prediction Function
def predict_price(token_id="bitcoin"):
    """Predict next-day price using trained LSTM model."""
    if not os.path.exists(MODEL_FILE):
        print("⚠️ No trained model found, training a new one...")
        train_model(token_id)

    model = LSTMModel()
    model.load_state_dict(torch.load(MODEL_FILE))
    model.eval()

    df = fetch_historical_prices(token_id, days=90)  # Use last 90 days for prediction
    if df is None or len(df) < 30:
        return None

    _, _, scaler = preprocess_data(df)  # Load the same scaler used during training
    last_30_days = torch.tensor(df["scaled_price"].values[-30:], dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

    with torch.no_grad():
        predicted_price_scaled = model(last_30_days).item()

    predicted_price = scaler.inverse_transform([[predicted_price_scaled]])[0][0]
    return round(predicted_price, 2)

# ✅ Run Training & Prediction
if __name__ == "__main__":
    train_model("bitcoin")
    print(f"🔮 Predicted Next-Day Price: ${predict_price('bitcoin')}")
