#!/usr/bin/env python3
"""
ACP Harness for Claude Code

This script demonstrates a simple ACP (Agent Communication Protocol) harness
for running Claude code in interactive mode with tmux-managed I/O.
"""

import subprocess
import sys
import time
import argparse
import os


class ClaudeACPHarness:
    def __init__(self, session_name="claude-harness"):
        self.session_name = session_name
        self.tmux_socket = f"/tmp/tmux-{os.getuid()}/default"

    def start_tmux_session(self):
        """Start a new tmux session for running Claude code."""
        try:
            # Check if session already exists
            subprocess.run(
                ["tmux", "has-session", "-t", self.session_name],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"Session '{self.session_name}' already exists.")
            return True
        except subprocess.CalledProcessError:
            # Session doesn't exist, create it
            result = subprocess.run(
                [
                    "tmux",
                    "new-session",
                    "-d",
                    "-s",
                    self.session_name,
                    "bash",
                    "-c",
                    "echo 'Claude ACP Harness Ready'; exec bash",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"Created tmux session: {self.session_name}")
                return True
            else:
                print(f"Failed to create tmux session: {result.stderr}")
                return False

    def send_command(self, command):
        """Send a command to the Claude code running in tmux."""
        result = subprocess.run(
            [
                "tmux",
                "send-keys",
                "-t",
                f"{self.session_name}",
                command,
                "Enter",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Sent command: {command}")
            return True
        else:
            print(f"Failed to send command: {result.stderr}")
            return False

    def read_output(self, duration=1):
        """
        Read output from the tmux session.

        Note: This is a simplified implementation. A production version would
        need to properly capture pane output.
        """
        time.sleep(duration)
        result = subprocess.run(
            [
                "tmux",
                "capture-pane",
                "-p",
                "-t",
                f"{self.session_name}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Failed to read output: {result.stderr}")
            return ""

    def attach_session(self):
        """Attach to the tmux session for direct interaction."""
        try:
            subprocess.run(["tmux", "attach-session", "-t", self.session_name])
        except KeyboardInterrupt:
            print("\nDetached from session.")

    def kill_session(self):
        """Kill the tmux session."""
        result = subprocess.run(
            ["tmux", "kill-session", "-t", self.session_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Killed tmux session: {self.session_name}")
            return True
        else:
            print(f"Failed to kill session: {result.stderr}")
            return False

    def run_interactive_mode(self):
        """Run in interactive mode, accepting user input."""
        print("Entering interactive mode. Type 'exit' to quit.")
        while True:
            try:
                user_input = input(">>> ")
                if user_input.lower() == "exit":
                    break
                elif user_input.lower() == "attach":
                    self.attach_session()
                else:
                    self.send_command(user_input)
                    output = self.read_output()
                    if output.strip():
                        print(output)
            except KeyboardInterrupt:
                print("\nExiting interactive mode.")
                break


def main():
    parser = argparse.ArgumentParser(description="Claude ACP Harness")
    parser.add_argument(
        "--session-name",
        default="claude-harness",
        help="Name of the tmux session (default: claude-harness)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--command",
        help="Send a single command to the Claude session",
    )
    parser.add_argument(
        "--attach",
        action="store_true",
        help="Attach to the tmux session",
    )
    parser.add_argument(
        "--kill",
        action="store_true",
        help="Kill the tmux session",
    )

    args = parser.parse_args()

    harness = ClaudeACPHarness(session_name=args.session_name)

    if args.kill:
        harness.kill_session()
        return

    if not harness.start_tmux_session():
        sys.exit(1)

    if args.attach:
        harness.attach_session()
        return

    if args.command:
        harness.send_command(args.command)
        output = harness.read_output()
        if output.strip():
            print(output)
        return

    if args.interactive:
        harness.run_interactive_mode()
        return

    # Default behavior - show help
    parser.print_help()


if __name__ == "__main__":
    main()
