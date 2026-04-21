import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from acp_protocol import (
    ACPCommandType,
    ACPRequest,
    ACPResponse,
    ACPStatus,
    parse_response,
    wrap_with_sentinels,
)
from command_router import CommandRouter
from config import (
    HarnessConfig,
    AuthMethod,
    ExecutionMode,
    SessionState,
    detect_auth_method,
)
from direct_executor import DirectExecutor
from session_lifecycle import ClaudeSession, SessionLifecycle
from verification_loop import VerificationLoop, GapClassification


class TestACPProtocol(unittest.TestCase):
    def test_request_schema(self):
        req = ACPRequest(type=ACPCommandType.PROMPT, payload="hello")
        self.assertEqual(req.type, ACPCommandType.PROMPT)
        self.assertEqual(req.payload, "hello")
        self.assertEqual(req.timeout, 120)
        self.assertIsNotNone(req.id)

    def test_request_empty_payload_rejected(self):
        with self.assertRaises(Exception):
            ACPRequest(type=ACPCommandType.PROMPT, payload="   ")

    def test_response_schema(self):
        resp = ACPResponse(
            id="test", status=ACPStatus.SUCCESS, result="ok", duration_ms=42
        )
        self.assertEqual(resp.id, "test")
        self.assertEqual(resp.status, ACPStatus.SUCCESS)
        self.assertEqual(resp.duration_ms, 42)

    def test_sentinel_wrapping(self):
        req = ACPRequest(
            id="abc123", type=ACPCommandType.PROMPT, payload="do something"
        )
        wrapped = wrap_with_sentinels(req)
        self.assertIn("### ACP_START:abc123 ###", wrapped)
        self.assertIn("### ACP_END:abc123 ###", wrapped)
        self.assertIn("do something", wrapped)

    def test_parse_response_success(self):
        raw = "some text\n### ACP_START:xyz ###\nthe result\n### ACP_END:xyz ###\nmore text"
        resp = parse_response(raw, "xyz")
        self.assertEqual(resp.status, ACPStatus.SUCCESS)
        self.assertEqual(resp.result, "the result")

    def test_parse_response_missing_sentinels(self):
        raw = "some output without markers"
        resp = parse_response(raw, "xyz")
        self.assertEqual(resp.status, ACPStatus.FAILURE)
        self.assertIn("Sentinel markers not found", resp.error or "")


