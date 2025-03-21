from fastapi import APIRouter, HTTPException
import requests
import logging
import time

router = APIRouter()

COINGECKO_API = "https://api.coingecko.com/api/v3"
DEFAULT_TOKEN = "avalanche-2"  # ✅ Default to AVAX

SUPPORTED_CHAINS = {
    "ethereum": 1,
    "avalanche": 43114,
    "sepolia": 11155111,
    "avalanche-fuji": 43113,
}

def fetch_token_data(token_id: str, retries=3, delay=2):
    """
    Fetch token data from CoinGecko with retry mechanism.
    """
    url = f"{COINGECKO_API}/coins/{token_id}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url)
            
            # ✅ Handle rate limits
            if response.status_code == 429:
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue  # Retry
            
            data = response.json()

            # ✅ Handle invalid tokens
            if response.status_code != 200 or "error" in data:
                logging.warning(f"Token {token_id} not found.")
                return None
            
            return data
        
        except requests.RequestException as e:
            logging.error(f"Error fetching token info: {e}")
            time.sleep(delay)
    
    return None  # Final failure

@router.get("/token-info/{token_id}")
def get_token_info(token_id: str):
    """
    Fetch token info from CoinGecko.
    ✅ Defaults to AVAX if the token is not found.
    """
    data = fetch_token_data(token_id) or fetch_token_data(DEFAULT_TOKEN)

    if not data:
        return {"error": f"Token '{token_id}' not found"}

    chain_id = SUPPORTED_CHAINS.get(data.get("asset_platform_id", "unknown"), None)

    return {
        "name": data.get("name", "Unknown"),
        "symbol": data.get("symbol", "").upper(),
        "image": data.get("image", {}).get("large", ""),
        "website": data.get("links", {}).get("homepage", [""])[0] if "links" in data else "",
        "socials": {
            "twitter": data.get("links", {}).get("twitter_screen_name", "") if "links" in data else "",
            "reddit": data.get("links", {}).get("subreddit_url", "") if "links" in data else "",
        },
        "fdv": data.get("market_data", {}).get("fully_diluted_valuation", {}).get("usd", None),
        "max_supply": data.get("market_data", {}).get("max_supply", None),
        "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd", None),
        "chain_id": chain_id,
    }
