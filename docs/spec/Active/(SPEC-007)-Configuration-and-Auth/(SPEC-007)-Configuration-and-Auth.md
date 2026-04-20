---
title: "Configuration and Auth"
artifact: SPEC-007
track: implementable
status: Active
type: feature
author: cristos
created: 2026-04-19
last-updated: 2026-04-19
parent-epic: EPIC-003
parent-initiative: INITIATIVE-001
priority-weight: high
swain-do: required
depends-on:
  - SPEC-001
---

# Configuration and Auth

## Summary

Implement the configuration system that controls auth method (subscription OAuth vs API key), provider settings, pool parameters, and verification tuning. Support Anthropic consumer-plan subscription OAuth as the default auth path.

## Acceptance Criteria

### AC-1: Subscription OAuth Auth
**Given** a user with an Anthropic Pro/Max subscription and Claude Code signed in
**When** the harness starts
**Then** it detects the existing Claude Code OAuth session
**And** uses subscription credentials for all session startup

### AC-2: API Key Fallback
**Given** no subscription OAuth is detected and ANTHROPIC_API_KEY is set
**When** the harness starts
**Then** it uses API key auth with a warning that per-token billing applies

### AC-3: Multi-Provider Config
**Given** configuration for multiple providers
**When** the harness initializes
**Then** it loads provider-specific settings (endpoint, model, auth handler)
**And** sessions are created with the correct provider configuration

### AC-4: Config File
**Given** `config/harness.yaml` exists
**When** the harness loads configuration
**Then** it reads: pool size, health interval, command timeout, auth preferences, provider list
**And** environment variables override file values

### AC-5: Validation
**Given** an invalid or incomplete configuration
**When** the harness starts
**Then** it reports specific errors and exits rather than running with defaults that may cause billing surprises

## Implementation Approach

Use Pydantic Settings for typed configuration with environment variable override support. Auth detection follows Anthropic's token precedence (from SPEC-001). Provider configs are pluggable — Anthropic provider is the default, with a Google provider stub for future OAuth support.

## Scope

- `src/config.py` — Pydantic Settings model, env var overrides, validation
- Update `config/harness.yaml` with new schema
- Auth detection function (reuses SPEC-001)
