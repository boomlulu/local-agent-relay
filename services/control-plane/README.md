# Local Agent Relay Control Plane

FastAPI backend skeleton for the Local Agent Relay task lifecycle.

## Run

From the repository root:

```bash
cd services/control-plane
/opt/homebrew/bin/python3.10 -m pip install --user -e ".[dev]"
local-agent-relay-api
```

Or without installing scripts:

```bash
cd services/control-plane
/opt/homebrew/bin/python3.10 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

## Smoke Test

```bash
curl -s http://127.0.0.1:8787/health
```

Create a shell task:

```bash
curl -s -X POST http://127.0.0.1:8787/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "hello shell",
    "instruction": "verify the local control plane can execute a command",
    "executor": "shell",
    "command": "echo task:$LOCAL_AGENT_RELAY_TASK_ID && echo instruction:$LOCAL_AGENT_RELAY_INSTRUCTION"
  }'
```

List tasks:

```bash
curl -s http://127.0.0.1:8787/tasks
```

## Data

Default SQLite path:

```text
./data/control_plane.sqlite3
```

Override with:

```bash
export LOCAL_AGENT_RELAY_DB=/absolute/path/to/control_plane.sqlite3
```

