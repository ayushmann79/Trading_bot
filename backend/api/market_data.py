import requests
import os
import asyncio
from web3 import Web3
from fastapi import APIRouter
from dotenv import load_dotenv
from database.db_setup import SessionLocal
from database.models import Trade

# Load environment variables
load_dotenv()

# API URLs
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
TOKEN_PRICE_API_URL = "https://api.coingecko.com/api/v3/simple/price"

# Load API keys
ALCHEMY_API_URL = os.getenv("ALCHEMY_API_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# FastAPI Router
router = APIRouter()

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))


def get_token_contract(token_name: str, network="ethereum") -> str:
    """
    Fetch the contract address of a token from CoinGecko.
    """
    url = f"{COINGECKO_API_URL}/coins/{token_name.lower()}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "platforms" in data and network in data["platforms"]:
            return data["platforms"][network]

        print(f"❌ Token '{token_name}' not found on {network}.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching contract address: {e}")
        return None


def get_wallet_balance():
    """Fetch ETH balance of the wallet."""
    try:
        balance = w3.eth.get_balance(WALLET_ADDRESS)
        return {"wallet": WALLET_ADDRESS, "balance": w3.from_wei(balance, 'ether')}
    except Exception as e:
        return {"error": f"Failed to fetch wallet balance: {str(e)}"}


@router.get("/portfolio")
async def portfolio():
    """API route to fetch ETH balance of the wallet."""
    return get_wallet_balance()


@router.get("/contract/{token_name}")
async def token_contract(token_name: str):
    """API route to fetch a token's contract address."""
    contract_address = get_token_contract(token_name)
    if contract_address:
        return {"token": token_name, "contract_address": contract_address}
    return {"error": f"Token '{token_name}' not found."}


@router.get("/prices/{token_ids}")
async def get_token_price(token_ids: str):
    """
    API route to fetch real-time token prices from CoinGecko.
    Supports multiple token IDs separated by commas.
    """
    params = {"ids": token_ids, "vs_currencies": "usd"}
    response = requests.get(TOKEN_PRICE_API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch price"}


@router.get("/trades")
async def get_trade_history():
    """Fetch all past trade history."""
    db = SessionLocal()
    trades = db.query(Trade).all()
    db.close()

    return [{"id": t.id, "token": t.token, "amount": t.amount, "price": t.price, "timestamp": t.timestamp} for t in trades]


# ✅ Fixed: Fetch prices for multiple tokens
async def run_tests():
    print(get_token_contract("tether"))  # Example: Get USDT contract address
    print(get_wallet_balance())  # Example: Get wallet balance

    # ✅ Fetch multiple token prices (Bitcoin, Ethereum, Solana)
    token_prices = await get_token_price("bitcoin,ethereum,solana")
    print(token_prices)

    # ✅ Fetch trade history
    trade_history = await get_trade_history()
    print(trade_history)


if __name__ == "__main__":
    asyncio.run(run_tests())  # ✅ Properly await async functions
