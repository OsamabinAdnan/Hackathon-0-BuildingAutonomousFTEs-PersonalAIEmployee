#!/usr/bin/env python
"""Test Facebook MCP Connection and Posting"""

from mcp_server.facebook_service import FacebookService
import asyncio
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_facebook():
    s = FacebookService()
    
    print("=== Facebook MCP Test ===\n")
    
    # Check credentials
    if not s._check_credentials():
        print("FAILED: Credentials not configured")
        return
    
    print("SUCCESS: Credentials OK")
    print(f"   Page ID: {s.page_id}")
    print()
    
    # Test 1: Get Page Info
    print("1. Get Page Info: ", end="")
    result = asyncio.run(s.get_page_info())
    if result.get('success'):
        print("SUCCESS")
        page = result.get('page', {})
        print(f"   Page Name: {page.get('name', 'N/A')}")
        print(f"   Followers: {page.get('followers_count', 'N/A')}")
    else:
        print("FAILED -", result.get('error'))
    print()
    
    # Test 2: Post to Facebook (Test Post)
    print("2. Create Test Post: ", end="")
    test_message = f"AI Employee Test Post - {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nThis is a test post from the Gold Tier AI Employee system."
    result = asyncio.run(s.post_facebook(message=test_message))
    if result.get('success'):
        print("SUCCESS")
        print(f"   Post ID: {result.get('post_id', 'N/A')}")
        print(f"   Page ID: {result.get('page_id', 'N/A')}")
    else:
        print("FAILED -", result.get('error'))
    print()
    
    # Test 3: Get Recent Posts
    print("3. Get Recent Posts: ", end="")
    result = asyncio.run(s.get_posts(limit=3))
    if result.get('success'):
        print("SUCCESS")
        print(f"   Found {result.get('count', 0)} posts")
        for i, post in enumerate(result.get('posts', [])[:3], 1):
            created = post.get('created_time', 'N/A')[:16] if post.get('created_time') else 'N/A'
            message = post.get('message', '')[:50]
            print(f"   {i}. {created} - {message}...")
    else:
        print("FAILED -", result.get('error'))
    print()
    
    print("=== All Tests Complete ===")

if __name__ == "__main__":
    test_facebook()
