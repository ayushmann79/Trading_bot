from fastapi import APIRouter, HTTPException
import requests
import logging

router = APIRouter()

COINGECKO_API = "https://api.coingecko.com/api/v3"

@router.get("/token-info/{token_id}")
def get_token_info(token_id: str):
    """
    Fetch detailed token info from CoinGecko.
    Default token: AVAX (Avalanche) if not found.
    """
    url = f"{COINGECKO_API}/coins/{token_id}"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "error" in data:
            logging.warning(f"Token {token_id} not found, using AVAX as default.")
            response = requests.get(f"{COINGECKO_API}/coins/avalanche-2")
            data = response.json()

        return {
            "name": data.get("name", "Unknown"),
            "symbol": data.get("symbol", "").upper(),
            "image": data["image"].get("large", ""),
            "website": data["links"].get("homepage", [""])[0],
            "socials": {
                "twitter": data["links"].get("twitter_screen_name", ""),
                "reddit": data["links"].get("subreddit_url", ""),
            },
            "fdv": data["market_data"].get("fully_diluted_valuation", {}).get("usd", None),
            "max_supply": data["market_data"].get("max_supply", None),
            "market_cap": data["market_data"].get("market_cap", {}).get("usd", None),
        }

    except requests.RequestException as e:
        logging.error(f"Error fetching token info: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
