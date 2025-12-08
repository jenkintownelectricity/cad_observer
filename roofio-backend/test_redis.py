#!/usr/bin/env python3
"""
Quick Redis Connection Test
============================

Run this to verify your Upstash Redis is configured correctly.

Usage:
    # Set environment variables first, then:
    python test_redis.py

    # Or with inline env vars:
    UPSTASH_REDIS_REST_URL=https://... UPSTASH_REDIS_REST_TOKEN=... python test_redis.py
"""

import os
import sys
from datetime import datetime

def test_redis():
    """Test Redis connection"""

    url = os.environ.get("UPSTASH_REDIS_REST_URL", "")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")

    if not url or not token:
        print("ERROR: Missing environment variables!")
        print("")
        print("Set these before running:")
        print("  export UPSTASH_REDIS_REST_URL='https://your-endpoint.upstash.io'")
        print("  export UPSTASH_REDIS_REST_TOKEN='your-token-here'")
        print("")
        print("Or create a .env file and use python-dotenv")
        return False

    print(f"Testing connection to: {url[:50]}...")
    print("")

    try:
        from upstash_redis import Redis

        redis = Redis(url=url, token=token)

        # Test 1: Basic SET/GET
        test_key = f"roofio:test:{datetime.utcnow().isoformat()}"
        test_value = "Hello from ROOFIO!"

        redis.set(test_key, test_value, ex=60)  # Expires in 60 seconds
        result = redis.get(test_key)

        if result == test_value:
            print("  [PASS] SET/GET works")
        else:
            print(f"  [FAIL] GET returned: {result}")
            return False

        # Test 2: Hash operations (used for sessions)
        hash_key = f"roofio:test:hash:{datetime.utcnow().isoformat()}"
        redis.hset(hash_key, values={"user_id": "test123", "role": "admin"})
        hash_result = redis.hgetall(hash_key)
        redis.expire(hash_key, 60)

        if hash_result.get("user_id") == "test123":
            print("  [PASS] HSET/HGETALL works (sessions will work)")
        else:
            print(f"  [FAIL] Hash result: {hash_result}")
            return False

        # Test 3: Sorted set (used for rate limiting)
        zset_key = f"roofio:test:zset:{datetime.utcnow().isoformat()}"
        redis.zadd(zset_key, {"item1": 1.0, "item2": 2.0})
        zset_count = redis.zcard(zset_key)
        redis.expire(zset_key, 60)

        if zset_count == 2:
            print("  [PASS] ZADD/ZCARD works (rate limiting will work)")
        else:
            print(f"  [FAIL] Zset count: {zset_count}")
            return False

        # Test 4: Stream (used for audit logging)
        stream_key = f"roofio:test:stream"
        redis.xadd(stream_key, {"event": "test", "timestamp": datetime.utcnow().isoformat()}, maxlen=100)
        print("  [PASS] XADD works (audit logging will work)")

        # Cleanup
        redis.delete(test_key)
        redis.delete(hash_key)
        redis.delete(zset_key)

        print("")
        print("=" * 50)
        print("SUCCESS! Redis is configured correctly.")
        print("=" * 50)
        print("")
        print("All session, rate limiting, and audit features will work!")

        return True

    except ImportError:
        print("ERROR: upstash-redis not installed!")
        print("")
        print("Install it with:")
        print("  pip install upstash-redis")
        return False

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("")
        print("Check your UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN")
        return False


if __name__ == "__main__":
    success = test_redis()
    sys.exit(0 if success else 1)