class TestConfig(unittest.TestCase):
    def test_default_config(self):
        config = HarnessConfig()
        self.assertEqual(config.pool_min_sessions, 2)
        self.assertEqual(config.preference_auth, AuthMethod.SUBSCRIPTION_OAUTH)
        self.assertEqual(config.api_port, 8420)

    def test_detect_auth_api_key(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=False):
            result = detect_auth_method()
            self.assertEqual(result, AuthMethod.API_KEY)

    def test_detect_auth_oauth_token(self):
        env = {"CLAUDE_CODE_OAUTH_TOKEN": "test-token"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            result = detect_auth_method()
            self.assertEqual(result, AuthMethod.CLAUDE_SETUP_TOKEN)

    def test_detect_auth_default_subscription(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(Path, "exists", return_value=True):
                result = detect_auth_method()
                self.assertEqual(result, AuthMethod.SUBSCRIPTION_OAUTH)


class TestSessionLifecycle(unittest.TestCase):
    def test_session_creation(self):
        session = ClaudeSession(session_id="test1", tmux_name="test-tmux")
        self.assertEqual(session.session_id, "test1")
        self.assertEqual(session.state, SessionState.STARTING)

    def test_session_uptime(self):
        import time

        session = ClaudeSession(started_at=time.time() - 60)
        self.assertGreater(session.uptime_seconds, 59)

    def test_session_idle_time(self):
        import time

        session = ClaudeSession(last_activity=time.time() - 30)
        self.assertGreater(session.idle_seconds, 29)

    def test_session_status_report(self):
        lifecycle = SessionLifecycle.__new__(SessionLifecycle)
        lifecycle._sessions = {}
        lifecycle.claude_executable = "claude"
        lifecycle.max_reconnect_retries = 3
        session = ClaudeSession(
            session_id="s1",
            tmux_name="t1",
            state=SessionState.READY,
            auth_method=AuthMethod.SUBSCRIPTION_OAUTH,
        )
        lifecycle._sessions["s1"] = session
        status = lifecycle.session_status(session)
        self.assertEqual(status["session_id"], "s1")
        self.assertEqual(status["state"], "ready")
        self.assertEqual(status["auth_method"], "subscription_oauth")


class TestVerificationLoop(unittest.TestCase):
    def test_gap_classification(self):
        vl = VerificationLoop(
            MagicMock(), loop_limit=5, reports_dir="/tmp/test-reports"
        )

        resp_small = ACPResponse(
            id="t", status=ACPStatus.SUCCESS, result="FAIL: minor typo"
        )
        self.assertEqual(vl._classify_gap(resp_small), GapClassification.SMALL)

        resp_large = ACPResponse(
            id="t",
            status=ACPStatus.SUCCESS,
            result="FAIL: large architectural mismatch, escalate",
        )
        self.assertEqual(vl._classify_gap(resp_large), GapClassification.LARGE)

        resp_medium = ACPResponse(
            id="t", status=ACPStatus.SUCCESS, result="FAIL: partial implementation"
        )
        self.assertEqual(vl._classify_gap(resp_medium), GapClassification.MEDIUM)

    def test_passes_verification(self):
        vl = VerificationLoop(
            MagicMock(), loop_limit=5, reports_dir="/tmp/test-reports"
        )

        pass_resp = ACPResponse(
            id="t", status=ACPStatus.SUCCESS, result="PASS: all criteria met"
        )
        self.assertTrue(vl._passes_verification(pass_resp))

        fail_resp = ACPResponse(
            id="t", status=ACPStatus.SUCCESS, result="FAIL: missing coverage"
        )
        self.assertFalse(vl._passes_verification(fail_resp))


class TestIntegrationTmux(unittest.TestCase):
    def setUp(self):
        self.session_name = "test-acp-integration"

    def tearDown(self):
        import subprocess

        try:
            subprocess.run(
                ["tmux", "kill-session", "-t", self.session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    def test_tmux_session_lifecycle(self):
        import subprocess
        import time

        try:
            result = subprocess.run(
                ["tmux", "new-session", "-d", "-s", self.session_name, "bash"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)

            subprocess.run(
                ["tmux", "send-keys", "-t", self.session_name, "echo 'test'", "Enter"],
                capture_output=True,
                text=True,
            )
            time.sleep(1)

            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", self.session_name],
                capture_output=True,
                text=True,
            )
            self.assertIn("test", result.stdout or "")
        except FileNotFoundError:
            self.skipTest("tmux not installed")


class TestDirectExecutorE2E(unittest.TestCase):
    """End-to-end tests that invoke Claude Code via --print mode."""

    @classmethod
    def setUpClass(cls):
        import shutil

        cls.claude_path = shutil.which("claude")
        if cls.claude_path is None:
            raise unittest.SkipTest("Claude Code CLI not found in PATH")

    def test_simple_prompt_returns_success(self):
        """Verify that a simple prompt to Claude returns a non-empty response."""
        config = HarnessConfig(
            claude_executable=self.claude_path,
            command_timeout=60,
        )
        executor = DirectExecutor(config)

        request = ACPRequest(
            type=ACPCommandType.PROMPT,
            payload="Respond with exactly: ACP_E2E_OK",
            timeout=60,
        )

        response = asyncio.run(executor.execute(request))
        self.assertEqual(
            response.status,
            ACPStatus.SUCCESS,
            f"Expected SUCCESS, got {response.status}: {response.error}",
        )
        self.assertIn("ACP_E2E_OK", response.result or "")
        self.assertGreater(response.duration_ms, 0)

    def test_timeout_returns_timeout_status(self):
        """Verify that a very short timeout returns TIMEOUT status."""
        config = HarnessConfig(
            claude_executable=self.claude_path,
            command_timeout=60,
        )
        executor = DirectExecutor(config)

        # 1s timeout with a long prompt — Claude startup takes ~3-5s
        request = ACPRequest(
            type=ACPCommandType.PROMPT,
            payload="Write a detailed essay about the history of computing from ancient times to modern AI",
            timeout=1,
        )

        response = asyncio.run(executor.execute(request))
        self.assertEqual(
            response.status,
            ACPStatus.TIMEOUT,
            f"Expected TIMEOUT, got {response.status}: {response.result}",
        )

    def test_multiple_requests_sequential(self):
        """Verify that multiple sequential requests each get valid responses."""
        config = HarnessConfig(
            claude_executable=self.claude_path,
            command_timeout=60,
        )
        executor = DirectExecutor(config)

        for i in range(3):
            request = ACPRequest(
                type=ACPCommandType.PROMPT,
                payload=f"Respond with exactly: ACP_SEQ_{i}",
                timeout=60,
            )
            response = asyncio.run(executor.execute(request))
            self.assertEqual(
                response.status,
                ACPStatus.SUCCESS,
                f"Request {i} failed: {response.error}",
            )
            self.assertIn(
                f"ACP_SEQ_{i}",
                response.result or "",
                f"Request {i} response: {response.result}",
            )


class TestCommandRouterPrintMode(unittest.TestCase):
    """Test CommandRouter in --print (direct) mode."""

    @classmethod
    def setUpClass(cls):
        import shutil

        cls.claude_path = shutil.which("claude")
        if cls.claude_path is None:
            raise unittest.SkipTest("Claude Code CLI not found in PATH")

    def test_submit_via_router(self):
        """Verify that CommandRouter in PRINT mode executes requests via DirectExecutor."""
        config = HarnessConfig(
            claude_executable=self.claude_path,
            execution_mode=ExecutionMode.PRINT,
            command_timeout=60,
        )
        lifecycle = SessionLifecycle(
            claude_executable=config.claude_executable,
            max_reconnect_retries=1,
        )
        router = CommandRouter(lifecycle, default_timeout=60, config=config)

        request = ACPRequest(
            type=ACPCommandType.PROMPT,
            payload="Respond with exactly: ROUTER_OK",
            timeout=60,
        )

        response = asyncio.run(router.submit(request))
        self.assertEqual(
            response.status,
            ACPStatus.SUCCESS,
            f"Expected SUCCESS, got {response.status}: {response.error}",
        )
        self.assertIn("ROUTER_OK", response.result or "")


if __name__ == "__main__":
    unittest.main()
