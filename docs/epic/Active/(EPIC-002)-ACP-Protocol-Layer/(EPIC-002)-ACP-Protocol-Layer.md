---
title: "ACP Protocol Layer"
artifact: EPIC-002
track: container
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
parent-vision: VISION-001
parent-initiative: INITIATIVE-001
priority-weight: high
success-criteria:
  - ACP requests (JSON) are routed to live Claude Code sessions
  - Responses are parsed from Claude Code output into structured JSON
  - Command router handles queuing, dispatch, and timeout
  - REST API exposes ACP calls over localhost HTTP
  - At least 3 command types supported: prompt, edit, verify
depends-on-artifacts: []
addresses: []
---

# ACP Protocol Layer

## Goal / Objective

Define and implement the ACP (Agent Communication Protocol) that structures interactions between callers and Claude Code sessions. Callers send structured JSON requests; the harness routes them to sessions, captures output, and returns structured JSON responses. This is the "programmable" layer that distinguishes the harness from raw `claude -p` piping.

## Scope

- ACP message format (request/response schema)
- Command router: queue, dispatch, timeout, retry
- Output parser: extract structured fields from Claude Code freeform text
- REST API: localhost HTTP server exposing ACP endpoints
- Provider abstraction: same ACP interface regardless of backend (Claude, Gemini, ChatGPT)

## Architecture Overview

```mermaid
graph LR
    Caller -->|ACP Request| REST_API
    REST_API -->|enqueue| Router
    Router -->|dispatch| Session1
    Router -->|dispatch| Session2
    Session1 -->|raw output| Parser
    Session2 -->|raw output| Parser
    Parser -->|ACP Response| REST_API
    REST_API -->|JSON| Caller
```

## Child Specs

- [SPEC-002](../../spec/Active/(SPEC-002)-SCP-Protocol-Server/(SPEC-002)-SCP-Protocol-Server.md) — SCP Protocol Server
- [SPEC-003](../../spec/Active/(SPEC-003)-Command-Router/(SPEC-003)-Command-Router.md) — Command Router
- [SPEC-006](../../spec/Active/(SPEC-006)-ACP-REST-API/(SPEC-006)-ACP-REST-API.md) — ACP REST API

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-19 | -- | Initial creation |