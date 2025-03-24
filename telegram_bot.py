import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import yfinance as yf
import asyncio

# Your Bot Token
TOKEN = "7851301405:AAFFQxBuNstIy_-LeVqE3UvKjQJEYnk7fPM"

# Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the AI Trading Bot!\nUse /price <symbol> to get live prices.")

# Help Command
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Show help message\n/price <symbol> - Get live stock/crypto price")


# Fetch the latest symbol-to-ID mapping from CoinGecko
def get_coin_mapping():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url).json()
    return {coin["symbol"].upper(): coin["id"] for coin in response}

# Load mapping once at startup
coin_mapping = get_coin_mapping()

async def get_price(update, context):
    symbol = context.args[0].upper()  # Convert user input to uppercase
    coin_id = coin_mapping.get(symbol)

    if not coin_id:
        await update.message.reply_text("Invalid symbol or data not found.")
        return
    
    # Fetch price for the corresponding CoinGecko ID
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(url).json()

    if coin_id in response:
        price = response[coin_id]["usd"]
        await update.message.reply_text(f"{symbol} Price: ${price}")
    else:
        await update.message.reply_text("Price data not available.")

# Main Function to Run the Bot
def main():
    app = Application.builder().token(TOKEN).build() 

    # Add Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", get_price))  #command for price checking

    # Start Bot
    print("ULA LALA LEO Now Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()


























