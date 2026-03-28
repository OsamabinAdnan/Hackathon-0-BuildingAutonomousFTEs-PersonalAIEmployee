#!/bin/bash
# =============================================================================
# Setup Cron Jobs Script (Linux/Mac)
# =============================================================================
# Purpose: Install cron jobs for the AI Employee system
#
# Usage:
#   ./setup_cron.sh install    # Install all cron jobs
#   ./setup_cron.sh remove     # Remove all cron jobs
#   ./setup_cron.sh list       # List current cron jobs
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cron job definitions
# Format: minute hour day-of-month month day-of-week command
CRON_JOBS=(
    # Weekly CEO Briefing - Every Monday at 10:00 AM
    "0 10 * * 1 $SCRIPT_DIR/weekly_briefing.sh >> $PROJECT_ROOT/AI_Employee_Vault_FTE/Logs/cron_briefing.log 2>&1 # AI_EMPLOYEE_BRIEFING"

    # LinkedIn Weekly Post - Every Monday at 9:00 AM
    "0 9 * * 1 cd $PROJECT_ROOT && python integrations/linkedin_poster.py --template weekly_update >> $PROJECT_ROOT/AI_Employee_Vault_FTE/Logs/cron_linkedin.log 2>&1 # AI_EMPLOYEE_LINKEDIN"

    # Orchestrator Health Check - Every 5 minutes
    "*/5 * * * * pgrep -f 'python.*orchestrator' > /dev/null || cd $PROJECT_ROOT && python -m orchestrator >> $PROJECT_ROOT/AI_Employee_Vault_FTE/Logs/cron_orchestrator.log 2>&1 # AI_EMPLOYEE_ORCHESTRATOR"
)

# Function to check if cron is installed
check_cron() {
    if ! command -v crontab &> /dev/null; then
        echo -e "${RED}Error: crontab is not installed${NC}"
        echo "Install with:"
        echo "  Ubuntu/Debian: sudo apt-get install cron"
        echo "  macOS: Should be pre-installed"
        echo "  RHEL/CentOS: sudo yum install cronie"
        exit 1
    fi
}

# Function to install cron jobs
install_cron() {
    echo -e "${CYAN}Installing AI Employee cron jobs...${NC}"

    # Get current crontab
    local current_cron=""
    if crontab -l 2>/dev/null; then
        current_cron=$(crontab -l 2>/dev/null)
    fi

    # Remove any existing AI Employee jobs
    local filtered_cron=$(echo "$current_cron" | grep -v "AI_EMPLOYEE_" || true)

    # Add new jobs
    local new_cron="$filtered_cron"
    for job in "${CRON_JOBS[@]}"; do
        new_cron="$new_cron"$'\n'"$job"
        echo -e "${GREEN}Added: $job${NC}"
    done

    # Install new crontab
    echo "$new_cron" | crontab -

    echo -e "${GREEN}Cron jobs installed successfully!${NC}"
    echo ""
    list_cron
}

# Function to remove cron jobs
remove_cron() {
    echo -e "${YELLOW}Removing AI Employee cron jobs...${NC}"

    # Get current crontab
    local current_cron=""
    if crontab -l 2>/dev/null; then
        current_cron=$(crontab -l 2>/dev/null)
    fi

    # Remove AI Employee jobs
    local filtered_cron=$(echo "$current_cron" | grep -v "AI_EMPLOYEE_" || true)

    # Install filtered crontab
    echo "$filtered_cron" | crontab -

    echo -e "${GREEN}AI Employee cron jobs removed.${NC}"
}

# Function to list AI Employee cron jobs
list_cron() {
    echo -e "${CYAN}Current AI Employee cron jobs:${NC}"
    echo ""

    if crontab -l 2>/dev/null | grep -q "AI_EMPLOYEE_"; then
        crontab -l 2>/dev/null | grep "AI_EMPLOYEE_" | while read -r line; do
            echo -e "  ${GREEN}$line${NC}"
        done
    else
        echo -e "  ${YELLOW}No AI Employee cron jobs found.${NC}"
    fi
    echo ""
}

# =============================================================================
# Main Script
# =============================================================================

check_cron

case "${1:-list}" in
    install)
        install_cron
        ;;
    remove)
        remove_cron
        ;;
    list)
        list_cron
        ;;
    *)
        echo "Usage: $0 {install|remove|list}"
        echo ""
        echo "Commands:"
        echo "  install  - Install all AI Employee cron jobs"
        echo "  remove   - Remove all AI Employee cron jobs"
        echo "  list     - List current AI Employee cron jobs"
        exit 1
        ;;
esac

exit 0
