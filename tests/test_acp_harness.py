"""
Tests for the Claude ACP Harness
"""

import unittest
import subprocess
import sys
import os

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from acp_harness import ClaudeACPHarness


class TestClaudeACPHarness(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.session_name = "test-claude-harness"
        self.harness = ClaudeACPHarness(session_name=self.session_name)

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Kill the test session if it exists
        try:
            subprocess.run(
                ["tmux", "kill-session", "-t", self.session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except:
            pass

    def test_init(self):
        """Test that the harness initializes correctly."""
        self.assertEqual(self.harness.session_name, self.session_name)

    def test_start_tmux_session(self):
        """Test that we can start a tmux session."""
        # This test requires tmux to be installed
        try:
            result = self.harness.start_tmux_session()
            self.assertTrue(result)

            # Verify the session exists
            result = subprocess.run(
                ["tmux", "has-session", "-t", self.session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.assertEqual(result.returncode, 0)
        except FileNotFoundError:
            # Skip if tmux is not installed
            self.skipTest("tmux not installed")

    def test_send_command(self):
        """Test that we can send a command to the tmux session."""
        try:
            # Start the session first
            self.assertTrue(self.harness.start_tmux_session())

            # Send a simple command
            result = self.harness.send_command("echo 'Hello, World!'")
            self.assertTrue(result)
        except FileNotFoundError:
            # Skip if tmux is not installed
            self.skipTest("tmux not installed")


if __name__ == "__main__":
    unittest.main()
