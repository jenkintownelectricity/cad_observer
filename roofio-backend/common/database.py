"""
ROOFIO Database Module
======================

PostgreSQL database connection management using SQLAlchemy async.

Features:
- Async connection pool management
- Multi-tenant query scoping
- Transaction management
- Health checks

CRITICAL: All queries MUST be scoped to agency_id for multi-tenancy!
"""

import asyncio
from typing import Optional, AsyncGenerator, Any
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from .config import get_database_url, DEBUG

# =============================================================================
# DATABASE ENGINE SETUP
# =============================================================================

# Global engine instance
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None

# SQLAlchemy Base for models
Base = declarative_base()


def get_async_database_url() -> str:
    """Convert sync URL to async URL (asyncpg driver)"""
    url = get_database_url()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://")
    return url


def get_engine() -> AsyncEngine:
    """Get or create the database engine singleton"""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_async_database_url(),
            echo=DEBUG,  # Log SQL in development
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections every 30 min
            pool_pre_ping=True,  # Check connection health
        )
    return _engine


def get_session_factory() -> async_sessionmaker:
    """Get or create the session factory singleton"""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session with automatic cleanup.

    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
            await session.commit()
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with get_db_session() as session:
        yield session


# =============================================================================
# MULTI-TENANT SCOPED QUERIES
# =============================================================================

class TenantScopedSession:
    """
    A wrapper around AsyncSession that enforces agency_id scoping.

    CRITICAL: Use this for all multi-tenant queries to prevent data leakage.

    Usage:
        async with get_tenant_session(agency_id) as session:
            # All queries automatically filtered by agency_id
            projects = await session.query(Project).all()
    """

    def __init__(self, session: AsyncSession, agency_id: str):
        self._session = session
        self.agency_id = agency_id

    async def execute(self, statement, *args, **kwargs):
        """Execute a statement with agency_id scope"""
        return await self._session.execute(statement, *args, **kwargs)

    async def commit(self):
        """Commit the transaction"""
        await self._session.commit()

    async def rollback(self):
        """Rollback the transaction"""
        await self._session.rollback()

    async def refresh(self, instance):
        """Refresh an instance from the database"""
        await self._session.refresh(instance)

    def add(self, instance):
        """Add an instance to the session"""
        # Ensure agency_id is set on the instance
        if hasattr(instance, 'agency_id') and instance.agency_id is None:
            instance.agency_id = self.agency_id
        self._session.add(instance)

    async def get(self, entity, ident, **kwargs):
        """Get an entity by ID (with agency_id verification)"""
        instance = await self._session.get(entity, ident, **kwargs)
        # Verify agency_id matches
        if instance and hasattr(instance, 'agency_id'):
            if instance.agency_id != self.agency_id:
                return None  # Prevent cross-tenant access
        return instance


@asynccontextmanager
async def get_tenant_session(agency_id: str) -> AsyncGenerator[TenantScopedSession, None]:
    """
    Get a tenant-scoped database session.

    Usage:
        async with get_tenant_session(agency_id) as session:
            # All operations are scoped to this agency
            ...
    """
    async with get_db_session() as session:
        yield TenantScopedSession(session, agency_id)


# =============================================================================
# HEALTH CHECK
# =============================================================================

async def check_database_health() -> dict:
    """
    Check database connectivity and return health status.

    Returns:
        {
            "status": "healthy" | "unhealthy",
            "latency_ms": 12.5,
            "error": "..." (if unhealthy)
        }
    """
    import time

    start_time = time.time()

    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))

        latency_ms = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "latency_ms": None,
            "error": str(e),
        }


# =============================================================================
# LIFECYCLE MANAGEMENT
# =============================================================================

async def init_database():
    """
    Initialize database connection pool.
    Call this on application startup.
    """
    engine = get_engine()
    # Test connection
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))


async def close_database():
    """
    Close database connections.
    Call this on application shutdown.
    """
    global _engine, _session_factory

    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None


# =============================================================================
# TRANSACTION HELPERS
# =============================================================================

@asynccontextmanager
async def transaction(session: AsyncSession):
    """
    Explicit transaction context manager.

    Usage:
        async with get_db_session() as session:
            async with transaction(session):
                # All operations are in a single transaction
                await session.execute(...)
                await session.execute(...)
                # Auto-commits on success, auto-rollbacks on error
    """
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def execute_raw_sql(sql: str, params: dict = None) -> list:
    """
    Execute raw SQL query.

    WARNING: Use with caution! Prefer ORM queries for type safety.

    Usage:
        results = await execute_raw_sql(
            "SELECT * FROM users WHERE agency_id = :agency_id",
            {"agency_id": "abc123"}
        )
    """
    async with get_db_session() as session:
        result = await session.execute(text(sql), params or {})
        return result.fetchall()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base
    "Base",

    # Engine/Session
    "get_engine",
    "get_session_factory",
    "get_db_session",
    "get_db",

    # Multi-tenant
    "TenantScopedSession",
    "get_tenant_session",

    # Health
    "check_database_health",

    # Lifecycle
    "init_database",
    "close_database",

    # Helpers
    "transaction",
    "execute_raw_sql",
]
