#!/usr/bin/env python3
"""Diagnostic script to test OpenAI API connectivity."""

import os
import sys

print("=== DIAGNOSTIC TEST ===\n")

# Check environment
api_key = os.getenv("OPENAI_API_KEY")
print(f"1. Environment check:")
print(f"   OPENAI_API_KEY set: {bool(api_key)}")
if api_key:
    print(f"   API Key starts with: {api_key[:10]}...")
else:
    print(f"   WARNING: No OPENAI_API_KEY environment variable!")

# Check OpenAI import
print(f"\n2. OpenAI SDK:")
try:
    import openai
    print(f"   ✓ OpenAI imported")
    print(f"   Version: {openai.__version__}")
except ImportError as e:
    print(f"   ✗ Failed to import openai: {e}")
    sys.exit(1)

# Test old-style API key setup
print(f"\n3. Testing old-style API setup (openai.api_key):")
try:
    test_key = "sk-test123"
    openai.api_key = test_key
    print(f"   ✓ Can set openai.api_key")
    print(f"   Current api_key: {openai.api_key[:10] if openai.api_key else 'None'}...")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test modern client setup
print(f"\n4. Testing modern client setup:")
try:
    from openai import OpenAI
    client = OpenAI(api_key="sk-test123")
    print(f"   ✓ Can create OpenAI client instance")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test with actual environment key if available
if api_key:
    print(f"\n5. Testing with actual environment API key:")
    try:
        import openai
        openai.api_key = api_key
        print(f"   ✓ API key set via openai.api_key")
        
        # Try a simple call
        print(f"   Attempting API call...")
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            temperature=0.0,
        )
        print(f"   ✓ SUCCESS! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ✗ Error: {type(e).__name__}: {e}")
else:
    print(f"\n5. Skipped (no API key in environment)")

print(f"\n=== END DIAGNOSTIC ===")
