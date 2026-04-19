#!/usr/bin/env python3
"""
Cleanup script for the Claude ACP Harness

This script helps clean up tmux sessions created by the ACP harness.
"""

import subprocess
import sys


def list_claude_sessions():
    """List all tmux sessions related to claude."""
    try:
        result = subprocess.run(
            ["tmux", "list-sessions"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            sessions = []
            for line in result.stdout.split("\n"):
                if "claude" in line:
                    session_name = line.split(":")[0]
                    sessions.append(session_name)
            return sessions
        else:
            return []
    except FileNotFoundError:
        print("tmux not found")
        return []


def kill_session(session_name):
    """Kill a specific tmux session."""
    try:
        result = subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Killed session: {session_name}")
            return True
        else:
            print(f"Failed to kill session {session_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error killing session {session_name}: {e}")
        return False


def main():
    print("Claude ACP Harness Cleanup")
    print("==========================")

    # List claude-related sessions
    sessions = list_claude_sessions()

    if not sessions:
        print("No claude-related tmux sessions found.")
        return 0

    print("Found claude-related sessions:")
    for i, session in enumerate(sessions):
        print(f"  {i + 1}. {session}")

    print("\nOptions:")
    print("  a. Kill all sessions")
    print("  b. Kill specific session")
    print("  c. Cancel")

    try:
        choice = input("Select option (a/b/c): ").strip().lower()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 0

    if choice == "a":
        # Kill all sessions
        for session in sessions:
            kill_session(session)
        print("All claude sessions cleaned up.")
    elif choice == "b":
        try:
            session_index = int(input("Enter session number to kill: ")) - 1
            if 0 <= session_index < len(sessions):
                kill_session(sessions[session_index])
            else:
                print("Invalid session number.")
        except ValueError:
            print("Invalid input.")
    elif choice == "c":
        print("Cancelled.")
    else:
        print("Invalid option.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
