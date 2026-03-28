#!/usr/bin/env python
"""Test Odoo MCP Connection and Tools"""

from mcp_server.odoo_service import OdooService
import asyncio

def test_odoo():
    s = OdooService()
    
    # Connect
    print("=== Odoo MCP Connection Test ===\n")
    connected = s._connect()
    print(f"Connection: {'SUCCESS (UID: ' + str(s.uid) + ')' if connected else 'FAILED'}")
    print()
    
    if not connected:
        return
    
    # Test 1: Get Financial Report
    print("1. Get Financial Report: ", end="")
    result = asyncio.run(s.get_financial_report())
    if result.get('success'):
        print("SUCCESS")
        report = result.get('report', {})
        print(f"   Revenue: ${report.get('revenue', 0):,.2f}")
        print(f"   Expenses: ${report.get('expenses', 0):,.2f}")
        print(f"   Profit: ${report.get('profit', 0):,.2f}")
    else:
        print("FAILED -", result.get('error'))
    print()
    
    # Test 2: List Unpaid Invoices
    print("2. List Unpaid Invoices: ", end="")
    result = asyncio.run(s.list_unpaid_invoices())
    if result.get('success'):
        print("SUCCESS")
        print(f"   Count: {result.get('count', 0)} invoices")
    else:
        print("FAILED -", result.get('error'))
    print()
    
    # Test 3: Get Profile
    print("3. Get User Profile: ", end="")
    result = asyncio.run(s.get_profile())
    if result.get('success'):
        print("SUCCESS")
        profile = result.get('profile', {})
        print(f"   Name: {profile.get('name', 'N/A')}")
        print(f"   Company: {profile.get('company', 'N/A')}")
    else:
        print("FAILED -", result.get('error'))
    print()
    
    print("=== All Tests Complete ===")

if __name__ == "__main__":
    test_odoo()
