# MVP Plan

## Goal

Create the first usable Local Agent Relay prototype:

- A local web dashboard for task submission and status.
- A control-plane backend with task lifecycle tracking.
- A Gemma bridge for local summaries.
- Three pipeline templates: Unity, Web, Backend.
- A notification path when a task finishes or needs attention.

## Milestone 1: Repository and Contracts

Deliverables:

- Project repository
- Architecture document
- Pipeline config examples
- Task lifecycle contract
- Adapter interface contract

Success:

- The project has enough structure to start coding without re-discussing the product boundary.

## Milestone 2: Backend Skeleton

Suggested stack:

- Python `FastAPI`
- SQLite for initial storage
- Server-Sent Events for dashboard updates
- `subprocess` runner for local commands

Endpoints:

```text
POST /tasks
GET  /tasks
GET  /tasks/{task_id}
GET  /tasks/{task_id}/events
POST /tasks/{task_id}/cancel
POST /projects
GET  /projects
```

## Milestone 3: Dashboard Skeleton

Suggested stack:

- Vite + React
- Task list
- Task detail
- Live logs
- Validation results
- Final report panel

## Milestone 4: First Executors

Start simple:

- `shell` executor
- `claude-code` executor stub or command adapter

The first executor should return:

```json
{
  "status": "completed",
  "summary": "string",
  "changed_files": [],
  "artifacts": [],
  "logs": []
}
```

## Milestone 5: First Validators

Implement common validators first:

- `shell-command`
- `git-diff-check`
- `log-error-scan`

Then add domain validators:

- Web: `npm test`, `npm run build`, Playwright screenshot
- Backend: test command, health check
- Unity: batchmode test command, log collection

## Milestone 6: Gemma Bridge

Capabilities:

- Text summary
- Image summary from screenshot
- Audio transcription or task extraction
- Short voice-friendly report

Use the local MLX command first:

```bash
mlx_vlm.generate --model "$MODEL" --prompt "..." --no-verbose
```

Later, wrap this in a persistent local service if command startup becomes too slow.

## Non-Goals for MVP

- Cloud deployment
- Full autonomous permissions
- Complex multi-agent debate
- Long-term memory beyond task history
- Production-grade secret management

## First Demo Scenario

Use a sample project and run:

1. Submit task from dashboard.
2. Execute a shell or Claude Code placeholder.
3. Run validation command.
4. Ask Gemma to summarize the result.
5. Show notification and final report.

