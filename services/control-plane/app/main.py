from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .config import APP_NAME, db_path
from .dashboard import render_dashboard
from .db import init_db
from .executors import run_task
from .repository import create_task, get_task, list_logs, list_tasks
from .schemas import CreateTaskRequest, LogRecord, TaskRecord, TaskWithLogs


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title=APP_NAME, version="0.1.0", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return render_dashboard()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "db": str(db_path())}


@app.post("/tasks", response_model=TaskRecord, status_code=201)
def post_task(payload: CreateTaskRequest, background_tasks: BackgroundTasks) -> TaskRecord:
    task = create_task(payload)
    background_tasks.add_task(run_task, task.id)
    return task


@app.get("/tasks", response_model=list[TaskRecord])
def get_tasks(limit: int = Query(default=100, ge=1, le=500)) -> list[TaskRecord]:
    return list_tasks(limit=limit)


@app.get("/tasks/{task_id}", response_model=TaskWithLogs)
def get_task_detail(task_id: str) -> TaskWithLogs:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    logs = [LogRecord(**row) for row in list_logs(task_id)]
    return TaskWithLogs(**task.model_dump(), logs=logs)


@app.get("/tasks/{task_id}/logs", response_model=list[LogRecord])
def get_task_logs(task_id: str) -> list[LogRecord]:
    if get_task(task_id) is None:
        raise HTTPException(status_code=404, detail="task not found")
    return [LogRecord(**row) for row in list_logs(task_id)]


def run() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8787, reload=True)


if __name__ == "__main__":
    run()
