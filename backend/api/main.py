from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.db_setup import get_db
from database import models
from backend.api import market_data, token_chart, token  # ✅ Import token.py
from backend.api.schemas import UserCreate, UserResponse, TradeCreate, TradeResponse
import datetime

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this if frontend runs on a different port
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ✅ Include API routes
app.include_router(market_data.router, prefix="/api", tags=["Market Data"])
app.include_router(token_chart.router, prefix="/api", tags=["Token Chart"])
app.include_router(token.router, prefix="/api", tags=["Token Info"])  # ✅ Add Token Info API

# Create a new user
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users
@app.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# Create a new trade
@app.post("/trades/", response_model=TradeResponse)
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    db_trade = models.Trade(
        user_id=trade.user_id, 
        amount=trade.amount,
        price=0.002,  # Simulating price, should be fetched dynamically
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

# Get all trades
@app.get("/trades/", response_model=list[TradeResponse])
def get_trades(db: Session = Depends(get_db)):
    return db.query(models.Trade).all()

# Buy Crypto
@app.post("/buy/")
def buy_crypto(trade: TradeCreate, db: Session = Depends(get_db)):
    new_trade = models.Trade(
        user_id=trade.user_id,
        amount=trade.amount,
        price=0.002,  # Fetch actual price from API if needed
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    return {"message": "Trade executed!", "trade": new_trade}

# Sell Crypto
@app.post("/sell/")
def sell_crypto(trade: TradeCreate, db: Session = Depends(get_db)):
    new_trade = models.Trade(
        user_id=trade.user_id,
        amount=-trade.amount,  # Negative amount for sell
        price=0.002,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    return {"message": "Trade executed!", "trade": new_trade}
