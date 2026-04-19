#!/usr/bin/env python3
"""
Demo script for the Claude ACP Harness

This script demonstrates how to use the ACP harness to manage
interactive Claude code sessions via tmux.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from acp_harness import ClaudeACPHarness


def main():
    print("Claude ACP Harness Demo")
    print("======================")

    # Create a harness instance
    harness = ClaudeACPHarness(session_name="claude-demo")

    # Start the tmux session
    print("Starting tmux session...")
    if not harness.start_tmux_session():
        print("Failed to start tmux session")
        return 1

    # Send a welcome message
    print("Sending welcome message...")
    harness.send_command("echo 'Welcome to the Claude ACP Harness Demo!'")

    # Wait a moment and read the output
    import time

    time.sleep(1)
    output = harness.read_output()
    if output:
        print("Output from session:")
        print(output)

    print("\nDemo completed successfully!")
    print("You can now interact with the session using:")
    print("  python src/acp_harness.py --interactive")
    print("Or attach directly with:")
    print("  tmux attach-session -t claude-demo")

    return 0


if __name__ == "__main__":
    sys.exit(main())
