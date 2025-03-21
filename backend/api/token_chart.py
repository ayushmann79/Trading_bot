from fastapi import APIRouter, HTTPException
import requests
import logging
import time

router = APIRouter()

COINGECKO_API = "https://api.coingecko.com/api/v3"
DEFAULT_TOKEN = "avalanche-2"  # ✅ Default fallback token

def fetch_chart_data(token_id: str, days="7", retries=3, delay=2):
    """
    Fetch historical price data with retries to handle API rate limits.
    """
    url = f"{COINGECKO_API}/coins/{token_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            data = response.json()

            # ✅ Handle API rate limits (429)
            if response.status_code == 429:
                logging.warning("Rate limit exceeded, retrying in 2 seconds...")
                time.sleep(delay)
                continue  # Retry the request

            # ✅ Handle invalid token_id
            if response.status_code == 404 or "prices" not in data or not data["prices"]:
                logging.error(f"Invalid or missing data for {token_id}")
                return None  # No data found

            return data  # Successfully fetched data

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            time.sleep(delay)

    return None  # If all retries fail, return None

@router.get("/token-chart/{token_id}")
def get_token_chart(token_id: str, days: str = "7"):
    """
    Fetch historical price data for a token.
    ✅ If token is missing, fallback to DEFAULT_TOKEN.
    """
    data = fetch_chart_data(token_id, days)

    if not data:  # If no data, retry with AVAX
        logging.warning(f"No chart data for {token_id}, attempting fallback to {DEFAULT_TOKEN}")
        data = fetch_chart_data(DEFAULT_TOKEN, days)

    if not data:  # Final failure
        raise HTTPException(status_code=404, detail="No price data available.")

    return data
