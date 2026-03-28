#!/bin/bash
# =============================================================================
# Weekly CEO Briefing Script (Linux/Mac)
# =============================================================================
# Schedules: Every Monday at 10:00 AM
# Purpose: Generate CEO briefing report for the past week
#
# Setup in crontab:
#   0 10 * * 1 /path/to/weekly_briefing.sh >> /var/log/ai_employee/briefing.log 2>&1
# =============================================================================

set -e

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VAULT_PATH="${VAULT_PATH:-$PROJECT_ROOT/AI_Employee_Vault_FTE}"

BRIEFINGS_PATH="$VAULT_PATH/Briefings"
LOGS_PATH="$VAULT_PATH/Logs"
DONE_PATH="$VAULT_PATH/Done"
PENDING_APPROVAL_PATH="$VAULT_PATH/Pending_Approval"
NEEDS_ACTION_PATH="$VAULT_PATH/Needs_Action"

VERBOSE="${VERBOSE:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    local color=$WHITE
    case $level in
        "INFO") color=$WHITE ;;
        "SUCCESS") color=$GREEN ;;
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac

    echo -e "${color}[$timestamp] [$level] $message${NC}"

    # Also write to log file
    mkdir -p "$LOGS_PATH"
    local log_file="$LOGS_PATH/briefing_$(date '+%Y%m%d').log"
    echo "[$timestamp] [$level] $message" >> "$log_file" 2>/dev/null || true
}

ensure_directory() {
    local path="$1"
    if [ ! -d "$path" ]; then
        mkdir -p "$path"
        log "INFO" "Created directory: $path"
    fi
}

count_files() {
    local path="$1"
    if [ ! -d "$path" ]; then
        echo 0
        return
    fi
    find "$path" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' '
}

count_category_files() {
    local base_path="$1"
    local category="$2"
    local category_path="$base_path/$category"

    if [ ! -d "$category_path" ]; then
        echo 0
        return
    fi

    find "$category_path" -name "*.md" -type f -maxdepth 1 2>/dev/null | wc -l | tr -d ' '
}

get_recent_activity() {
    local path="$1"
    local days="${2:-7}"

    if [ ! -d "$path" ]; then
        return
    fi

    # Find files modified in the last N days
    find "$path" -name "*.md" -type f -mtime -$days 2>/dev/null | head -10
}

# =============================================================================
# Main Script
# =============================================================================

log "INFO" "Starting Weekly CEO Briefing Generation"

# Ensure directories exist
ensure_directory "$BRIEFINGS_PATH"
ensure_directory "$LOGS_PATH"

# Gather statistics
log "INFO" "Gathering statistics..."

completed_count=$(count_files "$DONE_PATH")
pending_approval_count=$(count_files "$PENDING_APPROVAL_PATH")

email_count=$(count_category_files "$NEEDS_ACTION_PATH" "email")
whatsapp_count=$(count_category_files "$NEEDS_ACTION_PATH" "whatsapp")
linkedin_count=$(count_category_files "$NEEDS_ACTION_PATH" "linkedin")
files_count=$(count_category_files "$NEEDS_ACTION_PATH" "files")

total_needs_action=$((email_count + whatsapp_count + linkedin_count + files_count))

# Generate briefing filename
today=$(date '+%Y-%m-%d')
day_of_week=$(date '+%u')  # 1=Monday, 7=Sunday

if [ "$day_of_week" != "1" ]; then
    # Find the most recent Monday
    days_since_monday=$((day_of_week - 1))
    monday=$(date -d "$today -$days_since_monday days" '+%Y-%m-%d' 2>/dev/null || date -v-${days_since_monday}d '+%Y-%m-%d')
else
    monday=$today
fi

briefing_file="$BRIEFINGS_PATH/${monday}_Monday_Briefing.md"

log "INFO" "Generating briefing file: $briefing_file"

