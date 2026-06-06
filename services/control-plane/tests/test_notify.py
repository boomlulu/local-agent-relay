from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCAL_AGENT_RELAY_DB", str(tmp_path / "r.sqlite3"))
    monkeypatch.setenv(
        "LOCAL_AGENT_RELAY_GEMMA_MODEL", str(tmp_path / "no-model")
    )
    monkeypatch.setenv("LOCAL_AGENT_RELAY_NOTIFY", "0")
    pdir = tmp_path / "pipes"
    pdir.mkdir()
    (pdir / "test-notify.yaml").write_text(
        "pipeline_name: test-notify\n"
        "project_type: test\n"
        "validate:\n"
        "  - name: ok-check\n"
        "    adapter: shell-command\n"
        '    command: "true"\n'
        "notify:\n"
        "  - dashboard\n"
        "  - macos\n"
        "  - voice\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LOCAL_AGENT_RELAY_PIPELINES_DIR", str(pdir))
    from app.db import init_db

    init_db()
    yield


def test_notify_logs() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "notify task",
            "instruction": "do it",
            "executor": "shell",
            "command": "echo hi",
            "pipeline": "test-notify",
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["status"] == "completed"

    logs = detail["logs"]
    assert any(
        log["stream"] == "notify" and log["message"] == "dashboard updated"
        for log in logs
    )
    assert any("macos skipped (disabled)" in log["message"] for log in logs)
    assert any("voice skipped (disabled)" in log["message"] for log in logs)


def test_no_pipeline_no_notify() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "no pipeline",
            "instruction": "do it",
            "executor": "shell",
            "command": "echo hi",
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["status"] == "completed"
    assert not any(log["stream"] == "notify" for log in detail["logs"])
