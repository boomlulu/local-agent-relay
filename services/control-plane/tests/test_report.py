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
    pdir = tmp_path / "pipes"
    pdir.mkdir()
    (pdir / "test-report.yaml").write_text(
        "pipeline_name: test-report\n"
        "project_type: test\n"
        "validate:\n"
        "  - name: ok-check\n"
        "    adapter: shell-command\n"
        '    command: "true"\n'
        "report:\n"
        "  adapter: gemma-summary\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LOCAL_AGENT_RELAY_PIPELINES_DIR", str(pdir))
    from app.db import init_db

    init_db()
    yield


def test_report_generated() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "report task",
            "instruction": "do it",
            "executor": "shell",
            "command": "echo hi",
            "pipeline": "test-report",
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["status"] == "completed"
    assert detail["report"] is not None
    assert "## Execution" in detail["report"]
    assert "ok-check" in detail["report"]
    assert "All validations passed." in detail["report"]


def test_no_pipeline_no_report() -> None:
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
    assert detail["report"] is None