# Get recent activity
recent_files=$(get_recent_activity "$DONE_PATH" 7)
recent_activity=""
if [ -n "$recent_files" ]; then
    while IFS= read -r file; do
        filename=$(basename "$file")
        mod_time=$(stat -c '%y' "$file" 2>/dev/null | cut -d'.' -f1 || stat -f '%Sm' "$file" 2>/dev/null)
        recent_activity="- [x] $filename ($mod_time)\n$recent_activity"
    done <<< "$recent_files"
else
    recent_activity="_No completed tasks in the past 7 days._"
fi

# Build proactive suggestions
suggestions=""
if [ "$email_count" -gt 3 ]; then
    suggestions="- Consider prioritizing email responses ($email_count pending)\n$suggestions"
fi
if [ "$whatsapp_count" -gt 2 ]; then
    suggestions="- WhatsApp messages need attention ($whatsapp_count pending)\n$suggestions"
fi
if [ "$pending_approval_count" -gt 0 ]; then
    suggestions="- Review pending approvals to unblock tasks\n$suggestions"
fi

if [ -z "$suggestions" ]; then
    suggestions="No specific suggestions at this time."
fi

# Generate briefing content
cat > "$briefing_file" << EOF
---
generated: $(date -Iseconds)
period: $(date -d "$monday - 7 days" '+%Y-%m-%d' 2>/dev/null || date -v-7d '+%Y-%m-%d') to $monday
type: weekly_ceo_briefing
---

# Monday Morning CEO Briefing

*Generated: $(date '+%Y-%m-%d %H:%M:%S')*

---

## Executive Summary

This briefing covers the past 7 days of AI Employee activity.

---

## Key Metrics

| Metric | Count |
|--------|-------|
| Tasks Completed | $completed_count |
| Pending Approvals | $pending_approval_count |
| Awaiting Action | $total_needs_action |

---

## Needs Action by Category

| Category | Items |
|----------|-------|
| Email | $email_count |
| WhatsApp | $whatsapp_count |
| LinkedIn | $linkedin_count |
| Files | $files_count |

---

## Completed Tasks (Last 7 Days)

Total: $completed_count tasks

$(echo -e "$recent_activity")

---

## Pending Approval Queue

$(
    if [ "$pending_approval_count" -gt 0 ]; then
        echo "**$pending_approval_count items awaiting your review in /Pending_Approval**"
    else
        echo "No items pending approval."
    fi
)

---

## Bottlenecks

$(
    if [ "$total_needs_action" -gt 5 ]; then
        echo "**Warning:** $total_needs_action items still need attention."
    else
        echo "No significant bottlenecks identified."
    fi
)

---

## Proactive Suggestions

$(echo -e "$suggestions")

---

## Next Week Focus

1. Review and process items in /Needs_Action
2. Clear pending approvals
3. Schedule LinkedIn posts for engagement

---

*This briefing was auto-generated by your AI Employee.*
*To customize, edit: scheduling/weekly_briefing.sh*
EOF

log "SUCCESS" "Briefing generated successfully: $briefing_file"

# Output summary
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}       WEEKLY CEO BRIEFING READY       ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "File: $briefing_file"
echo ""
echo -e "Summary:"
echo -e "  Completed Tasks: ${GREEN}$completed_count${NC}"
if [ "$pending_approval_count" -gt 0 ]; then
    echo -e "  Pending Approvals: ${YELLOW}$pending_approval_count${NC}"
else
    echo -e "  Pending Approvals: ${GREEN}$pending_approval_count${NC}"
fi
if [ "$total_needs_action" -gt 5 ]; then
    echo -e "  Needs Action: ${YELLOW}$total_needs_action${NC}"
else
    echo -e "  Needs Action: ${GREEN}$total_needs_action${NC}"
fi
echo ""

# Open in default editor if verbose
if [ "$VERBOSE" = "true" ]; then
    log "INFO" "Opening briefing file..."
    ${EDITOR:-nano} "$briefing_file" 2>/dev/null || open "$briefing_file" 2>/dev/null || xdg-open "$briefing_file" 2>/dev/null || true
fi

exit 0
