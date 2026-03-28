@echo off
echo ============================================
echo  Odoo 19 Setup for AI Employee (Gold Tier)
echo ============================================
echo.

echo Step 1: Cleaning up any existing containers...
docker-compose down

echo.
echo Step 2: Starting Odoo with automatic initialization...
echo Please wait - do not close this window...
echo.

docker-compose up -d

echo.
echo ============================================
echo  SETUP INITIATED!
echo ============================================
echo.
echo Odoo is now starting with automatic initialization.
echo This may take 5-10 minutes for the first startup.
echo.
echo To monitor progress: docker-compose logs -f
echo Access Odoo at: http://localhost:8069 when ready
echo Master password: admin
echo.
echo Press any key to continue...
pause >nul