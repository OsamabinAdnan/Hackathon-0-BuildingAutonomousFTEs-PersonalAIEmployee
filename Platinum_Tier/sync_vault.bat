@echo off
REM ==========================================
REM PLATINUM TIER - VAULT SYNC SCRIPT
REM ==========================================
REM Syncs vault via Git every 5 minutes
REM Use this for Cloud→Local or Local→Cloud sync

set VAULT_PATH=%~dp0AI_Employee_Vault_FTE
cd /d "%VAULT_PATH%"

echo ==========================================
echo  Platinum Tier - Vault Sync
echo  Path: %VAULT_PATH%
echo  Time: %DATE% %TIME%
echo ==========================================

REM Check if Git is initialized
if not exist ".git" (
    echo Git not initialized yet. Initializing...
    git init
    git config user.email "platinum-agent@local"
    git config user.name "Platinum Agent"
    
    REM Create initial commit
    git add .
    git commit -m "Initial Platinum vault setup"
    
    echo.
    echo Git initialized!
    echo To setup remote sync, run:
    echo   git remote add origin ^<your-repo-url^>
    echo   git push -u origin main
    goto :EOF
)

REM Pull latest changes (from Cloud or Local)
echo Pulling latest changes...
git pull origin main --no-edit 2>nul
if errorlevel 1 (
    echo No remote configured or pull failed.
    echo To setup remote sync:
    echo   git remote add origin ^<your-repo-url^>
    echo   git push -u origin main
) else (
    echo Pull successful.
)

REM Add local changes
echo Adding local changes...
git add .

REM Check if there are changes to commit
git diff --cached --quiet
if errorlevel 1 (
    REM There are changes
    echo Committing changes...
    git commit -m "Auto-sync: %DATE% %TIME%"
    
    REM Push changes
    echo Pushing changes...
    git push origin main 2>nul
    if errorlevel 1 (
        echo Push failed. Pulling and retrying...
        git pull --rebase origin main
        git push origin main
    ) else (
        echo Push successful!
    )
) else (
    echo No changes to sync.
)

echo.
echo Sync complete at %TIME%
