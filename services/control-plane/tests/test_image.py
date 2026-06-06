from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


PNG_1x1 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M8AAAMBAQDJ/pLvAAAAAElFTkSuQmCC"


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCAL_AGENT_RELAY_DB", str(tmp_path / "i.sqlite3"))
    monkeypatch.setenv("LOCAL_AGENT_RELAY_UPLOADS", str(tmp_path / "up"))
    from app.db import init_db

    init_db()
    yield


def test_post_with_image() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "image task",
            "instruction": "describe it",
            "executor": "shell",
            "command": "echo hi",
            "image_base64": PNG_1x1,
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["image_path"]
    assert Path(detail["image_path"]).is_file()
    assert detail["status"] == "completed"


def test_post_without_image() -> None:
    client = TestClient(app)
    response = client.post(
        "/tasks",
        json={
            "title": "no image task",
            "instruction": "describe it",
            "executor": "shell",
            "command": "echo hi",
        },
    )
    assert response.status_code == 201
    task_id = response.json()["id"]

    detail = client.get(f"/tasks/{task_id}").json()
    assert detail["image_path"] is None


def test_save_image_bad() -> None:
    from app.main import _save_image

    assert _save_image("not-base64!!") is None
    assert _save_image(None) is None
