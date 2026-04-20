---
title: "Subscription ACP Harness"
artifact: VISION-001
track: standing
status: Active
product-type: competitive
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
priority-weight: high
depends-on-artifacts:
  - PERSONA-001
  - PERSONA-002
evidence-pool: "trove: ai-agent-session-pricing@7957127"
---

# Subscription ACP Harness

## Target Audience

Individual developers and small teams on AI provider consumer subscription plans (Anthropic Pro/Max, OpenAI Plus/Pro, Google AI) who want programmatic, structured access to AI capabilities without incurring per-MTok API charges.

## Value Proposition

Enable developers to invoke AI models through structured protocol calls executed by their existing signed-in subscription sessions, rather than through API keys that bill per token. The harness turns a subscription session into a programmable endpoint.

## Competitive Landscape

**Incumbents:** OpenClaw reuses `claude -p` sessions but provides no structured protocol, no session pooling, and no automated verification. API-key-based tools (LangChain, CrewAI) all bill per-token. Opencode supports Google OAuth but not Anthropic consumer-plan sessions.

**Gap:** No tool provides ACP-protocol-level structured interaction with subscription-backed Claude Code sessions. Anthropic bans consumer OAuth tokens for third-party API access — but Claude Code sessions themselves are sanctioned. The harness sits in that sanctioned path.

**Why now:** Anthropic's 2026 consumer-plan OAuth ban closed the direct-token extraction avenue. The only remaining sanctioned path is the live Claude Code session itself. This creates a clear niche for a tool that makes that session programmable.

## Moat

Protocol-native integration. The harness doesn't just pipe stdin/stdout — it structures interactions through ACP (Agent Communication Protocol), enabling multi-step workflows, session pooling, automated verification loops, and result validation that raw CLI reuse cannot provide. The INITIATIVE-022 verification-loop pattern applies: structured calls get structured verification.

## Scaling Model

Single-user first (one machine, one subscription). Multi-session pooling next (one subscription, parallel sessions). Eventually: multi-provider abstraction (Claude, ChatGPT, Gemini) under one harness. Network effects are limited — this is a developer tool, not a platform. Growth comes from provider coverage and protocol depth.

## Success Metrics

- Developers can issue structured ACP calls and receive validated responses through their existing subscription
- Per-call cost is $0 beyond the subscription fee (no API token charges)
- Automated verification loops (INITIATIVE-022 pattern) run against harness output
- Session uptime > 99% during active subscription periods
- Supports at least 2 providers (Anthropic + Google) within 3 months

## Non-Goals

- Reselling subscription access to third parties (TOS violation)
- Bypassing rate limits or usage caps imposed by the subscription
- Replacing API-key-based workflows for production services
- Supporting Team/Enterprise plans (they already have API access)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-19 | -- | Initial creation |
