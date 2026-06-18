# app/services/wallet_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.wallet import Wallet
from app.models.user import User
from app.services.transaction_service import TransactionService

class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_service = TransactionService(db)
    
    def get_wallet_by_user_id(self, user_id: int):
        wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        return wallet
    
    def add_money(self, user_id: int, amount: float, description: str = None):
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        wallet = self.get_wallet_by_user_id(user_id)
        
        
        wallet.balance += amount
        
        
        transaction = self.transaction_service.create_transaction(
            wallet_id=wallet.id,
            transaction_type="credit",
            amount=amount,
            description=description or "Money added to wallet",
            sender_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "wallet": wallet,
            "transaction": transaction
        }
    
    def withdraw_money(self, user_id: int, amount: float, description: str = None):
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        wallet = self.get_wallet_by_user_id(user_id)
        
        if wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
       
        wallet.balance -= amount
        
        
        transaction = self.transaction_service.create_transaction(
            wallet_id=wallet.id,
            transaction_type="debit",
            amount=amount,
            description=description or "Money withdrawn from wallet",
            sender_id=user_id
        )
        
        self.db.commit()
        self.db.refresh(wallet)
        
        return {
            "wallet": wallet,
            "transaction": transaction
        }