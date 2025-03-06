from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database.db_setup import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    trades = relationship("Trade", back_populates="user")


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer, nullable=False)

    user = relationship("User", back_populates="trades")

from datetime import datetime
from database.db_setup import Base

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String, nullable=False)  # Ensure this column exists
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)  # ✅ Add this line
