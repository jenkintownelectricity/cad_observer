#!/usr/bin/env python3
"""
Quick PostgreSQL (Supabase) Connection Test
============================================

Run this to verify your Supabase database is configured correctly.

Usage:
    $env:DATABASE_URL='postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres'
    python test_postgres.py
"""

import os
import sys
import asyncio

async def test_postgres():
    """Test PostgreSQL connection"""

    database_url = os.environ.get("DATABASE_URL", "")

    if not database_url:
        print("ERROR: Missing DATABASE_URL!")
        print("")
        print("Set it before running:")
        print("  $env:DATABASE_URL='postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres'")
        return False

    # Mask password in output
    display_url = database_url.split("@")[-1] if "@" in database_url else database_url[:50]
    print(f"Testing connection to: ...@{display_url}")
    print("")

    try:
        import asyncpg

        # Test 1: Basic connection
        print("  Connecting...")
        conn = await asyncpg.connect(database_url)
        print("  [PASS] Connected to PostgreSQL")

        # Test 2: Check version
        version = await conn.fetchval("SELECT version()")
        print(f"  [INFO] {version[:60]}...")

        # Test 3: Create test table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS roofio_test (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("  [PASS] CREATE TABLE works")

        # Test 4: Insert
        await conn.execute(
            "INSERT INTO roofio_test (name) VALUES ($1)",
            "test_entry"
        )
        print("  [PASS] INSERT works")

        # Test 5: Select
        row = await conn.fetchrow("SELECT * FROM roofio_test ORDER BY id DESC LIMIT 1")
        if row and row['name'] == 'test_entry':
            print("  [PASS] SELECT works")
        else:
            print("  [FAIL] SELECT returned unexpected result")

        # Test 6: Delete (cleanup)
        await conn.execute("DELETE FROM roofio_test WHERE name = 'test_entry'")
        print("  [PASS] DELETE works")

        # Test 7: Check for required extensions
        extensions = await conn.fetch("SELECT extname FROM pg_extension")
        ext_names = [e['extname'] for e in extensions]
        print(f"  [INFO] Extensions: {', '.join(ext_names)}")

        # Cleanup
        await conn.execute("DROP TABLE IF EXISTS roofio_test")
        await conn.close()

        print("")
        print("=" * 50)
        print("SUCCESS! PostgreSQL is configured correctly.")
        print("=" * 50)
        print("")
        print("Database ready for users, projects, and logs!")

        return True

    except ImportError:
        print("ERROR: asyncpg not installed!")
        print("")
        print("Install it with:")
        print("  pip install asyncpg")
        return False

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("")
        print("Check your DATABASE_URL and ensure the password is correct")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_postgres())
    sys.exit(0 if success else 1)
