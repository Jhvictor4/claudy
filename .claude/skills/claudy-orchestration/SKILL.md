---
name: claudy-orchestration
description: Use this skill when delegating to sub-agents that require more flexibility than the Task tool provides - when launching multiple agents in parallel, managing persistent sessions across calls, or coordinating complex multi-agent workflows with custom orchestration patterns.
---

# Claudy Orchestration

Multi-agent session manager for Claude Code. Spawn and manage persistent Claude agent sessions with automatic cleanup.

## Quick Start

### Installation

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "claudy": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/kangjihyeok/claude-agentic-skills.git@main#subdirectory=claudy",
        "fastmcp",
        "run",
        "claudy.mcp_server:mcp"
      ]
    }
  }
}
```

### CLI Usage

```bash
# Start the server (required first step)
uvx claudy server start

# Call an agent session
uvx claudy call <name> "<message>" [--verbosity quiet|normal|verbose]

# List all sessions
uvx claudy list

# Get session status
uvx claudy status <name>

# Cleanup sessions
uvx claudy cleanup <name>
uvx claudy cleanup --all

# Stop the server
uvx claudy server stop
```

## MCP Tools

### `claudy_call`

Send a message to an agent session (auto-creates if doesn't exist).

**Parameters:**
- `name` (str): Session name
- `message` (str): Message to send
- `verbosity` (str): "quiet", "normal", or "verbose" (default: "normal")
- `fork` (bool): Fork before sending (default: false)
- `fork_name` (str, optional): Name for forked session
- `parent_session_id` (str, optional): Parent to inherit from (auto-detected)

**Returns:** `{"success": true, "name": "...", "response": "...", "session_id": "..."}`

### `claudy_call_async`

Start agent task in background, returns immediately for parallel execution.

**Parameters:**
- `name` (str): Session name
- `message` (str): Message to send
- `verbosity` (str): "quiet", "normal", or "verbose" (default: "normal")
- `parent_session_id` (str, optional): Parent to inherit from

**Returns:** `{"success": true, "name": "...", "status": "running"}`

### `claudy_get_results`

Wait for and aggregate results from multiple background agents (blocking until complete).

**Parameters:**
- `names` (list[str]): List of session names to wait for
- `timeout` (int, optional): Timeout in seconds

**Returns:** `{"success": true, "results": {"name1": {...}, "name2": {...}}}`

### `claudy_check_status`

Check if background tasks are still running.

**Parameters:**
- `names` (list[str], optional): Session names to check (if None, checks all)

**Returns:** `{"success": true, "tasks": {"name1": "running", "name2": "completed"}}`

### `claudy_list`

List all active agent sessions.

**Returns:** `{"success": true, "sessions": [...]}`

### `claudy_status`

Get detailed status of a specific session.

**Parameters:**
- `name` (str): Session name

**Returns:** Session metadata (created_at, last_used, message_count, etc.)

### `claudy_cleanup`

Cleanup one or all sessions.

**Parameters:**
- `name` (str, optional): Session name to cleanup
- `all` (bool): Cleanup all sessions (default: false)

**Returns:** `{"success": true, "message": "..."}`

## Usage Patterns

### Basic Session Management

```
# Auto-create and call a session
Use claudy_call with name="researcher" and message="Search for latest AI papers"

# Check status
Use claudy_status with name="researcher"

# Cleanup
Use claudy_cleanup with name="researcher"
```

### Context Preservation

```
1. claudy_call(name="memory_test", message="Remember this number: 42")
2. claudy_call(name="memory_test", message="What number did I ask you to remember?")
   → "42" ✓ Context preserved!
```

### Session Forking

```
# Create base session
claudy_call(name="analysis", message="Analyze this codebase")

# Fork to explore alternatives
claudy_call(
    name="analysis",
    message="Try refactoring approach B",
    fork=True,
    fork_name="analysis_fork_b"
)

# Original session unchanged
claudy_call(name="analysis", message="Continue with approach A")
```

### Parallel Execution

```
# Launch multiple agents in parallel
claudy_call_async('security', 'Audit code for vulnerabilities')
claudy_call_async('performance', 'Find performance bottlenecks')
claudy_call_async('docs', 'Generate API documentation')

# Collect all results
claudy_get_results(['security', 'performance', 'docs'])
```

## Key Features

- **MCP Native**: Built with FastMCP for seamless Claude Code integration
- **Context Preservation**: Agents remember full conversation history
- **Session Forking**: Branch conversations to explore alternative paths
- **Auto Cleanup**: 20-minute idle timeout prevents resource leaks
- **Permission Inheritance**: Auto-created sessions bypass permissions
- **Parallel Execution**: Run multiple agents concurrently with `claudy_call_async`
- **Zero Configuration**: Works out of the box with uvx

## Configuration

Sessions auto-cleanup after 20 minutes of inactivity. To customize:

Edit `claudy/config.py`:
```python
SESSION_IDLE_TIMEOUT = 1200  # 20 minutes in seconds
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes
```

## Architecture

```
Claude Code MCP Client
    ↓ (MCP stdio)
FastMCP Server
    ↓
ClaudeSDKClient Sessions (in-memory)
    └─ Auto cleanup (20min idle timeout)
```

**Design:**
- Single process (no HTTP server in MCP mode)
- Global session storage (shared across all MCP connections)
- Background TTL cleanup task
- Auto-detection of current Claude session ID for permission inheritance

## Important Notes

### Server Start Required

For CLI usage, you **must** start the server first:

```bash
uvx claudy server start
```

Then you can use `call`, `list`, `status`, `cleanup` commands. The server will **NOT** auto-start.

### Session Persistence

Sessions are **in-memory only**. They are lost when:
- Server stops
- Session idle for 20+ minutes
- Manual cleanup via `claudy_cleanup`

### MCP vs CLI Mode

- **MCP mode** (recommended): Direct stdio, used by Claude Code
- **CLI mode**: HTTP server, requires `claudy server start`

Both modes share the same session storage when running.

## Troubleshooting

### "Server is not running"

Run `uvx claudy server start` before using CLI commands.

### Sessions disappearing

Sessions cleanup after 20 minutes of inactivity. Use them regularly or reduce `SESSION_IDLE_TIMEOUT`.

### Fork fails

Ensure parent session has sent at least one message (session_id must exist).

## Requirements

- Python 3.10+
- Claude Code 2.0+ (for claude-agent-sdk)
- fastmcp >= 2.12.0
- claude-agent-sdk >= 0.1.4

## License

MIT License

---

**Built with ❤️ using [FastMCP](https://github.com/jlowin/fastmcp) and [claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk-python)**
