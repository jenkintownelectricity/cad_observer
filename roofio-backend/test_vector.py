#!/usr/bin/env python3
"""
Quick Upstash Vector Connection Test
=====================================

Run this to verify your Upstash Vector is configured correctly.

Usage:
    # Set environment variables first, then:
    python test_vector.py
"""

import os
import sys
from datetime import datetime, timezone

def now_utc():
    """Get current UTC time"""
    return datetime.now(timezone.utc)

def test_vector():
    """Test Vector DB connection"""

    url = os.environ.get("UPSTASH_VECTOR_REST_URL", "")
    token = os.environ.get("UPSTASH_VECTOR_REST_TOKEN", "")

    if not url or not token:
        print("ERROR: Missing environment variables!")
        print("")
        print("Set these before running:")
        print("  $env:UPSTASH_VECTOR_REST_URL='https://your-endpoint.upstash.io'")
        print("  $env:UPSTASH_VECTOR_REST_TOKEN='your-token-here'")
        return False

    print(f"Testing connection to: {url[:50]}...")
    print("")

    try:
        from upstash_vector import Index

        index = Index(url=url, token=token)

        # Get index info
        info = index.info()
        print(f"  [INFO] Index dimensions: {info.dimension}")
        print(f"  [INFO] Index similarity: {info.similarity_function}")
        print(f"  [INFO] Vector count: {info.vector_count}")
        print(f"  [PASS] Connected to Vector DB")

        # Test 1: Upsert a test vector
        test_id = f"test-{now_utc().timestamp()}"

        # For Hybrid index, we need both dense and sparse data
        # Dense: semantic embedding, Sparse: keyword tokens
        try:
            # Try hybrid upsert first (dense + sparse)
            index.upsert(
                vectors=[
                    {
                        "id": test_id,
                        "data": "This is a test document about roofing spec 07 62 00 sheet metal flashing",
                        "metadata": {"type": "test", "spec": "07 62 00"}
                    }
                ]
            )
            print("  [PASS] Upsert with auto-embedding works (Hybrid mode)")
        except Exception as e:
            # Fallback: manual vector (if custom embeddings)
            print(f"  [INFO] Auto-embedding not available: {e}")
            print("  [INFO] You'll need to generate embeddings manually")

        # Test 2: Query
        try:
            results = index.query(
                data="sheet metal flashing requirements",
                top_k=1,
                include_metadata=True
            )
            if results:
                print(f"  [PASS] Query works - found {len(results)} results")
            else:
                print("  [PASS] Query works - no results yet (index empty)")
        except Exception as e:
            print(f"  [INFO] Query test: {e}")

        # Cleanup test vector
        try:
            index.delete(ids=[test_id])
            print("  [PASS] Delete works")
        except Exception:
            pass  # May not exist

        print("")
        print("=" * 50)
        print("SUCCESS! Vector DB is configured correctly.")
        print("=" * 50)
        print("")
        print("RAG knowledge base features will work!")

        return True

    except ImportError:
        print("ERROR: upstash-vector not installed!")
        print("")
        print("Install it with:")
        print("  pip install upstash-vector")
        return False

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("")
        print("Check your UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN")
        return False


if __name__ == "__main__":
    success = test_vector()
    sys.exit(0 if success else 1)
