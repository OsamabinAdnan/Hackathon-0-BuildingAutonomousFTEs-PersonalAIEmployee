# =============================================================================
# LinkedIn Scheduled Post Script (Windows PowerShell)
# =============================================================================
# Purpose: Post scheduled content to LinkedIn for business/sales growth
#
# Usage:
#   .\linkedin_post.ps1 -Template "milestone"
#   .\linkedin_post.ps1 -Text "Exciting news! We just launched..."
#   .\linkedin_post.ps1 -FromFile "posts\weekly_update.md"
#
# Schedule in Windows Task Scheduler:
#   Trigger: Weekly, Monday and Thursday at 9:00 AM
#   Action: powershell.exe -ExecutionPolicy Bypass -File "path/to/linkedin_post.ps1" -Template "weekly_update"
# =============================================================================

param(
    [string]$Template = "",
    [string]$Text = "",
    [string]$FromFile = "",
    [string]$Visibility = "PUBLIC",
    [switch]$DryRun,
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

# =============================================================================
# Post Templates
# =============================================================================

$Templates = @{
    "product_launch" = @"
🚀 Exciting News!

We're thrilled to announce our latest offering!

This has been in development for months, and we can't wait to share it with you.

Key features:
• Feature 1
• Feature 2
• Feature 3

Ready to learn more? Drop a comment or DM us!

#Innovation #ProductLaunch #ExcitingTimes
"@

    "milestone" = @"
🎉 Milestone Alert!

We just reached [MILESTONE]!

This wouldn't have been possible without:
• Our amazing team
• Our supportive clients
• Our incredible community

Thank you all for being part of this journey!

Here's to the next milestone! 🚀

#Milestone #Growth #Gratitude
"@

    "tip" = @"
💡 Pro Tip of the Day

[INSERT TIP HERE]

Save this for later and share with someone who needs it!

#ProTip #BusinessTips #Learning
"@

    "industry_news" = @"
📰 Industry Update

Did you see the latest news about [TOPIC]?

Our take:
[INSERT COMMENTARY]

What are your thoughts? Drop a comment below!

#IndustryNews #ThoughtLeadership
"@

    "team_announcement" = @"
👥 Team Update!

Please welcome our newest team member!

We're excited to have [NAME] join us as [ROLE]!

[Fun fact about the new team member]

Welcome to the team! 🎉

#TeamGrowth #Hiring #Welcome
"@

    "customer_success" = @"
⭐ Customer Success Story

We're proud to share how we helped [CUSTOMER] achieve [RESULT]:

Before: [BEFORE STATE]
After: [AFTER STATE]

"We couldn't be happier with the results!" - [CUSTOMER QUOTE]

Let's write your success story next!

#CustomerSuccess #CaseStudy #Results
"@

    "weekly_update" = @"
📊 Weekly Wrap-Up

This week at [COMPANY]:

✅ Achievement 1
✅ Achievement 2
✅ Achievement 3

Looking ahead to next week:
• Focus area 1
• Focus area 2

What were your wins this week? Share below!

#WeeklyUpdate #BusinessGrowth #Progress
"@
}

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
    if (Test-Path $LogsPath) {
        $logFile = Join-Path $LogsPath "linkedin_post_$(Get-Date -Format 'yyyyMMdd').log"
        "[$timestamp] [$Level] $Message" | Out-File -FilePath $logFile -Append -ErrorAction SilentlyContinue
    }
}

