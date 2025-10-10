"""
Command-line interface for ScaleBox Python SDK
"""

import argparse
import asyncio
import sys
from typing import Optional

from . import __version__
from .code_interpreter import Sandbox, AsyncSandbox
from .connection_config import ConnectionConfig


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="scalebox",
        description="ScaleBox Python SDK - Multi-language code execution sandbox",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"ScaleBox Python SDK {__version__}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Sandbox command
    sandbox_parser = subparsers.add_parser("sandbox", help="Sandbox operations")
    sandbox_parser.add_argument("--create", action="store_true", help="Create a new sandbox")
    sandbox_parser.add_argument("--list", action="store_true", help="List sandboxes")
    sandbox_parser.add_argument("--destroy", help="Destroy a sandbox by ID")
    
    # Code execution command
    exec_parser = subparsers.add_parser("exec", help="Execute code")
    exec_parser.add_argument("--code", required=True, help="Code to execute")
    exec_parser.add_argument("--language", default="python", help="Programming language")
    exec_parser.add_argument("--sandbox-id", help="Sandbox ID to use")
    exec_parser.add_argument("--async", action="store_true", help="Use async execution")
    
    # Configuration
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--domain", help="API domain")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    return parser


async def async_main():
    """Async main function."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create connection config
    config = ConnectionConfig(
        api_key=args.api_key,
        domain=args.domain,
        debug=args.debug,
    )
    
    if args.command == "sandbox":
        if args.create:
            print("Creating sandbox...")
            if args.async:
                sandbox = await AsyncSandbox.create()
                print(f"Created async sandbox: {sandbox.id}")
            else:
                sandbox = Sandbox.create()
                print(f"Created sandbox: {sandbox.id}")
        elif args.list:
            print("Listing sandboxes...")
            # TODO: Implement sandbox listing
            print("Sandbox listing not implemented yet")
        elif args.destroy:
            print(f"Destroying sandbox: {args.destroy}")
            # TODO: Implement sandbox destruction
            print("Sandbox destruction not implemented yet")
    
    elif args.command == "exec":
        print(f"Executing {args.language} code...")
        print(f"Code: {args.code}")
        
        if args.async:
            sandbox = await AsyncSandbox.create()
            try:
                result = await sandbox.run_code(args.code, language=args.language)
                print(f"Result: {result.logs.stdout}")
            finally:
                await sandbox.close()
        else:
            sandbox = Sandbox.create()
            try:
                result = sandbox.run_code(args.code, language=args.language)
                print(f"Result: {result.logs.stdout}")
            finally:
                sandbox.close()


def main():
    """Main entry point."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
