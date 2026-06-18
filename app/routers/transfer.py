# app/routes/transfers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.transfer_service import TransferService
from app.schemas.transfer import TransferCreate, TransferResponse
from app.utils.dependencies import get_current_user, require_user
from app.models.user import User

router = APIRouter(prefix="/transfers", tags=["Transfers"])

@router.post("/send")
def send_money(
    transfer_data: TransferCreate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Transfer money from current user's wallet to another user"""
    transfer_service = TransferService(db)
    
    result = transfer_service.transfer_money(
        sender_id=current_user.id,
        receiver_email=transfer_data.receiver_email,
        amount=transfer_data.amount,
        description=transfer_data.description
    )
    
    return {
        "message": "Transfer successful",
        "sender_balance": result["sender_balance"],
        "receiver_balance": result["receiver_balance"],
        "transaction_reference": result["debit_transaction"].transaction_reference,
        "status": "SUCCESS"
    }

@router.get("/{transaction_reference}")
def get_transfer(
    transaction_reference: str,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get transfer details by transaction reference"""
    transfer_service = TransferService(db)
    transaction = transfer_service.get_transfer_by_id(
        transaction_reference=transaction_reference,
        user_id=current_user.id
    )
    
    return transaction