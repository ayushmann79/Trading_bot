from pydantic import BaseModel
from typing import List, Optional


class TradeBase(BaseModel):
    amount: int


class TradeCreate(TradeBase):
    user_id: int


class TradeResponse(TradeBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    trades: List[TradeResponse] = []

    class Config:
        orm_mode = True
