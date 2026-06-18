# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.database import engine, Base
from app.routers import auth, wallet, transaction, transfer
from app.config import settings
import logging
import time
from typing import Callable
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Digital Wallet & Money Transfer System",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
@app.middleware("http")
async def add_process_time_header(request: Callable, call_next):
    """Add process time header to response"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify actual hosts
)

# Include routers with versioning
api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(wallet.router, prefix=api_prefix)
app.include_router(transaction.router, prefix=api_prefix)
app.include_router(transfer.router, prefix=api_prefix)

@app.get("/")
async def root():
    return {
        "message": "Digital Wallet System API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )