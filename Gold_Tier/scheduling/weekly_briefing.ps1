# =============================================================================
# Weekly CEO Briefing Script (Windows PowerShell) - Gold Tier
# =============================================================================
# Schedules: Every Monday at 10:00 AM
# Purpose: Generate CEO briefing report with Odoo + Facebook + Vault data
#
# Setup in Windows Task Scheduler:
#   Trigger: Weekly, every Monday at 10:00 AM
#   Action: powershell.exe -ExecutionPolicy Bypass -File "path/to/weekly_briefing.ps1"
# =============================================================================

param(
    [string]$VaultPath = "",
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# =============================================================================
# Configuration
# =============================================================================

# Determine script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

if ([string]::IsNullOrEmpty($VaultPath)) {
    $VaultPath = Join-Path $ProjectRoot "AI_Employee_Vault_FTE"
}

$BriefingsPath = Join-Path $VaultPath "Briefings"
$LogsPath = Join-Path $VaultPath "Logs"
$DonePath = Join-Path $VaultPath "Done"
$PendingApprovalPath = Join-Path $VaultPath "Pending_Approval"
$NeedsActionPath = Join-Path $VaultPath "Needs_Action"

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
        default { "White" }
    }

    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color

    # Also write to log file
    $logFile = Join-Path $LogsPath "briefing_$(Get-Date -Format 'yyyyMMdd').log"
    "[$timestamp] [$Level] $Message" | Out-File -FilePath $logFile -Append -ErrorAction SilentlyContinue
}

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Log "Created directory: $Path"
    }
}

function Get-OdooFinancialData {
    param([string]$Period = "week")
    
    Write-Log "Fetching Odoo financial data..."
    
    try {
        # Call Odoo MCP via Python
        $pythonScript = @"
from mcp_server.odoo_service import OdooService
import asyncio
import json

async def get_data():
    service = OdooService()
    if service._connect():
        result = await service.get_financial_report(period="$Period")
        print(json.dumps(result))
    else:
        print(json.dumps({'success': False, 'error': 'Connection failed'}))

asyncio.run(get_data())
"@
        
        $result = python -c $pythonScript 2>&1
        return $result | ConvertFrom-Json
    }
    catch {
        Write-Log "Failed to fetch Odoo data: $_" "ERROR"
        return $null
    }
}

function Get-FacebookMetrics {
    Write-Log "Fetching Facebook metrics..."
    
    try {
        $pythonScript = @"
from mcp_server.facebook_service import FacebookService
import asyncio
import json

async def get_metrics():
    service = FacebookService()
    posts = await service.get_posts(limit=10)
    insights = await service.get_facebook_insights()
    print(json.dumps({
        'posts': posts,
        'insights': insights
    }))

asyncio.run(get_metrics())
"@
        
        $result = python -c $pythonScript 2>&1
        return $result | ConvertFrom-Json
    }
    catch {
        Write-Log "Failed to fetch Facebook data: $_" "ERROR"
        return $null
    }
}

function Get-CompletedTasksCount {
    param([string]$Path)

    if (-not (Test-Path $Path)) { return 0 }

    $files = Get-ChildItem -Path $Path -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
    return ($files | Measure-Object).Count
}

function Get-PendingItemsCount {
    param([string]$Path)

    if (-not (Test-Path $Path)) { return 0 }

    $files = Get-ChildItem -Path $Path -Filter "*.md" -Recurse -ErrorAction SilentlyContinue
    return ($files | Measure-Object).Count
}

function Get-NeedsActionByCategory {
    param([string]$Path)

    $categories = @{}
    $subdirs = @("email", "whatsapp", "linkedin", "files")

    foreach ($category in $subdirs) {
        $categoryPath = Join-Path $Path $category
        if (Test-Path $categoryPath) {
            $files = Get-ChildItem -Path $categoryPath -Filter "*.md" -ErrorAction SilentlyContinue
            $categories[$category] = ($files | Measure-Object).Count
        } else {
            $categories[$category] = 0
        }
    }

    return $categories
}

function Get-RecentActivity {
    param([string]$Path, [int]$Days = 7)

    if (-not (Test-Path $Path)) { return @() }

    $cutoff = (Get-Date).AddDays(-$Days)
    $files = Get-ChildItem -Path $Path -Filter "*.md" -Recurse -ErrorAction SilentlyContinue |
             Where-Object { $_.LastWriteTime -ge $cutoff } |
             Sort-Object LastWriteTime -Descending |
             Select-Object -First 10

    return $files | ForEach-Object {
        @{
            Name = $_.Name
            Path = $_.FullName
            Time = $_.LastWriteTime
        }
    }
}

# =============================================================================
# Main Script
# =============================================================================

try {
    Write-Log "Starting Weekly CEO Briefing Generation" "INFO"

    # Ensure directories exist
    Ensure-Directory -Path $BriefingsPath
    Ensure-Directory -Path $LogsPath

    # Gather statistics
    Write-Log "Gathering statistics..." "INFO"

    # Get Odoo financial data (Gold Tier)
    $odooData = Get-OdooFinancialData -Period "week"
    
    # Get Facebook metrics (Gold Tier)
    $facebookData = Get-FacebookMetrics
    
    # Get vault statistics
    $completedCount = Get-CompletedTasksCount -Path $DonePath
    $pendingApprovalCount = Get-PendingItemsCount -Path $PendingApprovalPath
    $categories = Get-NeedsActionByCategory -Path $NeedsActionPath
    $recentActivity = Get-RecentActivity -Path $DonePath -Days 7

    # Calculate totals
    $totalNeedsAction = ($categories.Values | Measure-Object -Sum).Sum

    # Generate briefing filename
    $today = Get-Date
    $monday = $today
    if ($today.DayOfWeek -ne "Monday") {
        # Find the most recent Monday
        $daysSinceMonday = ($today.DayOfWeek - [DayOfWeek]::Monday + 7) % 7
        $monday = $today.AddDays(-$daysSinceMonday)
    }
    $briefingFile = Join-Path $BriefingsPath "$($monday.ToString('yyyy-MM-dd'))_Monday_Briefing.md"

    Write-Log "Generating briefing file: $briefingFile" "INFO"

    # Build briefing content (Gold Tier with Odoo + Facebook)
    $odooRevenue = if ($odooData.success) { "$($odooData.report.revenue)" } else { "N/A" }
    $odooProfit = if ($odooData.success) { "$($odooData.report.profit)" } else { "N/A" }
    $facebookPosts = if ($facebookData.posts.success) { $facebookData.posts.count } else { 0 }
    
    $briefing = @"
---
generated: $($today.ToString('yyyy-MM-ddTHH:mm:ssZ'))
period: $($monday.AddDays(-7).ToString('yyyy-MM-dd')) to $($monday.ToString('yyyy-MM-dd'))
type: weekly_ceo_briefing
---

# Monday Morning CEO Briefing

*Generated: $($today.ToString('yyyy-MM-dd HH:mm:ss'))*

---

## Executive Summary

This Gold Tier briefing covers the past 7 days of AI Employee activity including financial performance and social media metrics.

---

## Financial Performance (from Odoo)

| Metric | Amount |
|--------|--------|
| Revenue This Week | \$$odooRevenue |
| Profit This Week | \$$odooProfit |
| Invoices Processed | $(if ($odooData.success) { $odooData.report.invoice_count } else { "N/A" }) |

---

## Social Media Performance

### Facebook
- Posts This Week: $facebookPosts
$(if ($facebookData.insights.success) {
"- Engagement: $($facebookData.insights.data.page_engaged_users.value)"
} else {
"- Engagement: N/A"
})

---

## Key Metrics

| Metric | Count |
|--------|-------|
| Tasks Completed | $completedCount |
| Pending Approvals | $pendingApprovalCount |
| Awaiting Action | $totalNeedsAction |

---

## Needs Action by Category

| Category | Items |
|----------|-------|
| Email | $($categories['email']) |
| WhatsApp | $($categories['whatsapp']) |
| LinkedIn | $($categories['linkedin']) |
| Files | $($categories['files']) |

---

## Completed Tasks (Last 7 Days)

Total: $completedCount tasks

$(
    if ($recentActivity.Count -gt 0) {
        $recentActivity | ForEach-Object {
            "- [x] $($_.Name) ($($_.Time.ToString('yyyy-MM-dd HH:mm')))"
        }
    } else {
        "_No completed tasks in the past 7 days._"
    }
)

---

## Pending Approval Queue

$(
    if ($pendingApprovalCount -gt 0) {
        "**$pendingApprovalCount items awaiting your review in /Pending_Approval**"
    } else {
        "No items pending approval."
    }
)

---

## Bottlenecks

$(
    if ($totalNeedsAction -gt 5) {
        "**Warning:** $totalNeedsAction items still need attention."
    } else {
        "No significant bottlenecks identified."
    }
)

---

## Proactive Suggestions

$(
    if ($categories['email'] -gt 3) {
        "- Consider prioritizing email responses ($($categories['email']) pending)"
    }
    if ($categories['whatsapp'] -gt 2) {
        "- WhatsApp messages need attention ($($categories['whatsapp']) pending)"
    }
    if ($pendingApprovalCount -gt 0) {
        "- Review pending approvals to unblock tasks"
    }
    if ($odooData.success -and $odooData.report.unpaid_invoices -gt 0) {
        "- Follow up on $($odooData.report.unpaid_invoices) unpaid invoices"
    }
)

---

## Next Week Focus

1. Review and process items in /Needs_Action
2. Clear pending approvals
3. Schedule LinkedIn posts for engagement

---

*This briefing was auto-generated by your AI Employee.*
*To customize, edit: scheduling/weekly_briefing.ps1*
"@

    # Write briefing file
    $briefing | Out-File -FilePath $briefingFile -Encoding UTF8 -Force

    Write-Log "Briefing generated successfully: $briefingFile" "SUCCESS"

    # Output summary
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "       WEEKLY CEO BRIEFING READY       " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "File: $briefingFile" -ForegroundColor White
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Yellow
    Write-Host "  Completed Tasks: $completedCount" -ForegroundColor Green
    Write-Host "  Pending Approvals: $pendingApprovalCount" -ForegroundColor $(if ($pendingApprovalCount -gt 0) { "Yellow" } else { "Green" })
    Write-Host "  Needs Action: $totalNeedsAction" -ForegroundColor $(if ($totalNeedsAction -gt 5) { "Yellow" } else { "Green" })
    Write-Host ""

    # Open in default editor (optional)
    if ($Verbose) {
        Write-Log "Opening briefing file..." "INFO"
        Start-Process $briefingFile
    }

} catch {
    Write-Log "Error generating briefing: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
    exit 1
}
