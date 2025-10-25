#!/usr/bin/env python3
"""stdio-to-HTTP proxy for MCP integration."""

import asyncio
import json
import sys

from fastmcp import Client

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


async def _handle_stdio_loop(client: Client):
    """Handle stdio loop with connected client."""
    # MCP stdio protocol: read JSON-RPC from stdin, write to stdout
    while True:
        try:
            # Read line from stdin
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )

            if not line:
                break  # EOF

            # Parse JSON-RPC request
            request = json.loads(line.strip())

            # Handle different MCP methods
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            try:
                if method == "initialize":
                    # MCP initialization
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": "claudy",
                                "version": "0.1.0"
                            }
                        }
                    }

                elif method == "tools/list":
                    # List tools from HTTP server
                    tools = await client.list_tools()
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "inputSchema": tool.inputSchema
                                }
                                for tool in tools
                            ]
                        }
                    }

                elif method == "tools/call":
                    # Forward tool call to HTTP server
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})

                    result = await client.call_tool(tool_name, tool_args)

                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result.data
                                }
                            ]
                        }
                    }

                else:
                    # Unknown method
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }

            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }

            # Write response to stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            # Invalid JSON, write error
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            # Other errors
            sys.stderr.write(f"Error in stdio proxy: {str(e)}\n")
            sys.stderr.flush()
            break


async def run_stdio_proxy():
    """Run stdio MCP server that forwards to HTTP daemon."""
    # Connect to HTTP daemon (with retries)
    max_retries = 5
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            client = Client(f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/mcp")
            # Try to connect
            async with client:
                # Successfully connected, handle stdio loop
                await _handle_stdio_loop(client)
                return
        except Exception as e:
            if attempt < max_retries - 1:
                sys.stderr.write(f"Connection attempt {attempt + 1} failed, retrying in {retry_delay}s...\n")
                sys.stderr.flush()
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                sys.stderr.write(f"Failed to connect to HTTP daemon after {max_retries} attempts: {e}\n")
                sys.exit(1)


def main():
    """Entry point for stdio proxy."""
    asyncio.run(run_stdio_proxy())


if __name__ == "__main__":
    main()
