from fastapi import APIRouter, HTTPException
import requests
import logging

router = APIRouter()

COINGECKO_API = "https://api.coingecko.com/api/v3"

@router.get("/token-chart/{token_id}")
def get_token_chart(token_id: str, days: str = "7"):
    """
    Fetch historical price data for a token.
    Supports: 1 day, 7 days, 30 days, and max.
    If data is unavailable, falls back to 'max'.
    """

    if days == "all":
        days = "max"  # ✅ Normalize "all" to "max"

    url = f"{COINGECKO_API}/coins/{token_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        # ✅ Handle API rate limits
        if response.status_code == 429:
            logging.error("Rate limit exceeded, please slow down API requests.")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

        # ✅ Handle invalid token_id
        if response.status_code == 404:
            logging.error(f"Invalid token_id: {token_id}")
            raise HTTPException(status_code=404, detail="Token not found.")

        # ✅ Handle missing or empty data
        if response.status_code != 200 or "prices" not in data or not data["prices"]:
            logging.warning(f"Error fetching {days}-day data for {token_id}, retrying with 'max'.")

            # Retry with max
            params["days"] = "max"
            response = requests.get(url, params=params)
            data = response.json()

            if response.status_code != 200 or "prices" not in data or not data["prices"]:
                logging.error(f"No data available for {token_id} even with 'max' range.")
                raise HTTPException(status_code=404, detail="No price data available.")

        return data

    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
