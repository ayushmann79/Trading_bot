import requests
import os
import asyncio
from web3 import Web3
from fastapi import APIRouter
from dotenv import load_dotenv
from database.db_setup import SessionLocal
from database.models import Trade
from backend.api.ai_model import predict_price
# Load environment variables
load_dotenv()

# API URLs
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
TOKEN_PRICE_API_URL = f"{COINGECKO_API_URL}/simple/price"

# Load API keys
ALCHEMY_API_URL = os.getenv("ALCHEMY_API_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# FastAPI Router
router = APIRouter()

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))


def get_token_contract(token_name: str, network="ethereum") -> str:
    """Fetch the contract address of a token from CoinGecko."""
    url = f"{COINGECKO_API_URL}/coins/{token_name.lower()}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "platforms" in data and network in data["platforms"]:
            return data["platforms"][network]

        return None
    except requests.exceptions.RequestException as e:
        return None


@router.get("/portfolio")
async def portfolio():
    """Fetch ETH balance of the wallet."""
    try:
        balance = w3.eth.get_balance(WALLET_ADDRESS)
        return {"wallet": WALLET_ADDRESS, "balance": w3.from_wei(balance, 'ether')}
    except Exception as e:
        return {"error": str(e)}


@router.get("/contract/{token_name}")
async def token_contract(token_name: str):
    """Fetch a token's contract address."""
    contract_address = get_token_contract(token_name)
    return {"token": token_name, "contract_address": contract_address} if contract_address else {"error": "Token not found"}


@router.get("/prices/{token_ids}")
async def get_token_price(token_ids: str):
    """Fetch real-time token prices from CoinGecko."""
    params = {"ids": token_ids, "vs_currencies": "usd"}
    response = requests.get(TOKEN_PRICE_API_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch price"}


@router.get("/trades")
async def get_trade_history():
    """Fetch all past trade history from the database."""
    db = SessionLocal()
    trades = db.query(Trade).all()
    db.close()
    return [{"id": t.id, "token": t.token, "amount": t.amount, "price": t.price, "timestamp": t.timestamp} for t in trades]


@router.get("/ai-predict/{token_id}")
async def ai_price_prediction(token_id: str):
    """Predict next-day price using AI."""
    predicted_price = predict_price(token_id)
    return {"token": token_id, "predicted_price": predicted_price} if predicted_price else {"error": "Prediction failed"}


# ✅ Automated Testing of AI Prediction API
async def run_tests():
    print(await ai_price_prediction("ethereum"))

if __name__ == "__main__":
    asyncio.run(run_tests())
