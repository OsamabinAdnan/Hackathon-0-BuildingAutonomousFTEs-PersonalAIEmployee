@echo off
REM ==========================================
REM PLATINUM TIER - SETUP AUTO-SYNC
REM ==========================================
REM Creates Windows Task Scheduler job to sync vault every 5 minutes

set SCRIPT_PATH=%~dp0sync_vault.bat
set VAULT_PATH=%~dp0AI_Employee_Vault_FTE

echo ==========================================
echo  Platinum Tier - Auto-Sync Setup
echo ==========================================
echo.
echo This will create a Windows Task Scheduler job
echo to sync the vault every 5 minutes.
echo.
echo Script: %SCRIPT_PATH%
echo Vault: %VAULT_PATH%
echo.

REM Create scheduled task
echo Creating scheduled task...
schtasks /Create /TN "Platinum_Vault_Sync" /TR "\"%SCRIPT_PATH%\"" /SC MINUTE /MO 5 /RU SYSTEM /F

if errorlevel 1 (
    echo.
    echo Failed to create task automatically.
    echo.
    echo Manual setup instructions:
    echo 1. Open Task Scheduler
    echo 2. Create Basic Task
    echo 3. Name: Platinum Vault Sync
    echo 4. Trigger: Daily
    echo 5. Repeat task every: 5 minutes
    echo 6. Action: Start a program
    echo 7. Program: %SCRIPT_PATH%
) else (
    echo.
    echo SUCCESS! Auto-sync scheduled.
    echo.
    echo Task details:
    echo   Name: Platinum_Vault_Sync
    echo   Schedule: Every 5 minutes
    echo   Script: %SCRIPT_PATH%
    echo.
    echo To view task:
    echo   Open Task Scheduler ^→ Find "Platinum_Vault_Sync"
    echo.
    echo To run sync now:
    echo   schtasks /Run /TN "Platinum_Vault_Sync"
    echo.
    echo To remove task:
    echo   schtasks /Delete /TN "Platinum_Vault_Sync" /F
)

pause
