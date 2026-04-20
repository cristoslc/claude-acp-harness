# Makefile for Claude ACP Harness

.PHONY: help install test demo clean cleanup

help:
	@echo "Claude ACP Harness Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install     Install dependencies"
	@echo "  make test        Run tests"
	@echo "  make demo        Run demo script"
	@echo "  make clean       Remove generated files"
	@echo "  make cleanup     Clean up tmux sessions"

install:
	uv sync

test:
	uv run pytest

demo:
	python scripts/demo.py

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

cleanup:
	python scripts/cleanup.py

session:
	python src/acp_harness.py --interactive

attach:
	@echo "Use 'tmux attach-session -t claude-harness' to attach"
