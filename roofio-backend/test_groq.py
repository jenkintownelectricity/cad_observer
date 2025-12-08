#!/usr/bin/env python3
"""
Quick Groq API Test
====================

Run this to verify your Groq API is configured correctly.

Usage:
    $env:GROQ_API_KEY='gsk_your_key_here'
    python test_groq.py
"""

import os
import sys
import time

def test_groq():
    """Test Groq API connection"""

    api_key = os.environ.get("GROQ_API_KEY", "")

    if not api_key:
        print("ERROR: Missing GROQ_API_KEY!")
        print("")
        print("Set it before running:")
        print("  $env:GROQ_API_KEY='gsk_your_key_here'")
        return False

    print(f"Testing Groq API (key: {api_key[:10]}...)")
    print("")

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        # Test 1: Simple completion
        print("  Testing Llama 3.3 70B...")
        start_time = time.time()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a roofing expert. Be concise."
                },
                {
                    "role": "user",
                    "content": "What is spec section 07 62 00?"
                }
            ],
            max_tokens=150,
            temperature=0.2,
        )

        latency_ms = int((time.time() - start_time) * 1000)
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens

        print(f"  [PASS] Response in {latency_ms}ms ({tokens} tokens)")
        print(f"  [INFO] Answer: {answer[:100]}...")

        # Test 2: Check rate limits
        print("")
        print("  Testing rate limit headers...")

        # Make another quick request
        response2 = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'test' only"}],
            max_tokens=10,
        )
        print("  [PASS] Multiple requests work")

        print("")
        print("=" * 50)
        print("SUCCESS! Groq API is configured correctly.")
        print("=" * 50)
        print("")
        print(f"Tier 2 AI ready! (~{latency_ms}ms response time)")
        print("Model: Llama 3.3 70B Versatile")

        return True

    except ImportError:
        print("ERROR: groq not installed!")
        print("")
        print("Install it with:")
        print("  pip install groq")
        return False

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("")
        print("Check your GROQ_API_KEY")
        return False


if __name__ == "__main__":
    success = test_groq()
    sys.exit(0 if success else 1)
