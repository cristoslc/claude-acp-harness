---
title: "Session Pool Manager"
artifact: SPEC-004
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
depends-on:
  - SPEC-001
---

# Session Pool Manager

## Summary

Implement the session pool that maintains a configurable minimum number of live Claude Code sessions, handles health checking, auto-reconnection, and session rotation.

## Acceptance Criteria

### AC-1: Pool Minimum
**Given** a pool configured with `min_sessions: 2`
**When** the harness starts
**Then** 2 sessions are started and transition to `Ready`
**And** the pool reports `healthy` when all minimum sessions are ready

### AC-2: Auto-Reconnect
**Given** a session in `Reconnecting` state
**When** reconnection succeeds
**Then** the session transitions to `Ready` and re-enters the pool
**When** reconnection fails after 3 retries
**Then** the session is killed and a replacement session is started

### AC-3: Health Checking
**Given** sessions in the pool
**When** the health-check interval elapses (default: 30s)
**Then** each session is probed for responsiveness
**And** unresponsive sessions transition to `Reconnecting`

### AC-4: Session Rotation
**Given** a session that has been `Active` for longer than `max_session_age` (default: 4h)
**When** it returns to `Idle`
**Then** the pool drains it and starts a replacement

### AC-5: Pool Status
**Given** any pool state
**When** the operator queries pool status
**Then** it returns: total sessions, healthy count, state breakdown, and auth method distribution

## Implementation Approach

Build a `SessionPool` class with a background `asyncio` task for health checking. Use the session lifecycle from SPEC-001. Configuration from `config/harness.yaml` for pool size, health interval, and max session age.

## Scope

- `src/session_pool.py` — pool management, health checking, rotation
- Configuration integration with `config/harness.yaml`
