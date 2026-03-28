#!/usr/bin/env python
"""Test all messaging services - Gold Tier."""

import asyncio
import sys
import os

# Add Gold_Tier to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_whatsapp():
    """Test WhatsApp message."""
    print("\n" + "="*50)
    print("TESTING WHATSAPP")
    print("="*50)
    try:
        from mcp_server.whatsapp_service import WhatsAppService
        service = WhatsAppService()
        result = service.send_message(
            contact='Me Telenor',
            message='Test message from AI Employee'
        )
        print(f"Result: {result}")
        return result.get('success', False)
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_email():
    """Test email sending."""
    print("\n" + "="*50)
    print("TESTING EMAIL")
    print("="*50)
    try:
        from mcp_server.email_service import EmailService
        service = EmailService()
        result = await service.send_email(
            to='binadnanosama@gmail.com',
            subject='Test Email from AI Employee',
            body='This is a test email sent from the Gold Tier AI Employee system.'
        )
        print(f"Result: {result}")
        return result.get('success', False)
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_linkedin():
    """Test LinkedIn post."""
    print("\n" + "="*50)
    print("TESTING LINKEDIN")
    print("="*50)
    try:
        from mcp_server.linkedin_service import LinkedInService
        service = LinkedInService()
        result = await service.post_share(
            text='🤖 Test post from AI Employee Gold Tier! #AI #Automation',
            visibility='PUBLIC'
        )
        print(f"Result: {result}")
        return result.get('success', False)
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_facebook():
    """Test Facebook post."""
    print("\n" + "="*50)
    print("TESTING FACEBOOK")
    print("="*50)
    try:
        from mcp_server.facebook_service import FacebookService
        service = FacebookService()
        result = await service.post_facebook(
            message='🤖 Test post from AI Employee Gold Tier! #AI #Automation'
        )
        print(f"Result: {result}")
        return result.get('success', False)
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AI EMPLOYEE GOLD TIER - SERVICE TESTS")
    print("="*60)
    
    results = {}
    
    # Test 1: WhatsApp
    results['WhatsApp'] = test_whatsapp()
    input("\nPress Enter to continue to Email test...")
    
    # Test 2: Email
    results['Email'] = asyncio.run(test_email())
    input("\nPress Enter to continue to LinkedIn test...")
    
    # Test 3: LinkedIn
    results['LinkedIn'] = asyncio.run(test_linkedin())
    input("\nPress Enter to continue to Facebook test...")
    
    # Test 4: Facebook
    results['Facebook'] = asyncio.run(test_facebook())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for service, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {service}: {status}")
    print("="*60)

if __name__ == '__main__':
    main()
