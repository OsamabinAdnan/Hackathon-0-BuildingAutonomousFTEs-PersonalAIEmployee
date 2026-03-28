"""
Allow running MCP server as a module: python -m mcp_server

Usage:
    python -m mcp_server              # Run with stdio transport
    python -m mcp_server --http       # Run with HTTP transport
    python -m mcp_server --check      # Check service availability
"""

import argparse
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_server')


def check_services():
    """Check which services are available."""
    from .direct_executor import DirectExecutor

    executor = DirectExecutor()
    status = executor.check_services()

    print("\n" + "=" * 50)
    print("MCP Server - Service Status")
    print("=" * 50)

    for service, available in status.items():
        status_str = "[OK]" if available else "[NOT CONFIGURED]"
        print(f"  {service.capitalize()}: {status_str}")

    print("\n" + "=" * 50)

    if not all(status.values()):
        print("\nConfiguration tips:")
        if not status.get('email'):
            print("  Email: Run 'python -m watchers.gmail --setup-oauth'")
        if not status.get('linkedin'):
            print("  LinkedIn: Set LINKEDIN_ACCESS_TOKEN in .env")
        print("")

    return all(status.values())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AI Employee MCP Server - External action tools'
    )
    parser.add_argument(
        '--transport',
        type=str,
        default='stdio',
        choices=['stdio', 'http'],
        help='Transport type (default: stdio)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for HTTP transport (default: 8000)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check service availability and exit'
    )

    args = parser.parse_args()

    if args.check:
        success = check_services()
        sys.exit(0 if success else 1)

    # Run MCP server
    from .server import run_server
    run_server(transport=args.transport, port=args.port)


if __name__ == '__main__':
    main()
