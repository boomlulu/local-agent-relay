# Local Agent Relay

Local Agent Relay is a local agent control plane for managing development agents, validation pipelines, and human-friendly multimodal feedback.

The core idea:

- Claude Code / Codex handle complex implementation work.
- Gemma 4 12B acts as a local multimodal assistant for voice, image, summaries, routing hints, and user-facing handoff.
- The control plane owns state, permissions, queues, validation, logs, notifications, and recovery.

## Why This Exists

This project is designed around two practical pains:

- Managing multiple development agents from VSCode is hard, especially when work finishes without clear notification.
- Feature validation often requires manual context switching into Unity, web browsers, backend terminals, or API tools.

Local Agent Relay turns those workflows into explicit pipelines:

```text
Input -> Plan -> Execute -> Validate -> Report -> Notify
```

## MVP Scope

The first version should support three project profiles:

- Unity game development
- Web frontend development
- Backend/server development

Each profile uses the same control-plane lifecycle but different validators.

## Planned Components

```text
apps/
  dashboard/        Web UI for tasks, agents, traces, validation reports

services/
  control-plane/    Task state machine, queue, runners, logs, notifications
  gemma-bridge/     Local Gemma MLX adapter for text/image/audio
  model-gateway/    Optional unified model calling layer

configs/
  pipelines/        Project pipeline templates

docs/
  architecture.md   System architecture
  mvp.md            First implementation milestone
```

## Gemma Local Model

Known working local model:

```text
/Users/boom/.cache/huggingface/hub/models--mlx-community--gemma-4-12B-it-4bit/snapshots/8de8ab4d40f6b95a76ffa491e23dd430e1f725b5
```

Known working command:

```bash
mlx_vlm.generate \
  --model /Users/boom/.cache/huggingface/hub/models--mlx-community--gemma-4-12B-it-4bit/snapshots/8de8ab4d40f6b95a76ffa491e23dd430e1f725b5 \
  --prompt "用中文简短解释一下什么是多模态模型。" \
  --max-tokens 200 \
  --temperature 0.2 \
  --no-verbose
```

## First Build Target

Build a local dashboard and control-plane service that can:

1. Create a task from text input.
2. Run an executor adapter such as Claude Code or a shell placeholder.
3. Run a validator adapter based on project profile.
4. Ask Gemma to summarize logs and results.
5. Notify the user when the task is done or blocked.

