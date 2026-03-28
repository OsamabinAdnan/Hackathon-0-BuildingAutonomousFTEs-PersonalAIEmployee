"""
Allow running watchers as a module: python -m watchers

This runs the FileSystem Watcher only (manual Claude triggering mode).
"""

import argparse
from .filesystem_watcher import FileSystemWatcher


def main():
    """Main entry point for watchers module."""
    parser = argparse.ArgumentParser(
        description='FileSystem Watcher - Monitors /Inbox folder'
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
