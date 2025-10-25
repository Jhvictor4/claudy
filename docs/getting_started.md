# Getting Started with Claudy

## Installation

```bash
pip install claudy
```

## Quick Start

### 1. Spawn an Agent

```bash
claudy spawn analyzer
```

### 2. Send Messages (Context Preserved!)

```bash
claudy call analyzer "Analyze this code for bugs"
claudy call analyzer "Prioritize the top 3 issues"  # Remembers previous context!
claudy call analyzer "Generate fixes for issue #1"
```

### 3. Cleanup

```bash
claudy cleanup analyzer
```

## Verbosity Levels

```bash
# Quiet mode - only response text (saves tokens)
claudy call agent "Quick question" --quiet

# Normal mode - JSON with metadata (default)
claudy call agent "Detailed analysis"

# Verbose mode - includes thinking and tool calls
claudy call agent "Deep analysis" --verbose
```

## Common Commands

```bash
# List all sessions
claudy list

# Get session status
claudy status analyzer

# Server management
claudy server status
claudy server start
claudy server stop
claudy server restart

# Cleanup all sessions
claudy cleanup --all
```

## Example: Code Review Workflow

```bash
# Spawn a reviewer
claudy spawn reviewer

# Multi-turn conversation
claudy call reviewer "Review main.py for security issues"
claudy call reviewer "Focus on the authentication module you mentioned"
claudy call reviewer "Show me code snippets for fixing issue #2"

# Cleanup
claudy cleanup reviewer
```

## Example: Parallel Analysis

```bash
# Spawn multiple agents
claudy spawn analyzer
claudy spawn tester
claudy spawn documenter

# Work with them
claudy call analyzer "Analyze code quality" &
claudy call tester "Run test suite" &
claudy call documenter "Generate API docs" &
wait

# Cleanup all
claudy cleanup --all
```

## Multi-Terminal Usage

Claudy sessions are shared across terminals:

```bash
# Terminal 1
claudy spawn long_task
claudy call long_task "Start complex analysis"

# Terminal 2 (simultaneously)
claudy status long_task  # Check progress
claudy call long_task "Pause and summarize"
```

## Server Auto-start

The HTTP server starts automatically on first use. You don't need to manage it manually!

```bash
# Server starts automatically
claudy spawn test

# Check server status
claudy server status
```

## Context Preservation Example

```bash
$ claudy spawn memory_test

$ claudy call memory_test "Remember this number: 42"
{"response": "I'll remember it."}

$ claudy call memory_test "What number did I ask you to remember?"
{"response": "42"}  # ✓ Context preserved!
```

## Troubleshooting

### Server Won't Start

```bash
claudy server status
claudy server restart
```

### Session Not Found

```bash
# List all active sessions
claudy list

# Check specific session
claudy status myagent
```

### Clean State

```bash
# Remove all sessions and restart
claudy cleanup --all
claudy server restart
```

## Next Steps

- See [MCP Setup Guide](mcp_setup.md) for Claude Code integration
- See [README](../README.md) for HTTP API usage
- See [API Reference](api_reference.md) for detailed command docs
