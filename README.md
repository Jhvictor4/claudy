# Claudy

Multi-agent orchestration for Claude Code. A thin wrapper around claude-agent-sdk for easy multi-task launching.

[![PyPI](https://img.shields.io/pypi/v/claudy)](https://pypi.org/project/claudy/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Why?

Claude skills, plugins, and agent SDK made building multi-agent systems incredibly easy. But there was a gap:

- Claude can't easily orchestrate multiple agent launches by itself
- Existing orchestration tools felt too heavy for simple use cases
- I just wanted to run multiple agents in parallel and aggregate results

So I built this - a thin wrapper that lets Claude spawn and manage agent sessions through MCP tools. That's it.

## Installation

### Option 1: Claude Code Plugin (Recommended)

Install the complete plugin (includes both skill and MCP server):

```bash
# In Claude Code
Add plugin: https://github.com/Jhvictor4/claudy
```

This installs:
- **claudy-orchestration skill** - Automatic CLI integration
- **claudy MCP server** - Direct tool access

### Option 2: Skill Only

For CLI integration without MCP tools:

1. Download [`claudy-orchestration.zip`](./claudy-orchestration.zip)
2. In Claude Code, go to Skills → Install from file
3. Select the downloaded zip

### Option 3: MCP Server Only

For direct MCP tool access without skill, add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "claudy": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "claudy", "mcp"
      ]
    }
  }
}
```

Done. `uvx` handles the rest.

## CLI Usage

You can also use claudy from the command line:

```bash
# Call an agent
uvx claudy call researcher "Search for latest AI papers"

# List active sessions
uvx claudy list

# Check session status
uvx claudy status researcher

# Cleanup
uvx claudy cleanup researcher
# or cleanup all
uvx claudy cleanup --all

# Start HTTP server (for programmatic access)
uvx claudy server
```

Sessions persist across calls and auto-cleanup after 2 hours of inactivity.

## MCP Tools (for Claude)

When you install claudy as an MCP server, Claude gets these tools:

### Basic Operations

**`claudy_call(name, message, verbosity="normal")`**

Send a message to an agent. Auto-creates session if it doesn't exist.

```python
claudy_call(
    name="researcher",
    message="Find the latest papers on transformers"
)
# Returns: {"success": true, "response": {...}}
```

**`claudy_list()`**

List all active sessions.

**`claudy_status(name)`**

Get session details (created_at, last_used, message_count, etc).

**`claudy_cleanup(name=None, all=False)`**

Cleanup sessions.

### Parallel Execution

**`claudy_call_async(name, message)`**

Launch agent in background. Returns immediately.

```python
claudy_call_async(name="security", message="Audit auth.py")
claudy_call_async(name="performance", message="Profile database queries")
claudy_call_async(name="docs", message="Check documentation coverage")
```

**`claudy_get_results(names, timeout=None)`**

Wait for multiple agents and aggregate results.

```python
results = claudy_get_results(
    names=["security", "performance", "docs"],
    timeout=300
)
# Returns: {"success": true, "results": {"security": {...}, ...}}
```

**`claudy_check_status(names=None)`**

Check if background tasks are running.

```python
claudy_check_status(names=["security", "performance"])
# Returns: {"security": "running", "performance": "completed"}
```

### Session Forking

**`claudy_call(name, message, fork=True, fork_name="new_name")`**

Fork a session to explore alternative paths.

```python
# Base analysis
claudy_call(name="analysis", message="Analyze refactoring options")

# Fork to try different approach
claudy_call(
    name="analysis",
    message="Try microservices approach",
    fork=True,
    fork_name="analysis_microservices"
)

# Original continues independently
claudy_call(name="analysis", message="Continue with monolith optimization")
```

## Examples

### Parallel codebase analysis

```python
# Fan-out: launch 4 agents
claudy_call_async("security", "Audit for vulnerabilities")
claudy_call_async("perf", "Find performance bottlenecks")
claudy_call_async("arch", "Review architecture patterns")
claudy_call_async("deps", "Check outdated dependencies")

# Fan-in: aggregate results
results = claudy_get_results(
    ["security", "perf", "arch", "deps"],
    timeout=600
)
```

### Context preservation

```python
claudy_call("research", "Remember this number: 42")
claudy_call("research", "What number did I tell you?")
# → "42" ✓
```

### Exploring alternatives

```python
# Try multiple approaches in parallel
claudy_call_async("approach_a", "Use Redis for caching")
claudy_call_async("approach_b", "Use Memcached for caching")
claudy_call_async("approach_c", "Use in-memory dict for caching")

# Compare results
results = claudy_get_results(["approach_a", "approach_b", "approach_c"])
```

## How It Works

```
Claude Code
    ↓ MCP (stdio)
FastMCP Server
    ↓
ClaudeSDKClient sessions (in-memory)
    • Auto-cleanup after 2hr idle
    • Background async tasks
    • Session forking support
```

### Key Points

- **Single process**: FastMCP server manages everything
- **In-memory sessions**: Shared across all MCP connections
- **Auto-creation**: Sessions created on first call
- **Permission bypass**: Child agents inherit parent permissions (no spam prompts)
- **TTL cleanup**: Background task removes idle sessions every 5 minutes

### Session Auto-Creation

When you call a new session:

1. Detects current Claude session ID from `~/.claude/projects/`
2. Creates `ClaudeSDKClient` with `bypassPermissions=True`
3. Stores with metadata (created_at, last_used, message_count)

### Parallel Execution

```
claudy_call_async()
  → asyncio.create_task()
  → stored in _background_tasks[name]
  → returns immediately

claudy_get_results([names])
  → await asyncio.gather(*tasks)
  → returns aggregated results
```

## Configuration

Edit `claudy/mcp_server.py`:

```python
SESSION_IDLE_TIMEOUT = 7200  # 2 hours
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes
```

## Development

```bash
git clone https://github.com/kangjihyeok/claudy.git
cd claudy

# Install
uv pip install -e .

# Run MCP server
fastmcp dev claudy/mcp_server.py:mcp

# Run tests
pytest tests/
```

### Local Development in Claude Code

Use absolute path in `.mcp.json`:

```json
{
  "mcpServers": {
    "claudy": {
      "type": "stdio",
      "command": "fastmcp",
      "args": ["run", "/absolute/path/to/claudy/claudy/mcp_server.py:mcp"]
    }
  }
}
```

## Troubleshooting

**"canUseTool callback is not provided"**

This error shows up on claude.ai web. Use Claude Desktop instead - it has full MCP support for local servers.

**Sessions disappear**

Sessions are in-memory. They reset when:
- MCP server restarts
- 2-hour idle timeout
- Manual cleanup

This is intentional - sessions are for temporary task delegation.

**Parallel execution hangs**

1. Check status: `claudy_check_status()`
2. Add timeout: `claudy_get_results(names, timeout=300)`
3. Check MCP server logs

## Requirements

- Python 3.10+
- Claude Code 2.0+ (for MCP support)
- fastmcp >= 2.12.0
- claude-agent-sdk >= 0.1.4

## Contributing

PRs welcome. Keep it simple.

1. Fork
2. Create feature branch
3. Make changes
4. Submit PR

## License

MIT

## Built With

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk-python) - Official Claude agent SDK

---

Made by [@Jhvictor4](https://github.com/Jhvictor4)
