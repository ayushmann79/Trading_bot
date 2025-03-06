from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db_setup import get_db
from database import models
from backend.api.schemas import UserCreate, UserResponse, TradeCreate, TradeResponse

app = FastAPI()


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
    db_trade = models.Trade(user_id=trade.user_id, amount=trade.amount)
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


# Get all trades
@app.get("/trades/", response_model=list[TradeResponse])
def get_trades(db: Session = Depends(get_db)):
    return db.query(models.Trade).all()
