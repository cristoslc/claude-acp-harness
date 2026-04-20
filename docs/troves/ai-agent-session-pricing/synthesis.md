# Synthesis: AI Agent Session Pricing, OAuth, and Subscription-Based Billing (2026)

## Key Findings

### 1. **OAuth-Based Login for Subscription Access**
- **OpenAI**: Supports OAuth 2.1 for MCP apps, enabling users to authenticate and leverage their ChatGPT subscription benefits (e.g., avoiding per-token billing). Requires hosting protected resource metadata and publishing OAuth metadata from an authorization server.
- **Anthropic**: Allows OAuth tokens for authentication within sanctioned integrations (e.g., Claude Code, OpenClaw). However, **OAuth tokens from consumer plans (Free, Pro, Max) are banned for third-party API access** to prevent bypassing per-token billing. Team and Enterprise plans are exempt.
- **Google**: Supports OAuth 2.0 for Gemini API access, enabling users to authenticate with their Google AI subscription instead of per-token billing. Tools like `opencode-gemini-auth` facilitate this integration.

### 2. **Provider-Specific Policies**

#### OpenAI
- **OAuth Flow**: ChatGPT acts as the client, performing dynamic client registration (DCR) and PKCE for secure token exchange.
- **mTLS**: ChatGPT presents an OpenAI-managed client certificate for TLS connections. Verify the certificate chains to the OpenAI Connectors mTLS intermediate CA and has a SAN of `mtls.connectors.openai.com`.
- **Token Verification**: MCP servers must verify access tokens on each request (signature, issuer, audience, scopes).

#### Anthropic
- **Consumer Plan Restrictions**: OAuth tokens from Free, Pro, and Max plans are throttled or rejected for API access outside of sanctioned integrations (e.g., Claude Code, OpenClaw).
- **Team/Enterprise**: OAuth tokens are allowed for API access.
- **API Keys**: The recommended path for programmatic access, especially for CI/CD and automation.
- **Claude CLI**: OpenClaw and similar tools can reuse Claude CLI sessions (`claude -p`) for OAuth authentication, as this usage is sanctioned by Anthropic.

#### Google
- **OAuth for Subscriptions**: Users with a Google AI subscription can authenticate via OAuth to access Gemini models without per-token billing.
- **API Keys**: Simpler for most use cases but do not leverage subscription benefits.
- **Plugins**: Tools like `opencode-gemini-auth` enable OAuth-based authentication in third-party clients (e.g., Opencode).

### 3. **Workarounds for Per-MTok Billing**

#### OAuth-Based Authentication
- **OpenAI**: Authenticate users via OAuth to leverage ChatGPT subscription benefits. Requires implementing the MCP authorization spec.
- **Anthropic**: Use API keys for programmatic access. OAuth tokens are restricted to sanctioned integrations.
- **Google**: Authenticate via OAuth to use Google AI subscriptions instead of per-token billing.

#### Session-Based Tools
- **OpenClaw**: Reuses Claude CLI sessions for OAuth authentication, enabling persistent sessions and avoiding per-token costs for sanctioned integrations.
- **Opencode**: Supports OAuth plugins (e.g., `opencode-gemini-auth`) to authenticate with Google AI subscriptions.
- **Claude Code**: Uses subscription OAuth credentials by default for Pro, Max, Team, and Enterprise users.

#### Open-Source Tools
- **Opencode**: Supports OAuth-based authentication for Google AI and other providers, enabling subscription-based access.
- **OpenClaw**: Sanctioned for Anthropic OAuth integration, including Claude CLI reuse and API key authentication.

### 4. **Cost Optimization Strategies**

#### Token Minimization
- **Tool Usage**: Minimize unnecessary tool calls (e.g., bash, file read, web fetch) to reduce token accumulation.
- **Prompt Caching**: Use Anthropic’s prompt caching feature (`cacheRetention: "short"` or `"long"`) to reduce repeated token costs for API-key authenticated requests.

