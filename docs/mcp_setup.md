# MCP Setup Guide

## What is MCP?

The Model Context Protocol (MCP) allows Claude Code to use Claudy as native tools and resources, providing seamless integration for managing agent sessions directly from Claude.

## Installation

First, install Claudy:

```bash
pip install claudy
```

## Claude Code Configuration

Add Claudy to your Claude Code MCP servers configuration:

**Location:** `~/.claude/config.json`

```json
{
  "mcpServers": {
    "claudy": {
      "command": "claudy",
      "args": ["mcp"]
    }
  }
}
```

## Verify Installation

1. Restart Claude Code
2. Claude should now have access to Claudy tools
3. Try asking: "Use the claudy_list tool to show active sessions"

## Available MCP Tools

### claudy_spawn

Spawn a new Claude agent session.

**Parameters:**
- `name` (required): Session name
- `tools` (optional): List of allowed tools
- `model` (optional): Model name override

**Example:**
```
Use claudy_spawn to create an analyzer agent
```

### claudy_call

Send a message to an agent session. Context is preserved!

**Parameters:**
- `name` (required): Session name
- `message` (required): Message to send
- `verbosity` (optional): "quiet", "normal", or "verbose"

**Example:**
```
Use claudy_call to ask the analyzer to find bugs in main.py
```

### claudy_list

List all active agent sessions.

**Example:**
```
Use claudy_list to show all active sessions
```

### claudy_status

Get detailed status of a specific session.

**Parameters:**
- `name` (required): Session name

**Example:**
```
Use claudy_status to check the analyzer session
```

### claudy_cleanup

Cleanup one or all agent sessions.

**Parameters:**
- `name` (optional): Session name
- `all` (optional): If true, cleanup all sessions

**Example:**
```
Use claudy_cleanup with all=true to remove all sessions
```

## Available MCP Resources

### claudy://sessions

List of all active Claudy agent sessions (JSON).

**Access:**
```
Read the claudy://sessions resource to see active agents
```

### claudy://server/status

Claudy HTTP server status and information (JSON).

**Access:**
```
Read the claudy://server/status resource to check server health
```

### claudy://session/{name}

Specific session status (JSON).

**Access:**
```
Read the claudy://session/analyzer resource for analyzer status
```

## Usage Examples

### Example 1: Code Review Workflow

```
You: "I need help reviewing my code for security issues"

Claude uses:
1. claudy_spawn(name="security_reviewer")
2. claudy_call(name="security_reviewer", message="Review main.py for security vulnerabilities")
3. claudy_call(name="security_reviewer", message="Focus on the authentication module")
4. claudy_cleanup(name="security_reviewer")
```

### Example 2: Parallel Analysis

```
You: "Analyze this codebase from multiple perspectives"

Claude uses:
1. claudy_spawn(name="quality")
2. claudy_spawn(name="performance")
3. claudy_spawn(name="security")
4. claudy_call(name="quality", message="Analyze code quality")
5. claudy_call(name="performance", message="Analyze performance")
6. claudy_call(name="security", message="Analyze security")
7. Read claudy://sessions to check all results
8. claudy_cleanup(all=true)
```

### Example 3: Multi-turn Conversation

```
You: "Create an agent to help me understand this complex algorithm"

Claude uses:
1. claudy_spawn(name="algo_expert")
2. claudy_call(name="algo_expert", message="Explain the quicksort algorithm in algorithm.py")
3. You: "What about the edge cases?"
4. claudy_call(name="algo_expert", message="What edge cases should I consider?")
   # Context from previous call is preserved!
5. claudy_cleanup(name="algo_expert")
```

## Benefits of MCP Integration

1. **Native Integration** - Claude uses Claudy as if it's a built-in feature
2. **Automatic Tool Selection** - Claude knows when to use agent sessions
3. **Resource Access** - Claude can query session status directly
4. **Seamless Workflow** - No manual command typing needed

## Troubleshooting

### Tools Not Showing Up

1. Check configuration file location: `~/.claude/config.json`
2. Verify `claudy mcp` command works:
   ```bash
   claudy mcp
   ```
3. Restart Claude Code

### Connection Errors

1. Make sure Claudy is installed globally:
   ```bash
   which claudy
   ```
2. Test the HTTP server:
   ```bash
   claudy server status
   ```

### Permission Issues

Some systems may require full path to claudy:

```json
{
  "mcpServers": {
    "claudy": {
      "command": "/usr/local/bin/claudy",
      "args": ["mcp"]
    }
  }
}
```

Find the path with:
```bash
which claudy
```

## Advanced: Custom Tool Permissions

You can spawn agents with specific tools:

```
Use claudy_spawn with name="readonly" and tools=["Read", "Grep", "Glob"]
```

This creates a read-only agent that can't modify files.

## Next Steps

- Try asking Claude to spawn agents for you
- Experiment with multi-turn conversations
- Use resources to monitor agent status
- See [Getting Started](getting_started.md) for CLI usage
