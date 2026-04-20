---
title: "Claude Session Lifecycle"
artifact: SPEC-001
track: implementable
status: Active
type: feature
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
parent-epic: EPIC-001
parent-initiative: INITIATIVE-001
priority-weight: high
swain-do: required
depends-on: []
---

# Claude Session Lifecycle

## Summary

Implement the Claude Code session lifecycle state machine, including detection of authentication method (subscription OAuth vs API key), session startup in tmux, state transitions, and health status reporting.

## Acceptance Criteria

### AC-1: Auth Detection
**Given** a Claude Code CLI is installed
**When** the harness starts a session
**Then** it detects whether the session authenticates via subscription OAuth or API key
**And** it logs the authentication method

### AC-2: Session Start
**Given** tmux is available and Claude Code is authenticated
**When** the harness requests a new session
**Then** a tmux pane opens with `claude` running inside it
**And** the session transitions to `Ready` state within 30 seconds

### AC-3: State Machine
**Given** a running session in `Ready` state
**When** a command is dispatched to it
**Then** the session transitions to `Active`
**And** when the command completes, it transitions to `Idle`

### AC-4: Crash Recovery
**Given** a session in `Active` state
**When** the tmux pane exits unexpectedly
**Then** the session transitions to `Reconnecting` and attempts to restart

### AC-5: Status Reporting
**Given** any number of sessions
**When** the operator queries session status
**Then** each session reports its state, auth method, uptime, and last-activity timestamp

## Implementation Approach

Extend the existing `ClaudeACPHarness` class with a `ClaudeSession` dataclass tracking state, add a `SessionLifecycle` class implementing the state machine, and a `detect_auth_method()` function that checks for `ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, and subscription OAuth credential files.

## Scope

- `src/session_lifecycle.py` — state machine and auth detection
- Extend `src/acp_harness.py` — integrate lifecycle into existing harness class
- Unit tests for all state transitions