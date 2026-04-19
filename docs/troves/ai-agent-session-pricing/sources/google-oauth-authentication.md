---
source_id: google-oauth-authentication
title: "Authentication with OAuth quickstart | Gemini API | Google AI for Developers"
author: Google
url: https://ai.google.dev/gemini-api/docs/oauth
url2: https://syntackle.com/blog/google-gemini-oauth-plugin-for-opencode-use-your-google-ai-subscription-instead-of-api-pricing/
date: 2026-04-19
fetched: 2026-04-19
type: documentation
freshness_ttl: 7  # days
proxy_used: false
content_hash: "--"
---

# Google AI OAuth Authentication (2026)

## OAuth 2.0 for Gemini API

### Overview

- **Purpose**: OAuth 2.0 enables secure authentication for Google AI services, including the Gemini API.
- **Use Case**: Authenticate users to leverage Google AI subscriptions instead of API-based per-token billing.

### Setup Steps

1. **Configure OAuth Consent Screen**
   - Navigate to the [Google Cloud Platform (GCP) Console](https://console.cloud.google.com/).
   - Open the **OAuth consent screen**.
   - Provide an app name, select scopes (e.g., `https://www.googleapis.com/auth/cloud-platform`), and add branding details.

2. **Create OAuth Credentials**
   - In the GCP Console, create an **OAuth 2.0 Client ID**.
   - Add authorized redirect URIs (e.g., `https://your-app.example.com/auth/callback`).

3. **Download Client Secret**
   - Download the JSON file containing the client secret (e.g., `client_secret_<identifier>.json`).
   - Rename it to `client_secret.json` and move it to your working directory.

4. **Generate Credentials**
   - Use the `gcloud` CLI to convert the client secret into usable credentials:
     ```bash
     gcloud auth application-default login --client-id-file=client_secret.json
     ```

### OAuth Flow

1. **Authorization Request**
   - Redirect the user to the Google OAuth 2.0 authorization endpoint:
     ```
     https://accounts.google.com/o/oauth2/v2/auth?client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>&response_type=code&scope=https://www.googleapis.com/auth/cloud-platform
     ```

2. **Token Exchange**
   - Exchange the authorization code for an access token and refresh token:
     ```bash
     curl -X POST https://oauth2.googleapis.com/token \
          -d "code=<AUTHORIZATION_CODE>" \
          -d "client_id=<CLIENT_ID>" \
          -d "client_secret=<CLIENT_SECRET>" \
          -d "redirect_uri=<REDIRECT_URI>" \
          -d "grant_type=authorization_code"
     ```

3. **API Requests**
   - Attach the access token to API requests:
     ```bash
     curl -X GET https://aiplatform.googleapis.com/v1/projects/<PROJECT_ID>/locations/<LOCATION>/endpoints/<ENDPOINT_ID> \
          -H "Authorization: Bearer <ACCESS_TOKEN>"
     ```

### Subscription-Based Access

- **Google AI Subscription**: Users with a Google AI subscription can authenticate via OAuth to access Gemini models without incurring per-token API costs.
- **Opencode Plugin**: The [`opencode-gemini-auth`](https://github.com/syntackle/opencode-gemini-auth) plugin enables Opencode users to authenticate with Google OAuth and use their Google AI subscription instead of API pricing.
  - **Setup**: Install the plugin and configure it with your Google OAuth credentials.
  - **Usage**: Authenticate via Google OAuth in Opencode to access Gemini models.

### Best Practices

1. **Use API Keys for Simplicity**: For most use cases, API keys are simpler and sufficient for accessing the Gemini API.
2. **OAuth for Subscription Access**: Use OAuth when leveraging Google AI subscriptions to avoid per-token billing.
3. **Token Management**: Store OAuth tokens securely and implement token rotation to minimize security risks.
4. **Scope Minimization**: Request only the scopes necessary for your application to adhere to the principle of least privilege.
5. **Error Handling**: Implement robust error handling for token expiration, revocation, and scope changes.