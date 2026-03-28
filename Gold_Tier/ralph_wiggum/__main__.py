"""
Allow running Ralph Wiggum loop as a module: python -m ralph_wiggum

Usage:
    python -m ralph_wiggum "Process all files in /Needs_Action"
    python -m ralph_wiggum "Process inbox" --max-iterations 15
    python -m ralph_wiggum "Generate briefing" --completion-file Briefings/latest.md
"""

import argparse
import logging
from . import start_ralph_loop

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ralph_wiggum')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Autonomous task completion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m ralph_wiggum "Process all files in /Needs_Action"
    python -m ralph_wiggum "Process inbox" --max-iterations 15
    python -m ralph_wiggum "Generate briefing" --completion-file Briefings/latest.md
        """
    )
    
    parser.add_argument(
        'prompt',
        type=str,
        help='Task prompt for Claude'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations (default: 10)'
    )
    
    parser.add_argument(
        '--vault-path',
        type=str,
        default='./AI_Employee_Vault_FTE',
        help='Path to Obsidian vault (default: ./AI_Employee_Vault_FTE)'
    )
    
    parser.add_argument(
        '--completion-file',
        type=str,
        default=None,
        help='Optional file to monitor for completion'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("RALPH WIGGUM LOOP")
    logger.info("=" * 60)
    logger.info(f"Prompt: {args.prompt[:100]}...")
    logger.info(f"Max iterations: {args.max_iterations}")
    logger.info(f"Vault path: {args.vault_path}")
    if args.completion_file:
        logger.info(f"Completion file: {args.completion_file}")
    logger.info("=" * 60)
    
    start_ralph_loop(
        prompt=args.prompt,
        max_iterations=args.max_iterations,
        vault_path=args.vault_path,
        completion_file=args.completion_file
    )


if __name__ == '__main__':
    main()
