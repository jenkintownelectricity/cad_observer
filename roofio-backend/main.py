"""
ROOFIO Backend API
==================

FastAPI application for the ROOFIO platform.

Run with:
    uvicorn main:app --reload --port 8000
"""

# Load .env file FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.database import init_database, close_database
from api.routes import (
    health_router,
    agency_router,
    user_router,
    project_router,
    position_router,
    ai_router,
    form_router,
    scan_router,
)


# =============================================================================
# LIFESPAN MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown"""
    # Startup
    print("Starting ROOFIO Backend...")
    await init_database()
    print("Database connection established")

    yield

    # Shutdown
    print("Shutting down ROOFIO Backend...")
    await close_database()
    print("Database connection closed")


# =============================================================================
# APPLICATION
# =============================================================================

app = FastAPI(
    title="ROOFIO API",
    description="Backend API for the ROOFIO Roofing Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",      # Flask dev
        "http://127.0.0.1:5000",      # Flask dev
        "http://localhost:3000",      # React dev
        "http://127.0.0.1:3000",      # React dev
        "https://*.vercel.app",       # Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROUTES
# =============================================================================

# Include all routers
app.include_router(health_router)
app.include_router(agency_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(position_router)
app.include_router(ai_router)
app.include_router(form_router)
app.include_router(scan_router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "ROOFIO API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
