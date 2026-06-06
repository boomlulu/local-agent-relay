from __future__ import annotations

import base64
import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .config import APP_NAME, db_path, uploads_dir
from .dashboard import render_dashboard
from .db import init_db
from .orchestrator import run_task
from .pipelines import load_pipelines
from .repository import (
    create_task,
    get_task,
    list_logs,
    list_tasks,
    list_validations,
)
from .schemas import (
    CreateTaskRequest,
    LogRecord,
    PipelineSummary,
    TaskRecord,
    TaskWithLogs,
    ValidationRecord,
)


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


@app.get("/pipelines", response_model=list[PipelineSummary])
def get_pipelines() -> list[PipelineSummary]:
    items = [
        PipelineSummary(
            pipeline_name=p.pipeline_name,
            project_type=p.project_type,
            validators=len(p.validate_steps),
            notify=p.notify,
        )
        for p in load_pipelines().values()
    ]
    return sorted(items, key=lambda x: x.pipeline_name)


def _save_image(image_base64: str | None) -> str | None:
    if not image_base64:
        return None
    try:
        raw = image_base64
        ext = "png"
        if raw.startswith("data:"):
            header, raw = raw.split(",", 1)
            if "image/jpeg" in header or "image/jpg" in header:
                ext = "jpg"
            elif "image/webp" in header:
                ext = "webp"
            elif "image/gif" in header:
                ext = "gif"
            elif "image/png" in header:
                ext = "png"
        data = base64.b64decode(raw)
        path = uploads_dir() / f"{uuid.uuid4()}.{ext}"
        path.write_bytes(data)
        return str(path)
    except Exception:
        return None


@app.post("/tasks", response_model=TaskRecord, status_code=201)
def post_task(payload: CreateTaskRequest, background_tasks: BackgroundTasks) -> TaskRecord:
    image_path = _save_image(payload.image_base64)
    task = create_task(payload, image_path=image_path)
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
    validations = [ValidationRecord(**row) for row in list_validations(task_id)]
    return TaskWithLogs(**task.model_dump(), logs=logs, validations=validations)


@app.get("/tasks/{task_id}/logs", response_model=list[LogRecord])
def get_task_logs(task_id: str) -> list[LogRecord]:
    if get_task(task_id) is None:
        raise HTTPException(status_code=404, detail="task not found")
    return [LogRecord(**row) for row in list_logs(task_id)]


@app.get("/tasks/{task_id}/validations", response_model=list[ValidationRecord])
def get_task_validations(task_id: str) -> list[ValidationRecord]:
    if get_task(task_id) is None:
        raise HTTPException(status_code=404, detail="task not found")
    return [ValidationRecord(**row) for row in list_validations(task_id)]


def run() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8787, reload=True)


if __name__ == "__main__":
    run()
