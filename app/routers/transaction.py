from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.transaction_service import TransactionService
from app.services.wallet_service import WalletService
from app.schemas.transaction import TransactionResponse, TransactionFilter, TransactionType, TransactionStatus
from app.utils.dependencies import get_current_user, require_admin, require_user
from app.models.user import User

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/")
def get_my_transactions(
    type: Optional[TransactionType] = None,
    status: Optional[TransactionStatus] = None,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user),
    db: Session = Depends(get_db)
):
    """Get current user's transactions with filtering and pagination"""
    from datetime import datetime
    
    transaction_service = TransactionService(db)
    
    
    filters = TransactionFilter()
    if type:
        filters.transaction_type = type
    if status:
        filters.status = status
    if date:
        try:
            filters.date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    if start_date:
        try:
            filters.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    if end_date:
        try:
            filters.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    result = transaction_service.get_transactions(
        user_id=current_user.id,
        filters=filters,
        page=page,
        limit=limit
    )
    
    return {
        "data": result["items"],
        "total_records": result["total"],
        "current_page": result["page"],
        "total_pages": result["total_pages"],
        "limit": result["limit"]
    }

@router.get("/admin/all")
def get_all_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all transactions (Admin only)"""
    transaction_service = TransactionService(db)
    result = transaction_service.get_transactions(
        filters=None,
        page=page,
        limit=limit
    )
    
    return {
        "data": result["items"],
        "total_records": result["total"],
        "current_page": result["page"],
        "total_pages": result["total_pages"],
        "limit": result["limit"]
    }