#### Session Management
- **Persistent Sessions**: Use tools like OpenClaw and Opencode to maintain persistent sessions, reducing the need for repeated authentication and token-heavy initialization.
- **Sub-Agent Cost Control**: Monitor and limit the number and duration of sub-agents to avoid cost multipliers.

#### Provider-Specific Optimizations
- **Anthropic**:
  - Use `service_tier: "auto"` (via `/fast on`) for priority processing on supported accounts.
  - Enable `context1m: true` for 1M context windows (API keys only).
- **Google**: Use OAuth to leverage Google AI subscriptions instead of per-token billing.
- **OpenAI**: Implement OAuth to avoid per-token costs for MCP apps.

## Points of Agreement
- **OAuth as a Subscription Lever**: All providers (OpenAI, Anthropic, Google) support OAuth for authenticating users and leveraging subscription benefits, though Anthropic restricts OAuth tokens from consumer plans for API access.
- **API Keys for Programmatic Access**: API keys are the recommended path for CI/CD, automation, and server-side billing control, especially for Anthropic.
- **Session Persistence**: Tools like OpenClaw and Opencode enable persistent sessions, reducing token costs associated with repeated initialization.
- **Cost Drivers**: Token accumulation from tool calls and sub-agents is a primary cost driver, outweighing session runtime costs in many cases.

## Points of Disagreement or Uncertainty
- **Anthropic’s Enforcement**: Anthropic’s policy on OAuth token usage is inconsistently enforced. While consumer plan tokens are technically "banned" for third-party API access, the enforcement mechanism (throttling vs. outright rejection) is unclear.
- **OpenAI’s CMID**: Client Metadata Documents (CMID) are in development and not yet widely adopted, leaving dynamic client registration (DCR) as the primary method for OAuth client management.
- **Google’s Subscription Flexibility**: It is unclear whether Google’s OAuth-based subscription access is limited to specific use cases (e.g., Opencode) or broadly applicable to all Gemini API integrations.

## Gaps and Open Questions
- **Anthropic’s Long-Term Policy**: Will Anthropic further restrict OAuth token usage or introduce new authentication methods for consumer plans?
- **OpenAI’s CMID Adoption**: When will CMID be fully adopted, and how will it impact existing OAuth integrations?
- **Google’s OAuth Scope**: Are there limitations on the types of applications that can use OAuth for subscription-based access?
- **Cost Transparency**: How can users accurately predict and monitor token costs, especially in multi-agent or tool-heavy workflows?
- **Provider-Specific Workarounds**: Are there additional tools or frameworks that abstract OAuth-based authentication for subscription access across multiple providers?

## Commercial Offerings: Session-Based Pricing

### Claude Managed Agents (Anthropic)

**Pricing Model**: Two-part billing — tokens + session runtime.
- **Tokens**: Standard Claude API rates (e.g., Opus 4.6: $5/MTok input, $25/MTok output). Prompt caching applies (cache reads at 10% of base input price).
- **Session Runtime**: $0.08 per session-hour, billed by the millisecond. Only accrues while the session is `running`; pauses during `idle`, `rescheduling`, or `terminated`.
- **Web Search**: $10 per 1,000 searches.
- **Code Execution**: Runtime replaces container-hour billing; no double-charging.

**Key Cost Drivers**:
- **Tool Execution Overhead**: Every tool call (bash, file read, web fetch, web search) adds input/output tokens. A research agent with 30+ tool calls can accumulate token costs that dwarf the $0.08/hour runtime.
- **Sub-Agent Cost Multiplier**: Multi-agent coordination (research preview) spawns sub-agents, each with its own token and runtime meter. Cost scales with the number and duration of sub-agents.

**Cost Optimization Strategies**:
- Use appropriate models (Haiku for simple tasks, Sonnet for complex reasoning).
- Implement prompt caching to reduce costs for repeated context.
- Monitor token consumption to identify optimization opportunities.

