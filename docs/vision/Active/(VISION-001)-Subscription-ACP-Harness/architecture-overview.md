# Subscription ACP Harness — Architecture Overview

## System Context

```mermaid
graph TB
    subgraph "Developer Machine"
        Caller["Caller<br/>(script, CI, agent)"]
        API["ACP REST API<br/>localhost:8420"]
        Router["Command Router"]
        Pool["Session Pool"]
        S1["Session 1<br/>tmux+claude"]
        S2["Session 2<br/>tmux+claude"]
        S3["Session N<br/>tmux+claude"]
        VL["Verification Loop"]
        Config["Configuration<br/>harness.yaml"]
    end

    subgraph "Provider (Anthropic)"
        Claude["Claude Code<br/>Subscription OAuth"]
    end

    Caller -->|ACP JSON| API
    API -->|validate + route| Router
    Router -->|dispatch| Pool
    Pool --> S1
    Pool --> S2
    Pool --> S3
    S1 -->|subscription auth| Claude
    S2 -->|subscription auth| Claude
    S3 -->|subscription auth| Claude
    S1 -->|raw output| Router
    Router -->|ACP response| API
    API -->|JSON| Caller
    API -->|verify calls| VL
    VL -->|loop back| Router
    Config -.->|pool size, timeout, auth| Pool
    Config -.->|loop limit| VL
```

## Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| ACP REST API | HTTP surface, schema validation, request routing |
| Command Router | Queue, dispatch, output capture, timeout/retry |
| Session Pool | Lifecycle management, health checking, rotation |
| Verification Loop | Post-call verification, retro, loop-back, teardown |
| Configuration | Auth method, provider settings, pool parameters |

## Data Flow

1. Caller sends `POST /acp/call` with ACP request
2. API validates schema, passes to Command Router
3. Router selects an `Idle` session from the pool
4. Router injects sentinel-wrapped payload via `tmux send-keys`
5. Router polls `tmux capture-pane` until end sentinel detected
6. Router parses output, constructs ACP response
7. API returns response to caller
8. If `type: verify`, Verification Loop wraps steps 2-7 with retro and loop-back