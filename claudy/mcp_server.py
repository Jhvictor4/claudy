#!/usr/bin/env python3
"""FastMCP-based Claudy server for managing Claude agent sessions."""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import TextBlock
from fastmcp import FastMCP, Context

# Session management configuration
SESSION_IDLE_TIMEOUT = 7200  # 2 hours in seconds
SESSION_CLEANUP_INTERVAL = 300  # Check every 5 minutes


def get_current_claude_session_id() -> Optional[str]:
    """Get the current Claude Code session ID from the project's session files."""
    try:
        cwd = os.getcwd()
        project_name = cwd.replace('/', '-')
        sessions_dir = Path.home() / ".claude" / "projects" / project_name

        if sessions_dir.exists():
            jsonl_files = sorted(
                sessions_dir.glob("*.jsonl"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if jsonl_files:
                return jsonl_files[0].stem  # Filename without extension is the session ID
    except Exception:
        pass
    return None


# Global session storage (shared across all MCP connections)
# Key: session_name, Value: (client, metadata)
_global_sessions: Dict[str, tuple[ClaudeSDKClient, dict]] = {}

# Background task storage for async execution
# Key: session_name, Value: asyncio.Task
_background_tasks: Dict[str, asyncio.Task] = {}


async def cleanup_idle_sessions():
    """Background task to cleanup idle sessions."""
    while True:
        try:
            await asyncio.sleep(SESSION_CLEANUP_INTERVAL)

            now = datetime.now()
            to_cleanup = []

            for name, (client, metadata) in _global_sessions.items():
                last_used = datetime.fromisoformat(metadata["last_used"])
                idle_seconds = (now - last_used).total_seconds()

                if idle_seconds > SESSION_IDLE_TIMEOUT:
                    to_cleanup.append(name)

            # Cleanup idle sessions
            for name in to_cleanup:
                if name in _global_sessions:
                    client, _ = _global_sessions[name]
                    try:
                        await client.disconnect()
                    except Exception:
                        pass  # Best effort cleanup
                    del _global_sessions[name]

        except Exception:
            pass  # Don't let background task crash


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Lifespan context manager for background tasks."""
    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_idle_sessions())

    try:
        yield
    finally:
        # Cleanup on shutdown
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

        # Disconnect all sessions
        for client, _ in _global_sessions.values():
            try:
                await client.disconnect()
            except Exception:
                pass
        _global_sessions.clear()


# Initialize FastMCP server
mcp = FastMCP(
    name="claudy",
    instructions="""Claudy: Multi-agent session manager for delegating complex tasks to specialized Claude agents.

WHEN TO USE:
- Running multiple analyses in parallel (e.g., code review + documentation + testing)
- Delegating long-running tasks to background agents
- Exploring alternative approaches via session forking
- Managing complex workflows that benefit from task isolation
- Offloading sub-tasks while keeping main context clean

KEY FEATURES:
- Auto-creates persistent agent sessions (no setup needed)
- Sessions remember full conversation history
- Fork sessions to explore different approaches
- 2-hour idle timeout (auto-cleanup)
- Sessions inherit permissions automatically

COMMON PATTERNS:
1. Parallel Analysis: Create agents for different aspects (security, performance, architecture)
2. Background Tasks: Delegate research/analysis while continuing main work
3. Branch Exploration: Fork a session to try alternative solutions
4. Specialized Agents: Create focused agents for specific domains

EXAMPLE WORKFLOWS:
- "Use claudy to create a 'reviewer' agent and have it analyze security issues"
- "Fork the current analysis into 'approach-a' and 'approach-b' to compare solutions"
- "Delegate documentation generation to a background agent while I continue coding"

Sessions are shared across all your Claude Code windows and persist until cleaned up.""",
    lifespan=lifespan
)


async def get_or_create_session(
    name: str,
    parent_session_id: Optional[str] = None
) -> tuple[ClaudeSDKClient, dict]:
    """Get existing session or create new one with auto-spawn."""
    if name in _global_sessions:
        client, metadata = _global_sessions[name]
        # Update last_used
        metadata["last_used"] = datetime.now().isoformat()
        return client, metadata

    # Auto-spawn new session
    options = ClaudeAgentOptions()
    options.permission_mode = "bypassPermissions"

    if parent_session_id:
        options.resume = parent_session_id
        options.fork_session = True

    client = ClaudeSDKClient(options=options)
    await client.connect()

    metadata = {
        "created_at": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat(),
        "message_count": 0,
        "session_id": None,
        "auto_created": True,
    }
    if parent_session_id:
        metadata["parent_session_id"] = parent_session_id

    _global_sessions[name] = (client, metadata)
    return client, metadata


async def _execute_call(
    name: str,
    message: str,
    verbosity: str = "normal",
    fork: bool = False,
    fork_name: Optional[str] = None,
    parent_session_id: Optional[str] = None,
) -> dict:
    """Internal helper to execute a call (used by both sync and async versions)."""
    # Auto-detect current Claude session ID if not provided
    if not parent_session_id:
        parent_session_id = get_current_claude_session_id()

    # Handle forking
    if fork:
        # Get parent session
        if name not in _global_sessions:
            return {
                "success": False,
                "error": f"Cannot fork non-existent session '{name}'",
            }

        _, parent_metadata = _global_sessions[name]
        parent_session_id = parent_metadata.get("session_id")

        if not parent_session_id:
            return {
                "success": False,
                "error": f"Cannot fork session '{name}': no session_id available. Send at least one message first.",
            }

        # Determine fork session name
        if not fork_name:
            fork_name = f"{name}_fork_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Check if fork name already exists
        if fork_name in _global_sessions:
            return {
                "success": False,
                "error": f"Fork session name '{fork_name}' already exists",
            }

        # Use fork_name as the target session
        name = fork_name

    # Get or create session
    client, metadata = await get_or_create_session(name, parent_session_id)

    # Send message and collect response
    await client.query(message)

    response_parts = []
    all_events = []
    session_id = None

    async for msg in client.receive_response():
        # Extract session_id from first message if available
        if session_id is None and hasattr(msg, "session_id"):
            session_id = msg.session_id
            if metadata["session_id"] is None:
                metadata["session_id"] = session_id

        # Collect all events for verbose mode
        if verbosity == "verbose":
            msg_dict = {"type": type(msg).__name__}

            if hasattr(msg, "content"):
                msg_dict["content"] = []
                for block in msg.content:
                    block_dict = {"type": getattr(block, "type", type(block).__name__)}

                    if isinstance(block, TextBlock):
                        block_dict["text"] = block.text
                    elif hasattr(block, "thinking"):
                        block_dict["thinking"] = block.thinking
                    elif hasattr(block, "name") and hasattr(block, "input"):
                        block_dict["name"] = block.name
                        block_dict["input"] = block.input
                    elif hasattr(block, "tool_use_id"):
                        block_dict["tool_use_id"] = block.tool_use_id
                        if hasattr(block, "content"):
                            block_dict["content"] = block.content

                    msg_dict["content"].append(block_dict)

            if hasattr(msg, "stop_reason"):
                msg_dict["stop_reason"] = msg.stop_reason
            if hasattr(msg, "role"):
                msg_dict["role"] = msg.role

            all_events.append(msg_dict)

        # Collect text for response
        if hasattr(msg, "content"):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    response_parts.append(block.text)

    # Update metadata
    metadata["last_used"] = datetime.now().isoformat()
    metadata["message_count"] += 1

    # Build response based on verbosity
    result = {
        "success": True,
        "name": name,
        "response": "\n".join(response_parts),
    }

    if session_id:
        result["session_id"] = session_id

    if fork:
        result["forked"] = True

    if verbosity == "verbose":
        result["events"] = all_events

    return result


@mcp.tool
async def claudy_call(
    name: str,
    message: str,
    verbosity: str = "normal",
    fork: bool = False,
    fork_name: Optional[str] = None,
    parent_session_id: Optional[str] = None,
) -> str:
    """Delegate a task to a persistent Claude agent session (blocking, waits for completion).

    Creates a new agent or continues an existing conversation. Sessions maintain full context
    across multiple calls, enabling complex multi-turn workflows. This is a BLOCKING call -
    use claudy_call_async for parallel execution.

    USE CASES:
    - Sequential work: Single-threaded task delegation
    - Iterative refinement: Multiple calls to same session build on previous responses
    - Alternative exploration: Use fork=True to branch conversation

    EXAMPLES:
    - Create reviewer: claudy_call('code-reviewer', 'Analyze main.py for bugs')
    - Continue conversation: claudy_call('code-reviewer', 'Focus on authentication module')
    - Fork to explore: claudy_call('code-reviewer', 'Try refactoring approach B', fork=True, fork_name='refactor-b')

    For PARALLEL execution, use: claudy_call_async + claudy_get_results

    Args:
        name: Session identifier (auto-creates if new). Use descriptive names like 'security-audit' or 'docs-generator'
        message: Task or question for the agent
        verbosity: Output detail level - 'quiet' (response only), 'normal' (default), 'verbose' (includes thinking)
        fork: Create independent copy of session to explore alternatives without affecting original
        fork_name: Name for forked session (auto-generated if omitted)
        parent_session_id: Advanced - explicit parent session to inherit from (auto-detected by default)

    Returns:
        JSON with 'success', 'response', 'session_id', and optional 'events' (if verbose)
    """
    result = await _execute_call(name, message, verbosity, fork, fork_name, parent_session_id)

    import json
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool
async def claudy_call_async(
    name: str,
    message: str,
    verbosity: str = "normal",
    parent_session_id: Optional[str] = None,
) -> str:
    """Start agent task in background, returns immediately for parallel execution.

    This is the NON-BLOCKING version that enables true parallel execution. The task runs
    in the background while you continue other work. Use claudy_get_results to collect
    results from multiple agents.

    PARALLEL WORKFLOW:
    1. Launch multiple agents with claudy_call_async
    2. Continue other work (they run in background)
    3. Collect all results with claudy_get_results([names])

    EXAMPLES:
    - Start security audit: claudy_call_async('security', 'Review for SQL injection')
    - Start performance analysis: claudy_call_async('perf', 'Find bottlenecks')
    - Start docs generation: claudy_call_async('docs', 'Generate API docs')
    - Collect all: claudy_get_results(['security', 'perf', 'docs'])

    Args:
        name: Session identifier (will be used to retrieve results later)
        message: Task for the agent
        verbosity: Output detail level - 'quiet', 'normal', 'verbose'
        parent_session_id: Advanced - explicit parent session to inherit from

    Returns:
        JSON with 'success', 'name', 'status': 'running'
    """
    # Create background task
    task = asyncio.create_task(_execute_call(name, message, verbosity, parent_session_id=parent_session_id))
    _background_tasks[name] = task

    import json
    return json.dumps({
        "success": True,
        "name": name,
        "status": "running",
        "message": f"Task '{name}' started in background"
    }, indent=2, ensure_ascii=False)


@mcp.tool
async def claudy_get_results(names: list[str], timeout: Optional[int] = None) -> str:
    """Wait for and aggregate results from multiple background agents (blocking until complete).

    This is the FAN-IN operation that collects results from agents started with claudy_call_async.
    It blocks until ALL specified agents complete, enabling true parallel execution patterns.

    PARALLEL PATTERN:
    ```
    # Step 1: Launch multiple agents in parallel (non-blocking)
    claudy_call_async('security', 'Audit code')
    claudy_call_async('performance', 'Find bottlenecks')
    claudy_call_async('docs', 'Generate docs')

    # Step 2: Collect all results (blocks until all complete)
    results = claudy_get_results(['security', 'performance', 'docs'])
    ```

    PARTIAL COLLECTION:
    - You can collect subset of running tasks
    - Uncollected tasks continue running in background

    Args:
        names: List of session names to wait for and collect
        timeout: Optional timeout in seconds (default: wait forever)

    Returns:
        JSON with aggregated results from all agents:
        {
            "success": true,
            "results": {
                "security": {"success": true, "response": "..."},
                "performance": {"success": true, "response": "..."},
                "docs": {"success": true, "response": "..."}
            }
        }
    """
    results = {}

    for name in names:
        if name not in _background_tasks:
            results[name] = {"success": False, "error": f"No background task found for '{name}'"}
            continue

        try:
            # Wait for task to complete (with optional timeout)
            if timeout:
                result = await asyncio.wait_for(_background_tasks[name], timeout=timeout)
            else:
                result = await _background_tasks[name]

            results[name] = result

            # Cleanup completed task
            del _background_tasks[name]

        except asyncio.TimeoutError:
            results[name] = {
                "success": False,
                "error": f"Task '{name}' timed out after {timeout} seconds",
                "status": "timeout"
            }
        except Exception as e:
            results[name] = {
                "success": False,
                "error": f"Task '{name}' failed: {str(e)}",
                "status": "error"
            }
            # Cleanup failed task
            if name in _background_tasks:
                del _background_tasks[name]

    import json
    return json.dumps({
        "success": True,
        "results": results
    }, indent=2, ensure_ascii=False)


@mcp.tool
async def claudy_check_status(names: Optional[list[str]] = None) -> str:
    """Check if background tasks are still running.

    Useful for monitoring long-running tasks without blocking. Returns status of
    specified tasks or all running tasks.

    Args:
        names: Optional list of session names to check. If None, checks all running tasks.

    Returns:
        JSON with status of each task:
        {
            "success": true,
            "tasks": {
                "security": "running",
                "performance": "completed",
                "docs": "running"
            }
        }
    """
    if names is None:
        names = list(_background_tasks.keys())

    tasks_status = {}

    for name in names:
        if name not in _background_tasks:
            tasks_status[name] = "not_found"
        elif _background_tasks[name].done():
            tasks_status[name] = "completed"
        else:
            tasks_status[name] = "running"

    import json
    return json.dumps({
        "success": True,
        "tasks": tasks_status
    }, indent=2, ensure_ascii=False)


@mcp.tool
async def claudy_list() -> str:
    """List all active agent sessions with their metadata."""
    sessions_list = [
        {"name": name, **metadata}
        for name, (_, metadata) in _global_sessions.items()
    ]

    import json
    return json.dumps(
        {"success": True, "sessions": sessions_list},
        indent=2,
        ensure_ascii=False
    )


@mcp.tool
async def claudy_status(name: str) -> str:
    """Get detailed status of a specific agent session.

    Args:
        name: Session name to check status
    """
    if name not in _global_sessions:
        import json
        return json.dumps(
            {
                "success": False,
                "error": f"Session '{name}' not found",
                "available_sessions": list(_global_sessions.keys()),
            },
            indent=2,
            ensure_ascii=False
        )

    _, metadata = _global_sessions[name]

    import json
    return json.dumps(
        {"success": True, "name": name, **metadata},
        indent=2,
        ensure_ascii=False
    )


@mcp.tool
async def claudy_cleanup(name: Optional[str] = None, all: bool = False) -> str:
    """Cleanup one or all agent sessions. Use this when done with agents.

    Args:
        name: Session name to cleanup (optional if all=true)
        all: If true, cleanup all sessions
    """
    if all:
        # Cleanup all sessions
        count = len(_global_sessions)
        for client, _ in list(_global_sessions.values()):
            try:
                await client.disconnect()
            except Exception:
                pass
        _global_sessions.clear()

        import json
        return json.dumps(
            {"success": True, "message": f"Cleaned up {count} session(s)"},
            indent=2,
            ensure_ascii=False
        )
    else:
        if not name:
            import json
            return json.dumps(
                {"success": False, "error": "Session name is required"},
                indent=2,
                ensure_ascii=False
            )

        if name not in _global_sessions:
            import json
            return json.dumps(
                {
                    "success": False,
                    "error": f"Session '{name}' not found",
                    "available_sessions": list(_global_sessions.keys()),
                },
                indent=2,
                ensure_ascii=False
            )

        # Cleanup single session
        client, _ = _global_sessions[name]
        try:
            await client.disconnect()
        except Exception:
            pass

        del _global_sessions[name]

        import json
        return json.dumps(
            {
                "success": True,
                "name": name,
                "message": f"Session '{name}' cleaned up successfully",
            },
            indent=2,
            ensure_ascii=False
        )


if __name__ == "__main__":
    # Run with FastMCP CLI
    mcp.run()
