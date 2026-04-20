---
title: "Subscription-Backed ACP Layer"
artifact: INITIATIVE-001
track: container
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
parent-vision:
  - VISION-001
priority-weight: high
success-criteria:
  - Structured ACP calls execute against subscription-backed Claude Code sessions
  - No per-MTok API charges for any call routed through the harness
  - Session pool maintains 2+ live Claude Code sessions with automatic reconnection
  - Automated verification loops run against harness output and loop back on failure
  - Configuration supports Anthropic consumer plans and Google OAuth without API keys
  - Teardown reports capture agent decisions before merge (INITIATIVE-022 pattern)
depends-on-artifacts: []
addresses: []
evidence-pool: "trove: ai-agent-session-pricing@7957127"
---

# Subscription-Backed ACP Layer

## Strategic Focus

Anthropic bans consumer-plan OAuth tokens for third-party API access, but Claude Code sessions are sanctioned. This initiative builds the ACP (Agent Communication Protocol) layer that makes those sessions programmable. Developers issue structured protocol calls; the harness routes them through existing subscription-backed sessions; results come back validated and machine-readable. No API keys, no per-token billing.

The verification loop pattern from INITIATIVE-022 applies directly: every ACP call can be verified, loops back on failure, and produces a teardown report. The harness is both the invocation path and the verification path.

## Desired Outcomes

Developers on consumer subscriptions invoke AI models through structured ACP calls. Calls execute against authenticated Claude Code (or Gemini/ChatGPT) sessions. Session pooling handles reconnection and multiplexing. Automated verification loops validate responses and iterate. The operator reviews results at teardown, not during execution.

## Progress

<!-- Auto-populated from session digests. See progress.md for full log. -->

## Scope Boundaries

**In scope:**

- ACP protocol layer with structured request/response over subscription sessions
- Session manager: detect, start, attach, pool, and reconnect Claude Code tmux sessions
- Command router: translate ACP calls to Claude Code input, parse output
- Automated verification loop (INITIATIVE-022 pattern): failure triggers retro, loops back
- Configuration system: auth method (subscription OAuth vs API key), provider settings
- Teardown reports with agent decision trails

**Out of scope:**

- Reselling subscription access (TOS violation)
- Bypassing provider rate limits or usage caps
- OAuth token extraction (banned by Anthropic for consumer plans)
- Multi-user serving (one harness per subscription)
- Cloud deployment (local-first)

## Tracks

**Track 1: Session Management.** Detect, start, pool, and reconnect tmux-backed Claude Code sessions. Handle subscription auth detection.

**Track 2: ACP Protocol Layer.** Structured request/response protocol, command routing, output parsing, REST API surface.

**Track 3: Verification Loop.** INITIATIVE-022 pattern: verification design runs after implementation, loops on failure, produces teardown reports.

## Child Epics

- [EPIC-001](../../epic/Active/(EPIC-001)-Session-Manager/(EPIC-001)-Session-Manager.md) — Session Manager
- [EPIC-002](../../epic/Active/(EPIC-002)-ACP-Protocol-Layer/(EPIC-002)-ACP-Protocol-Layer.md) — ACP Protocol Layer
- [EPIC-003](../../epic/Active/(EPIC-003)-Automation-and-Verification/(EPIC-003)-Automation-and-Verification.md) — Automation and Verification

## Small Work (Epic-less Specs)

<!-- Specs attached directly to this initiative without an epic wrapper. -->

## Key Dependencies

- Claude Code CLI (installed and authenticated)
- tmux (session management)
- INITIATIVE-022 verification-loop pattern (design reference)
- Python 3.12+ (runtime)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-19 | -- | Initial creation |