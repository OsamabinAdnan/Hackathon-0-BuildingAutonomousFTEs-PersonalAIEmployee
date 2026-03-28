"""
Allow running watchers as a module: python -m watchers

Silver Tier: Supports running all watchers or individual ones.

Usage:
    python -m watchers                  # All watchers (default)
    python -m watchers --watcher file   # FileSystem watcher only
    python -m watchers --watcher gmail  # Gmail watcher only
    python -m watchers --watcher whatsapp  # WhatsApp watcher only
    python -m watchers --watcher linkedin  # LinkedIn watcher only
"""

import argparse
import logging
import sys
import threading
from pathlib import Path
from colorama import init as colorama_init, Fore, Style

# Initialize colorama
colorama_init()

# Suppress Google API discovery cache warning
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

# Setup colored formatter BEFORE importing watchers
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    COMPONENT_COLORS = {
        'FILES': Fore.YELLOW,  # Gold color
        'GMAIL': Fore.LIGHTMAGENTA_EX,
        'WHATSAPP': Fore.LIGHTGREEN_EX,
        'LINKEDIN': Fore.LIGHTBLUE_EX,
    }

    def format(self, record):
        level_color = self.COLORS.get(record.levelno, Fore.WHITE)
        component_color = self.COMPONENT_COLORS.get(record.name, Fore.WHITE)

        # Format the message
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

            # Message: Based on component (Pink for Gmail, etc.)
            message_colored = f"{component_color}{message}{Style.RESET_ALL}"

            return f"{timestamp_colored} | {level_colored} | {message_colored}"
        else:
            # Fallback for unexpected formats
            return f"{component_color}{formatted_message}{Style.RESET_ALL}"

# Configure root logger with colored formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter(
    '%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s',
    datefmt='%H:%M:%S'
))

# Set up logging for all watcher loggers
for logger_name in ['FILES', 'GMAIL', 'WHATSAPP', 'LINKEDIN']:
    watcher_logger = logging.getLogger(logger_name)
    watcher_logger.setLevel(logging.INFO)
    watcher_logger.handlers = []  # Clear any existing handlers
    watcher_logger.addHandler(console_handler)
    watcher_logger.propagate = False  # Don't propagate to root logger

# Also set up root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = []
root_logger.addHandler(console_handler)

logger = logging.getLogger('watchers')


def run_filesystem_watcher(vault_path: str):
    """Run FileSystem watcher."""
    from .filesystem_watcher import FileSystemWatcher
    watcher = FileSystemWatcher(vault_path=vault_path)
    watcher.run()


def run_gmail_watcher(vault_path: str):
    """Run Gmail watcher."""
    try:
        from .gmail_watcher import GmailWatcher
        watcher = GmailWatcher(vault_path=vault_path)
        watcher.run()
    except ImportError as e:
        logger.error(f'Gmail watcher not available: {e}')
        logger.error('Install with: pip install google-api-python-client google-auth-oauthlib')


def run_whatsapp_watcher(vault_path: str):
    """Run WhatsApp watcher."""
    try:
        from .whatsapp_watcher import WhatsAppWatcher
        watcher = WhatsAppWatcher(vault_path=vault_path)
        watcher.run()
    except ImportError as e:
        logger.error(f'WhatsApp watcher not available: {e}')
        logger.error('Install with: pip install playwright && playwright install chromium')


def run_linkedin_watcher(vault_path: str):
    """Run LinkedIn watcher."""
    try:
        from .linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=vault_path)
        watcher.run()
    except ImportError as e:
        logger.error(f'LinkedIn watcher not available: {e}')


def run_all_watchers(vault_path: str):
    """Run all watchers in separate threads."""
    logger.info("=" * 50)
    logger.info("Starting All Watchers (Silver Tier)")
    logger.info("=" * 50)

    watcher_funcs = {
        'filesystem': run_filesystem_watcher,
        'gmail': run_gmail_watcher,
        'whatsapp': run_whatsapp_watcher,
        'linkedin': run_linkedin_watcher,
    }

    threads = []
    for name, func in watcher_funcs.items():
        logger.info(f"Starting {name} watcher...")
        thread = threading.Thread(target=func, args=(vault_path,), daemon=True, name=f'{name}_watcher')
        thread.start()
        threads.append(thread)

    logger.info("=" * 50)
    logger.info("All watchers started. Press Ctrl+C to stop.")
    logger.info("=" * 50)

    try:
        # Keep main thread alive
        while True:
            for thread in threads:
                if not thread.is_alive():
                    logger.warning(f"Watcher thread died: {thread.name}")
            import time
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Stopping all watchers...")


def main():
    """Main entry point for watchers module."""
    parser = argparse.ArgumentParser(
        description='AI Employee Watchers - Monitor various sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Watchers:
    file        FileSystem watcher (monitors /Inbox)
    gmail       Gmail API watcher (monitors emails)
    whatsapp    WhatsApp Web watcher (monitors messages)
    linkedin    LinkedIn API watcher (monitors notifications)
    all         Run all watchers (default)

Examples:
    python -m watchers                      # All watchers
    python -m watchers --watcher file       # FileSystem only
    python -m watchers --watcher gmail      # Gmail only
    python -m watchers --watcher whatsapp   # WhatsApp only
        """
    )
    parser.add_argument(
        '--vault-path',
        type=str,
        default='./AI_Employee_Vault_FTE',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--watcher',
        type=str,
        default='all',
        choices=['all', 'file', 'gmail', 'whatsapp', 'linkedin'],
        help='Which watcher to run (default: all)'
    )

    args = parser.parse_args()

    # Map watcher names to functions
    watcher_map = {
        'all': run_all_watchers,
        'file': run_filesystem_watcher,
        'gmail': run_gmail_watcher,
        'whatsapp': run_whatsapp_watcher,
        'linkedin': run_linkedin_watcher,
    }

    # Run selected watcher
    watcher_func = watcher_map.get(args.watcher)
    if watcher_func:
        watcher_func(args.vault_path)
    else:
        logger.error(f"Unknown watcher: {args.watcher}")
        sys.exit(1)


if __name__ == '__main__':
    main()
