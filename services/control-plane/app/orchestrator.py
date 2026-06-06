from __future__ import annotations

from .executors import run_gemma_task, run_shell_task
from .pipelines import resolve_pipeline
from .repository import add_log, get_task, now_iso, update_task
from .schemas import ExecutorResult, TaskStatus


def run_task(task_id: str) -> None:
    task = get_task(task_id)
    if task is None:
        return
    pipeline = resolve_pipeline(task.pipeline)  # reserved for Step2+, unused-ok now
    _ = pipeline
    update_task(task_id, status=TaskStatus.executing.value, started_at=now_iso())
    if task.executor == "gemma":
        result = run_gemma_task(task)
    elif task.executor == "shell":
        result = run_shell_task(task)
    else:
        msg = f"unsupported executor: {task.executor}"
        add_log(task_id, "error", msg)
        update_task(
            task_id,
            status=TaskStatus.failed_execution.value,
            error=msg,
            finished_at=now_iso(),
        )
        return
    _finalize_execute(task_id, result)


def _finalize_execute(task_id: str, result: ExecutorResult) -> None:
    status_map = {
        "completed": TaskStatus.completed.value,
        "failed_execution": TaskStatus.failed_execution.value,
        "timeout": TaskStatus.timeout.value,
    }
    update_task(
        task_id,
        status=status_map[result.status],
        summary=result.summary,
        exit_code=result.exit_code,
        error=result.error,
        finished_at=now_iso(),
    )
