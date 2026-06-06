from __future__ import annotations

from .executors import run_gemma_task, run_shell_task
from .pipelines import resolve_pipeline
from .repository import add_log, get_task, now_iso, update_task
from .schemas import ExecutorResult, TaskStatus
from .validators import run_validations


def run_task(task_id: str) -> None:
    task = get_task(task_id)
    if task is None:
        return
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

    if result.status != "completed":
        _finalize_execute(task_id, result)
        return

    pipeline = resolve_pipeline(task.pipeline)
    failed_names: list[str] = []
    if pipeline and pipeline.validate_steps:
        update_task(task_id, status=TaskStatus.validating.value)
        outcomes = run_validations(task, pipeline)
        failed_names = [o.name for o in outcomes if o.status == "failed"]

    if failed_names:
        update_task(
            task_id,
            status=TaskStatus.failed_validation.value,
            summary=result.summary,
            exit_code=result.exit_code,
            error="validation failed: " + ", ".join(failed_names),
            finished_at=now_iso(),
        )
        return

    update_task(
        task_id,
        status=TaskStatus.completed.value,
        summary=result.summary,
        exit_code=result.exit_code,
        error=None,
        finished_at=now_iso(),
    )


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
