---
source_id: openai-oauth-authentication
title: "Authentication – Apps SDK | OpenAI Developers"
author: OpenAI
url: https://developers.openai.com/apps-sdk/build/auth
date: 2026-04-19
fetched: 2026-04-19
type: documentation
freshness_ttl: 7  # days
proxy_used: false
content_hash: "--"
---

# Authentication – Apps SDK

## Custom auth with OAuth 2.1

For an authenticated MCP server, you are expected to implement an OAuth 2.1 flow that conforms to the [MCP authorization spec](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization).

### Key Requirements

1. **Host protected resource metadata** on your MCP server:
   - Expose an HTTPS endpoint (e.g., `GET https://your-mcp.example.com/.well-known/oauth-protected-resource`).
   - Return a JSON document describing the resource server and its available authorization servers:
     ```json
     {
       "resource": "https://your-mcp.example.com",
       "authorization_servers": ["https://auth.yourcompany.com"],
       "scopes_supported": ["files:read", "files:write"]
     }
     ```
   - If unauthenticated, return a `401 Unauthorized` with a `WWW-Authenticate` header pointing to the metadata URL.

2. **Publish OAuth metadata** from your authorization server:
   - Expose a well-known discovery document (e.g., `https://auth.yourcompany.com/.well-known/oauth-authorization-server` or `/.well-known/openid-configuration`).
   - Include required fields:
     ```json
     {
       "issuer": "https://auth.yourcompany.com",
       "authorization_endpoint": "https://auth.yourcompany.com/oauth2/v1/authorize",
       "token_endpoint": "https://auth.yourcompany.com/oauth2/v1/token",
       "registration_endpoint": "https://auth.yourcompany.com/oauth2/v1/register",
       "code_challenge_methods_supported": ["S256"]
     }
     ```

3. **Echo the `resource` parameter** throughout the OAuth flow:
   - ChatGPT appends `resource=https%3A%2F%2Fyour-mcp.example.com` to authorization and token requests.
   - Configure your authorization server to include this value in the access token (e.g., as the `aud` claim).

4. **Advertise PKCE support** for ChatGPT:
   - Ensure `code_challenge_methods_supported` includes `S256`.
   - ChatGPT uses PKCE to prevent authorization code replay attacks.

### OAuth Flow

1. ChatGPT queries your MCP server for protected resource metadata.
2. ChatGPT registers itself via dynamic client registration (DCR) with your authorization server.
3. The user authenticates and consents to the requested scopes.
4. ChatGPT exchanges the authorization code for an access token and attaches it to subsequent MCP requests (`Authorization: Bearer <token>`).
5. Your server verifies the token (issuer, audience, expiration, scopes) before executing the tool.

### Client Registration

- **Dynamic Client Registration (DCR)**: ChatGPT registers a fresh OAuth client with your authorization server for each connector, obtaining a unique `client_id`.
- **Client Metadata Documents (CMID)**: In development (expected 2026). ChatGPT will publish a stable document (e.g., `https://openai.com/chatgpt.json`) declaring its OAuth metadata and identity.

### Client Identification

- **mTLS**: ChatGPT presents an OpenAI-managed client certificate when connecting to MCP servers. Verify the certificate chains to the OpenAI Connectors mTLS intermediate CA and has a SAN of `mtls.connectors.openai.com`.
- **IP Allowlisting**: Use OpenAI’s [published egress IP ranges](https://openai.com/chatgpt-connectors.json).
- **No Support**: Machine-to-machine OAuth grants (e.g., client credentials), custom API keys, or customer-provided mTLS certificates.

### Mutual TLS (mTLS)

ChatGPT presents an OpenAI-managed client certificate for TLS connections. Configure your application to trust the OpenAI certificate chain:

- [OpenAI Root CA](https://developers.openai.com/apps-sdk/mtls/openai-root-ca.pem)
- [OpenAI Connectors mTLS Intermediate CA](https://developers.openai.com/apps-sdk/mtls/openai-connectors-mtls-ca.pem)

**Validation Steps**:
1. Verify the leaf certificate chains to the OpenAI Connectors mTLS intermediate CA.
2. Verify the leaf certificate is valid for client authentication.
3. Verify the leaf certificate’s SAN is `mtls.connectors.openai.com`.

Use mTLS to authenticate ChatGPT as the MCP client. Continue using OAuth 2.1 to authenticate the end user.

### Token Verification

Your MCP server must verify the access token on each request:

1. Fetch the signing keys from your authorization server (JWKS).
2. Verify the token’s signature, issuer (`iss`), and audience (`aud`).
3. Reject expired tokens (`exp`) or tokens not yet valid (`nbf`).
4. Confirm the token includes the required scopes.
5. If verification fails, return `401 Unauthorized` with a `WWW-Authenticate` header pointing to your protected-resource metadata.

### Testing and Rollout

- **Local Testing**: Use a development tenant for short-lived tokens.
- **Dogfood**: Gate access to trusted testers before broad rollout.
- **Rotation**: Plan for token revocation, refresh, and scope changes.
- **Debugging**: Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to walk through OAuth steps.