---
title: "Automation Operator"
artifact: PERSONA-002
track: standing
status: Active
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
linked-artifacts:
  - VISION-001
depends-on-artifacts: []
---

# Automation Operator

## Archetype Label

CI/CD Orchestrator

## Demographic Summary

DevOps engineer or team lead, 30-50, moderate-to-high technical proficiency. Manages automated pipelines and wants AI-assisted verification without adding per-run API charges to CI budgets.

## Goals and Motivations

- Run AI-assisted code review, test generation, and verification as part of CI pipelines
- Leverage team member subscriptions rather than maintaining separate API billing
- Get pass/fail verdicts from AI verification loops, not freeform text
- Integrate AI verification into existing toolchains (GitHub Actions, Makefiles)

## Frustrations and Pain Points

- CI pipelines that call AI APIs rack up unpredictable per-token costs
- No way to gate merges on AI verification without an API key and per-token billing
- Verification loops from INITIATIVE-022 need an AI backend — currently that means API keys
- Team subscriptions are underutilized for automation because they require interactive sessions

## Behavioral Patterns

- Configures CI/CD pipelines with strict cost controls
- Prefers deterministic tools over probabilistic ones, but accepts AI when gated properly
- Uses verification loops with clear pass/fail outcomes
- Monitors costs closely and budgets per-pipeline AI spend

## Context of Use

CI/CD runner or dedicated automation machine. Non-interactive. Needs long-lived sessions that can persist across multiple pipeline runs. May use `claude setup-token` for long-lived OAuth tokens.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-19 | -- | Initial creation |
