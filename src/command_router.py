import asyncio
import logging
import subprocess
import time
from collections import deque
from typing import Optional

from acp_protocol import (
    ACPRequest,
    ACPResponse,
    ACPStatus,
    parse_response,
    wrap_with_sentinels,
)
from config import ExecutionMode, HarnessConfig, SessionState
from direct_executor import DirectExecutor
from session_lifecycle import ClaudeSession, SessionLifecycle

logger = logging.getLogger("acp-harness")


class PendingRequest:
    def __init__(self, request: ACPRequest, future: asyncio.Future):
        self.request = request
        self.future = future
        self.queued_at = time.time()


class CommandRouter:
    def __init__(
        self,
        lifecycle: SessionLifecycle,
        default_timeout: int = 120,
        config: Optional[HarnessConfig] = None,
    ):
        self.lifecycle = lifecycle
        self.default_timeout = default_timeout
        self.config = config
        self._queue: deque[PendingRequest] = deque()
        self._active_calls: dict[str, ClaudeSession] = {}
        self._call_history: list[dict] = []
        self._running = False
        self._dispatcher_task: Optional[asyncio.Task] = None
        self._direct_executor: Optional[DirectExecutor] = None

        if config and config.execution_mode == ExecutionMode.PRINT:
            self._direct_executor = DirectExecutor(config)

    async def start(self) -> None:
        self._running = True
        if self._direct_executor:
            logger.info("command_router_started", mode="print")
        else:
            self._dispatcher_task = asyncio.create_task(self._dispatch_loop())
            logger.info("command_router_started", mode="tmux")

    async def stop(self) -> None:
        self._running = False
        if self._dispatcher_task:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass

    async def submit(self, request: ACPRequest) -> ACPResponse:
        if self._direct_executor:
            response = await self._direct_executor.execute(request)
            self._record_call(request, response)
            return response

        future: asyncio.Future[ACPResponse] = asyncio.get_event_loop().create_future()
        pending = PendingRequest(request, future)
        self._queue.append(pending)
        return await asyncio.wait_for(future, timeout=request.timeout + 30)

    async def _dispatch_loop(self):
        while self._running:
            if self._queue:
                idle = self.lifecycle.get_sessions_by_state(SessionState.IDLE)
                ready = self.lifecycle.get_sessions_by_state(SessionState.READY)
                available = idle + ready
                if available:
                    pending = self._queue.popleft()
                    session = available[0]
                    try:
                        response = await self._execute(session, pending.request)
                        if not pending.future.done():
                            pending.future.set_result(response)
                    except Exception as e:
                        if not pending.future.done():
                            pending.future.set_result(
                                ACPResponse(
                                    id=pending.request.id,
                                    status=ACPStatus.FAILURE,
                                    error=str(e),
                                )
                            )
                else:
                    await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(0.2)

    async def _execute(
        self, session: ClaudeSession, request: ACPRequest
    ) -> ACPResponse:
        self._active_calls[request.id] = session
        wrapped = wrap_with_sentinels(request)
        dispatched = await self.lifecycle.dispatch_command(session, wrapped)
        if not dispatched:
            self._active_calls.pop(request.id, None)
            return ACPResponse(
                id=request.id,
                status=ACPStatus.FAILURE,
                error="Failed to dispatch command to session",
            )
        start_time = time.time()
        try:
            raw_output = await self._capture_output(
                session, request.id, request.timeout
            )
            elapsed = int((time.time() - start_time) * 1000)
            response = parse_response(raw_output, request.id)
            response.duration_ms = elapsed
            await self.lifecycle.mark_idle(session)
            self._record_call(request, response)
            return response
        except asyncio.TimeoutError:
            elapsed = int((time.time() - start_time) * 1000)
            await self.lifecycle.mark_idle(session)
            response = ACPResponse(
                id=request.id,
                status=ACPStatus.TIMEOUT,
                error=f"Command timed out after {request.timeout}s",
                duration_ms=elapsed,
            )
            self._record_call(request, response)
            return response
        except Exception as e:
            await self.lifecycle.mark_idle(session)
            self._active_calls.pop(request.id, None)
            return ACPResponse(
                id=request.id,
                status=ACPStatus.FAILURE,
                error=str(e),
            )
        finally:
            self._active_calls.pop(request.id, None)

    async def _capture_output(
        self, session: ClaudeSession, request_id: str, timeout: int
    ) -> str:
        end_marker = f"### ACP_END:{request_id} ###"
        collected: list[str] = []
        deadline = time.time() + timeout
        poll_interval = 0.1
        while time.time() < deadline:
            try:
                result = subprocess.run(
                    ["tmux", "capture-pane", "-p", "-t", session.tmux_name],
                    capture_output=True,
                    text=True,
                )
                output = result.stdout
                collected.append(output)
                if end_marker in output:
                    return "\n".join(collected)
            except Exception as e:
                logger.debug("Capture error: %s", e)
            await asyncio.sleep(poll_interval)
        raise asyncio.TimeoutError()

    def _record_call(self, request: ACPRequest, response: ACPResponse) -> None:
        self._call_history.append(
            {
                "request_id": request.id,
                "type": request.type.value,
                "status": response.status.value,
                "duration_ms": response.duration_ms,
                "timestamp": time.time(),
            }
        )
        if len(self._call_history) > 1000:
            self._call_history = self._call_history[-500:]

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    @property
    def active_count(self) -> int:
        return len(self._active_calls)

    @property
    def recent_history(self) -> list[dict]:
        return self._call_history[-20:]
