#!/usr/bin/env python
"""Test WhatsApp service."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.whatsapp_service import WhatsAppService

print("\n" + "="*60)
print("TESTING WHATSAPP - Send message to 'Me Telenor'")
print("="*60)

service = WhatsAppService()
result = service.send_message(
    contact='Me Telenor',
    message='Test message from AI Employee Gold Tier'
)

print(f"\nResult: {result}")
print("="*60)
if result.get('success'):
    print("✅ WHATSAPP TEST PASSED")
else:
    print(f"❌ WHATSAPP TEST FAILED: {result.get('error', 'Unknown error')}")
print("="*60 + "\n")
