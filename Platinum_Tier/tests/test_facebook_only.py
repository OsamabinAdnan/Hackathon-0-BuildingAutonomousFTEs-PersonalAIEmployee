#!/usr/bin/env python
"""Test Facebook service - Gold Tier."""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    print("\n" + "="*60)
    print("TESTING FACEBOOK - Create test post")
    print("="*60)
    
    from mcp_server.facebook_service import FacebookService
    
    service = FacebookService()
    result = await service.post_facebook(
        message='🤖 Test post from AI Employee Gold Tier! #AI #Automation'
    )
    
    print(f"\nResult: {result}")
    print("="*60)
    if result.get('success'):
        print("✅ FACEBOOK TEST PASSED")
        print(f"   Post ID: {result.get('post_id', 'N/A')}")
    else:
        print(f"❌ FACEBOOK TEST FAILED: {result.get('error', 'Unknown error')}")
    print("="*60 + "\n")

if __name__ == '__main__':
    asyncio.run(main())
