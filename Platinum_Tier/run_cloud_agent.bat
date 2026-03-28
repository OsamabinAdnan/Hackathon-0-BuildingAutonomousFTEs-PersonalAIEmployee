@echo off
REM ==========================================
REM PLATINUM TIER - CLOUD AGENT LAUNCHER
REM ==========================================
REM Runs Cloud Agent in draft_only mode
REM Use this in Terminal 1

echo ==========================================
echo  Platinum Tier - Cloud Agent
echo  Mode: draft_only (no real sending)
echo ==========================================
echo.

REM Set environment variables
set EXECUTION_MODE=draft_only
set CLOUD_AGENT=true

REM Start orchestrator
echo Starting Cloud Agent...
uv run python -m orchestrator

pause
