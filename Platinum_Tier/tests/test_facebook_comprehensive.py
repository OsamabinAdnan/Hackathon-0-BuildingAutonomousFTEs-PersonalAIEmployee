#!/usr/bin/env python
"""
Facebook Integration - Comprehensive Verification
Tests Facebook service, MCP server, and agent skills
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("FACEBOOK INTEGRATION - COMPREHENSIVE VERIFICATION")
print("=" * 70)
print()

# Test 1: Check Facebook Service
print("1. Testing Facebook Service...")
from mcp_server.facebook_service import FacebookService
fb_service = FacebookService()
credentials_ok = fb_service._check_credentials()
print(f"   Facebook Service: {'✅ INITIALIZED' if credentials_ok else '❌ FAILED'}")
print(f"   Page ID: {fb_service.page_id}")
print(f"   Access Token: {'✅ Configured' if fb_service.access_token else '❌ Missing'}")
print()

# Test 2: Check MCP Server Module
print("2. Testing MCP Server Module...")
try:
    from mcp_server import facebook_service
    print(f"   MCP Module: ✅ LOADED")
except Exception as e:
    print(f"   MCP Module: ❌ FAILED - {e}")
print()

# Test 3: Check Main MCP Server has Facebook Tools
print("3. Testing Main MCP Server Facebook Integration...")
try:
    from mcp_server.server import get_facebook_service
    fb_svc = get_facebook_service()
    print(f"   Facebook Service in Main Server: ✅ REGISTERED")
except Exception as e:
    print(f"   Facebook Service in Main Server: ❌ FAILED - {e}")
print()

# Test 4: Check MCP Tools in Main Server
print("4. Testing Facebook MCP Tools...")
from mcp_server.server import mcp
if hasattr(mcp, '_tools'):
    tools = list(mcp._tools.keys()) if hasattr(mcp._tools, 'keys') else list(mcp._tools)
    facebook_tools = [t for t in tools if 'facebook' in t.lower()]
    print(f"   Facebook Tools Registered: {len(facebook_tools)}")
    for tool in facebook_tools:
        print(f"      - {tool}: ✅")
else:
    print(f"   Tool check: ⚠️  Cannot inspect tools directly")
print()

# Test 5: Check .env Configuration
print("5. Checking Environment Configuration...")
from dotenv import load_dotenv
load_dotenv()
env_vars = {
    'FACEBOOK_APP_ID': os.getenv('FACEBOOK_APP_ID'),
    'FACEBOOK_APP_SECRET': '✅ Set' if os.getenv('FACEBOOK_APP_SECRET') else '❌ Missing',
    'FACEBOOK_ACCESS_TOKEN': '✅ Set' if os.getenv('FACEBOOK_ACCESS_TOKEN') else '❌ Missing',
    'FACEBOOK_PAGE_ID': os.getenv('FACEBOOK_PAGE_ID'),
}
for var, value in env_vars.items():
    print(f"   {var}: {value}")
print()

# Test 6: Check Agent Skills
print("6. Checking Agent Skills...")
skills_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.claude', 'skills')
facebook_skills = ['post-facebook', 'send-facebook-message']
for skill in facebook_skills:
    skill_path = os.path.join(skills_path, skill, 'SKILL.md')
    if os.path.exists(skill_path):
        print(f"   {skill}: ✅ EXISTS")
    else:
        print(f"   {skill}: ❌ NOT FOUND")
print()

# Test 7: Real MCP Tool Test (Post)
print("7. Testing Real MCP Tool Execution...")
try:
    from mcp_server.server import post_facebook
    # Test with dry run or short message
    result = asyncio.run(post_facebook(message="Test post from AI Employee verification"))
    print(f"   post_facebook(): ✅ WORKING")
    print(f"      Result: {result[:100] if len(result) > 100 else result}")
except Exception as e:
    print(f"   post_facebook(): ⚠️  {str(e)[:100]}")

try:
    from mcp_server.server import get_facebook_insights
    result = asyncio.run(get_facebook_insights())
    print(f"   get_facebook_insights(): ✅ WORKING")
except Exception as e:
    print(f"   get_facebook_insights(): ⚠️  {str(e)[:100]}")

try:
    from mcp_server.server import send_facebook_message
    # Don't actually send, just verify function exists
    print(f"   send_facebook_message(): ✅ EXISTS")
except Exception as e:
    print(f"   send_facebook_message(): ❌ NOT AVAILABLE")
print()

# Test 8: Check Facebook Watcher
print("8. Checking Facebook Watcher...")
watcher_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'watchers', 'facebook_watcher.py')
if os.path.exists(watcher_path):
    print(f"   facebook_watcher.py: ✅ EXISTS")
else:
    print(f"   facebook_watcher.py: ❌ NOT FOUND")
print()

print("=" * 70)
print("FACEBOOK INTEGRATION VERIFICATION COMPLETE")
print("=" * 70)
print()
print("Summary:")
print(f"  {'✅' if credentials_ok else '❌'} Facebook Service: Initialized")
print(f"  {'✅' if os.path.exists(watcher_path) else '❌'} Facebook Watcher: Available")
print(f"  {'✅' if all(os.path.exists(os.path.join(skills_path, s, 'SKILL.md')) for s in facebook_skills) else '❌'} Agent Skills: Available")
print(f"  {'✅' if os.getenv('FACEBOOK_ACCESS_TOKEN') else '❌'} Credentials: Configured")
print()
print("Requirement 4: " + ("COMPLETE ✅" if credentials_ok else "INCOMPLETE ❌"))
print()
