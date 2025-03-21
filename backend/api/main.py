from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.db_setup import get_db
from database import models
from backend.api import market_data, token_chart, token  
from backend.api.schemas import UserCreate, UserResponse, TradeCreate, TradeResponse
import datetime

# ✅ Fix AI Model Import
try:
    from backend.api.ai_model import predict_price
    AI_MODEL_AVAILABLE = True
except ModuleNotFoundError:
    print("⚠️ Warning: AI Model not found. Predictions will be unavailable.")
    AI_MODEL_AVAILABLE = False

app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ✅ Include API routes
app.include_router(market_data.router, prefix="/api", tags=["Market Data"])
app.include_router(token_chart.router, prefix="/api", tags=["Token Chart"])
app.include_router(token.router, prefix="/api", tags=["Token Info"])  

# ✅ AI Price Prediction Route (Optional)
if AI_MODEL_AVAILABLE:
    @app.get("/api/ai-predict/{token_id}")
    async def ai_price_prediction(token_id: str):
        """Predict next-day price using AI."""
        predicted_price = predict_price(token_id)
        return {"token": token_id, "predicted_price": predicted_price} if predicted_price else {"error": "Prediction failed"}

# ✅ User Management
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# ✅ Trade Management
@app.post("/trades/", response_model=TradeResponse)
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    db_trade = models.Trade(
        user_id=trade.user_id, 
        amount=trade.amount,
        price=0.002,  
        timestamp=datetime.datetime.utcnow()
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@app.get("/trades/", response_model=list[TradeResponse])
def get_trades(db: Session = Depends(get_db)):
    return db.query(models.Trade).all()

# ✅ Buy Crypto
@app.post("/buy/")
def buy_crypto(trade: TradeCreate, db: Session = Depends(get_db)):
    new_trade = models.Trade(
        user_id=trade.user_id,
        amount=trade.amount,
        price=0.002,  
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    return {"message": "Trade executed!", "trade": new_trade}

# ✅ Sell Crypto
@app.post("/sell/")
def sell_crypto(trade: TradeCreate, db: Session = Depends(get_db)):
    new_trade = models.Trade(
        user_id=trade.user_id,
        amount=-trade.amount,  
        price=0.002,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)
    return {"message": "Trade executed!", "trade": new_trade}
