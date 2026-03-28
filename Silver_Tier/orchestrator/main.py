"""
Orchestrator - Main controller for the Silver Tier AI Employee.

This is the primary entry point. The orchestrator:
1. Starts all Watchers (Gmail, WhatsApp, LinkedIn, FileSystem)
2. Monitors /Needs_Action/** subdirectories for new action files
3. Monitors /Approved for human-approved actions
4. Monitors /Rejected for human-rejected actions
5. Triggers Claude Code to process items
6. Generates Weekly CEO Briefing (Monday 10 AM)

Silver Tier: Monitors categorized subdirectories in /Needs_Action/

Usage:
    python -m orchestrator                      # Full autonomous mode
    python -m orchestrator --check-interval 5   # Custom check interval
    python -m orchestrator --status             # Show system status
    python -m orchestrator --briefing           # Generate CEO briefing
"""

import argparse
import logging
import subprocess
import sys
import threading
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from colorama import init as colorama_init, Fore, Style

# Initialize colorama
colorama_init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels and components."""

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    # Component-specific colors
    COMPONENT_COLORS = {
        'ORCHESTRATOR': Fore.WHITE,  # White for orchestrator
        'FILES': Fore.YELLOW,  # Gold for file watcher
        'GMAIL': Fore.LIGHTMAGENTA_EX,  # Pink/red for Gmail watcher
        'WHATSAPP': Fore.LIGHTGREEN_EX,  # Light green for WhatsApp watcher
        'LINKEDIN': Fore.LIGHTBLUE_EX,  # Light blue for LinkedIn watcher
        'CLAUDE': Fore.LIGHTRED_EX,  # Orange/red for Claude (closest to orange)
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)

        # Determine component color based on logger name
        component_color = Fore.WHITE  # Default (orchestrator)
        for comp_name, comp_color in self.COMPONENT_COLORS.items():
            if comp_name.lower() in record.name.lower():
                component_color = comp_color
                break

        # Format the message with appropriate colors
        formatted_message = super().format(record)

        # Split into parts: Timestamp | Level | Message
        parts = formatted_message.split(' | ', 2)

        if len(parts) >= 3:
            timestamp = parts[0]
            level = parts[1]
            message = parts[2]

            # Apply colors to each part
            # Timestamp: Cyan (or White)
            timestamp_colored = f"{Fore.CYAN}{timestamp}{Style.RESET_ALL}"

            # Level: Based on level (Green for INFO, Red for ERROR, etc.)
            level_colored = f"{level_color}{level}{Style.RESET_ALL}"

            # Message: Based on component (White for Orchestrator, etc.)
            message_colored = f"{component_color}{message}{Style.RESET_ALL}"

            return f"{timestamp_colored} | {level_colored} | {message_colored}"
        else:
            # Fallback for unexpected formats
            return f"{level_color}{formatted_message}{Style.RESET_ALL}"


# Setup logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
))
logger = logging.getLogger('ORCHESTRATOR')
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Set watcher logger format
watcher_names = ['FILES', 'GMAIL', 'WHATSAPP', 'LINKEDIN']
for watcher_name in watcher_names:
    watcher_logger = logging.getLogger(watcher_name)
    watcher_logger.setLevel(logging.INFO)
    watcher_logger.handlers = []  # Remove existing handlers
    watcher_handler = logging.StreamHandler()

    watcher_handler.setFormatter(ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    ))
    watcher_logger.addHandler(watcher_handler)

# Set Claude logger format
claude_logger = logging.getLogger('CLAUDE')  # Different name to trigger color
claude_logger.setLevel(logging.INFO)
claude_logger.handlers = []  # Remove existing handlers
claude_handler = logging.StreamHandler()
claude_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)-8s | [Claude] %(message)s',
    datefmt='%H:%M:%S'
))
claude_logger.addHandler(claude_handler)

# Valid categories for subdirectories
VALID_CATEGORIES = ['email', 'whatsapp', 'linkedin', 'files']


class Orchestrator:
    """
    Main orchestrator for Silver Tier AI Employee.

    Coordinates:
    - All Watchers (Gmail, WhatsApp, LinkedIn, FileSystem)
    - Action detection (monitors /Needs_Action/** subdirectories)
    - Approval detection (monitors /Approved)
    - Rejection handling (monitors /Rejected)
    - Claude Code triggering (processes items)
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks for new items
        """
        self.vault_path = Path(vault_path).resolve()
        self.check_interval = check_interval

        # Main folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.archive = self.vault_path / 'Archive'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'

        # Category subdirectories in Needs_Action
        self.needs_action_categories = {
            cat: self.needs_action / cat for cat in VALID_CATEGORIES
        }

        # Ensure folders exist
        for folder in [self.inbox, self.needs_action, self.in_progress,
                       self.plans, self.pending_approval, self.approved,
                       self.rejected, self.archive, self.done, self.logs, self.briefings]:
            folder.mkdir(parents=True, exist_ok=True)

        # Ensure category subdirectories exist
        for cat_path in self.needs_action_categories.values():
            cat_path.mkdir(parents=True, exist_ok=True)

        # State
        self.running = False
        self.watcher_threads = {}
        self.processed_files: set = set()
        self.executed_approvals: set = set()
        self.handled_rejections: set = set()

        # Dashboard update scheduling (every 20 minutes)
        self.dashboard_update_interval = 1200  # 20 minutes in seconds
        self.last_dashboard_update = 0
        self.dashboard_update_in_progress = False  # Prevent concurrent updates

        # Load already processed files
        self._load_processed_files()

        logger.info(f"Orchestrator initialized (Silver Tier)")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Monitoring:")
        for cat, path in self.needs_action_categories.items():
            count = len(list(path.glob('*.md'))) if path.exists() else 0
            logger.info(f"    - /Needs_Action/{cat}/ ({count} files)")
        logger.info(f"    - /Approved (human approved)")
        logger.info(f"    - /Rejected (human rejected)")

    def _load_processed_files(self):
        """Load already processed files from /Done folder."""
        if self.done.exists():
            for f in self.done.glob('*.md'):
                self.processed_files.add(f.name)
            logger.info(f"Loaded {len(self.processed_files)} previously processed files")

    def start_watcher(self, watcher_type: str):
        """
        Start a specific watcher in a separate process to avoid module lock issues.

        Args:
            watcher_type: Type of watcher ('filesystem', 'gmail', 'whatsapp', 'linkedin')
        """
        import subprocess
        import sys
        import os

        # Map watcher types to their module names
        watcher_map = {
            'filesystem': 'file',
            'gmail': 'gmail',
            'whatsapp': 'whatsapp',
            'linkedin': 'linkedin',
        }

        if watcher_type in watcher_map:
            # Use subprocess instead of thread to avoid module lock issues
            os.environ['PYTHONUNBUFFERED'] = '1'  # Ensure output is not buffered

            process = subprocess.Popen([
                sys.executable, '-m', 'watchers',
                '--watcher', watcher_map[watcher_type],
                '--vault-path', str(self.vault_path)
            ], cwd=str(self.vault_path.parent))

            # Store process reference instead of thread
            self.watcher_threads[watcher_type] = process
            logger.info(f"{watcher_type.capitalize()} watcher started as subprocess PID: {process.pid}")

    def start_all_watchers(self):
        """Start all available watchers."""
        logger.info("Starting all watchers...")
        self.start_watcher('filesystem')
        # Other watchers will be started when their modules are available
        self.start_watcher('gmail')
        self.start_watcher('whatsapp')
        self.start_watcher('linkedin')

    def get_pending_items(self) -> dict:
        """
        Get list of pending items in all /Needs_Action subdirectories.

        Returns:
            Dict with category as key and list of Path objects as value
        """
        items_by_category = {}
        for category, cat_path in self.needs_action_categories.items():
            items = []
            if cat_path.exists():
                for f in cat_path.glob('*.md'):
                    if f.name not in self.processed_files:
                        items.append(f)
            if items:
                items_by_category[category] = items
        return items_by_category

    def get_approved_items(self) -> list:
        """Get list of approved items in /Approved (including category subfolders)."""
        items = []
        # Search in root /Approved/ folder
        for f in self.approved.glob('*.md'):
            if f.name not in self.executed_approvals:
                items.append(f)
        
        # Also search in category subfolders (/Approved/email/, /Approved/whatsapp/, etc.)
        for category in VALID_CATEGORIES:
            category_path = self.approved / category
            if category_path.exists():
                for f in category_path.glob('*.md'):
                    if f.name not in self.executed_approvals:
                        items.append(f)
        
        return items

    def get_rejected_items(self) -> list:
        """Get list of rejected items in /Rejected (including category subfolders, excluding already processed ones)."""
        items = []
        # Search in root /Rejected/ folder
        for f in self.rejected.glob('*.md'):
            # Skip files that already have REJECTED_ prefix (already processed)
            if f.name.startswith('REJECTED_'):
                continue
            # Skip files we've already handled
            if f.name not in self.handled_rejections:
                items.append(f)
        
        # Also search in category subfolders (/Rejected/email/, /Rejected/whatsapp/, etc.)
        for category in VALID_CATEGORIES:
            category_path = self.rejected / category
            if category_path.exists():
                for f in category_path.glob('*.md'):
                    # Skip files that already have REJECTED_ prefix (already processed)
                    if f.name.startswith('REJECTED_'):
                        continue
                    # Skip files we've already handled
                    if f.name not in self.handled_rejections:
                        items.append(f)
        
        return items

    def trigger_claude_process(self, items_by_category: dict) -> bool:
        """
        Trigger Claude Code to process items from /Needs_Action subdirectories.

        Args:
            items_by_category: Dict with category as key and list of Path objects as value

        Returns:
            True if successful, False otherwise
        """
        if not items_by_category:
            return True

        # Flatten items for tracking
        all_items = []
        for items in items_by_category.values():
            all_items.extend(items)

        # Build category summary
        category_summary = []
        for category, items in items_by_category.items():
            category_summary.append(f"  /Needs_Action/{category}/: {len(items)} files")
            for item in items:
                category_summary.append(f"    - {item.name}")

        logger.info(f"Triggering Claude Code to process {len(all_items)} items:")
        logger.info(f"Categories:")
        for cat, items in items_by_category.items():
            logger.info(f"  {cat}: {len(items)} files")

        # Build prompt for Claude
        prompt = f"""Process the following files in /Needs_Action subdirectories:

Categories and files:
{chr(10).join(category_summary)}

IMPORTANT: Always print your actions in real-time. Use this format:
- [SKILL] Using skill: /skill-name
- [READ] Reading: filename
- [WRITE] Writing: filename
- [MOVE] Moving: source -> destination
- [DONE] Completed: action description

Instructions:
1. Use /process-inbox skill to begin workflow
2. Read Company_Handbook.md for rules and folder structure
3. For each file in /Needs_Action/{{category}}/:
   a. [MOVE] Move to /In_Progress (claim ownership)
   b. [WRITE] Create Plan.md in /Plans folder
   c. [READ] Read original file from /Archive if needed
   d. Determine if sensitive:
      - ROUTINE: Execute action, move to /Done
      - SENSITIVE: Create approval request in /Pending_Approval
4. [SKILL] Use /update-dashboard skill to update Dashboard.md with results.
   IMPORTANT: Use local system time for all timestamps in the dashboard.

CRITICAL: Always explicitly mention when you are using a skill by including the skill name in your output."""

        return self._run_claude(prompt, all_items, self.processed_files)

    def execute_approved_directly(self, items: list) -> bool:
        """
        Execute approved actions directly without spawning Claude.

        This bypasses the Claude session limitation by executing MCP tools directly
        from the orchestrator process.

        Args:
            items: List of Path objects (approved items)

        Returns:
            True if successful, False otherwise
        """
        if not items:
            return True

        import json
        import re

        logger.info(f"Executing {len(items)} approved actions directly (no Claude spawn)...")

        for item in items:
            try:
                # Read approval request file
                approval_content = item.read_text(encoding='utf-8', errors='replace')

                # Extract action type and details
                action_type = None
                if 'email_send' in approval_content or 'type: email' in approval_content:
                    action_type = 'email'
                elif 'whatsapp' in approval_content.lower():
                    action_type = 'whatsapp'
                elif 'linkedin' in approval_content.lower():
                    action_type = 'linkedin'

                if action_type == 'email':
                    # Extract email details from approval request
                    to_match = re.search(r'- To:\s*([^\n]+)', approval_content)
                    subject_match = re.search(r'- Subject:\s*([^\n]+)', approval_content)
                    body_match = re.search(r'- Body:\s*([\s\S]*?)(?=\n-|\n##|\Z)', approval_content)

                    if to_match and subject_match and body_match:
                        to = to_match.group(1).strip()
                        subject = subject_match.group(1).strip()
                        body = body_match.group(1).strip()

                        logger.info(f"[EMAIL] Sending to: {to}")
                        logger.info(f"[EMAIL] Subject: {subject}")

                        # Import and use email service directly
                        try:
                            from mcp_server.email_service import EmailService
                            import asyncio

                            # Initialize email service without passing unexpected arguments
                            email_service = EmailService(str(self.vault_path))

                            # Run the async email sending function
                            result = asyncio.run(email_service.send_email(to=to, subject=subject, body=body))

                            if result.get('success'):
                                logger.info(f"[EMAIL] ✓ Email sent successfully to {to}")

                                # Move files to Done
                                category = item.parent.name
                                done_path = self.vault_path / 'Done' / category / item.name
                                done_path.parent.mkdir(parents=True, exist_ok=True)
                                item.rename(done_path)
                                logger.info(f"[MOVE] Moved approval to /Done/{category}/")

                                # Move In_Progress file to Archive
                                in_progress_path = self.vault_path / 'In_Progress' / category
                                if in_progress_path.exists():
                                    for f in in_progress_path.glob('*.md'):
                                        archive_path = self.vault_path / 'Archive' / category / f.name
                                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                                        f.rename(archive_path)
                                        logger.info(f"[MOVE] Moved original to /Archive/{category}/")

                                self.executed_approvals.add(item.name)
                            else:
                                logger.error(f"[EMAIL] ✗ Failed to send email: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            logger.error(f"[EMAIL] ✗ Error sending email: {str(e)}")

                elif action_type == 'whatsapp':
                    # Extract WhatsApp details from approval request
                    # Try format: **Recipient:** or | **Recipient** |
                    contact_match = re.search(r'\*\*Recipient:\*\*\s*([^\n]+)', approval_content)
                    if not contact_match:
                        contact_match = re.search(r'\|\s*\*\*Recipient\*\*\s*\|\s*([^\n]+)', approval_content)

                    # Extract message content between **Message Content:** and next section
                    message_match = re.search(r'\*\*Message Content:\*\*([\s\S]*?)(?=\n---|\n##|\Z)', approval_content)

                    if contact_match and message_match:
                        contact = contact_match.group(1).strip()
                        message = message_match.group(1).strip()

                        # Logic check: Verify if we should process this or wait for watcher
                        # Since we want the watcher to handle it, we just log and skip file movement
                        # The watcher will move the file after successful sending

                        # Only log once per file to avoid spamming console
                        if item.name not in self.executed_approvals:
                            logger.info(f"[WHATSAPP] Approved message detected for: {contact}")
                            logger.info(f"[WHATSAPP] Delegating to WhatsApp Watcher for sending...")
                            # Mark as 'seen' so we don't log repeatedly, but DON'T move it
                            # The watcher will move it, which will remove it from the list naturally
                            self.executed_approvals.add(item.name)

                    else:
                        logger.warning(f"[WHATSAPP] Could not extract contact or message from approval request")

                elif action_type == 'linkedin':
                    # Extract LinkedIn post details from approval request
                    # Look for post content between markers or in Content section
                    content_match = re.search(r'\*\*Content:\*\*([\s\S]*?)(?=\n---|\n##|\Z)', approval_content)

                    if not content_match:
                        # Try alternative pattern for post content
                        content_match = re.search(r'🤖([\s\S]*?)(?=\n---|\n##|\Z)', approval_content)

                    visibility_match = re.search(r'\*\*Visibility:\*\*\s*(\w+)', approval_content)

                    if content_match:
                        post_text = content_match.group(1).strip() if content_match.group(1).startswith('**') else f"🤖{content_match.group(1).strip()}"
                        visibility = visibility_match.group(1).strip() if visibility_match else "PUBLIC"

                        logger.info(f"[LINKEDIN] Posting to LinkedIn (Visibility: {visibility})")
                        logger.info(f"[LINKEDIN] Post length: {len(post_text)} characters")

                        # Import and use LinkedIn service directly
                        try:
                            from mcp_server.linkedin_service import LinkedInService
                            import asyncio

                            # Initialize LinkedIn service
                            linkedin_service = LinkedInService()

                            # Run the async LinkedIn posting function
                            result = asyncio.run(linkedin_service.post_share(text=post_text, visibility=visibility))

                            if result.get('success'):
                                logger.info(f"[LINKEDIN] ✓ Post created successfully (Post ID: {result.get('post_id', 'N/A')})")

                                # Move files to Done
                                category = item.parent.name
                                done_path = self.vault_path / 'Done' / category / item.name
                                done_path.parent.mkdir(parents=True, exist_ok=True)
                                item.rename(done_path)
                                logger.info(f"[MOVE] Moved approval to /Done/{category}/")

                                # Move In_Progress file to Archive
                                in_progress_path = self.vault_path / 'In_Progress' / category
                                if in_progress_path.exists():
                                    for f in in_progress_path.glob('*.md'):
                                        archive_path = self.vault_path / 'Archive' / category / f.name
                                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                                        f.rename(archive_path)
                                        logger.info(f"[MOVE] Moved original to /Archive/{category}/")

                                self.executed_approvals.add(item.name)
                            else:
                                logger.error(f"[LINKEDIN] ✗ Failed to post: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            logger.error(f"[LINKEDIN] ✗ Error posting to LinkedIn: {str(e)}")
                    else:
                        logger.warning(f"[LINKEDIN] Could not extract post content from approval request")

            except Exception as e:
                logger.error(f"Error executing approved action {item.name}: {str(e)}")

        return True

    def trigger_claude_execute_approved(self, items: list) -> bool:
        """
        Trigger Claude Code to execute approved actions.

        Args:
            items: List of Path objects (approved items)

        Returns:
            True if successful, False otherwise
        """
        # Use direct execution instead of spawning Claude
        return self.execute_approved_directly(items)

    def handle_rejected(self, items: list):
        """
        Handle rejected items - find and delete associated action file, keep rejection file in /Rejected.

        Args:
            items: List of Path objects (rejected items)
        """
        for item in items:
            logger.info(f"Handling rejected item: {item.name}")

            # 1. Parse the rejection file to find the associated action file
            action_file_name = None
            action_file_path = None
            try:
                content = item.read_text(encoding='utf-8', errors='replace')
                import re
                patterns = [
                    r"Action File:\s*([^\s\n\r]+)",
                    r"\*\*Action File:\*\*\s*/[^/]+/([^\s\n\r]+)",
                    r"action_file:\s*([^\s\n\r]+)",
                ]

                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        action_file_name = match.group(1).strip()
                        action_file_name = action_file_name.replace('`', '')
                        break
            except Exception as e:
                logger.warning(f"Could not parse rejection file for associated action file: {e}")

            # 2. Find and delete the associated action file
            if action_file_name:
                # Search in all possible folders
                search_folders = [self.pending_approval, self.in_progress,
                                  self.approved] + list(self.needs_action_categories.values())
                found = False
                for folder in search_folders:
                    potential_path = folder / action_file_name
                    if potential_path.exists():
                        action_file_path = potential_path
                        try:
                            potential_path.unlink()
                            logger.info(f"Deleted associated action file: {action_file_name} from {folder.name}")
                            found = True
                            break
                        except Exception as e:
                            logger.error(f"Failed to delete associated action file: {e}")

                if not found:
                    logger.debug(f"Associated action file {action_file_name} not found in common folders")

            # 3. Update rejection file with action file details and add REJECTED_ prefix
            try:
                content = item.read_text(encoding='utf-8', errors='replace')
                audit_info = f"\n\n---\n\n## Rejection Audit\n"
                audit_info += f"- **Rejected At:** {datetime.now().isoformat()}\n"
                audit_info += f"- **Rejected By:** Human\n"
                if action_file_name:
                    audit_info += f"- **Associated Action File:** {action_file_name} (deleted)\n"
                    if action_file_path:
                        audit_info += f"- **Action File Location:** {action_file_path.parent.name}/{action_file_name}\n"
                audit_info += f"- **Status:** Archived in /Rejected folder\n"

                updated_content = content + audit_info
                item.write_text(updated_content, encoding='utf-8')

                new_name = f"REJECTED_{item.name}"
                new_path = self.rejected / new_name
                item.rename(new_path)

                self.handled_rejections.add(item.name)
                self.handled_rejections.add(new_name)
                logger.info(f"Updated and renamed rejection file: {new_name}")

            except Exception as e:
                logger.error(f"Failed to update rejection file: {e}")

    def generate_briefing(self):
        """Generate Weekly CEO Briefing."""
        logger.info("Generating Weekly CEO Briefing...")

        # Create briefings folder if not exists
        self.briefings.mkdir(parents=True, exist_ok=True)

        prompt = f"""Generate a Weekly CEO Briefing for the AI Employee system.

1. Read Business_Goals.md for objectives and metrics
2. Analyze tasks in /Done folder from the past week
3. Check for bottlenecks (tasks that stayed in /In_Progress too long)
4. Review pending items in /Needs_Action, /Pending_Approval
5. Create briefing file in /Briefings folder with name format: YYYY-MM-DD_Monday_Briefing.md

Briefing should include:
- Executive Summary (2-3 sentences)
- Revenue Summary (if financial data available)
- Completed Tasks (from /Done)
- Bottlenecks Identified
- Proactive Suggestions (unused subscriptions, optimization opportunities)
- Pending Items Count
- Upcoming Deadlines (from Business_Goals.md)

Use local system time for all timestamps.
Format as clean Markdown with proper headers and tables where appropriate."""

        try:
            process = subprocess.Popen(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                bufsize=1,
                universal_newlines=True
            )

            stdout, stderr = process.communicate(timeout=180)

            if process.returncode == 0:
                logger.info("Weekly CEO Briefing generated successfully")
                logger.info(f"Check /Briefings folder for the report")
                return True
            else:
                logger.warning(f"Failed to generate briefing: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to generate briefing: {e}")
            return False

    def update_dashboard(self):
        """Trigger Claude to update the dashboard."""
        prompt = """Update the Dashboard.md file with current system state.

Use the /update-dashboard skill to:
1. Count items in all folders (including /Needs_Action subdirectories)
2. Update statistics
3. Update queue distribution by category
4. Update recent activity
5. Update folder inventory

IMPORTANT: Use local system time for all timestamps in the dashboard, NOT UTC.
Make sure all counts are accurate and reflect the current state of the system.

Count files in each /Needs_Action subdirectory:
- /Needs_Action/email/
- /Needs_Action/whatsapp/
- /Needs_Action/linkedin/
- /Needs_Action/files/"""

        try:
            process = subprocess.Popen(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                bufsize=1,
                universal_newlines=True
            )

            stdout, stderr = process.communicate(timeout=300)

            if process.returncode == 0:
                logger.debug("Dashboard update completed")
                return True
            else:
                logger.warning(f"Dashboard update failed with return code {process.returncode}")
                if stderr:
                    logger.warning(f"Error output: {stderr}")
                if stdout:
                    logger.debug(f"Stdout output: {stdout}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("Dashboard update timed out after 5 minutes - will retry next cycle")
            process.kill()
            return False
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            return False

    def update_dashboard_async(self):
        """Update dashboard in background without blocking orchestrator."""
        def run_update():
            try:
                # Check if an update is already in progress
                if self.dashboard_update_in_progress:
                    logger.debug("Dashboard update already in progress, skipping this update")
                    return

                # Mark that an update is in progress
                self.dashboard_update_in_progress = True
                try:
                    self.update_dashboard()
                finally:
                    # Always mark the update as finished
                    self.dashboard_update_in_progress = False
            except Exception as e:
                logger.error(f"Background dashboard update failed: {e}")
                # Still mark as finished even if there's an exception
                self.dashboard_update_in_progress = False

        # Run dashboard update in a separate thread to avoid blocking
        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()

    def trigger_claude_dashboard_update(self):
        """Trigger Claude to update dashboard via /update-dashboard skill (scheduled every 10 minutes)."""
        claude_logger = logging.getLogger('CLAUDE')

        # Check if an update is already in progress
        if self.dashboard_update_in_progress:
            claude_logger.warning("Dashboard update already in progress, skipping scheduled update")
            return False

        # Mark that an update is in progress
        self.dashboard_update_in_progress = True

        prompt = """Update the Dashboard.md file with current system state using the /update-dashboard skill.

Use the /update-dashboard skill to:
1. Count items in all folders (including /Needs_Action subdirectories)
2. Update statistics and performance metrics
3. Update queue distribution by category
4. Update recent activity log
5. Update folder inventory
6. Refresh all timestamps to local system time

IMPORTANT: Use local system time for all timestamps in the dashboard, NOT UTC.
Make sure all counts are accurate and reflect the current state of the system.

Count files in each /Needs_Action subdirectory:
- /Needs_Action/email/
- /Needs_Action/whatsapp/
- /Needs_Action/linkedin/
- /Needs_Action/files/

This is a scheduled update (every 10 minutes) to keep the dashboard fresh."""

        try:
            process = subprocess.Popen(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                bufsize=1,
                universal_newlines=True
            )

            claude_logger.info("Starting scheduled dashboard update...")
            claude_logger.info("-" * 56)

            # Stream stdout in real-time
            for line in process.stdout:
                line = line.rstrip()
                if not line:
                    continue

                line_lower = line.lower()

                if '/update-dashboard' in line or 'skill' in line_lower:
                    claude_logger.info(">>> SKILL: " + line)
                elif '[read]' in line_lower:
                    claude_logger.info(">>> READ: " + line)
                elif '[write]' in line_lower:
                    claude_logger.info(">>> WRITE: " + line)
                elif 'dashboard' in line_lower and ('updated' in line_lower or 'update' in line_lower):
                    claude_logger.info(">>> STATUS: " + line)
                else:
                    claude_logger.info(line)

            process.wait()

            if process.returncode == 0:
                claude_logger.info("-" * 56)
                claude_logger.info("Scheduled dashboard update completed successfully")
                return True
            else:
                stderr = process.stderr.read() if process.stderr else ""
                claude_logger.error("Dashboard update FAILED: " + stderr)
                return False

        except subprocess.TimeoutExpired:
            claude_logger.warning("Scheduled dashboard update timed out after 5 minutes - will retry next cycle")
            process.kill()
            return False
        except FileNotFoundError:
            claude_logger.error("Claude not found. Make sure 'claude' is in PATH")
            return False
        except Exception as e:
            claude_logger.error("Dashboard update error: " + str(e))
            return False
        finally:
            # Always mark the update as finished
            self.dashboard_update_in_progress = False

    def _run_claude(self, prompt: str, items: list, tracked_set: set) -> bool:
        """Run Claude Code with given prompt - streams output in real-time."""
        claude_logger = logging.getLogger('CLAUDE')

        try:
            process = subprocess.Popen(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                bufsize=1,
                universal_newlines=True
            )
            claude_logger.info("Starting execution...")
            claude_logger.info("-" * 56)

            # Stream stdout in real-time
            for line in process.stdout:
                line = line.rstrip()
                if not line:
                    continue

                line_lower = line.lower()

                if '[skill]' in line_lower:
                    claude_logger.info(">>> SKILL: " + line)
                elif '/process-inbox' in line or '/update-dashboard' in line:
                    skill_name = '/process-inbox' if '/process-inbox' in line else '/update-dashboard'
                    claude_logger.info(f">>> SKILL USED: {skill_name} - " + line)
                elif 'skill' in line_lower and ('using' in line_lower or 'invoke' in line_lower or 'call' in line_lower):
                    claude_logger.info(">>> SKILL: " + line)
                elif '[read]' in line_lower:
                    claude_logger.info(">>> READ: " + line)
                elif '[write]' in line_lower:
                    claude_logger.info(">>> WRITE: " + line)
                elif '[move]' in line_lower:
                    claude_logger.info(">>> MOVE: " + line)
                elif '[done]' in line_lower:
                    claude_logger.info(">>> DONE: " + line)
                elif 'reading' in line_lower and ('file' in line_lower or '.md' in line_lower or '.txt' in line_lower):
                    claude_logger.info(">>> READ: " + line)
                elif 'writing' in line_lower or 'creating' in line_lower and ('file' in line_lower or '.md' in line_lower):
                    claude_logger.info(">>> WRITE: " + line)
                elif 'moving' in line_lower or 'moved' in line_lower:
                    claude_logger.info(">>> MOVE: " + line)
                elif 'done' in line_lower or 'complete' in line_lower:
                    claude_logger.info(">>> STATUS: " + line)
                else:
                    claude_logger.info(line)

            process.wait()

            if process.returncode == 0:
                claude_logger.info("-" * 56)
                claude_logger.info("Execution completed successfully")

                for item in items:
                    tracked_set.add(item.name)

                return True
            else:
                stderr = process.stderr.read() if process.stderr else ""
                claude_logger.error("FAILED: " + stderr)
                return False

        except subprocess.TimeoutExpired:
            claude_logger.error("Timed out after 5 minutes")
            return False
        except FileNotFoundError:
            claude_logger.error("Not found. Make sure 'claude' is in PATH")
            return False
        except Exception as e:
            claude_logger.error("Error: " + str(e))
            return False

    def run(self):
        """Main orchestrator loop."""
        self.running = True

        # Start all watchers
        self.start_all_watchers()

        logger.info("=" * 60)
        logger.info("ORCHESTRATOR STARTED (Silver Tier)")
        logger.info("=" * 60)
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        try:
            cycle = 0
            current_time = time.time()
            self.last_dashboard_update = current_time

            while self.running:
                cycle += 1
                current_time = time.time()

                # 1. Check for new items in /Needs_Action subdirectories
                pending_items = self.get_pending_items()
                if pending_items:
                    total_items = sum(len(items) for items in pending_items.values())
                    logger.info("-" * 60)
                    logger.info(f"[CYCLE {cycle}] PROCESSING {total_items} TASK(S)")
                    logger.info("-" * 60)
                    for cat, items in pending_items.items():
                        logger.info(f"  /Needs_Action/{cat}/:")
                        for item in items:
                            logger.info(f"    -> {item.name}")
                    logger.info("Handing over to Claude Code...")
                    logger.info("-" * 60)

                    success = self.trigger_claude_process(pending_items)

                    logger.info("-" * 60)
                    if success:
                        logger.info("Claude Code COMPLETED - Control returned to Orchestrator")
                    else:
                        logger.warning("Claude Code FAILED - Will retry in 30s")
                    logger.info("-" * 60)

                    if not success:
                        time.sleep(30)
                        continue

                # 2. Check for approved items in /Approved
                approved_items = self.get_approved_items()
                if approved_items:
                    logger.info("-" * 60)
                    logger.info(f"[CYCLE {cycle}] EXECUTING {len(approved_items)} APPROVED ACTION(S)")
                    logger.info("-" * 60)
                    success = self.trigger_claude_execute_approved(approved_items)
                    if success:
                        logger.info("Approved actions EXECUTED - Control returned to Orchestrator")
                    else:
                        logger.warning("Execution FAILED - Will retry in 30s")
                        time.sleep(30)
                        continue

                # 3. Check for rejected items in /Rejected
                rejected_items = self.get_rejected_items()
                if rejected_items:
                    logger.info("-" * 60)
                    logger.info(f"[CYCLE {cycle}] ARCHIVING {len(rejected_items)} REJECTED ITEM(S)")
                    logger.info("-" * 60)
                    self.handle_rejected(rejected_items)
                    logger.info("Rejected items archived")

                    logger.info("Updating dashboard after rejection handling...")
                    self.update_dashboard()
                    logger.info("Dashboard updated")

                # 4. Check if 10 minutes have passed for scheduled dashboard update
                time_since_last_update = current_time - self.last_dashboard_update
                if time_since_last_update >= self.dashboard_update_interval:
                    logger.info("-" * 60)
                    logger.info(f"[CYCLE {cycle}] SCHEDULED DASHBOARD UPDATE (every 10 minutes)")
                    logger.info("-" * 60)
                    logger.info("Triggering Claude to update dashboard via /update-dashboard skill...")
                    self.trigger_claude_dashboard_update()
                    self.last_dashboard_update = current_time
                    logger.info("-" * 60)
                else:
                    # Show status when idle
                    # Update dashboard after each cycle to reflect current state (non-blocking)
                    logger.info("Updating dashboard in background...")
                    self.update_dashboard_async()

                # Show status when idle
                if not pending_items and not approved_items and not rejected_items:
                    time_until_next_update = self.dashboard_update_interval - time_since_last_update
                    logger.info(f"[CYCLE {cycle}] Idle - No pending tasks. Next check in {self.check_interval}s...")
                    logger.info(f"  Next scheduled dashboard update in {int(time_until_next_update)}s")

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("=" * 60)
            logger.info("ORCHESTRATOR STOPPED by user")
            logger.info("=" * 60)
            self.running = False

    def stop(self):
        """Stop the orchestrator and all watcher processes."""
        self.running = False

        # Terminate all watcher processes
        for watcher_type, process in self.watcher_threads.items():
            try:
                if hasattr(process, 'terminate'):  # It's a subprocess
                    process.terminate()
                    try:
                        process.wait(timeout=5)  # Wait up to 5 seconds
                    except subprocess.TimeoutExpired:
                        process.kill()  # Force kill if it doesn't terminate
                    logger.info(f"{watcher_type.capitalize()} watcher stopped")
                else:  # It's a thread (fallback)
                    # Thread stopping is not directly supported
                    logger.info(f"{watcher_type.capitalize()} watcher (thread) termination not supported")
            except Exception as e:
                logger.error(f"Error stopping {watcher_type} watcher: {e}")


def show_status(vault_path: str):
    """Show system status."""
    vault = Path(vault_path)

    print("\n" + "=" * 50)
    print("Personal AI Employee - Silver Tier Status")
    print("=" * 50)

    # Check vault exists
    if vault.exists():
        print(f"\n[OK] Vault: {vault.resolve()}")
    else:
        print(f"\n[ERROR] Vault not found: {vault.resolve()}")
        return

    # Count items in folders
    folders = {
        'Inbox': vault / 'Inbox',
        'Needs_Action': vault / 'Needs_Action',
        'In_Progress': vault / 'In_Progress',
        'Plans': vault / 'Plans',
        'Pending_Approval': vault / 'Pending_Approval',
        'Approved': vault / 'Approved',
        'Rejected': vault / 'Rejected',
        'Archive': vault / 'Archive',
        'Done': vault / 'Done',
        'Briefings': vault / 'Briefings',
        'Logs': vault / 'Logs',
    }

    print("\nFolder Counts:")
    for name, folder in folders.items():
        if folder.exists():
            count = len(list(folder.glob('*.md')))
            print(f"  /{name}: {count} files")
        else:
            print(f"  /{name}: (not found)")

    # Count items in Needs_Action subdirectories
    print("\nNeeds_Action by Category:")
    needs_action = vault / 'Needs_Action'
    if needs_action.exists():
        for cat in VALID_CATEGORIES:
            cat_path = needs_action / cat
            if cat_path.exists():
                count = len(list(cat_path.glob('*.md')))
                print(f"  /{cat}: {count} files")
            else:
                print(f"  /{cat}: (not found)")

    # Check for Dashboard
    dashboard = vault / 'Dashboard.md'
    if dashboard.exists():
        print(f"\n[OK] Dashboard.md exists")
    else:
        print(f"\n[ERROR] Dashboard.md not found")

    # Check for Company_Handbook
    handbook = vault / 'Company_Handbook.md'
    if handbook.exists():
        print(f"[OK] Company_Handbook.md exists")
    else:
        print(f"[ERROR] Company_Handbook.md not found")

    # Check Claude Code
    if shutil.which('claude'):
        print(f"[OK] Claude Code is available")
    else:
        print(f"[ERROR] Claude Code not found in PATH")

    print("\n" + "=" * 50 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator - Silver Tier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    (default)       Start full orchestrator (all watchers + auto Claude triggers)
    --status        Show system status
    --briefing      Generate Weekly CEO Briefing
    --vault-only    Print vault path only

The orchestrator monitors:
    - /Needs_Action/{email,whatsapp,linkedin,files}/: New tasks by category
    - /Approved: Human-approved actions to execute
    - /Rejected: Human-rejected items to archive

Usage:
    python -m orchestrator                      # Full autonomous mode
    python -m orchestrator --check-interval 5   # Custom check interval
    python -m orchestrator --status             # Check system status
    python -m orchestrator --briefing           # Generate CEO briefing
        """
    )

    parser.add_argument(
        '--vault-path',
        type=str,
        default='./AI_Employee_Vault_FTE',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=60,
        help='Seconds between checks for new items (default: 60)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
    )
    parser.add_argument(
        '--briefing',
        action='store_true',
        help='Generate Weekly CEO Briefing and exit'
    )
    parser.add_argument(
        '--vault-only',
        action='store_true',
        help='Print vault path and exit'
    )

    args = parser.parse_args()

    if args.status:
        show_status(args.vault_path)
    elif args.vault_only:
        print(f"Vault path: {Path(args.vault_path).resolve()}")
    elif args.briefing:
        orchestrator = Orchestrator(vault_path=args.vault_path)
        orchestrator.generate_briefing()
    else:
        orchestrator = Orchestrator(
            vault_path=args.vault_path,
            check_interval=args.check_interval
        )
        orchestrator.run()


if __name__ == '__main__':
    main()
