# ACP Harness

Agent Communication Protocol (ACP) Harness for Claude Code with tmux I/O management and verification loops.

## Overview

The ACP Harness provides a structured way to invoke Claude Code via a REST API, managing persistent tmux-based sessions and implementing the INITIATIVE-022 verification pattern for automated feedback loops.

## Quick Start

### Prerequisites

- Python 3.8+
- tmux
- Claude Code (`claude`) - must be authenticated
- uv (recommended for package management)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd claude-acp-harness

# Install dependencies with uv
uv sync

# Or install with pip
pip install -e ".[dev,observability]"
```

### Running Locally

```bash
# Start the server
uv run python -m uvicorn src.rest_api:app --reload --host 0.0.0.0 --port 8000

# Or use the CLI
claude-harness --config config/harness.yaml
```

The API will be available at `http://localhost:8000` with interactive documentation at `/docs`.

## Configuration

Configuration can be provided via:

1. Environment variables (prefixed with `ACP_`)
2. YAML config file (`config/harness.yaml`)
3. Default values

### Environment Variables

```bash
export ACP_POOL_MIN_SESSIONS=2
export ACP_COMMAND_TIMEOUT=120
export ACP_API_HOST=127.0.0.1
export ACP_API_PORT=8000
export ACP_LOG_LEVEL=INFO
```

### YAML Config

```yaml
# config/harness.yaml
pool:
  min_sessions: 2
  health_interval: 30
  max_session_age: 4
  max_reconnect_retries: 3

io:
  command_timeout: 120

claude:
  executable: claude

api:
  host: 127.0.0.1
  port: 8000

logging:
  level: INFO

verification:
  loop_limit: 5
  reports_dir: verification-reports

auth:
  method: subscription_oauth
  provider: anthropic
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/acp/call` | POST | Submit an ACP request to Claude |
| `/acp/verify` | POST | Submit request with verification loop |
| `/acp/status` | GET | Get current harness status |
| `/acp/reports` | GET | Get recent verification reports |
| `/metrics` | GET | Prometheus metrics |
| `/health` | GET | Health check |
| `/docs` | GET | OpenAPI documentation (Swagger UI) |
| `/redoc` | GET | OpenAPI documentation (ReDoc) |

## Docker Deployment

### Building

```bash
docker build -t claude-acp-harness:latest .
```

**Important:** You must authenticate Claude Code on the host machine before running the container:

```bash
claude --auth
```

This creates credentials in `~/.config/claude/` which are mounted into the container.

### Running with Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Run

```bash
docker run -d \
  --name claude-acp-harness \
  -p 8000:8000 \
  -v ~/.config/claude:/root/.config/claude:ro \
  -v $(pwd)/logs:/app/logs \
  claude-acp-harness:latest
```

## Authentication

The harness supports multiple authentication methods for AI service providers:

### Default: Subscription OAuth (Recommended)

Claude Code handles authentication internally. Simply run:

```bash
claude --auth
```

This is the recommended approach as it uses subscription-based billing.

### Fallback: API Key

If no subscription OAuth is detected, the harness can fall back to API key authentication:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**Warning:** This uses per-token billing which can be more expensive for high-volume usage.

## Monitoring

### Logging

Structured JSON logging is enabled by default. Logs include:

- Request/response traces
- Session lifecycle events
- Verification loop results
- Error details with stack traces

### Metrics

Prometheus metrics are exposed at `/metrics`:

- `acp_requests_total` - Total requests by method/endpoint/status
- `acp_request_duration_seconds` - Request latency histogram
- `acp_active_sessions` - Current active Claude sessions
- `acp_session_errors_total` - Session error counts
- `acp_commands_dispatched_total` - Commands sent to Claude
- `acp_verifications_total` - Verification cycles completed

### Tracing

OpenTelemetry tracing is available when `opentelemetry` extras are installed. Configure via environment variables:

```bash
export OTEL_SERVICE_NAME=claude-acp-harness
export OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4317
```

## Development

### Pre-commit Hooks

```bash
# Install pre-commit
uv add --dev pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks include:
- Trailing whitespace check
- YAML/JSON validation
- Ruff linting and formatting
- MyPy type checking
- Pytest test suite

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_acp_harness.py::test_acp_protocol
```

### Benchmarking

```bash
# Run performance benchmarks
uv run python scripts/benchmark.py

# Custom parameters
uv run python scripts/benchmark.py \
    --requests 100 \
    --concurrency 10 \
    --payload-size 1000 \
    --output benchmark-results.json
```

## Architecture

```
┌─────────────────┐
│   REST API      │  FastAPI endpoints
│   /acp/call     │
│   /acp/verify   │
└────────┬────────┘
         │
┌────────▼────────┐
│ Command Router  │  Async queue & dispatch
│                 │  Timeout & retry logic
└────────┬────────┘
         │
┌────────▼────────┐
│ Session Pool    │  Health checks & rotation
│ Manager         │  Auto-reconnect logic
└────────┬────────┘
         │
┌────────▼────────┐
│ tmux Sessions   │  Persistent Claude Code
│                 │  processes
└─────────────────┘
```

## ACP Protocol

The Agent Communication Protocol uses JSON-encoded requests with sentinel markers:

### Request Format

```json
{
  "id": "uuid-v4",
  "type": "prompt",
  "payload": "Your prompt to Claude...",
  "timeout": 120,
  "metadata": {}
}
```

### Response Format

```json
{
  "id": "uuid-v4",
  "status": "success",
  "result": "Claude's response...",
  "duration_ms": 5234,
  "metadata": {}
}
```

### Sentinel Markers

Requests are wrapped with unique markers to delimit Claude's output:

```
### ACP_START:{request_id} ###
{payload}
### ACP_END:{request_id} ###
```

## Verification Loop (INITIATIVE-022)

The verification loop implements automated quality checks:

1. Execute initial request
2. Analyze response for gaps
3. Generate follow-up prompts
4. Iterate until verification passes
5. Generate final report

Access via `/acp/verify` endpoint.

## License

MIT
