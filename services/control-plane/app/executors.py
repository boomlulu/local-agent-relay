from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

from .config import default_workdir, gemma_model_path
from .gemma import run_gemma
from .repository import add_log
from .schemas import ExecutorResult, TaskRecord


def build_gemma_prompt(instruction: str) -> str:
    local_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    return f"""你是 Local Agent Relay 的本地助手 Gemma。
请直接回答用户，不要展示推理过程。
如果用户询问当前时间、日期、今天、现在等信息，必须使用下面提供的本机时间。

当前本机时间：{local_time}

用户请求：
{instruction}
"""


def run_gemma_task(task: TaskRecord) -> ExecutorResult:
    cwd = Path(task.project_root).expanduser().resolve() if task.project_root else default_workdir()
    timeout = int(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_TIMEOUT", "240"))
    max_tokens = int(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_MAX_TOKENS", "1024"))

    add_log(task.id, "system", f"executor=gemma cwd={cwd}")
    add_log(task.id, "system", f"model={gemma_model_path()}")
    if task.image_path:
        add_log(task.id, "system", f"image={task.image_path}")

    call = run_gemma(
        build_gemma_prompt(task.instruction),
        max_tokens=max_tokens,
        timeout_seconds=timeout,
        cwd=str(cwd),
        image=task.image_path,
    )

    if call.status == "model_missing":
        add_log(task.id, "error", call.error)
        return ExecutorResult(status="failed_execution", error=call.error)

    if call.status == "timeout":
        if call.stdout:
            add_log(task.id, "stdout", call.stdout.rstrip())
        if call.stderr:
            add_log(task.id, "stderr", call.stderr.rstrip())
        message = f"Gemma task timed out after {timeout} seconds"
        add_log(task.id, "error", message)
        return ExecutorResult(status="timeout", error=message)

    if call.status == "failed" and call.returncode is None:
        add_log(task.id, "error", call.error)
        return ExecutorResult(status="failed_execution", error=call.error)

    answer = call.stdout.strip()
    if answer:
        add_log(task.id, "stdout", answer)
    if call.stderr:
        add_log(task.id, "stderr", call.stderr.rstrip())

    rc = call.returncode
    return ExecutorResult(
        status="completed" if rc == 0 else "failed_execution",
        summary=answer or "Gemma task completed",
        exit_code=rc,
        error=None if rc == 0 else (call.stderr.strip() or "Gemma task failed"),
    )


def run_shell_task(task: TaskRecord) -> ExecutorResult:
    command = task.command or "printf '%s\\n' \"$LOCAL_AGENT_RELAY_INSTRUCTION\""
    cwd = Path(task.project_root).expanduser().resolve() if task.project_root else default_workdir()

    add_log(task.id, "system", f"executor=shell cwd={cwd}")
    add_log(task.id, "system", f"command={command}")

    env = os.environ.copy()
    env["LOCAL_AGENT_RELAY_TASK_ID"] = task.id
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
        add_log(task.id, "error", str(exc))
        return ExecutorResult(status="failed_execution", error=str(exc))

    if stdout:
        add_log(task.id, "stdout", stdout.rstrip())
    if stderr:
        add_log(task.id, "stderr", stderr.rstrip())

    rc = proc.returncode
    return ExecutorResult(
        status="completed" if rc == 0 else "failed_execution",
        summary="Shell task completed" if rc == 0 else "Shell task failed",
        exit_code=rc,
        error=None if rc == 0 else (stderr.strip() or "Shell task failed"),
        changed_files=[],
    )
