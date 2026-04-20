---
title: "Sentinel-based end-of-response detection"
artifact: ADR-002
track: standing
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
---

# ADR-002: Sentinel-based end-of-response detection

## Status

Active

## Context

The harness sends prompts to Claude Code via tmux and must detect when a response is complete. Options:

1. **Sentinel markers** — wrap payloads with unique delimiters, detect end-of-response when closing sentinel appears in output
2. **Idle timeout** — assume response is complete after N seconds of no new output
3. **Prompt character detection** — watch for the next shell/claude prompt

## Decision

Use sentinel markers. Wrap each ACP payload: inject `### ACP_START:<id> ###` before the prompt and `### ACP_END:<id> ###` as an explicit end marker. The command router captures output between these markers.

## Consequences

- Deterministic completion detection — no false positives from pauses in long responses
- Requires Claude Code to echo the end marker (inject it as part of the prompt instructions)
- Minimal overhead — two lines per call
- Parseable even if output contains arbitrary text

## Alternatives Considered

- **Idle timeout**: unreliable — long thinking pauses trigger premature completion
- **Prompt detection**: fragile — prompt format changes between Claude Code versions
