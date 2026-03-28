#!/usr/bin/env python
"""Quick Odoo Connection Test"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.odoo_service import OdooService

print("=== Odoo Connection Test ===\n")

s = OdooService()
print(f"URL: {s.url}")
print(f"DB: {s.db}")
print(f"Username: {s.username}")
print()

connected = s._connect()
print(f"Connection: {'SUCCESS (UID: ' + str(s.uid) + ')' if connected else 'FAILED'}")

if not connected:
    print("\n❌ Odoo is NOT connected!")
    print("\nMake sure:")
    print("1. Odoo Docker containers are running (docker-compose ps)")
    print("2. ODOO_USERNAME and ODOO_PASSWORD are set in .env")
    print("3. Odoo is initialized and accessible at http://localhost:8069")
    print("4. You can access http://localhost:8069 in browser")
else:
    print("\n✅ Odoo is connected and ready!")
    print(f"   User ID: {s.uid}")
