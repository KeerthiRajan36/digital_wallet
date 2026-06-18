# app/services/transfer_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.services.transaction_service import TransactionService
from app.services.wallet_service import WalletService
from datetime import datetime
import uuid

class TransferService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_service = TransactionService(db)
        self.wallet_service = WalletService(db)
    
    def transfer_money(self, sender_id: int, receiver_email: str, amount: float, 
                       description: str = None):
        
        sender = self.db.query(User).filter(User.id == sender_id).first()
        if not sender:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        
        receiver = self.db.query(User).filter(User.email == receiver_email).first()
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found"
            )
        
        
        if sender_id == receiver.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer money to yourself"
            )
        
        
        sender_wallet = self.wallet_service.get_wallet_by_user_id(sender_id)
        receiver_wallet = self.wallet_service.get_wallet_by_user_id(receiver.id)
        
        
        if sender_wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )
        
        
        try:
            
            sender_wallet.balance -= amount
            
            
            debit_transaction = Transaction(
                transaction_reference=self.transaction_service.generate_transaction_reference(),
                wallet_id=sender_wallet.id,
                sender_id=sender_id,
                receiver_id=receiver.id,
                transaction_type=TransactionType.DEBIT,
                amount=amount,
                status=TransactionStatus.SUCCESS,
                description=description or f"Transfer to {receiver.email}",
                completed_at=datetime.utcnow()
            )
            
            
            receiver_wallet.balance += amount
            
            
            credit_transaction = Transaction(
                transaction_reference=self.transaction_service.generate_transaction_reference(),
                wallet_id=receiver_wallet.id,
                sender_id=sender_id,
                receiver_id=receiver.id,
                transaction_type=TransactionType.CREDIT,
                amount=amount,
                status=TransactionStatus.SUCCESS,
                description=description or f"Transfer from {sender.email}",
                completed_at=datetime.utcnow()
            )
            
            self.db.add(debit_transaction)
            self.db.add(credit_transaction)
            self.db.commit()
            
            
            self.db.refresh(sender_wallet)
            self.db.refresh(receiver_wallet)
            
            return {
                "success": True,
                "sender_balance": sender_wallet.balance,
                "receiver_balance": receiver_wallet.balance,
                "debit_transaction": debit_transaction,
                "credit_transaction": credit_transaction
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transfer failed: {str(e)}"
            )
    
    def get_transfer_by_id(self, transaction_reference: str, user_id: int = None):
        transaction = self.db.query(Transaction).filter(
            Transaction.transaction_reference == transaction_reference
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        
        if user_id and transaction.sender_id != user_id and transaction.receiver_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this transaction"
            )
        
        return transaction