function Invoke-LinkedInPost {
    param([string]$Text, [string]$Visibility)

    # Check for LinkedIn access token
    $accessToken = $env:LINKEDIN_ACCESS_TOKEN

    if ([string]::IsNullOrEmpty($accessToken)) {
        Write-Log "ERROR: LINKEDIN_ACCESS_TOKEN environment variable not set" "ERROR"
        Write-Log "Please set the environment variable and try again" "ERROR"
        return $false
    }

    # Check if using LinkedIn poster integration
    $linkedinPoster = Join-Path $ProjectRoot "integrations\linkedin_poster.py"

    if (Test-Path $linkedinPoster) {
        # Use the Python integration
        $tempFile = Join-Path $env:TEMP "linkedin_post_$(Get-Date -Format 'yyyyMMddHHmmss').txt"
        $Text | Out-File -FilePath $tempFile -Encoding UTF8 -Force

        try {
            $result = & python $linkedinPoster --file $tempFile --visibility $Visibility 2>&1
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

            if ($LASTEXITCODE -eq 0) {
                return $true
            } else {
                Write-Log "LinkedIn poster failed: $result" "ERROR"
                return $false
            }
        } catch {
            Write-Log "Error running LinkedIn poster: $_" "ERROR"
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
            return $false
        }
    } else {
        # Use direct API call
        Write-Log "Using direct API call..." "INFO"

        $headers = @{
            "Authorization" = "Bearer $accessToken"
            "Content-Type" = "application/json"
            "X-Restli-Protocol-Version" = "2.0.0"
        }

        $body = @{
            author = "urn:li:person:YOUR_PERSON_URN"  # Replace with actual URN
            lifecycleState = "PUBLISHED"
            specificContent = @{
                "com.linkedin.ugc.ShareContent" = @{
                    shareCommentary = @{
                        text = $Text
                    }
                    shareMediaCategory = "NONE"
                }
            }
            visibility = @{
                "com.linkedin.ugc.MemberNetworkVisibility" = $Visibility
            }
        } | ConvertTo-Json -Depth 10

        try {
            $response = Invoke-RestMethod -Uri "https://api.linkedin.com/v2/ugcPosts" -Method Post -Headers $headers -Body $body -ContentType "application/json"
            Write-Log "Post created successfully!" "SUCCESS"
            return $true
        } catch {
            Write-Log "API call failed: $_" "ERROR"
            return $false
        }
    }
}

# =============================================================================
# Main Script
# =============================================================================

try {
    Write-Log "Starting LinkedIn Post Script" "INFO"

    # Ensure logs directory exists
    if (-not (Test-Path $LogsPath)) {
        New-Item -ItemType Directory -Path $LogsPath -Force | Out-Null
    }

    # Determine post content
    $postText = ""

    if (-not [string]::IsNullOrEmpty($Text)) {
        # Direct text provided
        $postText = $Text
        Write-Log "Using provided text" "INFO"

    } elseif (-not [string]::IsNullOrEmpty($FromFile)) {
        # Load from file
        $filePath = $FromFile
        if (-not [System.IO.Path]::IsPathRooted($filePath)) {
            $filePath = Join-Path $VaultPath $FromFile
        }

        if (Test-Path $filePath) {
            $postText = Get-Content $filePath -Raw
            Write-Log "Loaded content from file: $filePath" "INFO"
        } else {
            Write-Log "File not found: $filePath" "ERROR"
            exit 1
        }

    } elseif (-not [string]::IsNullOrEmpty($Template)) {
        # Use template
        if ($Templates.ContainsKey($Template)) {
            $postText = $Templates[$Template]
            Write-Log "Using template: $Template" "INFO"
        } else {
            Write-Log "Unknown template: $Template" "ERROR"
            Write-Log "Available templates: $($Templates.Keys -join ', ')" "INFO"
            exit 1
        }

    } else {
        # Default to weekly_update template
        $postText = $Templates["weekly_update"]
        Write-Log "Using default template: weekly_update" "INFO"
    }

    # Validate post content
    if ([string]::IsNullOrWhiteSpace($postText)) {
        Write-Log "No post content provided" "ERROR"
        exit 1
    }

    if ($postText.Length -gt 3000) {
        Write-Log "Post text exceeds 3000 characters (current: $($postText.Length))" "WARNING"
        Write-Log "Truncating to 3000 characters..." "WARNING"
        $postText = $postText.Substring(0, 3000)
    }

    # Show preview
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "         LINKEDIN POST PREVIEW         " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Visibility: $Visibility" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Content:" -ForegroundColor White
    Write-Host $postText
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    if ($DryRun) {
        Write-Log "DRY RUN - Post not published" "WARNING"
        exit 0
    }

    # Post to LinkedIn
    Write-Log "Publishing to LinkedIn..." "INFO"
    $success = Invoke-LinkedInPost -Text $postText -Visibility $Visibility

    if ($success) {
        Write-Log "Post published successfully!" "SUCCESS"

        # Log the post
        $postLogFile = Join-Path $LogsPath "linkedin_posts.log"
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Visibility: $Visibility | Length: $($postText.Length) chars"
        $logEntry | Out-File -FilePath $postLogFile -Append -ErrorAction SilentlyContinue
    } else {
        Write-Log "Failed to publish post" "ERROR"
        exit 1
    }

} catch {
    Write-Log "Error: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
    exit 1
}
