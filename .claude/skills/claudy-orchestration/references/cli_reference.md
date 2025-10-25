# Claudy CLI Reference

Complete reference for claudy command-line interface.

## Installation

Claudy can be used via `uvx` without installation:

```bash
uvx claudy <command>
```

## Commands

### call - Send message to agent

```bash
uvx claudy call <name> <message> [options]
```

**Arguments:**
- `name`: Session name (creates new session if doesn't exist)
- `message`: Message to send to the agent

**Options:**
- `--verbosity <level>`: Output verbosity (quiet/normal/verbose, default: normal)
- `--fork`: Fork session before sending message
- `--fork-name <name>`: Name for forked session

**Examples:**
```bash
# Create and call agent
uvx claudy call researcher "Search for latest AI papers"

# Call with quiet output
uvx claudy call researcher "Continue analysis" --verbosity quiet

# Fork session
uvx claudy call analysis "Try approach B" --fork --fork-name analysis_b
```

### list - List all sessions

```bash
uvx claudy list
```

Shows all active agent sessions with metadata (created_at, last_used, message_count).

### status - Get session details

```bash
uvx claudy status <name>
```

**Arguments:**
- `name`: Session name to check

Shows detailed session information including idle time.

### cleanup - Remove sessions

```bash
uvx claudy cleanup <name>
# or
uvx claudy cleanup --all
```

**Arguments:**
- `name`: Session name to cleanup (optional if using --all)

**Options:**
- `--all`: Remove all sessions

### server - Start HTTP server

```bash
uvx claudy server [options]
```

**Options:**
- `--host <host>`: Server host (default: 127.0.0.1)
- `--port <port>`: Server port (default: 8000)

Starts HTTP server for programmatic access to claudy.

## Session Behavior

- **Auto-creation**: Sessions are created automatically on first `call`
- **TTL cleanup**: Sessions auto-cleanup after 20 minutes of inactivity
- **In-memory**: Sessions reset when server restarts
- **Context preservation**: Each session remembers full conversation history

## JSON Output Format

All commands return JSON for easy parsing:

```json
{
  "success": true,
  "name": "researcher",
  "session_id": "uuid",
  "response": {
    "content": [...],
    "stop_reason": "end_turn"
  }
}
```

Error responses:
```json
{
  "success": false,
  "error": "Session not found"
}
```
