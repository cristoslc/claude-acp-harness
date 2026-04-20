---
source_id: hermes-agent
title: "Hermes Agent: AI That Learns & Grows With You | Open Source"
author: Nous Research
url: https://hermesagent.agency/
date: 2026-04-19
fetched: 2026-04-19
type: website
proxy_used: false
---

# Hermes Agent: Open-Source Autonomous AI Agent

## Overview

Hermes Agent is an open-source autonomous AI agent built by Nous Research. It features persistent cross-session memory, a self-improving skills system, multi-platform messaging, 40+ built-in tools, and runs on any infrastructure (from a $5 VPS to serverless cloud).

### Key Differentiators

- **Persistent Memory**: Cross-session memory with FTS5 recall and LLM summarization. Remembers projects, preferences, and context indefinitely.
- **Self-Created Skills**: Autonomously creates, improves, and reuses procedural skills from experience. Skills are portable and shareable via [agentskills.io](https://agentskills.io).
- **Multi-Platform**: CLI, Telegram, Discord, Slack, WhatsApp — all from a single unified gateway.
- **Infrastructure Agnostic**: Local, Docker, SSH, Daytona, Singularity, Modal. Costs nearly nothing when idle.
- **Model Agnostic**: Works with Nous Portal, OpenRouter, OpenAI, or any OpenAI-compatible endpoint.

## Core Capabilities

| Capability               | Description                                                                                     |
|--------------------------|-------------------------------------------------------------------------------------------------|
| **Closed Learning Loop** | Agent-curated memory, autonomous skill creation, self-improvement, Honcho user modeling.      |
| **40+ Built-in Tools**  | Web search, file operations, terminal commands, image generation, TTS, vision, and more.      |
| **Skills System**        | Procedural memory the agent creates and reuses. Portable and shareable.                       |
| **MCP Integration**      | Connect to any MCP server for extended tool capabilities.                                      |
| **Scheduled Automations**| Built-in cron scheduler with delivery to any platform.                                          |

## Technical Architecture

| Component          | Implementation                                                                                  |
|-------------------|-------------------------------------------------------------------------------------------------|
| **Terminal Backends** | Local, Docker, SSH, Daytona, Singularity, Modal                                               |
| **Messaging Platforms** | CLI, Telegram, Discord, Slack, WhatsApp                                                       |
| **Memory System**  | FTS5 cross-session recall + LLM summarization                                                  |
| **Skills System**  | Autonomous creation, self-improvement, [agentskills.io](https://agentskills.io) compatibility |
| **Model Providers** | Nous Portal, OpenRouter, OpenAI, any OpenAI-compatible endpoint                                |

## Use Cases

- **Developer Automation**: Spawn isolated subagents for parallel workstreams. Run terminal commands, manage files, search the web, and execute code autonomously.
- **Personal AI Assistant**: Manage tasks, schedule automations, and receive reports on any platform (e.g., Telegram).
- **Research & Analysis**: Web search, content extraction, vision, and batch processing built-in.
- **Team & Enterprise**: Connect to Slack/Discord for team-wide AI assistance. MCP integration extends capabilities.

## Cost Structure

- **Open Source**: Free to self-host. No subscription or usage limits.
- **Infrastructure**: Runs on any infrastructure (e.g., $5 VPS, serverless cloud). Costs nearly nothing when idle.
- **Model Costs**: Pay only for the API usage of the models you connect (e.g., OpenAI, OpenRouter, Nous Portal).
- **Skills**: Community-contributed skills are free and portable.

## Installation

1. Run the one-line installer on Linux, macOS, or WSL2.
2. Set your model provider (Nous Portal, OpenRouter, OpenAI, or custom endpoint).
3. Connect your messaging platform (Telegram, Discord, Slack, WhatsApp).
4. Start your first conversation. Hermes Agent begins learning immediately.

## FAQ

### What is Hermes Agent?
Hermes Agent is an open-source autonomous AI agent with persistent cross-session memory, self-improving skills, multi-platform messaging, and 40+ built-in tools. It runs on any infrastructure and gets more capable the longer it runs.

### How is Hermes Agent different from ChatGPT or Claude?
ChatGPT and Claude are stateless—every conversation starts fresh. Hermes Agent maintains persistent memory, autonomously creates and improves skills, runs scheduled automations, and operates independently on your infrastructure.

### Who built Hermes Agent?
Nous Research, the lab behind the Hermes, Nomos, and Psyche model families.

### What messaging platforms does Hermes Agent support?
CLI, Telegram, Discord, Slack, and WhatsApp—all from a single unified gateway.

### Is Hermes Agent free and open source?
Yes. Fully open source and free to self-host. No subscription, no usage limits, no vendor lock-in.

### What AI models does Hermes Agent work with?
Nous Portal, OpenRouter, OpenAI, and any OpenAI-compatible API endpoint.
