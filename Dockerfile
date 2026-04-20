# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    tmux \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code globally via npm
RUN npm install -g @anthropic-ai/claude-code

# Set working directory
WORKDIR /app

# Install uv for fast Python package management
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency files first for layer caching
COPY pyproject.toml ./

# Install Python dependencies using uv
RUN uv pip install --system -e ".[observability]"

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Create directories for tmux sessions and logs
RUN mkdir -p /app/.tmux-sessions /app/logs

# Expose the API port
EXPOSE 8000

# NOTE: Claude Code authentication must be done interactively
# Users need to run: docker run -it <image> claude --auth
# Or exec into a running container and run: claude --auth
# The auth token is stored in ~/.config/claude/

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/acp/status || exit 1

# Default command runs the ACP harness
CMD ["uv", "run", "--with", "fastapi,uvicorn", "python", "-m", "uvicorn", "src.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
