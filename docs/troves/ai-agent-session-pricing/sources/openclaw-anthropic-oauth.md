---
source_id: openclaw-anthropic-oauth
 title: "Anthropic - OpenClaw"
author: OpenClaw
url: https://docs.openclaw.ai/providers/anthropic
url2: https://docs.openclaw.ai/concepts/oauth
date: 2026-04-19
fetched: 2026-04-19
type: documentation
freshness_ttl: 7  # days
proxy_used: false
content_hash: "--"
---

# OpenClaw Anthropic OAuth Integration (2026)

## Overview

OpenClaw supports **subscription-based authentication** via OAuth for providers that offer it, including Anthropic. This allows users to leverage their Claude Pro, Max, Team, or Enterprise subscriptions for API access instead of per-token billing.

## Anthropic OAuth Support

### Allowed Usage

- **Claude CLI Reuse**: OpenClaw treats Claude CLI reuse (`claude -p`) as sanctioned for integration unless Anthropic publishes a new policy.
- **API Key Auth**: Anthropic API keys remain the clearest production path for always-on gateway hosts and explicit server-side billing control.
- **Legacy Token Auth**: Anthropic token auth (`sk-ant-oat-*`) is supported but may expire or be revoked. Migrate to API keys for new setups.

### Configuration

#### Option A: Anthropic API Key

1. **Setup**:
   ```bash
   openclaw onboard
   # Choose: Anthropic API key
   ```

2. **Config Snippet**:
   ```json
   {
     "env": { "ANTHROPIC_API_KEY": "sk-ant-..." },
     "agents": { "defaults": { "model": { "primary": "anthropic/claude-opus-4-6" } } }
   }
   ```

#### Option B: Claude CLI Backend

- **Behavior**: OpenClaw reuses the bundled Anthropic `claude-cli` backend for OAuth authentication.
- **Setup**: No additional configuration is required if Claude CLI is already logged in.
- **Runtime**: OpenClaw automatically detects and reuses the Claude CLI session.

### Fast Mode (Anthropic API)

- **Behavior**: OpenClaw’s `/fast` toggle maps to Anthropic’s `service_tier` parameter.
  - `/fast on` → `service_tier: "auto"`
  - `/fast off` → `service_tier: "standard_only"`
- **Default**: `fastMode: true` for `anthropic/claude-sonnet-4-6`.
- **Limitations**:
  - Only applies to direct `api.anthropic.com` requests. Proxies/gateways are unaffected.
  - Explicit `serviceTier`/`service_tier` model params override `/fast`.
  - Accounts without Priority Tier capacity may resolve to `standard` even with `service_tier: "auto"`.

### Prompt Caching (Anthropic API)

- **Behavior**: OpenClaw supports Anthropic’s prompt caching feature for API-key authenticated requests.
- **Configuration**: Use the `cacheRetention` parameter:
  - `none`: No caching.
  - `short`: 5-minute cache (default for API Key auth).
  - `long`: 1-hour cache.

  ```json
  {
    "agents": {
      "defaults": {
        "models": {
          "anthropic/claude-opus-4-6": {
            "params": { "cacheRetention": "long" }
          }
        }
      }
    }
  }
  ```

- **Defaults**: `cacheRetention: "short"` for Anthropic API Key auth.
- **Overrides**: Per-agent `params` override model-level defaults.

### 1M Context Window (Anthropic Beta)

- **Behavior**: Enable Anthropic’s 1M context window beta with `params.context1m: true`.
- **Configuration**:
  ```json
  {
    "agents": {
      "defaults": {
        "models": {
          "anthropic/claude-opus-4-6": {
            "params": { "context1m": true }
          }
        }
      }
    }
  }
  ```

- **Mapping**: OpenClaw maps this to `anthropic-beta: context-1m-2025-08-07`.
- **Limitations**:
  - Only activates when `params.context1m` is explicitly `true`.
  - Requires Anthropic to allow long-context usage on the credential.
  - Rejected for legacy Anthropic token auth (`sk-ant-oat-*`). OpenClaw falls back to the standard context window and logs a warning.

## Troubleshooting

- **401 Errors**: Legacy Anthropic token auth may expire or be revoked. Migrate to an API key.
- **No API Key**: Auth is per-agent. Re-run onboarding or configure an API key.
- **Context1m Rejected**: Legacy token auth does not support 1M context. Use an API key.
- **Fast Mode Unavailable**: `/fast` is ignored for proxied requests. Use direct `api.anthropic.com` requests.
