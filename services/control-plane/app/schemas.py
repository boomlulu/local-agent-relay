from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    created = "created"
    executing = "executing"
    validating = "validating"
    reporting = "reporting"
    completed = "completed"
    failed_execution = "failed_execution"
    failed_validation = "failed_validation"
    needs_user_input = "needs_user_input"
    timeout = "timeout"
    cancelled = "cancelled"


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    instruction: str = Field(min_length=1)
    executor: Literal["gemma", "shell"] = "gemma"
    command: str | None = None
    project_root: str | None = None
    pipeline: str | None = None


class TaskRecord(BaseModel):
    id: str
    title: str
    instruction: str
    executor: str
    command: str | None
    project_root: str | None
    pipeline: str | None
    status: TaskStatus
    summary: str | None
    exit_code: int | None
    error: str | None
    created_at: str
    updated_at: str
    started_at: str | None
    finished_at: str | None


class LogRecord(BaseModel):
    id: int
    task_id: str
    stream: str
    message: str
    created_at: str


class ValidationRecord(BaseModel):
    id: int
    task_id: str
    name: str
    adapter: str
    status: str
    detail: str | None
    exit_code: int | None
    created_at: str


class TaskWithLogs(TaskRecord):
    logs: list[LogRecord]
    validations: list[ValidationRecord] = Field(default_factory=list)


class ExecutorResult(BaseModel):
    status: Literal["completed", "failed_execution", "timeout"]
    summary: str | None = None
    exit_code: int | None = None
    error: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
