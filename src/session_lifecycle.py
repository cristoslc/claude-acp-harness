import asyncio
import enum
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field

from config import AuthMethod, SessionState, detect_auth_method

logger = logging.getLogger("acp-harness")


@dataclass
class ClaudeSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tmux_name: str = ""
    state: SessionState = SessionState.STARTING
    auth_method: AuthMethod = AuthMethod.SUBSCRIPTION_OAUTH
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    command_count: int = 0
    tmux_socket: str = ""

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self.started_at

    @property
    def idle_seconds(self) -> float:
        return time.time() - self.last_activity


class SessionLifecycle:
    def __init__(
        self, claude_executable: str = "claude", max_reconnect_retries: int = 3
    ):
        self.claude_executable = claude_executable
        self.max_reconnect_retries = max_reconnect_retries
        self._sessions: dict[str, ClaudeSession] = {}

    async def start_session(self, session_id: str | None = None) -> ClaudeSession:
        import subprocess

        sid = session_id or str(uuid.uuid4())[:8]
        tmux_name = f"claude-acp-{sid}"
        session = ClaudeSession(
            session_id=sid,
            tmux_name=tmux_name,
            auth_method=detect_auth_method(),
        )
        try:
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", tmux_name, "bash"],
                check=True,
                capture_output=True,
                text=True,
            )
            await asyncio.sleep(0.5)
            subprocess.run(
                ["tmux", "send-keys", "-t", tmux_name, self.claude_executable, "Enter"],
                capture_output=True,
                text=True,
            )
            session.state = SessionState.STARTING
            await asyncio.sleep(2)
            ready = await self._check_session_ready(tmux_name)
            session.state = SessionState.READY if ready else SessionState.FAILED
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error("Failed to start session %s: %s", sid, e)
            session.state = SessionState.FAILED
        self._sessions[sid] = session
        return session

    async def _check_session_ready(self, tmux_name: str) -> bool:
        import subprocess

        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", tmux_name],
                capture_output=True,
                text=True,
            )
            output = result.stdout.lower()
            return "claude" in output or ">" in output
        except Exception:
            return False

    async def dispatch_command(self, session: ClaudeSession, command: str) -> bool:
        import subprocess

        if session.state not in (SessionState.READY, SessionState.IDLE):
            logger.warning(
                "Cannot dispatch to session %s in state %s",
                session.session_id,
                session.state,
            )
            return False
        session.state = SessionState.ACTIVE
        session.last_activity = time.time()
        try:
            subprocess.run(
                ["tmux", "send-keys", "-t", session.tmux_name, command, "Enter"],
                capture_output=True,
                text=True,
            )
            session.command_count += 1
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error("Failed to dispatch to session %s: %s", session.session_id, e)
            session.state = SessionState.RECONNECTING
            return False

    async def mark_idle(self, session: ClaudeSession):
        session.state = SessionState.IDLE
        session.last_activity = time.time()

    async def kill_session(self, session: ClaudeSession):
        import subprocess

        session.state = SessionState.KILLED
        try:
            subprocess.run(
                ["tmux", "kill-session", "-t", session.tmux_name],
                capture_output=True,
                text=True,
            )
        except Exception:
            pass
        self._sessions.pop(session.session_id, None)

    async def reconnect_session(self, session: ClaudeSession) -> ClaudeSession:
        import subprocess

        session.state = SessionState.RECONNECTING
        for attempt in range(self.max_reconnect_retries):
            try:
                subprocess.run(
                    ["tmux", "kill-session", "-t", session.tmux_name],
                    capture_output=True,
                    text=True,
                )
            except Exception:
                pass
            await asyncio.sleep(1 + attempt)
            new_session = await self.start_session(session.session_id)
            if new_session.state == SessionState.READY:
                return new_session
            logger.warning(
                "Reconnect attempt %d/%d failed for %s",
                attempt + 1,
                self.max_reconnect_retries,
                session.session_id,
            )
        session.state = SessionState.FAILED
        return session

    def get_session(self, session_id: str) -> Optional[ClaudeSession]:
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> list[ClaudeSession]:
        return list(self._sessions.values())

    def get_sessions_by_state(self, state: SessionState) -> list[ClaudeSession]:
        return [s for s in self._sessions.values() if s.state == state]

    def session_status(self, session: ClaudeSession) -> dict:
        return {
            "session_id": session.session_id,
            "tmux_name": session.tmux_name,
            "state": session.state.value,
            "auth_method": session.auth_method.value,
            "uptime_seconds": round(session.uptime_seconds, 1),
            "idle_seconds": round(session.idle_seconds, 1),
            "command_count": session.command_count,
            "last_activity": session.last_activity,
        }
