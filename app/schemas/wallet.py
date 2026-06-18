# app/schemas/wallet.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: float
    currency: str
    created_at: datetime
    updated_at:Optional[datetime]=None
    
    class Config:
        from_attributes = True

class WalletBalanceUpdate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    description: Optional[str] = None