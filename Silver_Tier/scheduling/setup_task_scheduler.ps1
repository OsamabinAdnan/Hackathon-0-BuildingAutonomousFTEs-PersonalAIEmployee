# =============================================================================
# Setup Windows Task Scheduler Script (PowerShell)
# =============================================================================
# Purpose: Install scheduled tasks for the AI Employee system on Windows
#
# Usage:
#   .\setup_task_scheduler.ps1 -Install    # Install all scheduled tasks
#   .\setup_task_scheduler.ps1 -Remove     # Remove all scheduled tasks
#   .\setup_task_scheduler.ps1 -List       # List current scheduled tasks
# =============================================================================

param(
    [switch]$Install,
    [switch]$Remove,
    [switch]$List
)

# =============================================================================
# Configuration
# =============================================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Task definitions
$Tasks = @(
    @{
        Name = "AI_Employee_Weekly_Briefing"
        Description = "Generate weekly CEO briefing every Monday at 10:00 AM"
        Script = Join-Path $ScriptDir "weekly_briefing.ps1"
        Trigger = @{
            Frequency = "Weekly"
            DaysOfWeek = "Monday"
            At = "10:00 AM"
        }
    },
    @{
        Name = "AI_Employee_LinkedIn_Post"
        Description = "Post weekly update to LinkedIn every Monday at 9:00 AM"
        Script = Join-Path $ScriptDir "linkedin_post.ps1"
        Arguments = "-Template weekly_update"
        Trigger = @{
            Frequency = "Weekly"
            DaysOfWeek = "Monday"
            At = "9:00 AM"
        }
    },
    @{
        Name = "AI_Employee_Orchestrator_Startup"
        Description = "Start the AI Employee orchestrator at system startup"
        Script = Join-Path $ScriptDir "run_orchestrator.ps1"
        Trigger = @{
            Frequency = "AtStartup"
        }
    }
)

# =============================================================================
# Helper Functions
# =============================================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")

    $color = switch ($Level) {
        "INFO" { "White" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        "CYAN" { "Cyan" }
        default { "White" }
    }

    Write-Host "[$Level] $Message" -ForegroundColor $color
}

function New-ScheduledTask {
    param([hashtable]$TaskDef)

    $taskName = $TaskDef.Name
    $taskDesc = $TaskDef.Description
    $scriptPath = $TaskDef.Script
    $arguments = $TaskDef.Arguments
    $trigger = $TaskDef.Trigger

    # Check if script exists
    if (-not (Test-Path $scriptPath)) {
        Write-Log "Script not found: $scriptPath" "ERROR"
        return $false
    }

    # Create action
    $actionArgs = "-ExecutionPolicy Bypass -File `"$scriptPath`""
    if (-not [string]::IsNullOrEmpty($arguments)) {
        $actionArgs += " $arguments"
    }

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs -WorkingDirectory $ProjectRoot

    # Create trigger based on frequency
    $taskTrigger = switch ($trigger.Frequency) {
        "Weekly" {
            $dayOfWeek = [DayOfWeek]$trigger.DaysOfWeek
            $time = [DateTime]::Parse($trigger.At)
            New-ScheduledTaskTrigger -Weekly -DaysOfWeek $dayOfWeek -At $time
        }
        "AtStartup" {
            New-ScheduledTaskTrigger -AtStartup
        }
        "Daily" {
            $time = [DateTime]::Parse($trigger.At)
            New-ScheduledTaskTrigger -Daily -At $time
        }
        default {
            Write-Log "Unknown trigger frequency: $($trigger.Frequency)" "ERROR"
            return $false
        }
    }

    # Create settings
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    # Register task
    try {
        Register-ScheduledTask -TaskName $taskName -Description $taskDesc -Action $action -Trigger $taskTrigger -Settings $settings -RunLevel Highest -Force | Out-Null
        Write-Log "Created task: $taskName" "SUCCESS"
        return $true
    } catch {
        Write-Log "Failed to create task $taskName : $_" "ERROR"
        return $false
    }
}

function Remove-ScheduledTaskIfExists {
    param([string]$TaskName)

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($null -ne $task) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Null
            Write-Log "Removed task: $TaskName" "SUCCESS"
        }
    } catch {
        Write-Log "Task not found or already removed: $TaskName" "WARNING"
    }
}

function Get-AIEmployeeTasks {
    Get-ScheduledTask | Where-Object { $_.TaskName -like "AI_Employee_*" }
}

# =============================================================================
# Main Script
# =============================================================================

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Log "This script requires administrator privileges" "ERROR"
    Write-Log "Please run PowerShell as Administrator and try again" "WARNING"
    exit 1
}

if ($List -or (-not $Install -and -not $Remove)) {
    # List current tasks
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   AI EMPLOYEE SCHEDULED TASKS        " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    $currentTasks = Get-AIEmployeeTasks
    if ($currentTasks) {
        foreach ($task in $currentTasks) {
            Write-Host "Task: $($task.TaskName)" -ForegroundColor Yellow
            Write-Host "  State: $($task.State)" -ForegroundColor White
            Write-Host "  Description: $($task.Description)" -ForegroundColor White
            Write-Host ""
        }
    } else {
        Write-Host "No AI Employee scheduled tasks found." -ForegroundColor Yellow
        Write-Host ""
    }

    Write-Host "Available tasks to install:" -ForegroundColor Cyan
    foreach ($taskDef in $Tasks) {
        Write-Host "  - $($taskDef.Name): $($taskDef.Description)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\setup_task_scheduler.ps1 -Install   # Install all tasks"
    Write-Host "  .\setup_task_scheduler.ps1 -Remove    # Remove all tasks"
    Write-Host ""
    exit 0
}

if ($Remove) {
    Write-Log "Removing AI Employee scheduled tasks..." "CYAN"
    foreach ($taskDef in $Tasks) {
        Remove-ScheduledTaskIfExists -TaskName $taskDef.Name
    }
    Write-Log "All AI Employee tasks removed" "SUCCESS"
    exit 0
}

if ($Install) {
    Write-Log "Installing AI Employee scheduled tasks..." "CYAN"

    $success = $true
    foreach ($taskDef in $Tasks) {
        # Remove existing task first
        Remove-ScheduledTaskIfExists -TaskName $taskDef.Name

        # Create new task
        if (-not (New-ScheduledTask -TaskDef $taskDef)) {
            $success = $false
        }
    }

    if ($success) {
        Write-Log "All tasks installed successfully!" "SUCCESS"

        # List installed tasks
        Write-Host ""
        Write-Host "Installed tasks:" -ForegroundColor Cyan
        Get-AIEmployeeTasks | ForEach-Object {
            Write-Host "  - $($_.TaskName) [$($_.State)]" -ForegroundColor Green
        }
    } else {
        Write-Log "Some tasks failed to install" "ERROR"
        exit 1
    }
}

exit 0
