from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .config import default_workdir
from .repository import add_log, get_task, now_iso, update_task
from .schemas import TaskStatus


def run_shell_task(task_id: str) -> None:
    task = get_task(task_id)
    if task is None:
        return

    command = task.command or "printf '%s\\n' \"$LOCAL_AGENT_RELAY_INSTRUCTION\""
    cwd = Path(task.project_root).expanduser().resolve() if task.project_root else default_workdir()

    update_task(task_id, status=TaskStatus.executing.value, started_at=now_iso())
    add_log(task_id, "system", f"executor=shell cwd={cwd}")
    add_log(task_id, "system", f"command={command}")

    env = os.environ.copy()
    env["LOCAL_AGENT_RELAY_TASK_ID"] = task_id
    env["LOCAL_AGENT_RELAY_INSTRUCTION"] = task.instruction

    try:
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate()
    except Exception as exc:
        add_log(task_id, "error", str(exc))
        update_task(
            task_id,
            status=TaskStatus.failed_execution.value,
            error=str(exc),
            finished_at=now_iso(),
        )
        return

    if stdout:
        add_log(task_id, "stdout", stdout.rstrip())
    if stderr:
        add_log(task_id, "stderr", stderr.rstrip())

    status = TaskStatus.completed if proc.returncode == 0 else TaskStatus.failed_execution
    summary = "Shell task completed" if proc.returncode == 0 else "Shell task failed"
    update_task(
        task_id,
        status=status.value,
        summary=summary,
        exit_code=proc.returncode,
        finished_at=now_iso(),
    )


def run_task(task_id: str) -> None:
    task = get_task(task_id)
    if task is None:
        return
    if task.executor == "shell":
        run_shell_task(task_id)
        return
    add_log(task_id, "error", f"unsupported executor: {task.executor}")
    update_task(
        task_id,
        status=TaskStatus.failed_execution.value,
        error=f"unsupported executor: {task.executor}",
        finished_at=now_iso(),
    )

