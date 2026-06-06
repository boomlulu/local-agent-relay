from __future__ import annotations

import os
from pathlib import Path

os.environ["LOCAL_AGENT_RELAY_DB"] = str(Path(__file__).parent / "tmp-test.sqlite3")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402


def test_root_page() -> None:
    init_db()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Local Agent Relay" in response.text
    assert "/docs" in response.text
    assert "创建任务" in response.text
    assert "taskForm" in response.text


def test_shell_task_lifecycle() -> None:
    init_db()
    client = TestClient(app)

    response = client.post(
        "/tasks",
        json={
            "title": "test task",
            "instruction": "hello from test",
            "executor": "shell",
            "command": "echo $LOCAL_AGENT_RELAY_INSTRUCTION",
        },
    )

    assert response.status_code == 201
    task = response.json()
    assert task["status"] in {"created", "completed"}

    detail = client.get(f"/tasks/{task['id']}").json()
    assert detail["status"] == "completed"
    assert detail["exit_code"] == 0
    assert any("hello from test" in log["message"] for log in detail["logs"])
