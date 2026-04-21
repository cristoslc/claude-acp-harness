import os
import enum
from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class AuthMethod(str, enum.Enum):
    SUBSCRIPTION_OAUTH = "subscription_oauth"
    API_KEY = "api_key"
    CLAUDE_SETUP_TOKEN = "claude_setup_token"


class ProviderType(str, enum.Enum):
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENAI = "openai"


class SessionState(str, enum.Enum):
    STARTING = "starting"
    READY = "ready"
    ACTIVE = "active"
    IDLE = "idle"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    KILLED = "killed"


class ExecutionMode(str, enum.Enum):
    TMUX = "tmux"
    PRINT = "print"


class HarnessConfig(BaseSettings):
    pool_min_sessions: int = Field(default=2, alias="POOL_MIN_SESSIONS")
    health_check_interval: int = Field(default=30, alias="HEALTH_CHECK_INTERVAL")
    command_timeout: int = Field(default=120, alias="COMMAND_TIMEOUT")
    max_session_age_hours: int = Field(default=4, alias="MAX_SESSION_AGE_HOURS")
    max_reconnect_retries: int = Field(default=3, alias="MAX_RECONNECT_RETRIES")
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8420, alias="API_PORT")
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.PRINT, alias="EXECUTION_MODE"
    )
    preference_auth: AuthMethod = Field(
        default=AuthMethod.SUBSCRIPTION_OAUTH, alias="PREFERENCE_AUTH"
    )
    preference_provider: ProviderType = Field(
        default=ProviderType.ANTHROPIC, alias="PREFERENCE_PROVIDER"
    )
    claude_executable: str = Field(default="claude", alias="CLAUDE_EXECUTABLE")
    verification_loop_limit: int = Field(default=5, alias="VERIFICATION_LOOP_LIMIT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    reports_dir: str = Field(default="verification-reports", alias="REPORTS_DIR")
    tmux_socket_prefix: str = Field(default="/tmp/tmux-", alias="TMUX_SOCKET_PREFIX")

    model_config = {"env_prefix": "ACP_", "env_file": ".env", "extra": "ignore"}


def detect_auth_method() -> AuthMethod:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return AuthMethod.API_KEY
    if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
        return AuthMethod.CLAUDE_SETUP_TOKEN
    claude_config = Path.home() / ".claude" / "credentials.json"
    if claude_config.exists():
        return AuthMethod.SUBSCRIPTION_OAUTH
    return AuthMethod.SUBSCRIPTION_OAUTH


def load_config(config_path: str = "config/harness.yaml") -> HarnessConfig:
    env_overrides: dict = {}
    if Path(config_path).exists():
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}
        pool = raw.get("pool", {})
        io_cfg = raw.get("io", {})
        claude_cfg = raw.get("claude", {})
        verification = raw.get("verification", {})
        auth_cfg = raw.get("auth", {})
        env_overrides = {
            "POOL_MIN_SESSIONS": pool.get("min_sessions"),
            "HEALTH_CHECK_INTERVAL": pool.get("health_interval"),
            "COMMAND_TIMEOUT": io_cfg.get("command_timeout"),
            "MAX_SESSION_AGE_HOURS": pool.get("max_session_age"),
            "MAX_RECONNECT_RETRIES": pool.get("max_reconnect_retries"),
            "API_HOST": raw.get("api", {}).get("host"),
            "API_PORT": raw.get("api", {}).get("port"),
            "CLAUDE_EXECUTABLE": claude_cfg.get("executable"),
            "VERIFICATION_LOOP_LIMIT": verification.get("loop_limit"),
            "LOG_LEVEL": raw.get("logging", {}).get("level"),
            "REPORTS_DIR": verification.get("reports_dir"),
        }
        if auth_cfg.get("method"):
            env_overrides["PREFERENCE_AUTH"] = auth_cfg["method"]
        if auth_cfg.get("provider"):
            env_overrides["PREFERENCE_PROVIDER"] = auth_cfg["provider"]
        env_overrides = {k: v for k, v in env_overrides.items() if v is not None}
    for k, v in env_overrides.items():
        os.environ.setdefault(f"ACP_{k}", str(v))
    config = HarnessConfig()
    detected = detect_auth_method()
    if (
        config.preference_auth == AuthMethod.SUBSCRIPTION_OAUTH
        and detected == AuthMethod.API_KEY
    ):
        import logging

        logging.getLogger("acp-harness").warning(
            "No subscription OAuth detected — falling back to API key auth. "
            "Per-token billing will apply."
        )
    return config
