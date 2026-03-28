#!/usr/bin/env python
"""Test Email service - Gold Tier."""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.email_service import EmailService

async def main():
    print("\n" + "="*60)
    print("TESTING EMAIL - Send to binadnanosama@gmail.com")
    print("="*60)

    service = EmailService()
    result = await service.send_email(
        to='binadnanosama@gmail.com',
        subject='Test Email from AI Employee Gold Tier',
        body='This is a test email sent from the Gold Tier AI Employee system.'
    )

    print(f"\nResult: {result}")
    print("="*60)
    if result.get('success'):
        print("✅ EMAIL TEST PASSED")
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
    else:
        print(f"❌ EMAIL TEST FAILED: {result.get('error', 'Unknown error')}")
    print("="*60 + "\n")

if __name__ == '__main__':
    asyncio.run(main())
