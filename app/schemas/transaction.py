# app/schemas/transaction.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    transaction_reference: str
    wallet_id: int
    sender_id: Optional[int]
    receiver_id: Optional[int]
    transaction_type: TransactionType
    amount: float
    status: TransactionStatus
    description: Optional[str]
    meta_data: Optional[str]  
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TransactionFilter(BaseModel):
    transaction_type: Optional[TransactionType] = None
    status: Optional[TransactionStatus] = None
    date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None