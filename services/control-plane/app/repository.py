from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from .db import session
from .schemas import CreateTaskRequest, TaskRecord, TaskStatus


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def create_task(payload: CreateTaskRequest) -> TaskRecord:
    task_id = str(uuid.uuid4())
    now = now_iso()
    with session() as conn:
        conn.execute(
            """
            INSERT INTO tasks (
              id, title, instruction, executor, command, project_root,
              pipeline, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                payload.title,
                payload.instruction,
                payload.executor,
                payload.command,
                payload.project_root,
                payload.pipeline,
                TaskStatus.created.value,
                now,
                now,
            ),
        )
    task = get_task(task_id)
    if task is None:
        raise RuntimeError("created task could not be loaded")
    return task


def get_task(task_id: str) -> TaskRecord | None:
    with session() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return TaskRecord(**row_to_dict(row)) if row else None


def list_tasks(limit: int = 100) -> list[TaskRecord]:
    with session() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [TaskRecord(**row_to_dict(row)) for row in rows]


def update_task(task_id: str, **fields: Any) -> None:
    if not fields:
        return
    fields["updated_at"] = now_iso()
    keys = list(fields.keys())
    assignments = ", ".join(f"{key} = ?" for key in keys)
    values = [fields[key] for key in keys]
    values.append(task_id)
    with session() as conn:
        conn.execute(f"UPDATE tasks SET {assignments} WHERE id = ?", values)


def add_log(task_id: str, stream: str, message: str) -> None:
    with session() as conn:
        conn.execute(
            "INSERT INTO logs (task_id, stream, message, created_at) VALUES (?, ?, ?, ?)",
            (task_id, stream, message, now_iso()),
        )


def list_logs(task_id: str) -> list[dict[str, Any]]:
    with session() as conn:
        rows = conn.execute(
            "SELECT * FROM logs WHERE task_id = ? ORDER BY id ASC", (task_id,)
        ).fetchall()
    return [row_to_dict(row) for row in rows]

