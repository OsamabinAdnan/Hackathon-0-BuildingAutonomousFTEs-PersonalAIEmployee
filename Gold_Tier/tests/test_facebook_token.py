#!/usr/bin/env python
"""Test new Facebook token"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.facebook_service import FacebookService

print("=" * 70)
print("FACEBOOK TOKEN TEST")
print("=" * 70)
print()

s = FacebookService()

print(f"1. Token configured: {'✅ YES' if s.access_token else '❌ NO'}")
print(f"   Token starts with: {s.access_token[:20] if s.access_token else 'N/A'}...")
print(f"   Page ID: {s.page_id}")
print()

print("2. Testing get_posts()...")
result = asyncio.run(s.get_posts(limit=3))
if result.get('success'):
    print(f"   ✅ SUCCESS - Retrieved {result.get('count', 0)} posts")
else:
    error = result.get('error', 'Unknown error')
    print(f"   ❌ FAILED - {error}")
    
    if 'expired' in error.lower():
        print()
        print("   TOKEN EXPIRED - You need a Page Access Token, not User Token!")
        print()
        print("   To get a NEVER-EXPIRING Page Token:")
        print("   1. Go to: https://developers.facebook.com/tools/explorer/")
        print("   2. Get a 60-day User Token first")
        print("   3. Make this API call:")
        print("      GET /me/accounts?access_token={YOUR_60_DAY_TOKEN}")
        print("   4. Copy the 'access_token' from your page in the response")
        print("   5. That Page Token NEVER expires!")
print()

print("3. Testing post_facebook()...")
result = asyncio.run(s.post_facebook(message="Token verification test"))
if result.get('success'):
    print(f"   ✅ SUCCESS - Post created: {result.get('post_id', 'N/A')}")
else:
    print(f"   ❌ FAILED - {result.get('error', 'Unknown error')}")
print()

print("=" * 70)
