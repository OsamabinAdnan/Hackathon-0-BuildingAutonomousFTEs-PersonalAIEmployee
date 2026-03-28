"""
Base Watcher - Abstract base class for all watchers.

All watchers follow this pattern:
1. Check for updates at specified interval
2. Create action files in /Needs_Action folder
3. Handle errors gracefully
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

from colorama import init as colorama_init, Fore, Style

# Initialize colorama
colorama_init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


# Setup logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations."""

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the base watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.

        Returns:
            List of new items detected
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create an action file in the Needs_Action folder.

        Args:
            item: The item to create an action file for

        Returns:
            Path to the created action file
        """
        pass

    def run(self):
        """Main loop - continuously check for updates."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')

        while True:
            try:
                items = self.check_for_updates()
                if items:
                    self.logger.info(f'Found {len(items)} new items')
                for item in items:
                    action_file = self.create_action_file(item)
                    self.logger.info(f'Created action file: {action_file.name}')
            except Exception as e:
                self.logger.error(f'Error in check cycle: {e}')

            time.sleep(self.check_interval)

    def _create_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Create YAML frontmatter for action files.

        Args:
            item_type: Type of the item (email, file_drop, etc.)
            **kwargs: Additional frontmatter fields

        Returns:
            Formatted YAML frontmatter string
        """
        lines = ['---']
        lines.append(f'type: {item_type}')
        lines.append(f'created: {datetime.now().isoformat()}')
        lines.append('status: pending')

        for key, value in kwargs.items():
            lines.append(f'{key}: {value}')

        lines.append('---')
        return '\n'.join(lines)
