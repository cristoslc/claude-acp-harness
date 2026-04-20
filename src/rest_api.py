import json
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from acp_protocol import ACPRequest, ACPResponse
from command_router import CommandRouter
from config import HarnessConfig
from observability import (
    get_logger,
    get_metrics,
    ACTIVE_SESSIONS,
)
from session_lifecycle import SessionLifecycle, SessionState
from session_pool import SessionPool
from verification_loop import VerificationLoop

logger = get_logger("acp-harness.rest_api")


def create_app(config: HarnessConfig) -> FastAPI:
    app = FastAPI(
        title="ACP Harness",
        description="Agent Communication Protocol Harness for Claude Code",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    lifecycle = SessionLifecycle(
        claude_executable=config.claude_executable,
        max_reconnect_retries=config.max_reconnect_retries,
    )
    pool = SessionPool(lifecycle, config)
    router = CommandRouter(lifecycle, default_timeout=config.command_timeout)
    verification = VerificationLoop(
        router,
        loop_limit=config.verification_loop_limit,
        reports_dir=config.reports_dir,
    )

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        """Middleware for collecting request metrics and logging."""
        start_time = time.time()

        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log successful response
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 3),
            )

            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration * 1000, 3),
            )
            raise

    @app.on_event("startup")
    async def startup() -> None:
        await pool.start()
        await router.start()
        ACTIVE_SESSIONS.set(len(lifecycle.get_all_sessions()))
        logger.info(
            "acp_harness_started",
            host=config.api_host,
            port=config.api_port,
            pool_min_sessions=config.pool_min_sessions,
        )

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await router.stop()
        await pool.stop()
        ACTIVE_SESSIONS.set(0)
        logger.info("acp_harness_stopped")

    @app.post("/acp/call", response_model=ACPResponse)
    async def acp_call(request: ACPRequest) -> ACPResponse:
        """Submit an ACP request to Claude Code.

        Returns the response from Claude after execution.
        """
        try:
            logger.info(
                "acp_call_received",
                request_id=request.id,
                command=request.payload[:50] if request.payload else None,
            )
            return await router.submit(request)
        except Exception as e:
            logger.error(
                "acp_call_failed",
                request_id=request.id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/acp/verify", response_model=ACPResponse)
    async def acp_verify(request: ACPRequest) -> ACPResponse:
        """Submit an ACP request with verification.

        Runs the INITIATIVE-022 verification loop and returns
        the final verified response along with a report.
        """
        try:
            logger.info(
                "acp_verify_received",
                request_id=request.id,
                command=request.payload[:50] if request.payload else None,
            )
            return await verification.execute_with_verification(request)
        except Exception as e:
            logger.error(
                "acp_verify_failed",
                request_id=request.id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/acp/status")
    async def acp_status() -> dict:
        """Get the current status of the ACP Harness."""
        sessions = lifecycle.get_all_sessions()
        ACTIVE_SESSIONS.set(len(sessions))

        status = {
            "pool": pool.status,
            "router": {
                "queue_size": router.queue_size,
                "active_count": router.active_count,
            },
            "sessions": [lifecycle.session_status(s) for s in sessions],
            "recent_calls": router.recent_history,
        }

        logger.debug("status_check", session_count=len(sessions))
        return status

    @app.get("/acp/reports")
    async def acp_reports() -> dict:
        """Get recent verification reports."""
        reports_dir = Path(config.reports_dir)
        if not reports_dir.exists():
            return {"reports": []}
        reports = []
        for f in sorted(reports_dir.glob("*.json"))[-20:]:
            try:
                data = json.loads(f.read_text())
                reports.append(
                    {
                        "report_id": data.get("report_id"),
                        "request_id": data.get("request_id"),
                        "passed": data.get("passed"),
                        "cycles": data.get("cycles"),
                        "timestamp": data.get("timestamp"),
                    }
                )
            except Exception:
                pass
        logger.debug("reports_listed", report_count=len(reports))
        return {"reports": reports}

    @app.get("/metrics")
    async def metrics() -> Response:
        """Prometheus metrics endpoint."""
        content, content_type = get_metrics()
        return Response(content=content, media_type=content_type)

    @app.get("/health")
    async def health() -> dict:
        """Health check endpoint for container orchestration."""
        sessions = lifecycle.get_all_sessions()
        healthy = (
            any(
                s.state == SessionState.READY or s.state == SessionState.ACTIVE
                for s in sessions
            )
            if sessions
            else False
        )

        status = "healthy" if healthy else "degraded"
        logger.debug("health_check", status=status, session_count=len(sessions))

        return {
            "status": status,
            "sessions": len(sessions),
            "healthy_sessions": sum(
                1
                for s in sessions
                if s.state == SessionState.READY or s.state == SessionState.ACTIVE
            ),
        }

    return app


app: Optional[FastAPI] = None


def init_app(config: Optional[HarnessConfig] = None) -> FastAPI:
    """Initialize the FastAPI application with optional config."""
    global app
    if app is None:
        cfg = config or HarnessConfig()
        app = create_app(cfg)
    return app
