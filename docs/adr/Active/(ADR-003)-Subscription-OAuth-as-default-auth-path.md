---
title: "Subscription OAuth as default auth path"
artifact: ADR-003
track: standing
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
---

# ADR-003: Subscription OAuth as default auth path

## Status

Active

## Context

Anthropic bans consumer-plan OAuth tokens for third-party API access (2026 policy). However, Claude Code sessions authenticated via subscription OAuth are sanctioned. The harness must choose its default authentication strategy:

1. **Subscription OAuth (default)** — reuse existing Claude Code session auth, zero per-token cost
2. **API key (fallback)** — use `ANTHROPIC_API_KEY`, incurs per-token billing
3. **Dual mode** — require user choice at startup

## Decision

Default to subscription OAuth. Use API key as fallback only when no subscription session is detected. Always warn when API key mode is active.

## Consequences

- Consumer-plan users get subscription benefits without per-token charges
- Aligns with Anthropic's sanctioned path (Claude Code session reuse, per OpenClaw precedent)
- Clear warning when per-token billing applies prevents billing surprises
- Future provider support (Google OAuth) follows the same pattern: subscription OAuth first, API key fallback

## Alternatives Considered

- **API key default**: contradicts the project's purpose (avoiding per-token billing)
- **Dual mode with prompt**: adds friction on every startup; most users want subscription auth