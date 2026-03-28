# =============================================================================
# Run Orchestrator Script (Windows PowerShell)
# =============================================================================
# Purpose: Start the AI Employee orchestrator and manage the process
#
# Usage:
#   .\run_orchestrator.ps1                    # Start normally
#   .\run_orchestrator.ps1 -Watchers          # Start watchers only
#   .\run_orchestrator.ps1 -Briefing          # Generate briefing and exit
#   .\run_orchestrator.ps1 -Status            # Check system status
#
# Setup for auto-start on boot:
#   1. Open Task Scheduler
#   2. Create Basic Task -> "AI Employee Orchestrator"
#   3. Trigger: "At startup"
#   4. Action: Start a program
#      Program: powershell.exe
#      Arguments: -ExecutionPolicy Bypass -WindowStyle Hidden -File "path\to\run_orchestrator.ps1"
# =============================================================================

param(
    [switch]$Watchers,
    [switch]$Briefing,
    [switch]$Status,
    [switch]$Stop,
    [int]$CheckInterval = 60,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# =============================================================================
# Configuration
# =============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VaultPath = Join-Path $ProjectRoot "AI_Employee_Vault_FTE"
$LogsPath = Join-Path $VaultPath "Logs"
$PidFile = Join-Path $ProjectRoot "orchestrator.pid"

# =============================================================================
# Helper Functions
# =============================================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "White" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        "CYAN" { "Cyan" }
        default { "White" }
    }

    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color

    # Also write to log file
    if (Test-Path $LogsPath) {
        $logFile = Join-Path $LogsPath "orchestrator_$(Get-Date -Format 'yyyyMMdd').log"
        "[$timestamp] [$Level] $Message" | Out-File -FilePath $logFile -Append -ErrorAction SilentlyContinue
    }
}

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Log "Created directory: $Path"
    }
}

function Get-ProcessStatus {
    param([string]$PidFilePath)

    if (Test-Path $PidFilePath) {
        $pid = Get-Content $PidFilePath -ErrorAction SilentlyContinue
        if (-not [string]::IsNullOrEmpty($pid)) {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($null -ne $process) {
                return @{
                    Running = $true
                    PID = $pid
                    StartTime = $process.StartTime
                    CPU = $process.CPU
                    Memory = [math]::Round($process.WorkingSet64 / 1MB, 2)
                }
            }
        }
    }
    return @{ Running = $false }
}

function Stop-Orchestrator {
    param([string]$PidFilePath)

    if (Test-Path $PidFilePath) {
        $pid = Get-Content $PidFilePath -ErrorAction SilentlyContinue
        if (-not [string]::IsNullOrEmpty($pid)) {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($null -ne $process) {
                Write-Log "Stopping orchestrator (PID: $pid)..." "WARNING"
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2

                # Verify stopped
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($null -eq $process) {
                    Write-Log "Orchestrator stopped successfully" "SUCCESS"
                    Remove-Item $PidFilePath -Force -ErrorAction SilentlyContinue
                } else {
                    Write-Log "Failed to stop orchestrator" "ERROR"
                }
            } else {
                Write-Log "Orchestrator process not running" "WARNING"
                Remove-Item $PidFilePath -Force -ErrorAction SilentlyContinue
            }
        }
    } else {
        Write-Log "No PID file found" "WARNING"
    }
}

