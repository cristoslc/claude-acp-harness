---
title: "SCP Protocol Server"
artifact: SPEC-002
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
---

# SCP Protocol Server

## Summary

Define and implement the ACP (Agent Communication Protocol) message format — structured JSON requests and responses that flow through the harness. This is the wire protocol that makes Claude Code sessions programmable rather than interactive-only.

## Acceptance Criteria

### AC-1: Request Schema
**Given** a caller sends an ACP request
**When** the request arrives at the harness
**Then** it validates against the schema: `{id, type, payload, timeout, metadata}`
**And** rejects malformed requests with a 400 response and error details

### AC-2: Response Schema
**Given** a session completes an ACP call
**When** the harness returns the result
**Then** it conforms to: `{id, status, result, error, duration_ms, metadata}`
**And** `status` is one of: `success`, `failure`, `timeout`, `rate_limited`

### AC-3: Command Types
**Given** a valid ACP request
**When** `type` is `prompt`, `edit`, or `verify`
**Then** the harness routes it correctly to the appropriate handler

### AC-4: Error Handling
**Given** a session fails mid-call
**When** the harness detects the failure
**Then** it returns a structured error response with `status: failure` and error details
**And** the session transitions to `Reconnecting` state

## Implementation Approach

Define Pydantic models for ACP requests and responses. Add schema validation at the REST API boundary. Enumerate supported command types as a Python enum.

## Scope

- `src/acp_protocol.py` — request/response schemas, validation, command types
- Pydantic models for type safety
- No session interaction yet (SPEC-003 handles routing)
