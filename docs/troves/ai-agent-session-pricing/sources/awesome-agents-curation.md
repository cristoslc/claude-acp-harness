---
source_id: awesome-agents-curation
title: "GitHub - kyrolabs/awesome-agents: 🤖 Awesome list of AI Agents"
author: kyrolabs
url: https://github.com/kyrolabs/awesome-agents
date: 2026-04-19
fetched: 2026-04-19
type: github-repository
proxy_used: false
---

# Awesome Agents: Open-Source AI Agent Tools and Frameworks

## Persistent Session Tools

### OpenClaw
- **Description**: Open-source AI agent framework for persistent, proactive personal AI agents with multi-channel messaging (Signal, Telegram, Discord, WhatsApp), cron scheduling, memory systems, MCP integration, skill plugins, sub-agent spawning, and browser automation.
- **Key Features**: Multi-channel, cron, memory, MCP, skills, sub-agents, browser automation.
- **Use Case**: Personal AI agents with persistent memory and multi-platform reach.
- **Cost**: Open source + model/API costs.

### Hermes Agent
- **Description**: Self-improving autonomous AI agent with persistent cross-session memory, self-created skills, multi-platform messaging, and runs anywhere (VPS, serverless).
- **Key Features**: Persistent memory, self-improving skills, multi-platform, infrastructure-agnostic.
- **Use Case**: Personal automation, research, team collaboration.
- **Cost**: Open source + model/API costs.

### ClaudeClaw
- **Description**: Persistent agent orchestrator as a Claude Code plugin. Multi-channel routing (Slack, WhatsApp, Telegram), OS-level sandbox isolation, composable extension system.
- **Key Features**: Multi-channel, sandbox isolation, composable extensions.
- **Use Case**: Secure, multi-channel agent orchestration.
- **Cost**: Open source + model/API costs.

### SwarmClaw
- **Description**: Self-hosted AI runtime for multi-agent orchestration with heartbeats, schedules, delegation, memory, and runtime skills across OpenClaw, Claude Code, Codex, Gemini CLI, and major LLM providers. Ships as a desktop app (Electron) and CLI.
- **Key Features**: Multi-agent, heartbeats, schedules, delegation, memory, runtime skills.
- **Use Case**: Multi-agent workflows with persistent sessions.
- **Cost**: Open source + model/API costs.

### Steel Browser
- **Description**: Open-source browser infrastructure for AI agents with session-backed automation, extraction, screenshots/PDFs, AI-native CLI, and reusable steel-browser skill.
- **Key Features**: Session-backed automation, extraction, screenshots, PDFs, CLI.
- **Use Case**: Browser-based agent workflows with persistent state.
- **Cost**: Open source + model/API costs.

### MemGPT
- **Description**: Create LLM agents with long-term memory and custom tools.
- **Key Features**: Long-term memory, custom tools, virtual context management.
- **Use Case**: Agents requiring extended memory and tooling.
- **Cost**: Open source + model/API costs.

### nanobot
- **Description**: Ultra-lightweight personal AI assistant framework (~4,000 lines of Python). Supports MCP, 9+ chat channels, and extensible skills system.
- **Key Features**: Lightweight, MCP, multi-channel, skills.
- **Use Case**: Personal AI assistants with minimal overhead.
- **Cost**: Open source + model/API costs.

## Multi-Agent Frameworks

### Maestro
- **Description**: Multi-agent development orchestration platform coordinating 22 specialized AI agents through 4-phase workflows with native parallel execution, persistent sessions, and least-privilege security tiers.
- **Key Features**: Multi-agent, parallel execution, persistent sessions, security tiers.
- **Use Case**: Complex, multi-agent workflows with persistent state.
- **Cost**: Open source + model/API costs.

### Swarms Framework
- **Description**: Bleeding-edge multi-agent orchestration framework for enterprise applications.
- **Key Features**: Multi-agent, orchestration, enterprise-ready.
- **Use Case**: Enterprise multi-agent workflows.
- **Cost**: Open source + model/API costs.

### CrewAI
- **Description**: Cutting-edge framework for orchestrating role-playing, autonomous AI agents.
- **Key Features**: Role-based, autonomous, multi-agent.
- **Use Case**: Role-based multi-agent collaboration.
- **Cost**: Open source + model/API costs.

### AutoGen
- **Description**: Enable next-gen LLM applications with multi-agent conversation and customization.
- **Key Features**: Multi-agent, conversation, customizable.
- **Use Case**: Research prototyping, multi-agent conversation.
- **Cost**: Open source + model/API costs.

## Cost-Efficient Deployment Options

### Serverless Persistence
- **Daytona, Modal**: Serverless infrastructure for agents. Environment hibernates when idle and wakes on demand. Run a meaningful personal agent on a $5 VPS.
- **Use Case**: Cost-efficient, bursty workloads.
- **Cost**: Pay-per-use (e.g., $5 VPS, serverless cloud).

### Self-Hosted
- **Local, Docker, SSH**: Run agents on your own infrastructure (e.g., $5 VPS, GPU cluster).
- **Use Case**: Full control, privacy, cost efficiency.
- **Cost**: Infrastructure costs only (e.g., $5 VPS).

## Key Considerations for Cost Efficiency

- **Session Management**: Use tools like Redis for memory cleanup in multi-agent setups.
- **Infrastructure**: Serverless (Daytona, Modal) for bursty workloads; self-hosted for steady usage.
- **Model Choice**: Use smaller models (e.g., Haiku) for simple tasks; larger models (e.g., Opus) for complex reasoning.
- **Open Source**: All tools listed are open source, reducing licensing costs. Pay only for model/API usage and infrastructure.
