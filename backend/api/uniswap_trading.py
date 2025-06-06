import os
import json
import time
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from backend.api.market_data import get_token_contract
from backend.api.ai_model import predict_price  # AI Model Integration

# Load environment variables
load_dotenv()

# Connect to Sepolia Testnet via Alchemy/Infura
ALCHEMY_API_URL = os.getenv("ALCHEMY_API_URL")
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

# Check Web3 Connection
if not w3.is_connected():
    raise Exception("⚠️ Web3 connection failed!")

# Wallet Credentials
PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# Uniswap V3 Router Address (Sepolia Testnet)
UNISWAP_ROUTER = Web3.to_checksum_address("0xE592427A0AEce92De3Edee1F18E0157C05861564")

# Load Uniswap ABI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ABI_PATH = os.path.join(BASE_DIR, "uniswap_router_abi.json")

with open(ABI_PATH, "r") as f:
    UNISWAP_ABI = json.load(f)

router_contract = w3.eth.contract(address=UNISWAP_ROUTER, abi=UNISWAP_ABI)

def swap_token_for_token(amount_eth, token_in, token_out):
    """
    Swap one token for another on Uniswap V3.
    :param amount_eth: Amount of ETH or token_in to swap.
    :param token_in: Token being swapped from (ETH, USDT, etc.).
    :param token_out: Token being swapped to (DAI, LINK, etc.).
    """
    if not w3.is_connected():
        print("⚠️ Web3 connection failed!")
        return
    
    # Convert token names to contract addresses (if needed)
    if len(token_in) < 10:
        token_in = get_token_contract(token_in)  # Convert symbol → contract
    if len(token_out) < 10:
        token_out = get_token_contract(token_out)  # Convert symbol → contract
    
    if not token_in or not token_out:
        print("❌ Invalid token name or contract address!")
        return

    # Convert ETH amount to Wei
    amount_wei = w3.to_wei(amount_eth, "ether")

    # Set Gas Fees
    gas_price = w3.eth.gas_price
    max_priority_fee = w3.to_wei('2', 'gwei')

    # Get correct nonce
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS, "pending")

    # Build Uniswap transaction
    txn = router_contract.functions.exactInputSingle({
        'tokenIn': Web3.to_checksum_address(token_in),
        'tokenOut': Web3.to_checksum_address(token_out),
        'fee': 3000,
        'recipient': WALLET_ADDRESS,
        'deadline': w3.eth.get_block('latest')["timestamp"] + 600,
        'amountIn': amount_wei,
        'amountOutMinimum': 0,
        'sqrtPriceLimitX96': 0
    }).build_transaction({
        'from': WALLET_ADDRESS,
        'value': amount_wei,
        'gas': 300000,
        'maxFeePerGas': gas_price + max_priority_fee,
        'maxPriorityFeePerGas': max_priority_fee,
        'nonce': nonce
    })

    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f"✅ Trade Executed! Swapped {amount_eth} {token_in} → {token_out}")
    print(f"🔗 Transaction Hash: {tx_hash.hex()}")
    print(f"📌 View on Sepolia: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")

def ai_auto_trade(token_id="ethereum", amount_eth=0.01):
    """
    AI-powered auto-trading on Uniswap.
    :param token_id: Token to trade.
    :param amount_eth: Amount of ETH to trade.
    """
    print(f"🔍 Checking AI prediction for {token_id}...")

    predicted_price = predict_price(token_id)
    if predicted_price is None:
        print("⚠️ AI prediction failed! Skipping trade.")
        return

    print(f"📈 AI Predicted Price for {token_id}: ${predicted_price:.2f}")

    # Get current price
    current_price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd").json()[token_id]["usd"]

    print(f"🔹 Current Price: ${current_price:.2f}")

    # AI Trading Logic
    if predicted_price > current_price * 1.02:  # If AI predicts 2% increase
        print(f"✅ AI suggests BUY {token_id} with {amount_eth} ETH!")
        swap_token_for_token(amount_eth, "weth", token_id)
    elif predicted_price < current_price * 0.98:  # If AI predicts 2% decrease
        print(f"🚨 AI suggests SELL {token_id} for ETH!")
        swap_token_for_token(amount_eth, token_id, "weth")
    else:
        print("🟡 AI suggests HOLD. No trade executed.")

if __name__ == "__main__":
    # Run AI Auto-Trade every 60 seconds
    while True:
        ai_auto_trade("ethereum", 0.01)  # Example: Trade ETH <-> USDT
        time.sleep(60)
