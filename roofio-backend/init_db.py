"""
ROOFIO Database Initialization
==============================

Creates all tables in Supabase PostgreSQL.

Usage:
    python init_db.py
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file BEFORE importing anything that reads environment variables
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")
else:
    print(f"WARNING: No .env file found at {env_path}")
    print("Make sure environment variables are set!")

from common.database import get_engine, Base
from common.models import (
    Agency,
    User,
    Project,
    AuditLog,
    AIActionLog,
    PositionConfig,
    FormTemplate,
    FormSubmission,
)


async def init_database():
    """Create all tables"""
    print("=" * 50)
    print("ROOFIO Database Initialization")
    print("=" * 50)

    engine = get_engine()

    print("\nConnecting to database...")

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
