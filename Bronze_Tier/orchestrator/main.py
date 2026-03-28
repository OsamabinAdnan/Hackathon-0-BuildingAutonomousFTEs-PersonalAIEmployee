"""
Orchestrator - Main controller for the Bronze Tier AI Employee.

This is the primary entry point. The orchestrator:
1. Starts the FileSystem Watcher (monitors /Inbox)
2. Monitors /Needs_Action for new action files
3. Monitors /Approved for human-approved actions
4. Monitors /Rejected for human-rejected actions
5. Triggers Claude Code to process items

Usage:
    python -m orchestrator                      # Full autonomous mode
    python -m orchestrator --check-interval 5   # Custom check interval
    python -m orchestrator --status             # Show system status
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
        'orchestrator': Fore.LIGHTBLUE_EX,
        'watchers': Fore.LIGHTYELLOW_EX,
        'claude': Fore.LIGHTCYAN_EX,
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)

        # Determine component color based on logger name
        component_color = Fore.WHITE  # Default
        for comp_name, comp_color in self.COMPONENT_COLORS.items():
            if comp_name in record.name.lower():
                component_color = comp_color
                break

        # Format the message with appropriate colors
        message = super().format(record)

        # Apply component color to the message part (excluding timestamp)
        parts = message.split(' | ', 2)  # Split on first two separators
        if len(parts) >= 3:
            timestamp_part = parts[0]
            level_part = parts[1]
            msg_part = parts[2]

            # Apply component color to message part
            colored_msg = f"{component_color}{msg_part}{Style.RESET_ALL}"
            message = f"{timestamp_part} | {level_part} | {colored_msg}"
        else:
            # If format doesn't match our expected pattern, apply component color to whole message
            message = f"{component_color}{message}{Style.RESET_ALL}"

        return f"{level_color}{message}{Style.RESET_ALL}"


# Setup logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Set watcher logger format
watcher_logger = logging.getLogger('watchers.filesystem')
watcher_logger.setLevel(logging.INFO)
watcher_logger.handlers = []  # Remove existing handlers
watcher_handler = logging.StreamHandler()
watcher_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)-8s | [Watcher] %(message)s',
    datefmt='%H:%M:%S'
))
watcher_logger.addHandler(watcher_handler)

# Set Claude logger format
claude_logger = logging.getLogger('claude')
claude_logger.setLevel(logging.INFO)
claude_logger.handlers = []  # Remove existing handlers
claude_handler = logging.StreamHandler()
claude_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)-8s | [Claude] %(message)s',
    datefmt='%H:%M:%S'
))
claude_logger.addHandler(claude_handler)


class Orchestrator:
    """
    Main orchestrator for Bronze Tier AI Employee.

    Coordinates:
    - FileSystem Watcher (monitors /Inbox)
    - Action detection (monitors /Needs_Action)
    - Approval detection (monitors /Approved)
    - Rejection handling (monitors /Rejected)
    - Claude Code triggering (processes items)
    """

    def __init__(self, vault_path: str, check_interval: int = 10):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks for new items
        """
        self.vault_path = Path(vault_path).resolve()
        self.check_interval = check_interval

        # Folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.archive = self.vault_path / 'Archive'
        self.done = self.vault_path / 'Done'

        # Ensure folders exist
        for folder in [self.inbox, self.needs_action, self.in_progress,
                       self.plans, self.pending_approval, self.approved,
                       self.rejected, self.archive, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # State
        self.running = False
        self.watcher_thread: Optional[threading.Thread] = None
        self.processed_files: set = set()
        self.executed_approvals: set = set()
        self.handled_rejections: set = set()

        # Load already processed files
        self._load_processed_files()

        logger.info(f"Orchestrator initialized")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Monitoring:")
        logger.info(f"    - /Needs_Action (new tasks)")
        logger.info(f"    - /Approved (human approved)")
        logger.info(f"    - /Rejected (human rejected)")

    def _load_processed_files(self):
        """Load already processed files from /Done folder."""
        if self.done.exists():
            for f in self.done.glob('*.md'):
                self.processed_files.add(f.name)
            logger.info(f"Loaded {len(self.processed_files)} previously processed files")

    def start_watcher(self):
        """Start the FileSystem Watcher in a separate thread."""
        from watchers.filesystem_watcher import FileSystemWatcher

        def run_watcher():
            try:
                watcher = FileSystemWatcher(vault_path=str(self.vault_path))
                watcher.run()
            except Exception as e:
                logger.error(f"Watcher error: {e}")

        self.watcher_thread = threading.Thread(target=run_watcher, daemon=True)
        self.watcher_thread.start()
        logger.info("FileSystem Watcher started")

    def get_pending_items(self) -> list:
        """Get list of pending items in /Needs_Action."""
        items = []
        for f in self.needs_action.glob('*.md'):
            if f.name not in self.processed_files:
                items.append(f)
        return items

    def get_approved_items(self) -> list:
        """Get list of approved items in /Approved."""
        items = []
        for f in self.approved.glob('*.md'):
            if f.name not in self.executed_approvals:
                items.append(f)
        return items

    def get_rejected_items(self) -> list:
        """Get list of rejected items in /Rejected (excluding already processed ones)."""
        items = []
        for f in self.rejected.glob('*.md'):
            # Skip files that already have REJECTED_ prefix (already processed)
            if f.name.startswith('REJECTED_'):
                continue
            # Skip files we've already handled
            if f.name not in self.handled_rejections:
                items.append(f)
        return items

    def trigger_claude_process(self, items: list) -> bool:
        """
        Trigger Claude Code to process items from /Needs_Action.

        Args:
            items: List of Path objects to process

        Returns:
            True if successful, False otherwise
        """
        if not items:
            return True

        item_names = [f.name for f in items]
        logger.info(f"Triggering Claude Code to process {len(items)} items:")
        for name in item_names:
            logger.info(f"  - {name}")

        # Build prompt for Claude
        prompt = f"""Process the following {len(items)} files in /Needs_Action folder:

Files to process:
{chr(10).join(f'- {name}' for name in item_names)}

IMPORTANT: Always print your actions in real-time. Use this format:
- [SKILL] Using skill: /skill-name
- [READ] Reading: filename
- [WRITE] Writing: filename
- [MOVE] Moving: source -> destination
- [DONE] Completed: action description

Instructions:
1. Use /process-inbox skill to begin workflow
2. Read Company_Handbook.md for rules and folder structure
3. For each file in /Needs_Action:
   a. [MOVE] Move to /In_Progress (claim ownership)
   b. [WRITE] Create Plan.md in /Plans folder
   c. [READ] Read original file from /Archive if needed
   d. Determine if sensitive:
      - ROUTINE: Execute action, move to /Done
      - SENSITIVE: Create approval request in /Pending_Approval
4. [SKILL] Use /update-dashboard skill to update Dashboard.md with results.
   IMPORTANT: Use local system time for all timestamps in the dashboard.

CRITICAL: Always explicitly mention when you are using a skill by including the skill name in your output. For example:
- Use "/process-inbox skill" when starting
- Use "/update-dashboard skill" when updating dashboard
- Use "/process-inbox" or "/update-dashboard" when invoking skills"""

        return self._run_claude(prompt, items, self.processed_files)

    def trigger_claude_execute_approved(self, items: list) -> bool:
        """
        Trigger Claude Code to execute approved actions.

        Args:
            items: List of Path objects (approved items)

        Returns:
            True if successful, False otherwise
        """
        if not items:
            return True

        item_names = [f.name for f in items]
        logger.info(f"Triggering Claude Code to execute {len(items)} approved items:")
        for name in item_names:
            logger.info(f"  - {name}")

        # Build prompt for Claude
        prompt = f"""Execute the following {len(items)} approved actions:

Approved files in /Approved:
{chr(10).join(f'- {name}' for name in item_names)}

Instructions:
1. For each file in /Approved:
   a. Read the approval request file
   b. Read the corresponding Plan.md from /Plans
   c. Execute the approved action
   d. Move approval file to /Done
   e. Move any related files from /Pending_Approval or /In_Progress to /Done
2. Update Dashboard.md with results. IMPORTANT: Use local system time for all timestamps.

These actions have been explicitly approved by human - proceed with execution."""

        return self._run_claude(prompt, items, self.executed_approvals)

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
                # Look for "Action File: FILE_..." or "**Action File:** /path/FILE_..." patterns
                # Try multiple patterns to catch different formats
                patterns = [
                    r"Action File:\s*([^\s\n\r]+)",  # Simple format
                    r"\*\*Action File:\*\*\s*/[^/]+/([^\s\n\r]+)",  # Markdown with path
                    r"action_file:\s*([^\s\n\r]+)",  # YAML frontmatter
                ]

                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        action_file_name = match.group(1).strip()
                        # Clean up backticks if present
                        action_file_name = action_file_name.replace('`', '')
                        break
            except Exception as e:
                logger.warning(f"Could not parse rejection file for associated action file: {e}")

            # 2. Find and delete the associated action file
            if action_file_name:
                # Search in folders where it might be
                search_folders = [self.pending_approval, self.in_progress, self.needs_action, self.approved]
                found = False
                for folder in search_folders:
                    potential_path = folder / action_file_name
                    if potential_path.exists():
                        action_file_path = potential_path
                        try:
                            # Delete the action file
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
                # Read current content
                content = item.read_text(encoding='utf-8', errors='replace')

                # Add audit information at the end
                audit_info = f"\n\n---\n\n## Rejection Audit\n"
                audit_info += f"- **Rejected At:** {datetime.now().isoformat()}\n"
                audit_info += f"- **Rejected By:** Human\n"
                if action_file_name:
                    audit_info += f"- **Associated Action File:** {action_file_name} (deleted)\n"
                    if action_file_path:
                        audit_info += f"- **Action File Location:** {action_file_path.parent.name}/{action_file_name}\n"
                audit_info += f"- **Status:** Archived in /Rejected folder\n"

                # Write updated content back
                updated_content = content + audit_info
                item.write_text(updated_content, encoding='utf-8')

                # Rename with REJECTED_ prefix
                new_name = f"REJECTED_{item.name}"
                new_path = self.rejected / new_name
                item.rename(new_path)

                # Mark both the original name and the new name as handled
                self.handled_rejections.add(item.name)
                self.handled_rejections.add(new_name)
                logger.info(f"Updated and renamed rejection file: {new_name}")

            except Exception as e:
                logger.error(f"Failed to update rejection file: {e}")

    def update_dashboard(self):
        """Trigger Claude to update the dashboard."""
        prompt = """Update the Dashboard.md file with current system state.

Use the /update-dashboard skill to:
1. Count items in all folders
2. Update statistics
3. Update queue distribution
4. Update recent activity
5. Update folder inventory

IMPORTANT: Use local system time for all timestamps in the dashboard, NOT UTC.
Make sure all counts are accurate and reflect the current state of the system."""

        try:
            # Get the dedicated logger for Claude output
            claude_logger = logging.getLogger('claude')

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

            # Just wait for completion, don't stream output
            stdout, stderr = process.communicate(timeout=120)

            if process.returncode == 0:
                logger.debug("Dashboard update completed")
                return True
            else:
                logger.warning(f"Dashboard update failed: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")
            return False

    def _run_claude(self, prompt: str, items: list, tracked_set: set) -> bool:
        """Run Claude Code with given prompt - streams output in real-time."""
        # Get the dedicated logger for Claude output
        claude_logger = logging.getLogger('claude')

        try:
            # Run Claude Code with streaming output
            # Use shell=True on Windows to find .cmd files
            # --dangerously-skip-permissions for autonomous operation within vault
            process = subprocess.Popen(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            claude_logger.info("(stdout/stderr now read with UTF-8/replacement decoding)")
            claude_logger.info("Starting execution...")
            claude_logger.info("-" * 56)

            claude_logger.info("Starting execution...")
            claude_logger.info("-" * 56)

            # Stream stdout in real-time
            for line in process.stdout:
                line = line.rstrip()
                if not line:
                    continue

                # Detect explicit tags from Claude output
                line_lower = line.lower()

                if '[skill]' in line_lower:
                    # Skill invocation
                    claude_logger.info(">>> SKILL: " + line)
                elif '/process-inbox' in line or '/update-dashboard' in line:
                    # Explicit skill names mentioned
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
                    # Regular output
                    claude_logger.info(line)

            process.wait()

            if process.returncode == 0:
                claude_logger.info("-" * 56)
                claude_logger.info("Execution completed successfully")

                # Mark items as processed
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

        # Start the FileSystem Watcher
        self.start_watcher()

        logger.info("=" * 60)
        logger.info("ORCHESTRATOR STARTED")
        logger.info("=" * 60)
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)

        try:
            cycle = 0
            while self.running:
                cycle += 1

                # 1. Check for new items in /Needs_Action
                pending_items = self.get_pending_items()
                if pending_items:
                    logger.info("-" * 60)
                    logger.info(f"[CYCLE {cycle}] PROCESSING {len(pending_items)} TASK(S)")
                    logger.info("-" * 60)
                    logger.info("Files to process:")
                    for item in pending_items:
                        logger.info(f"  -> {item.name}")
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

                    # Update dashboard after handling rejections
                    logger.info("Updating dashboard after rejection handling...")
                    self.update_dashboard()
                    logger.info("Dashboard updated")

                # Show status when idle
                if not pending_items and not approved_items and not rejected_items:
                    logger.info(f"[CYCLE {cycle}] Idle - No pending tasks. Next check in {self.check_interval}s...")

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("=" * 60)
            logger.info("ORCHESTRATOR STOPPED by user")
            logger.info("=" * 60)
            self.running = False

    def stop(self):
        """Stop the orchestrator."""
        self.running = False


def show_status(vault_path: str):
    """Show system status."""
    vault = Path(vault_path)

    print("\n" + "=" * 50)
    print("Personal AI Employee - Bronze Tier Status")
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
        'Done': vault / 'Done'
    }

    print("\nFolder Counts:")
    for name, folder in folders.items():
        if folder.exists():
            count = len(list(folder.glob('*.md')))
            print(f"  /{name}: {count} files")
        else:
            print(f"  /{name}: (not found)")

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
        description='AI Employee Orchestrator - Bronze Tier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    (default)       Start full orchestrator (watcher + auto Claude triggers)
    --status        Show system status
    --vault-only    Print vault path only

The orchestrator monitors:
    - /Needs_Action: New tasks to process
    - /Approved: Human-approved actions to execute
    - /Rejected: Human-rejected items to archive

Usage:
    python -m orchestrator                      # Full autonomous mode
    python -m orchestrator --check-interval 5   # Custom check interval
    python -m orchestrator --status             # Check system status
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
        default=10,
        help='Seconds between checks for new items (default: 10)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
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
    else:
        orchestrator = Orchestrator(
            vault_path=args.vault_path,
            check_interval=args.check_interval
        )
        orchestrator.run()


if __name__ == '__main__':
    main()
