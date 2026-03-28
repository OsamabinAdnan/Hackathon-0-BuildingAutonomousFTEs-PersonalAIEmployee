#!/usr/bin/env python
"""
WhatsApp Watcher - Standalone Test
Tests WhatsApp message sending using WhatsAppWatcher (same as orchestrator uses)
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from watchers.whatsapp_watcher import WhatsAppWatcher

print("=" * 70)
print("WHATSAPP WATCHER - STANDALONE TEST")
print("=" * 70)
print()

# Initialize watcher
print("1. Initializing WhatsApp Watcher...")
watcher = WhatsAppWatcher(vault_path='./AI_Employee_Vault_FTE', check_interval=30)
print(f"   Session: {watcher.session_path}")
print(f"   Headless: {watcher.headless}")
print()

async def send_test():
    # Initialize browser
    print("2. Initializing browser...")
    if not await watcher.init_browser():
        print("   ❌ Failed to initialize browser")
        return False
    print("   ✅ Browser initialized")
    print()
    
    # Navigate to WhatsApp
    print("3. Navigating to WhatsApp Web...")
    if not await watcher.navigate_to_whatsapp():
        print("   ❌ Not logged in to WhatsApp Web")
        print("   Please scan QR code in the browser window")
        print("   Waiting 60 seconds for login...")
        await asyncio.sleep(60)
        # Check again
        if not await watcher.navigate_to_whatsapp():
            print("   ❌ Still not logged in after waiting")
            return False
    print("   ✅ WhatsApp Web loaded (logged in)")
    print()
    
    # Send message using the watcher's send_whatsapp_message method
    print("4. Sending test message...")
    print(f"   To: Me Telenor (+923022311916)")
    print(f"   Message: Test message from Gold Tier MCP verification")
    
    success = await watcher.send_whatsapp_message(
        contact="+923022311916",
        message="Test message from Gold Tier MCP verification"
    )
    
    if success:
        print("   ✅ Message sent successfully!")
        print()
        return True
    else:
        print("   ❌ Failed to send message")
        print()
        return False

# Run async test
result = asyncio.run(send_test())

if result:
    print("=" * 70)
    print("SUCCESS - Message sent to Me Telenor (+923022311916)")
    print("=" * 70)
else:
    print("=" * 70)
    print("FAILED - Message not sent")
    print("=" * 70)
    print()
    print("Troubleshooting:")
    print("1. Check if browser window opened")
    print("2. Check if you're logged into WhatsApp Web")
    print("3. Make sure contact +923022311916 exists in WhatsApp")
    print("4. Check if the contact name matches exactly (Me Telenor)")

# Cleanup
async def cleanup():
    try:
        if watcher.context:
            await watcher.context.close()
            print("\nBrowser closed successfully")
    except Exception as e:
        print(f"\nCleanup note: {e}")
        print("(This is normal - browser may already be closed)")

asyncio.run(cleanup())
