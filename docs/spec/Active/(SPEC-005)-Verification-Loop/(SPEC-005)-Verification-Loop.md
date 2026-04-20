---
title: "Verification Loop"
artifact: SPEC-005
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
  - SPEC-002
  - SPEC-003
---

# Verification Loop

## Summary

Implement the INITIATIVE-022 automated verification loop pattern for ACP harness calls. After implementation, verification design runs against the current intent snapshot. Failure triggers a retro, then loops back. The loop iterates up to a configurable limit before escalating.

## Acceptance Criteria

### AC-1: Post-Call Verification
**Given** an ACP call of type `verify` completes
**When** the harness receives the result
**Then** it runs verification design against the current intent snapshot
**And** verification checks alignment with current SPEC acceptance criteria

### AC-2: Failure Loop-Back
**Given** verification fails
**When** the failure is categorized as small or medium gap
**Then** the harness re-dispatches the ACP call with retro feedback
**And** increments the cycle counter

### AC-3: Cycle Limit
**Given** the verification loop counter reaches the configured limit (default: 5)
**When** verification still fails
**Then** the harness escalates to the operator with a teardown report
**And** returns `status: escalation_required`

### AC-4: Teardown Report
**Given** the verification loop completes (pass or escalation)
**When** the harness generates the teardown report
**Then** it includes: agent decisions per cycle, verification history, test design, and results
**And** the report is saved to `verification-reports/<timestamp>.json`

### AC-5: Reconciliation Spectrum
**Given** a verification failure
**When** the gap is classified
**Then** small gaps add a ticket, medium gaps update the SPEC or ADR, large gaps escalate

## Implementation Approach

Build a `VerificationLoop` class that wraps ACP calls with pre/post verification. Use the ACP protocol (SPEC-002) for verification requests. The retro step produces structured feedback injected into the next cycle's prompt. Teardown reports are JSON documents.

## Scope

- `src/verification_loop.py` — loop, retro, reconciliation, teardown report
- `verification-reports/` directory for output
