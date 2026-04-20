---
title: "Command Router"
artifact: SPEC-003
track: implementable
status: Active
type: feature
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
parent-epic: EPIC-002
parent-initiative: INITIATIVE-001
priority-weight: high
swain-do: required
depends-on:
  - SPEC-001
  - SPEC-002
---

# Command Router

## Summary

Implement the command router that takes validated ACP requests, dispatches them to available sessions in the pool, captures raw output, parses it into structured responses, and handles timeouts and retries.

## Acceptance Criteria

### AC-1: Dispatch to Pool
**Given** a valid ACP request and a pool with available sessions
**When** the router dispatches the command
**Then** it selects the least-recently-used `Idle` session
**And** sends the payload as keystrokes to the tmux pane

### AC-2: Output Capture
**Given** a dispatched command
**When** Claude Code produces output
**Then** the router captures the pane output until an end-of-response marker is detected
**And** parses the output into the ACP response format

### AC-3: Timeout Handling
**Given** a dispatched command with `timeout` specified
**When** no end-of-response marker appears within the timeout
**Then** the router returns `status: timeout` and releases the session back to `Idle`

### AC-4: Queue Backpressure
**Given** all sessions are `Active`
**When** a new request arrives
**Then** the router queues it and dispatches when a session becomes `Idle`
**And** returns a `202 Accepted` with estimated wait time

### AC-5: Retry on Transient Failure
**Given** a command that fails due to session crash
**When** the session transitions to `Reconnecting`
**Then** the router retries the command on the next available session (up to 2 retries)

## Implementation Approach

Build a `CommandRouter` class that maintains a reference to the session pool and a request queue. Dispatch via tmux `send-keys`. Capture output via `tmux capture-pane` with a delimiter-based end-of-response protocol (wrap ACP payloads in sentinel markers so the parser knows when output is complete). Use `asyncio` for non-blocking dispatch and output polling.

## Scope

- `src/command_router.py` — dispatch, capture, parse, timeout, retry
- End-of-response sentinel protocol
- Integration with session pool (SPEC-004)