**Sources**: [anthropic-managed-agents-pricing](sources/anthropic-managed-agents-pricing.md), [anthropic-platform-pricing](sources/anthropic-platform-pricing.md)

---

## Open-Source Tools: Persistent Sessions and Cost Efficiency

### Key Tools

| Tool               | Persistent Sessions | Multi-Agent | Cost Structure               | Key Features                                  |
|--------------------|---------------------|-------------|-----------------------------|-----------------------------------------------|
| **Hermes Agent**   | ✓                   | ✗           | Open source + model costs   | Self-improving skills, cross-session memory, multi-platform, infrastructure-agnostic |
| **OpenClaw**       | ✓                   | ✓           | Open source + model costs   | Multi-channel, cron, memory, MCP, skills, sub-agents, browser automation |
| **CrewAI**         | ✓                   | ✓           | Open source + model costs   | Role-based multi-agent, shared memory         |
| **AutoGen**        | ✓                   | ✓           | Open source + model costs   | Multi-agent conversation, customizable       |
| **LangGraph**      | ✓                   | ✓           | Open source + model costs   | Stateful workflows, DAG-based control        |
| **MemGPT**         | ✓                   | ✗           | Open source + model costs   | Long-term memory, virtual context management  |
| **Steel Browser**  | ✓                   | ✗           | Open source + model costs   | Browser automation, session-backed            |
| **nanobot**        | ✓                   | ✗           | Open source + model costs   | Lightweight, MCP, multi-channel, skills       |

**Cost Optimization Strategies for Open-Source Tools**:
- **Serverless Persistence**: Use Daytona or Modal for bursty workloads. Environment hibernates when idle (costs nearly nothing).
- **Self-Hosted**: Run on a $5 VPS or GPU cluster for steady usage.
- **Memory Management**: Use tools like Redis for memory cleanup in multi-agent setups.
- **Model Choice**: Use smaller models (e.g., Haiku) for simple tasks; larger models (e.g., Opus) for complex reasoning.

**Sources**: [hermes-agent](sources/hermes-agent.md), [awesome-agents-curation](sources/awesome-agents-curation.md), [cost-efficient-tools](sources/cost-efficient-tools.md)

---

## Recommendations

### For Developers
1. **Use OAuth for Subscription Access**:
   - OpenAI: Implement OAuth 2.1 for MCP apps to leverage ChatGPT subscription benefits.
   - Google: Use OAuth to authenticate with Google AI subscriptions for Gemini API access.
   - Anthropic: Use API keys for programmatic access. Reserve OAuth for sanctioned integrations (e.g., Claude Code, OpenClaw).

2. **Minimize Token Costs**:
   - Reduce unnecessary tool calls.
   - Use prompt caching (Anthropic) and session persistence (OpenClaw, Opencode).
   - Monitor token usage and sub-agent costs.

3. **Leverage Open-Source Tools**:
   - Use OpenClaw for Anthropic OAuth integration and session persistence.
   - Use Opencode plugins (e.g., `opencode-gemini-auth`) for Google OAuth authentication.

### For Providers
1. **Clarify Policies**:
   - Anthropic: Provide clearer guidance on OAuth token usage for consumer vs. Team/Enterprise plans.
   - OpenAI: Accelerate CMID adoption to simplify OAuth client management.
   - Google: Clarify the scope of OAuth-based subscription access for the Gemini API.

2. **Improve Cost Transparency**:
   - Provide tools or APIs for real-time token cost monitoring and prediction.
   - Offer granular breakdowns of token costs by tool usage, sub-agents, and session runtime.

3. **Support Open-Source Integrations**:
   - Endorse and document sanctioned integrations (e.g., OpenClaw, Opencode) for OAuth-based authentication.
   - Provide SDKs or libraries to simplify OAuth implementation for third-party tools.
