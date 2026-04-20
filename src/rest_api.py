import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from acp_protocol import ACPRequest, ACPResponse, ACPStatus
from command_router import CommandRouter
from config import HarnessConfig
from session_lifecycle import SessionLifecycle, SessionState
from session_pool import SessionPool
from verification_loop import VerificationLoop

logger = logging.getLogger("acp-harness")


def create_app(config: HarnessConfig) -> FastAPI:
    app = FastAPI(title="ACP Harness", version="0.1.0")

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

    @app.on_event("startup")
    async def startup():
        await pool.start()
        await router.start()
        logger.info("ACP Harness started on %s:%d", config.api_host, config.api_port)

    @app.on_event("shutdown")
    async def shutdown():
        await router.stop()
        await pool.stop()
        logger.info("ACP Harness stopped")

    @app.post("/acp/call")
    async def acp_call(request: ACPRequest) -> ACPResponse:
        try:
            return await router.submit(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/acp/verify")
    async def acp_verify(request: ACPRequest) -> ACPResponse:
        try:
            return await verification.execute_with_verification(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/acp/status")
    async def acp_status():
        sessions = lifecycle.get_all_sessions()
        return {
            "pool": pool.status,
            "router": {
                "queue_size": router.queue_size,
                "active_count": router.active_count,
            },
            "sessions": [lifecycle.session_status(s) for s in sessions],
            "recent_calls": router.recent_history,
        }

    @app.get("/acp/reports")
    async def acp_reports():
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
        return {"reports": reports}

    return app
