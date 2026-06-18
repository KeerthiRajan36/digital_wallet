# app/services/transaction_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.wallet import Wallet
from app.schemas.transaction import TransactionFilter
import uuid
from datetime import datetime

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_transaction_reference(self):
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    def create_transaction(self, wallet_id: int, transaction_type: str, amount: float, 
                          description: str = None, sender_id: int = None, 
                          receiver_id: int = None):
        transaction = Transaction(
            transaction_reference=self.generate_transaction_reference(),
            wallet_id=wallet_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            transaction_type=TransactionType[transaction_type.upper()],
            amount=amount,
            status=TransactionStatus.SUCCESS,
            description=description,
            completed_at=datetime.utcnow()
        )
        
        self.db.add(transaction)
        self.db.flush()
        
        return transaction
    
    def get_transactions(self, user_id: int = None, wallet_id: int = None, 
                         filters: TransactionFilter = None, 
                         page: int = 1, limit: int = 20):
        query = self.db.query(Transaction)
        
        
        if wallet_id:
            query = query.filter(Transaction.wallet_id == wallet_id)
        
        
        if user_id:
            wallet = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
            if wallet:
                query = query.filter(Transaction.wallet_id == wallet.id)
            else:
                return {
                    "total": 0,
                    "page": page,
                    "limit": limit,
                    "total_pages": 0,
                    "items": []
                }
        
        
        if filters:
            if filters.transaction_type:
                query = query.filter(Transaction.transaction_type == filters.transaction_type)
            if filters.status:
                query = query.filter(Transaction.status == filters.status)
            if filters.date:
                date_filter = filters.date
                start_date = datetime.combine(date_filter, datetime.min.time())
                end_date = datetime.combine(date_filter, datetime.max.time())
                query = query.filter(Transaction.created_at.between(start_date, end_date))
            if filters.start_date:
                query = query.filter(Transaction.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(Transaction.created_at <= filters.end_date)
        
        
        query = query.order_by(Transaction.created_at.desc())
        
       
        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0,
            "items": items
        }
    
    def get_transaction_by_reference(self, transaction_reference: str):
        transaction = self.db.query(Transaction).filter(
            Transaction.transaction_reference == transaction_reference
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction