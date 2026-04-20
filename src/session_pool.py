import asyncio
import logging
from typing import Optional

from config import HarnessConfig, SessionState
from session_lifecycle import ClaudeSession, SessionLifecycle

logger = logging.getLogger("acp-harness")


class SessionPool:
    def __init__(self, lifecycle: SessionLifecycle, config: HarnessConfig):
        self.lifecycle = lifecycle
        self.config = config
        self._health_task: Optional[asyncio.Task] = None
        self._rotation_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        self._running = True
        for _ in range(self.config.pool_min_sessions):
            session = await self.lifecycle.start_session()
            if session.state == SessionState.FAILED:
                logger.error("Initial session failed to start")
            else:
                logger.info("Started session %s", session.session_id)
        self._health_task = asyncio.create_task(self._health_check_loop())
        self._rotation_task = asyncio.create_task(self._rotation_loop())

    async def stop(self):
        self._running = False
        for task in (self._health_task, self._rotation_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        for session in self.lifecycle.get_all_sessions():
            await self.lifecycle.kill_session(session)

    async def _health_check_loop(self):
        while self._running:
            await asyncio.sleep(self.config.health_check_interval)
            await self._check_all()

    async def _rotation_loop(self):
        while self._running:
            await asyncio.sleep(300)
            max_age = self.config.max_session_age_hours * 3600
            for session in self.lifecycle.get_all_sessions():
                if (
                    session.state in (SessionState.IDLE, SessionState.READY)
                    and session.uptime_seconds > max_age
                ):
                    logger.info(
                        "Rotating session %s (age: %.1fh)",
                        session.session_id,
                        session.uptime_seconds / 3600,
                    )
                    await self.lifecycle.kill_session(session)
                    await self._ensure_minimum()

    async def _check_all(self):
        for session in self.lifecycle.get_all_sessions():
            if session.state == SessionState.ACTIVE:
                continue
            if session.state in (
                SessionState.STARTING,
                SessionState.READY,
                SessionState.IDLE,
            ):
                alive = await self._probe(session)
                if not alive:
                    logger.warning("Session %s failed health check", session.session_id)
                    await self._reconnect_or_replace(session)

    async def _probe(self, session: ClaudeSession) -> bool:
        import subprocess

        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session.tmux_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _reconnect_or_replace(self, session: ClaudeSession):
        new_session = await self.lifecycle.reconnect_session(session)
        if new_session.state == SessionState.FAILED:
            await self.lifecycle.kill_session(new_session)
            await self._ensure_minimum()

    async def _ensure_minimum(self):
        healthy = len(
            [
                s
                for s in self.lifecycle.get_all_sessions()
                if s.state
                in (SessionState.READY, SessionState.IDLE, SessionState.ACTIVE)
            ]
        )
        deficit = self.config.pool_min_sessions - healthy
        for _ in range(max(0, deficit)):
            session = await self.lifecycle.start_session()
            if session.state == SessionState.FAILED:
                logger.error("Failed to start replacement session")

    @property
    def status(self) -> dict:
        sessions = self.lifecycle.get_all_sessions()
        state_counts = {}
        auth_counts = {}
        for s in sessions:
            state_counts[s.state.value] = state_counts.get(s.state.value, 0) + 1
            auth_counts[s.auth_method.value] = (
                auth_counts.get(s.auth_method.value, 0) + 1
            )
        healthy = sum(
            1
            for s in sessions
            if s.state in (SessionState.READY, SessionState.IDLE, SessionState.ACTIVE)
        )
        return {
            "total": len(sessions),
            "healthy": healthy,
            "state_breakdown": state_counts,
            "auth_distribution": auth_counts,
        }
