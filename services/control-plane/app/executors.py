from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

from .config import default_workdir, gemma_model_path, python_bin
from .repository import add_log, get_task, now_iso, update_task
from .schemas import TaskStatus


def build_gemma_prompt(instruction: str) -> str:
    local_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    return f"""你是 Local Agent Relay 的本地助手 Gemma。
请直接回答用户，不要展示推理过程。
如果用户询问当前时间、日期、今天、现在等信息，必须使用下面提供的本机时间。

当前本机时间：{local_time}

用户请求：
{instruction}
"""


def run_gemma_task(task_id: str) -> None:
    task = get_task(task_id)
    if task is None:
        return

    model_path = gemma_model_path()
    cwd = Path(task.project_root).expanduser().resolve() if task.project_root else default_workdir()
    timeout_seconds = int(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_TIMEOUT", "240"))

    update_task(task_id, status=TaskStatus.executing.value, started_at=now_iso())
    add_log(task_id, "system", f"executor=gemma cwd={cwd}")
    add_log(task_id, "system", f"model={model_path}")

    if not model_path.exists():
        message = f"Gemma model path does not exist: {model_path}"
        add_log(task_id, "error", message)
        update_task(
            task_id,
            status=TaskStatus.failed_execution.value,
            error=message,
            finished_at=now_iso(),
        )
        return

    command = [
        python_bin(),
        "-m",
        "mlx_vlm.generate",
        "--model",
        str(model_path),
        "--prompt",
        build_gemma_prompt(task.instruction),
        "--max-tokens",
        "500",
        "--temperature",
        "0.2",
        "--no-verbose",
    ]

    try:
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        if stdout:
            add_log(task_id, "stdout", stdout.rstrip())
        if stderr:
            add_log(task_id, "stderr", stderr.rstrip())
        message = f"Gemma task timed out after {timeout_seconds} seconds"
        add_log(task_id, "error", message)
        update_task(
            task_id,
            status=TaskStatus.timeout.value,
            error=message,
            finished_at=now_iso(),
        )
        return
    except Exception as exc:
        add_log(task_id, "error", str(exc))
        update_task(
            task_id,
            status=TaskStatus.failed_execution.value,
            error=str(exc),
            finished_at=now_iso(),
        )
        return

    answer = stdout.strip()
    if answer:
        add_log(task_id, "stdout", answer)
    if stderr:
        add_log(task_id, "stderr", stderr.rstrip())

    status = TaskStatus.completed if proc.returncode == 0 else TaskStatus.failed_execution
    summary = answer if answer else "Gemma task completed"
    update_task(
        task_id,
        status=status.value,
        summary=summary,
        exit_code=proc.returncode,
        error=None if proc.returncode == 0 else (stderr.strip() or "Gemma task failed"),
        finished_at=now_iso(),
    )


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
    if task.executor == "gemma":
        run_gemma_task(task_id)
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
