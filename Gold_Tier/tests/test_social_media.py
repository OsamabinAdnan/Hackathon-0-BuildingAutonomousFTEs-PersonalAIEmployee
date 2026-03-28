#!/usr/bin/env python
"""Test LinkedIn and Facebook services - Gold Tier."""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_linkedin():
    """Test LinkedIn post."""
    print("\n" + "="*60)
    print("TESTING LINKEDIN - Create test post")
    print("="*60)
    
    from mcp_server.linkedin_service import LinkedInService
    
    service = LinkedInService()
    result = await service.post_share(
        text='🤖 Test post from AI Employee Gold Tier! #AI #Automation',
        visibility='PUBLIC'
    )
    
    print(f"\nResult: {result}")
    print("="*60)
    if result.get('success'):
        print("✅ LINKEDIN TEST PASSED")
        print(f"   Post ID: {result.get('post_id', 'N/A')}")
    else:
        print(f"❌ LINKEDIN TEST FAILED: {result.get('error', 'Unknown error')}")
    print("="*60)
    return result.get('success', False)

async def test_facebook():
    """Test Facebook post."""
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
    print("="*60)
    return result.get('success', False)

async def main():
    """Run both tests."""
    print("\n" + "="*70)
    print("GOLD TIER - SOCIAL MEDIA TESTS")
    print("="*70)
    
    # Test LinkedIn
    linkedin_result = await test_linkedin()
    
    input("\nPress Enter to continue to Facebook test...")
    
    # Test Facebook
    facebook_result = await test_facebook()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"  LinkedIn:  {'✅ PASSED' if linkedin_result else '❌ FAILED'}")
    print(f"  Facebook:  {'✅ PASSED' if facebook_result else '❌ FAILED'}")
    print("="*70 + "\n")

if __name__ == '__main__':
    asyncio.run(main())
