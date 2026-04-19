# Claude ACP Harness

An ACP (Agent Communication Protocol) harness for Claude code that runs in interactive mode, with tmux managing input and output.

## Overview

This project provides a framework for running Claude code in interactive mode, where:
- Claude code executes continuously in a tmux session
- Input/Output is managed through tmux panes
- The harness facilitates communication between the host system and Claude code

## Features

- Interactive Claude code execution
- Tmux-based I/O management
- Session persistence
- Easy monitoring and control
- Integration with Swain skills

## Project Structure

```
claude-acp-harness/
├── README.md
├── Makefile
├── pyproject.toml
├── .gitignore
├── .agents/              # Swain skills installed here
├── config/
│   └── harness.yaml      # Configuration file
├── src/
│   └── acp_harness.py    # Main harness implementation
├── scripts/
│   ├── demo.py           # Demonstration script
│   └── cleanup.py        # Cleanup utility
└── tests/
    └── test_acp_harness.py
```

## Setup

1. Install dependencies:
```bash
make install
```

2. Swain skills are already installed in `.agents/`:
```bash
npx skills install -y cristoslc/Swain
```

## Usage

### Running the demo
```bash
make demo
```

### Interactive mode
```bash
make session
```
or directly:
```bash
python src/acp_harness.py --interactive
```

### Attaching to tmux session
```bash
make attach
```
or directly:
```bash
tmux attach-session -t claude-harness
```

### Sending a single command
```bash
python src/acp_harness.py --command "echo 'Hello Claude!'"
```

### Cleaning up sessions
```bash
make cleanup
```

## Configuration

The harness can be configured via `config/harness.yaml`:
- Session settings: Name, socket path
- I/O settings: Poll interval, timeouts
- Claude settings: Executable path, working directory
- Logging settings: Log level, file location

## Requirements

- Python 3.8+
- uv (for dependency management)
- tmux (for session management)
- npx (for Swain skills installation)

## Development

### Running tests
```bash
make test
```

### Code formatting
```bash
uv run black src/ tests/ scripts/
```

### Linting
```bash
uv run flake8 src/ tests/ scripts/
```