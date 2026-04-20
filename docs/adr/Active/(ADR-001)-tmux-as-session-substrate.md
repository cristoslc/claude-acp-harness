---
title: "tmux as session substrate"
artifact: ADR-001
track: standing
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
---

# ADR-001: tmux as session substrate

## Status

Active

## Context

The harness needs to run Claude Code sessions persistently and interact with them programmatically. Options for session substrate:

1. **tmux** — terminal multiplexer, sessions survive detach, programmatic I/O via `send-keys` and `capture-pane`
2. **screen** — similar to tmux but less scriptable
3. **subprocess pipes** — direct stdin/stdout, but no persistence across disconnects
4. **headless browser / web session** — Claude Code on the Web, but adds browser dependency

## Decision

Use tmux as the session substrate.

## Consequences

- Sessions persist across harness restarts (tmux server stays alive)
- Programmatic I/O via well-documented tmux commands
- No additional dependencies beyond what's already in the project
- `tmux capture-pane` provides raw text output — parsing required
- tmux session naming clashes possible — harness must manage unique names

## Alternatives Considered

- **subprocess pipes**: simpler but no persistence, no way to "reattach" after crash
- **screen**: less scriptable, less community support for programmatic control
- **browser automation**: Claude Code on the Web uses subscription OAuth natively, but adds Playwright/Selenium dependency and is slower
