# app/schemas/transfer.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from app.schemas.transaction import TransactionResponse

class TransferCreate(BaseModel):
    receiver_email: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class TransferResponse(BaseModel):
    transaction: TransactionResponse
    sender_balance: float
    receiver_balance: float
    transfer_status: str