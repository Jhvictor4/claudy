---
name: claudy-orchestration
description: Use this skill when delegating to sub-agents that require more flexibility than the Task tool provides - when launching multiple agents in parallel, managing persistent sessions across calls, or coordinating complex multi-agent workflows with custom orchestration patterns.
---

# Claudy Orchestration

## Overview

Claudy is a multi-agent orchestration tool built on claude-agent-sdk. Use it to spawn and manage persistent Claude agent sessions via CLI commands.

## When to Use Claudy vs Task Tool

**Use the Task tool (default) when:**
- Launching a single specialized agent (code-reviewer, Explore, etc.)
- Agent types are predefined and well-suited to the task
- No need for session persistence or cross-call context

**Use Claudy (this skill) when:**
- Launching multiple agents in parallel with custom workflows
- Need persistent sessions that remember context across multiple calls
- Require fine-grained control over agent lifecycle (create, fork, cleanup)
- Building complex orchestration patterns not supported by Task tool
- Delegating to agents with undefined or custom roles

**Example scenarios for Claudy:**
- "Launch 5 agents to analyze different aspects of the codebase in parallel"
- "Create a research agent, have it gather info, then fork it to explore 3 different approaches"
- "Delegate long-running analysis to background agents and aggregate results later"

## Quick Start

Claudy runs via `uvx` without installation. All commands use the pattern:

```bash
uvx claudy <command> [arguments]
```

Basic workflow:

```bash
# 1. Create and call an agent
uvx claudy call researcher "Search for latest AI papers"

# 2. Continue conversation (context preserved)
uvx claudy call researcher "Summarize the top 3 papers"

# 3. Check status
uvx claudy status researcher

# 4. Cleanup when done
uvx claudy cleanup researcher
```

## Basic Operations

### Creating and Calling Agents

Use `call` to send messages to agents. Sessions auto-create if they don't exist:

```bash
uvx claudy call <name> "<message>" [--verbosity quiet|normal|verbose]
```

**Example:**
```bash
# Create new agent
uvx claudy call security "Audit auth.py for vulnerabilities"

# Continue conversation
uvx claudy call security "Focus on SQL injection risks"
```

Output is JSON. Parse `response.content` for the agent's reply.

### Listing Sessions

View all active sessions:

```bash
uvx claudy list
```

Shows session names, IDs, creation time, last used time, and message count.

### Checking Session Status

Get detailed status for a specific session:

```bash
uvx claudy status <name>
```

Useful for monitoring idle time (sessions auto-cleanup after 2 hours).

### Cleaning Up Sessions

Remove sessions manually:

```bash
# Single session
uvx claudy cleanup <name>

# All sessions
uvx claudy cleanup --all
```

Sessions are in-memory and reset when the server restarts.

## Parallel Execution Patterns

Claudy's killer feature is parallel agent orchestration with the fan-out/fan-in pattern.

### Fan-out/Fan-in Pattern (Recommended)

**Core concept**: Launch multiple agents simultaneously (fan-out), then aggregate results (fan-in).

**Using MCP tools (preferred when available):**

```python
# Fan-out: Launch agents in background
claudy_call_async(name="security", message="Audit for vulnerabilities")
claudy_call_async(name="performance", message="Profile bottlenecks")
claudy_call_async(name="docs", message="Check documentation")

# Optional: Monitor progress
claudy_check_status(names=["security", "performance", "docs"])

# Fan-in: Wait and aggregate all results
results = claudy_get_results(
    names=["security", "performance", "docs"],
    timeout=300
)
# Process aggregated results
```

**Using CLI (when MCP not available):**

```bash
# Fan-out: Launch with background processes
uvx claudy call security "Audit security" &
uvx claudy call performance "Profile performance" &
uvx claudy call docs "Check documentation" &
wait

# Fan-in: Parse JSON responses
# (Use jq or similar to aggregate)
```

**When to use**: Analyzing multiple independent aspects simultaneously (security + performance + docs).

### Role-based Persistent Sessions

**Core concept**: Create specialized agents with specific roles, maintain context across multiple interactions.

**Pattern:**

