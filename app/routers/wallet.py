# app/routes/wallet.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.wallet_service import WalletService
from app.services.auth_service import AuthService
from app.schemas.wallet import WalletResponse, WalletBalanceUpdate
from app.utils.dependencies import get_current_user, require_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.get("/me", response_model=WalletResponse)
def get_my_wallet(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's wallet"""
    wallet_service = WalletService(db)
    return wallet_service.get_wallet_by_user_id(current_user.id)

@router.get("/{user_id}", response_model=WalletResponse)
def get_wallet_by_user_id(
    user_id: int,
    current_user: User = Depends(require_admin),  
    db: Session = Depends(get_db)
):
    """Get wallet by user ID (Admin only)"""
    wallet_service = WalletService(db)
    return wallet_service.get_wallet_by_user_id(user_id)

@router.post("/add-money")
def add_money(
    data: WalletBalanceUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Add money to wallet"""
    wallet_service = WalletService(db)
    result = wallet_service.add_money(
        user_id=current_user.id,
        amount=data.amount,
        description=data.description
    )
    return {
        "message": "Money added successfully",
        "balance": result["wallet"].balance,
        "transaction_reference": result["transaction"].transaction_reference
    }

@router.post("/withdraw")
def withdraw_money(
    data: WalletBalanceUpdate,
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Withdraw money from wallet"""
    wallet_service = WalletService(db)
    result = wallet_service.withdraw_money(
        user_id=current_user.id,
        amount=data.amount,
        description=data.description
    )
    return {
        "message": "Money withdrawn successfully",
        "balance": result["wallet"].balance,
        "transaction_reference": result["transaction"].transaction_reference
    }