function Show-Status {
    $orchestratorStatus = Get-ProcessStatus -PidFilePath $PidFile

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "       AI EMPLOYEE SYSTEM STATUS       " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Orchestrator status
    if ($orchestratorStatus.Running) {
        Write-Host "Orchestrator:" -ForegroundColor Yellow
        Write-Host "  Status: Running" -ForegroundColor Green
        Write-Host "  PID: $($orchestratorStatus.PID)" -ForegroundColor White
        Write-Host "  Started: $($orchestratorStatus.StartTime)" -ForegroundColor White
        Write-Host "  Memory: $($orchestratorStatus.Memory) MB" -ForegroundColor White
    } else {
        Write-Host "Orchestrator: Not Running" -ForegroundColor Red
    }

    Write-Host ""

    # Check vault folders
    Write-Host "Vault Status:" -ForegroundColor Yellow

    $folders = @(
        @{ Name = "Needs_Action/email"; Path = Join-Path $VaultPath "Needs_Action\email" },
        @{ Name = "Needs_Action/whatsapp"; Path = Join-Path $VaultPath "Needs_Action\whatsapp" },
        @{ Name = "Needs_Action/linkedin"; Path = Join-Path $VaultPath "Needs_Action\linkedin" },
        @{ Name = "Needs_Action/files"; Path = Join-Path $VaultPath "Needs_Action\files" },
        @{ Name = "Pending_Approval"; Path = Join-Path $VaultPath "Pending_Approval" },
        @{ Name = "Done"; Path = Join-Path $VaultPath "Done" }
    )

    foreach ($folder in $folders) {
        if (Test-Path $folder.Path) {
            $count = (Get-ChildItem -Path $folder.Path -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
            Write-Host "  $($folder.Name): $count items" -ForegroundColor White
        } else {
            Write-Host "  $($folder.Name): Not found" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

# =============================================================================
# Main Script
# =============================================================================

try {
    # Ensure logs directory exists
    Ensure-Directory -Path $LogsPath

    # Handle stop command
    if ($Stop) {
        Stop-Orchestrator -PidFilePath $PidFile
        exit 0
    }

    # Handle status command
    if ($Status) {
        Show-Status
        exit 0
    }

    # Handle briefing command
    if ($Briefing) {
        Write-Log "Generating CEO briefing..." "INFO"
        $briefingScript = Join-Path $ScriptDir "weekly_briefing.ps1"

        if (Test-Path $briefingScript) {
            & $briefingScript -Verbose:$Verbose
        } else {
            Write-Log "Briefing script not found: $briefingScript" "ERROR"
            exit 1
        }
        exit 0
    }

    # Check if already running
    $currentStatus = Get-ProcessStatus -PidFilePath $PidFile
    if ($currentStatus.Running) {
        Write-Log "Orchestrator already running (PID: $($currentStatus.PID))" "WARNING"
        Write-Log "Use -Stop to stop the current instance" "INFO"
        exit 0
    }

    # Start orchestrator
    Write-Log "Starting AI Employee Orchestrator" "CYAN"

    $orchestratorPath = Join-Path $ProjectRoot "orchestrator\main.py"

    if (-not (Test-Path $orchestratorPath)) {
        Write-Log "Orchestrator not found: $orchestratorPath" "ERROR"
        exit 1
    }

    # Build arguments
    $pythonArgs = @()
    if ($Watchers) {
        $pythonArgs += "--watchers-only"
    }
    if ($Verbose) {
        $pythonArgs += "--verbose"
    }
    $pythonArgs += "--check-interval"
    $pythonArgs += $CheckInterval

    # Start process
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "python"
    $processInfo.Arguments = "-m orchestrator $($pythonArgs -join ' ')"
    $processInfo.WorkingDirectory = $ProjectRoot
    $processInfo.UseShellExecute = $false
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.CreateNoWindow = -not $Verbose

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo

    # Output handlers
    $outputAction = {
        param([object]$sender, [System.Diagnostics.DataReceivedEventArgs]$e)
        if (-not [string]::IsNullOrEmpty($e.Data)) {
            Write-Host $e.Data
        }
    }

    $errorAction = {
        param([object]$sender, [System.Diagnostics.DataReceivedEventArgs]$e)
        if (-not [string]::IsNullOrEmpty($e.Data)) {
            Write-Host $e.Data -ForegroundColor Red
        }
    }

    $process.add_OutputDataReceived($outputAction)
    $process.add_ErrorDataReceived($errorAction)

    $process.Start() | Out-Null
    $process.BeginOutputReadLine()
    $process.BeginErrorReadLine()

    # Save PID
    $process.Id | Out-File -FilePath $PidFile -Force

    Write-Log "Orchestrator started (PID: $($process.Id))" "SUCCESS"

    # Wait for process to exit
    $process.WaitForExit()

    # Cleanup
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    Write-Log "Orchestrator stopped" "INFO"

} catch {
    Write-Log "Error: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    exit 1
}