```bash
# 1. Initialize role-based agents (one-time setup)
uvx claudy call solver "You are the implementation expert. Understand this problem: [description]"
uvx claudy call reviewer "You are the code reviewer. Focus on correctness and edge cases."
uvx claudy call tester "You are the test engineer. Generate comprehensive test cases."

# 2. Implementation cycle (agents remember their roles)
uvx claudy call solver "Implement the solution using dynamic programming"

# 3. Parallel review while solver works
uvx claudy call reviewer "Review this code for overflow issues: [code]" &
uvx claudy call tester "Prepare edge case tests for array size 10^5" &
wait

# 4. Incremental refinement (context preserved)
uvx claudy call solver "Fix the overflow issue that reviewer mentioned"
uvx claudy call reviewer "Verify the fix in lines 42-45"

# 5. Continuous interaction (each agent remembers everything)
uvx claudy call reviewer "Are all the issues I mentioned earlier resolved?"
# → reviewer recalls the entire history of issues raised
```

**Why this works:**
- Each agent maintains full conversation context
- Agents specialize in their role over time
- No need to re-explain context in every call
- Enables iterative refinement with persistent memory

**When to use**:
- Complex problems requiring multiple perspectives
- Iterative workflows with review cycles
- Long-running tasks with role specialization

### Multi-approach Exploration with Forking

**Core concept**: Fork a session to explore alternative solutions simultaneously.

```bash
# Base understanding
uvx claudy call solver "Analyze the problem constraints"

# Fork to try different algorithms
uvx claudy call solver "Try DP approach" --fork --fork-name solver_dp
uvx claudy call solver "Try segment tree" --fork --fork-name solver_segtree

# Each fork evolves independently
uvx claudy call solver_dp "Optimize for time complexity"
uvx claudy call solver_segtree "Optimize for space complexity"

# Compare final results
uvx claudy status solver_dp
uvx claudy status solver_segtree
```

**When to use**: Exploring multiple solution paths without losing progress.

### Dynamic Agent Scaling

**Core concept**: Spawn N agents based on input data.

```bash
# Example: Analyze multiple files
for file in src/*.py; do
  agent_name="analyzer_$(basename $file .py)"
  uvx claudy call "$agent_name" "Analyze $file for code quality" &
done
wait

# Aggregate results
uvx claudy list  # Get all agent names
```

**When to use**: Processing multiple independent items in parallel.

## Session Management

### Context Preservation

Sessions remember full conversation history:

```bash
uvx claudy call memory_test "Remember this number: 42"
uvx claudy call memory_test "What number did I tell you?"
# Response: "42" ✓
```

Use this for multi-turn delegations where agents build on previous context.

### Session Forking

Fork sessions to explore alternative approaches without losing original:

```bash
# Base analysis
uvx claudy call analysis "Analyze refactoring options"

# Fork to try alternative
uvx claudy call analysis "Try microservices approach" \
  --fork --fork-name analysis_microservices

# Original continues independently
uvx claudy call analysis "Continue with monolith optimization"
```

Both sessions now independent. Use forking to:
- Explore multiple solution paths in parallel
- A/B test different approaches
- Branch conversations at decision points

## Workflow Examples

### Example 1: Comprehensive Codebase Analysis

```bash
# Launch 4 specialized agents
uvx claudy call security "Audit for vulnerabilities in src/" &
uvx claudy call performance "Profile performance bottlenecks" &
uvx claudy call architecture "Review architectural patterns" &
uvx claudy call dependencies "Check for outdated dependencies" &
wait

# View all results
uvx claudy list
# Parse JSON responses from each agent
```

### Example 2: Multi-Path Research

```bash
# Create base research agent
uvx claudy call research "Research state-of-the-art RAG systems"

# Fork to explore different architectures
uvx claudy call research "Investigate vector databases" \
  --fork --fork-name research_vectordb

uvx claudy call research "Investigate hybrid search" \
  --fork --fork-name research_hybrid

# Each fork explores independently
# Compare findings later
```

### Example 3: Incremental Delegation

```bash
# Start high-level analysis
uvx claudy call analyzer "Analyze this codebase structure"

# Based on findings, delegate specific tasks
uvx claudy call refactorer "Refactor the auth module per analyzer's suggestions"
uvx claudy call tester "Write tests for the refactored auth module"
uvx claudy call documenter "Document the new auth implementation"

# All agents work independently but share context through your coordination
```

## Reference Materials

For detailed CLI documentation, see `references/cli_reference.md`.

## Notes

- Sessions auto-cleanup after 2 hours of inactivity (configurable)
- All sessions are in-memory (reset on server restart)
- Agents created via claudy inherit parent permissions (no prompt spam)
- Output is always JSON for easy parsing and automation
