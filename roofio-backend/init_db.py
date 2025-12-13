"""
ROOFIO Database Initialization
==============================

Creates all tables in Supabase PostgreSQL.

Usage:
    python init_db.py
"""

import asyncio
import os

# Load .env file BEFORE importing anything that reads environment variables
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")
else:
    print(f"WARNING: No .env file found at {env_path}")
    print("Make sure environment variables are set!")

# Direct imports to avoid common/__init__.py relative import issues
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

# Convert to async URL
def get_async_database_url() -> str:
    if DATABASE_URL.startswith("postgresql://"):
        return DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    if DATABASE_URL.startswith("postgres://"):
        return DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
    return DATABASE_URL

# Create Base and import models
Base = declarative_base()

# Import models AFTER Base is defined - use direct file import
import importlib.util
models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "common", "models.py")
spec = importlib.util.spec_from_file_location("models", models_path)
models = importlib.util.module_from_spec(spec)

# We need to inject our Base into the models module before loading
import sys
# Create a minimal common.database module with just Base
class FakeDatabase:
    Base = Base
sys.modules['common'] = type(sys)('common')
sys.modules['common.database'] = FakeDatabase()

spec.loader.exec_module(models)


async def init_database():
    """Create all tables"""
    print("=" * 50)
    print("ROOFIO Database Initialization")
    print("=" * 50)

    print(f"\nConnecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'database'}...")

    engine = create_async_engine(
        get_async_database_url(),
        echo=False,
        pool_size=5,
        max_overflow=10,
    )

    print("Connected!")

    async with engine.begin() as conn:
        print("Creating tables...")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        print("\nTables created:")
        for table in Base.metadata.tables:
            print(f"  ✓ {table}")

    print("\n" + "=" * 50)
    print("SUCCESS! Database initialized.")
    print("=" * 50)

    # Cleanup
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
