import asyncio
import logging
import subprocess
import time
from typing import Optional

from acp_protocol import ACPRequest, ACPResponse, ACPStatus
from config import HarnessConfig

logger = logging.getLogger("acp-harness")


class DirectExecutor:
    """Execute ACP requests directly via `claude --print`."""

    def __init__(self, config: HarnessConfig) -> None:
        self.config = config
        self.claude_executable = config.claude_executable
        self._call_count = 0

    async def execute(self, request: ACPRequest) -> ACPResponse:
        """Execute an ACP request and return the response."""
        self._call_count += 1
        start_time = time.time()

        payload = request.payload.strip()
        logger.info(
            "executing_request request_id=%s payload_preview=%.100s timeout=%d",
            request.id,
            payload,
            request.timeout,
        )

        proc: Optional[asyncio.subprocess.Process] = None

        try:
            proc = await asyncio.create_subprocess_exec(
                self.claude_executable,
                "--print",
                "--output-format",
                "text",
                "--max-turns",
                "1",
                payload,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            result = await asyncio.wait_for(proc.communicate(), timeout=request.timeout)

            stdout_bytes, stderr_bytes = result
            stdout = stdout_bytes.decode("utf-8") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8") if stderr_bytes else ""
            elapsed_ms = int((time.time() - start_time) * 1000)

            if proc.returncode != 0:
                logger.error(
                    "claude_nonzero_exit request_id=%s returncode=%d stderr=%.500s",
                    request.id,
                    proc.returncode,
                    stderr.strip(),
                )
                return ACPResponse(
                    id=request.id,
                    status=ACPStatus.FAILURE,
                    error=f"Claude exited with code {proc.returncode}: {stderr[:500]}",
                    duration_ms=elapsed_ms,
                )

            output = stdout.strip()
            logger.info(
                "request_completed request_id=%s output_length=%d duration_ms=%d",
                request.id,
                len(output),
                elapsed_ms,
            )

            return ACPResponse(
                id=request.id,
                status=ACPStatus.SUCCESS,
                result=output,
                duration_ms=elapsed_ms,
            )

        except asyncio.TimeoutError:
            elapsed_ms = int((time.time() - start_time) * 1000)
            if proc and proc.returncode is None:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
            logger.error(
                "request_timed_out request_id=%s timeout=%d duration_ms=%d",
                request.id,
                request.timeout,
                elapsed_ms,
            )
            return ACPResponse(
                id=request.id,
                status=ACPStatus.TIMEOUT,
                error=f"Command timed out after {request.timeout}s",
                duration_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "request_failed request_id=%s error=%s error_type=%s duration_ms=%d",
                request.id,
                e,
                type(e).__name__,
                elapsed_ms,
            )
            return ACPResponse(
                id=request.id,
                status=ACPStatus.FAILURE,
                error=str(e),
                duration_ms=elapsed_ms,
            )

    @property
    def call_count(self) -> int:
        return self._call_count
