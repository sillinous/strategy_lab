"""
Strategy Lab Backend - Main Application
FastAPI application for trading strategy development and backtesting
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.database import init_db
from app.api import strategies, backtests
from app.utils.exceptions import StrategyLabException

# Setup logging
logger = setup_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Initializes database and performs cleanup
    """
    logger.info("Starting Strategy Lab Backend")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Strategy Lab Backend")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(StrategyLabException)
async def strategy_lab_exception_handler(request: Request, exc: StrategyLabException):
    """Handle custom Strategy Lab exceptions"""
    logger.error(f"Strategy Lab error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": exc.__class__.__name__}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )


# Include routers
app.include_router(strategies.router, prefix="/api/v1")
app.include_router(backtests.router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "status": "operational",
        "endpoints": {
            "strategies": "/api/v1/strategies",
            "backtests": "/api/v1/backtests",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
