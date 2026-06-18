# app/models/transaction.py
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_reference = Column(String, unique=True, index=True, nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(String)
    meta_data = Column(String)  # Changed from 'metadata' to 'meta_data' to avoid reserved keyword
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_transfers")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_transfers")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_reference', 'transaction_reference'),
        Index('idx_user_email', 'sender_id', 'receiver_id'),
    )