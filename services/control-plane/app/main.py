from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .config import APP_NAME, db_path
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
    return """
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Local Agent Relay</title>
        <style>
          body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #1f2328;
            background: #ffffff;
          }
          main {
            width: min(920px, calc(100% - 40px));
            margin: 0 auto;
            padding: 48px 0;
          }
          h1 {
            margin: 0 0 10px;
            font-size: 42px;
            line-height: 1.1;
            letter-spacing: 0;
          }
          p {
            color: #667085;
            font-size: 17px;
            line-height: 1.6;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
            margin-top: 28px;
          }
          a.card {
            display: block;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            padding: 16px;
            color: inherit;
            text-decoration: none;
            background: #f6f8fa;
          }
          a.card:hover {
            border-color: #0f766e;
          }
          h2 {
            margin: 0 0 6px;
            font-size: 18px;
          }
          code {
            display: block;
            margin-top: 18px;
            padding: 14px;
            overflow-x: auto;
            border-radius: 8px;
            background: #0f172a;
            color: #e5e7eb;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>Local Agent Relay</h1>
          <p>Control Plane API 已启动。当前版本是后端骨架，可以创建 shell 任务、查看状态和读取日志；Dashboard 下一步开发。</p>
          <div class="grid">
            <a class="card" href="/health">
              <h2>Health</h2>
              <p>查看服务状态和 SQLite 路径。</p>
            </a>
            <a class="card" href="/docs">
              <h2>API Docs</h2>
              <p>打开 FastAPI 交互式接口文档。</p>
            </a>
            <a class="card" href="/tasks">
              <h2>Tasks</h2>
              <p>查看最近任务列表。</p>
            </a>
          </div>
          <code>curl -s -X POST http://127.0.0.1:8787/tasks \\
  -H 'Content-Type: application/json' \\
  -d '{"title":"hello","instruction":"run a quick task","executor":"shell","command":"echo hello from relay"}'</code>
        </main>
      </body>
    </html>
    """


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
