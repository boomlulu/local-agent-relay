from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCAL_AGENT_RELAY_DB", str(tmp_path / "v.sqlite3"))
    pdir = tmp_path / "pipes"
    pdir.mkdir()
    (pdir / "test-pass.yaml").write_text(
        "pipeline_name: test-pass\n"
        "project_type: test\n"
        "validate:\n"
        "  - name: ok-check\n"
        "    adapter: shell-command\n"
        '    command: "true"\n',
        encoding="utf-8",
    )
    (pdir / "test-fail.yaml").write_text(
        "pipeline_name: test-fail\n"
        "project_type: test\n"
        "validate:\n"
        "  - name: bad-check\n"
        "    adapter: shell-command\n"
        '    command: "false"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("LOCAL_AGENT_RELAY_PIPELINES_DIR", str(pdir))
    from app.db import init_db

    init_db()
    yield


def test_validate_pass() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "pass task",
            "instruction": "do it",
            "executor": "shell",
            "command": "echo hi",
            "pipeline": "test-pass",
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["status"] == "completed"

    validations = client.get(f"/tasks/{task_id}/validations").json()
    assert len(validations) == 1
    assert validations[0]["name"] == "ok-check"
    assert validations[0]["status"] == "passed"


def test_validate_fail() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "fail task",
            "instruction": "do it",
            "executor": "shell",
            "command": "echo hi",
            "pipeline": "test-fail",
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["status"] == "failed_validation"
    assert "validation failed" in (detail["error"] or "")

    validations = client.get(f"/tasks/{task_id}/validations").json()
    assert len(validations) == 1
    assert validations[0]["name"] == "bad-check"
    assert validations[0]["status"] == "failed"


def test_no_pipeline() -> None:
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

    validations = client.get(f"/tasks/{task_id}/validations").json()
    assert validations == []
