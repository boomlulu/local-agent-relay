# Architecture

## Product Shape

Local Agent Relay is a local-first agent orchestration system.

It is not a single agent. It is a control plane that coordinates agents, tools, validation pipelines, logs, artifacts, and notifications.

## Roles

### Control Plane

The control plane is intentionally boring and reliable.

Responsibilities:

- Task lifecycle
- Queueing
- Agent runner process management
- Validator execution
- Artifact collection
- Trace and logs
- Notifications
- User approval gates
- Error handling and retry policy

The control plane should not rely on an LLM to maintain state.

### Claude Code / Codex

Primary execution agents.

Responsibilities:

- Complex implementation
- Multi-file edits
- Code reasoning
- Test fixing
- Refactoring
- Pulling context from the workspace

### Gemma 4 12B

Local assistant and relay.

Responsibilities:

- Voice-to-task interpretation when audio input is available
- Image and screenshot understanding
- Short local summaries
- Converting verbose agent output into human-friendly status
- Producing voice-friendly notification text
- Extracting structured intent from user instructions

Gemma should not directly own secrets, permissions, process execution, or final state transitions.

## Core Pipeline

```text
Input -> Plan -> Execute -> Validate -> Report -> Notify
```

### Input

Sources:

- Web dashboard
- Voice input
- VSCode context
- CLI
- Future webhooks

### Plan

Output is a structured task:

```json
{
  "project_id": "example-web",
  "task_type": "feature",
  "instruction": "Add a dashboard filter",
  "executor": "claude-code",
  "pipeline": "web-basic",
  "requires_validation": true
}
```

### Execute

Executor adapters run implementation agents.

Adapter examples:

- `claude-code`
- `codex`
- `shell`
- `gemma-local`

### Validate

Validator adapters run project-specific checks.

Shared validators:

- `git-diff-check`
- `shell-command`
- `unit-test`
- `build`
- `log-error-scan`
- `screenshot-vision`

Domain validators:

- Unity: `unity-editmode`, `unity-playmode`, `unity-build`
- Web: `npm-test`, `npm-build`, `playwright`
- Backend: `pytest`, `docker-compose-health`, `http-smoke-test`

### Report

Reporter collects:

- Agent summary
- Changed files
- Command logs
- Validation results
- Screenshots
- Errors
- Follow-up recommendation

Gemma can create the human-friendly report and short voice notification.

### Notify

Notification targets:

- Dashboard
- macOS notification
- Local TTS
- Webhook

## Data Model

Minimum entities:

- `Project`
- `PipelineTemplate`
- `Task`
- `Run`
- `Step`
- `Artifact`
- `LogEntry`
- `Notification`

## State Machine

Happy path:

```text
created -> planned -> executing -> validating -> reporting -> completed
```

Failure and pause states:

```text
needs_user_input
failed_execution
failed_validation
timeout
cancelled
```

## Design Principle

Keep intelligence and reliability separate:

- LLMs interpret, summarize, plan, and explain.
- Code owns state, permissions, process control, validation, and auditability.

