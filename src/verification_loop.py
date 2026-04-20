import json
import logging
import time
import uuid
from pathlib import Path
from typing import Optional

from acp_protocol import ACPCommandType, ACPRequest, ACPResponse, ACPStatus
from command_router import CommandRouter

logger = logging.getLogger("acp-harness")


class GapClassification:
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class VerificationLoop:
    def __init__(
        self,
        router: CommandRouter,
        loop_limit: int = 5,
        reports_dir: str = "verification-reports",
    ):
        self.router = router
        self.loop_limit = loop_limit
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self._history: list[dict] = []

    async def execute_with_verification(self, request: ACPRequest) -> ACPResponse:
        if request.type != ACPCommandType.VERIFY:
            return await self.router.submit(request)

        cycle = 0
        implementation_response: Optional[ACPResponse] = None
        decisions: list[dict] = []

        while cycle < self.loop_limit:
            cycle += 1
            impl_request = ACPRequest(
                id=str(uuid.uuid4()),
                type=ACPCommandType.PROMPT,
                payload=self._build_implementation_prompt(request, cycle, decisions),
                timeout=request.timeout,
                metadata={"verification_cycle": cycle, "parent_id": request.id},
            )
            implementation_response = await self.router.submit(impl_request)

            if implementation_response.status != ACPStatus.SUCCESS:
                decisions.append(
                    {
                        "cycle": cycle,
                        "action": "implementation_failed",
                        "detail": implementation_response.error or "unknown error",
                        "timestamp": time.time(),
                    }
                )
                continue

            verify_request = ACPRequest(
                id=str(uuid.uuid4()),
                type=ACPCommandType.VERIFY,
                payload=self._build_verification_prompt(
                    request, implementation_response
                ),
                timeout=request.timeout,
                metadata={"verification_cycle": cycle, "parent_id": request.id},
            )
            verify_response = await self.router.submit(verify_request)

            if (
                verify_response.status == ACPStatus.SUCCESS
                and self._passes_verification(verify_response)
            ):
                decisions.append(
                    {
                        "cycle": cycle,
                        "action": "verification_passed",
                        "detail": "all criteria met",
                        "timestamp": time.time(),
                    }
                )
                report = self._generate_report(
                    request,
                    cycle,
                    decisions,
                    implementation_response,
                    verify_response,
                    passed=True,
                )
                return ACPResponse(
                    id=request.id,
                    status=ACPStatus.SUCCESS,
                    result=implementation_response.result,
                    duration_ms=implementation_response.duration_ms,
                    metadata={
                        "verification_cycles": cycle,
                        "report_id": report["report_id"],
                    },
                )

            gap = self._classify_gap(verify_response)
            decisions.append(
                {
                    "cycle": cycle,
                    "action": "verification_failed",
                    "gap_classification": gap,
                    "detail": verify_response.result
                    or verify_response.error
                    or "no detail",
                    "timestamp": time.time(),
                }
            )
            if gap == GapClassification.LARGE:
                break

        report = self._generate_report(
            request, cycle, decisions, implementation_response, None, passed=False
        )
        return ACPResponse(
            id=request.id,
            status=ACPStatus.ESCALATION_REQUIRED,
            error=f"Verification loop exhausted after {cycle} cycles",
            metadata={"verification_cycles": cycle, "report_id": report["report_id"]},
        )

    def _build_implementation_prompt(
        self, original: ACPRequest, cycle: int, decisions: list[dict]
    ) -> str:
        base = original.payload
        if cycle > 1 and decisions:
            retro = decisions[-1]
            return (
                f"{base}\n\n"
                f"[VERIFICATION FEEDBACK — cycle {cycle}]\n"
                f"Previous attempt failed verification.\n"
                f"Gap: {retro.get('gap_classification', 'unknown')}\n"
                f"Detail: {retro.get('detail', 'no detail')}\n"
                f"Address the gap and retry."
            )
        return base

    def _build_verification_prompt(
        self, original: ACPRequest, impl_response: ACPResponse
    ) -> str:
        return (
            f"Verify the following implementation against the original request.\n\n"
            f"ORIGINAL REQUEST:\n{original.payload}\n\n"
            f"IMPLEMENTATION RESULT:\n{impl_response.result}\n\n"
            f"Does the implementation satisfy the request? Respond with PASS or FAIL and explain why."
        )

    def _passes_verification(self, verify_response: ACPResponse) -> bool:
        result = (verify_response.result or "").lower()
        return "pass" in result and "fail" not in result

    def _classify_gap(self, verify_response: ACPResponse) -> str:
        result = (verify_response.result or "").lower()
        if "large" in result or "escalat" in result:
            return GapClassification.LARGE
        if "medium" in result or "partial" in result:
            return GapClassification.MEDIUM
        return GapClassification.SMALL

    def _generate_report(
        self,
        request: ACPRequest,
        cycles: int,
        decisions: list[dict],
        impl_response: Optional[ACPResponse],
        verify_response: Optional[ACPResponse],
        passed: bool,
    ) -> dict:
        report_id = str(uuid.uuid4())[:8]
        report = {
            "report_id": report_id,
            "request_id": request.id,
            "passed": passed,
            "cycles": cycles,
            "loop_limit": self.loop_limit,
            "decisions": decisions,
            "implementation_result": impl_response.result if impl_response else None,
            "verification_result": verify_response.result if verify_response else None,
            "timestamp": time.time(),
        }
        report_path = self.reports_dir / f"{report_id}.json"
        report_path.write_text(json.dumps(report, indent=2))
        self._history.append(report)
        return report
