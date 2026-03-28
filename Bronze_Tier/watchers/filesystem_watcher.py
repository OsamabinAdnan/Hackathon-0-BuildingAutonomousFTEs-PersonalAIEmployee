"""
File System Watcher - Monitors the /Inbox folder for new files.

This watcher uses the watchdog library to monitor the vault's /Inbox folder.
When a file is detected, it:
1. Creates an action file in /Needs_Action
2. Moves the original file to /Archive (to prevent re-detection)

Usage:
    python -m watchers --vault-path ./AI_Employee_Vault_FTE
"""

import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging - use specific logger name for hierarchy
logger = logging.getLogger('watchers.filesystem')


class InboxHandler(FileSystemEventHandler):
    """Handler for file system events in the /Inbox folder."""

    def __init__(self, vault_path: Path):
        """
        Initialize the handler.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = vault_path
        self.inbox = vault_path / 'Inbox'
        self.needs_action = vault_path / 'Needs_Action'
        self.archive = vault_path / 'Archive'

        # Ensure directories exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.archive.mkdir(parents=True, exist_ok=True)

        # Track processed files to avoid duplicates
        self.processed_files = set()

        logger.info(f'Handler initialized')
        logger.debug(f'  Inbox: {self.inbox}')
        logger.debug(f'  Needs_Action: {self.needs_action}')
        logger.debug(f'  Archive: {self.archive}')

    def on_created(self, event):
        """
        Handle file creation event.

        Args:
            event: File system event
        """
        if event.is_directory:
            logger.debug(f'Ignoring directory: {event.src_path}')
            return

        source = Path(event.src_path)
        logger.info(f'New file detected in /Inbox: {source.name}')

        # Create action file and archive
        self.process_file(source)

    def on_moved(self, event):
        """
        Handle file move event (for files moved into /Inbox).

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        dest = Path(event.dest_path)
        logger.info(f'File moved into /Inbox: {dest.name}')
        self.process_file(dest)

    def scan_existing_files(self):
        """Scan for existing files in /Inbox and process them."""
        if not self.inbox.exists():
            return

        # Get all files in Inbox (excluding directories and .md files)
        existing_files = [
            f for f in self.inbox.iterdir()
            if f.is_file() and not f.name.endswith('.md')
        ]

        if existing_files:
            logger.info(f'Found {len(existing_files)} existing file(s) in /Inbox')
            for f in existing_files:
                logger.debug(f'  - {f.name}')
                self.process_file(f)

    def process_file(self, source: Path):
        """
        Process a file: create action file and move to archive.

        Args:
            source: Path to the source file in /Inbox
        """
        # Skip if already processed (prevent duplicates)
        if source.name in self.processed_files:
            logger.debug(f'Skipping already processed file: {source.name}')
            return

        # Mark as processed
        self.processed_files.add(source.name)

        try:
            # Get file info
            file_size = source.stat().st_size
            file_ext = source.suffix.lower()

            # Create unique filename for action file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            action_filename = f'FILE_{timestamp}_{source.stem}.md'
            action_path = self.needs_action / action_filename

            # Create archive filename (with timestamp to avoid conflicts)
            archive_name = f'{timestamp}_{source.name}'
            archive_path = self.archive / archive_name

            # Create action file content
            content = f'''---
type: file_drop
original_name: {source.name}
archive_path: /Archive/{archive_name}
size_bytes: {file_size}
extension: {file_ext}
created: {datetime.now().isoformat()}
priority: medium
status: pending
---

# File Detected in /Inbox

## File Information
- **Original Name:** {source.name}
- **Size:** {self._format_size(file_size)}
- **Extension:** {file_ext}
- **Archived At:** /Archive/{archive_name}

## Suggested Actions
- [ ] Read the archived file
- [ ] Process according to file type
- [ ] Move to /Done when complete

## Notes
_Add any notes about this file here_
'''
            action_path.write_text(content, encoding='utf-8')
            logger.info(f'Created action file: {action_path.name}')

            # Move original file to archive
            shutil.move(str(source), str(archive_path))
            logger.info(f'Moved original to archive: {archive_path.name}')

        except Exception as e:
            logger.error(f'Failed to process {source.name}: {e}')

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'


class FileSystemWatcher:
    """
    File System Watcher using watchdog.

    Monitors the /Inbox folder for new files:
    - Creates action files in /Needs_Action
    - Moves original files to /Archive
    - Scans for existing files on startup
    """

    def __init__(self, vault_path: str):
        """
        Initialize the file system watcher.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.observer = Observer()
        self.handler = InboxHandler(self.vault_path)

        logger.info(f'Watching: {self.inbox}')
        logger.debug(f'Vault: {self.vault_path}')

    def start(self):
        """Start watching the /Inbox folder."""
        # Scan for existing files first
        self.handler.scan_existing_files()

        # Then start watching for new files
        self.observer.schedule(
            self.handler,
            str(self.inbox),
            recursive=False
        )
        self.observer.start()
        logger.info('Started')

    def stop(self):
        """Stop watching the folder."""
        self.observer.stop()
        self.observer.join()
        logger.info('File system watcher stopped')

    def run(self):
        """Run the watcher (blocking)."""
        self.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info('Stopping...')
            self.stop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee - Monitors /Inbox folder'
    )
    parser.add_argument(
        '--vault-path',
        type=str,
        default='./AI_Employee_Vault_FTE',
        help='Path to the Obsidian vault'
    )

    args = parser.parse_args()

    watcher = FileSystemWatcher(vault_path=args.vault_path)
    watcher.run()


if __name__ == '__main__':
    main()
