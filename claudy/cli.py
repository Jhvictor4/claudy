#!/usr/bin/env python3
"""CLI for Claudy - Universal Claude agent manager."""

import argparse
import json
import os
import subprocess
import sys
import time

import asyncio
from fastmcp import Client

from .config import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    VERBOSITY_QUIET,
    VERBOSITY_NORMAL,
    VERBOSITY_VERBOSE,
    get_server_pid,
    get_server_port,
    save_server_pid,
    save_server_port,
    clear_server_info,
)


def is_server_running():
    """Check if the HTTP server is running."""
    port = get_server_port()
    pid = get_server_pid()

    if not port or not pid:
        return False

    # Check if process is alive
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
        return True
    except (OSError, ProcessLookupError):
        # Process doesn't exist, clean up stale files
        clear_server_info()
        return False


def start_server():
    """Start the FastMCP HTTP server in the background using uv run."""
    # Get the path to mcp_server.py
    import pathlib
    mcp_server_path = pathlib.Path(__file__).parent / "mcp_server.py"

    # Start server using uv run fastmcp
    process = subprocess.Popen(
        [
            "uv",
            "run",
            "fastmcp",
            "run",
            f"{mcp_server_path}:mcp",
            "--transport",
            "http",
            "--port",
            str(DEFAULT_PORT),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Save PID and PORT
    save_server_pid(process.pid)
    save_server_port(DEFAULT_PORT)

    # Give it a moment to initialize
    time.sleep(2)

    # Check if it's running - try to connect with FastMCP Client
    try:
        async def check_health():
            client = Client(f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/mcp")
            async with client:
                # Try to list tools as a health check
                await client.list_tools()
                return True

        return asyncio.run(check_health())
    except Exception:
        return False


def ensure_server_running():
    """Ensure the server is running, start it if needed."""
    if not is_server_running():
        if not start_server():
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": "Failed to start server",
                        "error_code": "SERVER_START_ERROR",
                    },
                    ensure_ascii=False,
                )
            )
            sys.exit(1)


def stop_server():
    """Stop the agent server."""
    pid = get_server_pid()

    if not pid:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "Server is not running",
                    "error_code": "SERVER_NOT_RUNNING",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    try:
        os.kill(pid, 15)  # SIGTERM
        time.sleep(0.5)  # Give it time to shutdown gracefully

        # Check if it's still running
        try:
            os.kill(pid, 0)
            # Still running, force kill
            os.kill(pid, 9)  # SIGKILL
        except (OSError, ProcessLookupError):
            pass  # Already dead

        clear_server_info()
        print(json.dumps({"success": True, "message": "Server stopped"}, ensure_ascii=False))

    except (OSError, ProcessLookupError):
        clear_server_info()
        print(json.dumps({"success": True, "message": "Server was not running"}, ensure_ascii=False))


def call_tool(tool_name: str, params: dict) -> dict:
    """Call a FastMCP tool via FastMCP Client."""
    port = get_server_port() or DEFAULT_PORT

    async def _call():
        try:
            client = Client(f"http://{DEFAULT_HOST}:{port}/mcp")
            async with client:
                result = await client.call_tool(tool_name, params)
                # FastMCP tools return JSON strings, need to parse
                return json.loads(result.data)

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "error_code": "JSON_ERROR",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "UNKNOWN_ERROR",
            }

    return asyncio.run(_call())


def print_output(result: dict, verbosity: str = VERBOSITY_NORMAL):
    """Print output based on verbosity level and result type."""
    if not result.get("success"):
        # Always print errors as JSON
        print(json.dumps(result, ensure_ascii=False))
        return

    # For successful operations, format based on verbosity
    if verbosity == VERBOSITY_QUIET:
        # Only print the response text
        if "response" in result:
            print(result["response"])
    else:
        # Print full JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claudy - Universal Claude agent manager (FastMCP-based)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="claudy 0.1.0",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Call command
    call_parser = subparsers.add_parser(
        "call", help="Send a message to an agent session (auto-creates if doesn't exist)"
    )
    call_parser.add_argument("name", help="Session name")
    call_parser.add_argument("message", help="Message to send")
    call_parser.add_argument(
        "--quiet", action="store_true", help="Only show final response"
    )
    call_parser.add_argument(
        "--verbose", action="store_true", help="Show everything including thinking"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all active sessions")

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Get status of a specific session"
    )
    status_parser.add_argument("name", help="Session name")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup one or all sessions")
    cleanup_parser.add_argument("name", nargs="?", help="Session name")
    cleanup_parser.add_argument("--all", action="store_true", help="Cleanup all sessions")

    # Server management commands
    server_parser = subparsers.add_parser("server", help="Manage the HTTP server")
    server_parser.add_argument(
        "action",
        choices=["start", "stop", "status", "restart"],
        help="Server action",
    )

    # MCP server command (for MCP integration)
    mcp_parser = subparsers.add_parser("mcp", help="Start MCP server (for Claude Code)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle MCP command (stdio mode)
    if args.command == "mcp":
        from .mcp_server import mcp
        mcp.run()
        return

    # Handle server management commands
    if args.command == "server":
        if args.action == "start":
            if is_server_running():
                print(
                    json.dumps(
                        {"success": True, "message": "Server is already running"},
                        ensure_ascii=False,
                    )
                )
            else:
                if start_server():
                    print(json.dumps({"success": True, "message": "Server started"}, ensure_ascii=False))
                else:
                    print(
                        json.dumps(
                            {"success": False, "error": "Failed to start server"},
                            ensure_ascii=False,
                        )
                    )
                    sys.exit(1)
        elif args.action == "stop":
            stop_server()
        elif args.action == "status":
            if is_server_running():
                port = get_server_port()
                pid = get_server_pid()
                print(
                    json.dumps(
                        {"success": True, "running": True, "port": port, "pid": pid},
                        ensure_ascii=False,
                    )
                )
            else:
                print(json.dumps({"success": True, "running": False}, ensure_ascii=False))
        elif args.action == "restart":
            if is_server_running():
                stop_server()
                time.sleep(1)
            if start_server():
                print(json.dumps({"success": True, "message": "Server restarted"}, ensure_ascii=False))
            else:
                print(
                    json.dumps(
                        {"success": False, "error": "Failed to restart server"},
                        ensure_ascii=False,
                    )
                )
                sys.exit(1)
        sys.exit(0)

    # For all other commands, ensure server is running
    ensure_server_running()

    # Execute command
    try:
        if args.command == "call":
            verbosity = (
                VERBOSITY_QUIET
                if args.quiet
                else (VERBOSITY_VERBOSE if args.verbose else VERBOSITY_NORMAL)
            )
            result = call_tool(
                "claudy_call",
                {
                    "name": args.name,
                    "message": args.message,
                    "verbosity": verbosity,
                },
            )
            print_output(result, verbosity)

        elif args.command == "list":
            result = call_tool("claudy_list", {})
            print_output(result)

        elif args.command == "status":
            result = call_tool("claudy_status", {"name": args.name})
            print_output(result)

        elif args.command == "cleanup":
            if args.all:
                result = call_tool("claudy_cleanup", {"all": True})
            elif args.name:
                result = call_tool("claudy_cleanup", {"name": args.name})
            else:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Either provide a session name or use --all",
                        },
                        ensure_ascii=False,
                    )
                )
                sys.exit(1)
            print_output(result)

        # Exit with appropriate code
        sys.exit(0 if result.get("success") else 1)

    except KeyboardInterrupt:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "Interrupted by user",
                    "error_code": "INTERRUPTED",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)
    except Exception as e:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": str(e),
                    "error_code": "UNKNOWN_ERROR",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
