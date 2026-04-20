---
title: "Subscription Developer"
artifact: PERSONA-001
track: standing
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
linked-artifacts:
  - VISION-001
depends-on-artifacts: []
---

# Subscription Developer

## Archetype Label

Solo Power User

## Demographic Summary

Individual developer, 25-45, high technical proficiency. Pays for Anthropic Pro/Max, OpenAI Plus, or Google AI subscriptions personally. Writes code daily, uses AI coding assistants heavily, and resents paying per-token API charges for tasks their subscription already covers.

## Goals and Motivations

- Automate repetitive coding tasks (refactoring, test generation, doc writing) without per-MTok API costs
- Run multi-step workflows (edit → test → iterate) under their existing subscription
- Get structured, machine-readable responses from AI rather than freeform chat output
- Maintain a single subscription rather than subscribing to multiple AI APIs

## Frustrations and Pain Points

- Anthropic bans consumer-plan OAuth tokens for API access — no way to programmatically use a Pro/Max subscription
- Per-token API billing is unpredictable and expensive for tool-heavy workflows
- Claude Code gives great interactive results but can't be scripted without `claude -p` hacks
- Existing tools (OpenClaw) provide basic CLI reuse but no structured protocol or verification

## Behavioral Patterns

- Uses Claude Code interactively for hours, then wants to automate the same patterns
- Prefers local-first tools over cloud services
- Familiar with tmux, terminal multiplexers, and CLI workflows
- Writes scripts and wrappers around every tool they use regularly

## Context of Use

Local development machine. Terminal-centric workflow. Fires up Claude Code in tmux, interacts with it for hours. Wants to programmatically invoke the same session rather than opening a new one or paying per-token.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-19 | -- | Initial creation |
