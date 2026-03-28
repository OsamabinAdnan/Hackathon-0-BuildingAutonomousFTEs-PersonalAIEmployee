"""
Base Watcher - Abstract base class for all watchers.

All watchers follow this pattern:
1. Check for updates at specified interval
2. Create action files in /Needs_Action/{category}/ folder
3. Handle errors gracefully

Silver Tier: Supports categorized action files in subdirectories.
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

    # Valid categories for subdirectories
    VALID_CATEGORIES = {'email', 'whatsapp', 'linkedin', 'files'}

    def __init__(self, vault_path: str, check_interval: int = 60, category: str = 'files'):
        """
        Initialize the base watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
            category: Category subdirectory for action files (default: 'files')
                      Must be one of: 'email', 'whatsapp', 'linkedin', 'files'
        """
        self.vault_path = Path(vault_path)
        self.category = category.lower() if category else 'files'

        # Validate category
        if self.category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {self.VALID_CATEGORIES}")

        # Set up categorized needs_action folder
        self.needs_action = self.vault_path / 'Needs_Action' / self.category
        self.check_interval = check_interval

        # Setup logger with category in name
        self.logger = logging.getLogger(f'watchers.{self.category}')
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
        Create an action file in the Needs_Action/{category} folder.

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
        self.logger.info(f'Category: {self.category}')
        self.logger.info(f'Output: /Needs_Action/{self.category}/')
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
            item_type: Type of the item (email, whatsapp, linkedin, file_drop, etc.)
            **kwargs: Additional frontmatter fields

        Returns:
            Formatted YAML frontmatter string
        """
        lines = ['---']
        lines.append(f'type: {item_type}')
        lines.append(f'category: {self.category}')
        lines.append(f'created: {datetime.now().isoformat()}')
        lines.append('status: pending')

        for key, value in kwargs.items():
            # Escape special characters in values
            if isinstance(value, str):
                value = value.replace('"', '\\"')
            lines.append(f'{key}: {value}')

        lines.append('---')
        return '\n'.join(lines)

    def get_action_filename(self, prefix: str, identifier: str) -> str:
        """
        Generate a unique action filename.

        Args:
            prefix: Prefix for the filename (e.g., 'EMAIL', 'WHATSAPP', 'LINKEDIN')
            identifier: Unique identifier for the item

        Returns:
            Formatted filename with timestamp
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Clean identifier for use in filename
        safe_id = ''.join(c if c.isalnum() or c in '-_' else '_' for c in str(identifier))[:50]
        return f'{prefix}_{timestamp}_{safe_id}.md'
