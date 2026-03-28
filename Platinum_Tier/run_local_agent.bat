@echo off
REM ==========================================
REM PLATINUM TIER - LOCAL AGENT LAUNCHER
REM ==========================================
REM Runs Local Agent in full execution mode
REM Use this in Terminal 2

echo ==========================================
echo  Platinum Tier - Local Agent
echo  Mode: full (executes approved actions)
echo ==========================================
echo.

REM Set environment variables
set EXECUTION_MODE=full
set CLOUD_AGENT=false

REM Start orchestrator
echo Starting Local Agent...
uv run python -m orchestrator

pause
