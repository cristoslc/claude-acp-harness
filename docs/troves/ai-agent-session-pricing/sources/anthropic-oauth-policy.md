---
source_id: anthropic-oauth-policy
title: "Authentication - Claude Code Docs"
author: Anthropic
url: https://code.claude.com/docs/en/authentication
url2: https://www.reddit.com/r/ClaudeAI/comments/1r8ecyq/anthropic_bans_oauth_tokens_from_consumer_plans/
date: 2026-04-19
fetched: 2026-04-19
type: documentation
freshness_ttl: 7  # days
proxy_used: false
content_hash: "--"
---

# Anthropic OAuth and Authentication Policy (2026)

## Authentication Methods

### Subscription OAuth (Default)
- **Scope**: Claude Pro, Max, Team, and Enterprise users.
- **Behavior**: Claude Code on the Web **always** uses subscription credentials. API keys (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`) are ignored in sandbox environments.
- **CI/CD**: Generate a one-year OAuth token with `claude setup-token` for non-interactive environments (e.g., CI pipelines, scripts).

### API Key Authentication
- **Scope**: Terminal CLI sessions only.
- **Behavior**: API keys (`ANTHROPIC_API_KEY`) take precedence over subscription OAuth if both are present. This can cause authentication failures if the key belongs to a disabled or expired organization.
- **Interactive Mode**: Users are prompted once to approve or decline the key. The choice is remembered and can be toggled later in `/config`.
- **Non-Interactive Mode (`-p`)**: The key is always used when present.

### Token Precedence

1. Cloud provider credentials (if `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, or `CLAUDE_CODE_USE_FOUNDRY` is set).
2. `ANTHROPIC_AUTH_TOKEN` environment variable (sent as `Authorization: Bearer`).
3. `ANTHROPIC_API_KEY` environment variable (sent as `X-Api-Key`).
4. `apiKeyHelper` script output (for dynamic/rotating credentials).
5. `CLAUDE_CODE_OAUTH_TOKEN` environment variable (long-lived OAuth token).
6. Subscription OAuth credentials (default for Pro/Max/Team/Enterprise).

## Policy Changes (2026)

### Ban on OAuth Tokens from Consumer Plans

- **Announcement**: [Reddit: Anthropic bans OAuth tokens from consumer plans in third-party Tools](https://www.reddit.com/r/ClaudeAI/comments/1r8ecyq/anthropic_bans_oauth_tokens_from_consumer_plans/)
- **Scope**: Applies to **Claude Free, Pro, and Max** plans (consumer plans). **Team and Enterprise plans are exempt.**
- **Rationale**: Users were extracting OAuth tokens from Claude Code (which uses OAuth for authentication) and using them outside of Claude Code to access API endpoints with subscription-based usage limits instead of per-token billing.
- **Enforcement**: Anthropic does not technically "ban" tokens but throttles or rejects requests from OAuth tokens tied to consumer plans when used outside of sanctioned integrations (e.g., Claude Code, OpenClaw).
- **Workaround**: Use an **Anthropic API key** for programmatic access. API keys are decoupled from personal usage and offer dedicated allocation.

### Allowed Usage

- **Claude Code**: OAuth tokens are allowed for authentication within Claude Code (CLI, Desktop, Web).
- **OpenClaw**: Anthropic staff confirmed OpenClaw-style Claude CLI reuse (`claude -p`) is sanctioned for this integration unless Anthropic publishes a new policy.
- **API Keys**: The clearest production path for always-on gateway hosts and explicit server-side billing control.

### Best Practices

1. **For Teams/Enterprise**: Use subscription OAuth or API keys.
2. **For CI/CD/Automation**: Use `claude setup-token` to generate a long-lived OAuth token or an API key.
3. **For Consumer Plans**: Avoid OAuth tokens for programmatic API access. Use API keys instead.
4. **Token Rotation**: Rotate API keys and OAuth tokens regularly to minimize blast radius.
5. **Monitoring**: Track token usage and revoke compromised or unused tokens.

## Troubleshooting

- **401 Errors**: OAuth tokens from consumer plans may be throttled or rejected. Migrate to an API key.
- **No API Key Found**: Auth is per-agent. Re-run onboarding for the agent or configure an API key on the gateway host.
- **No Credentials Found**: Run `openclaw models status` to see the active auth profile. Re-run onboarding or configure an API key.
- **Rate-Limit Cooldowns**: Anthropic rate limits can be model-scoped. Add another Anthropic profile or wait for cooldown.
