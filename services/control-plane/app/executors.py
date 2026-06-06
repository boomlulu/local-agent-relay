from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

from .config import default_workdir, gemma_model_path, python_bin
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
    model_path = gemma_model_path()
    cwd = Path(task.project_root).expanduser().resolve() if task.project_root else default_workdir()
    timeout_seconds = int(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_TIMEOUT", "240"))

    add_log(task.id, "system", f"executor=gemma cwd={cwd}")
    add_log(task.id, "system", f"model={model_path}")

    if not model_path.exists():
        message = f"Gemma model path does not exist: {model_path}"
        add_log(task.id, "error", message)
        return ExecutorResult(status="failed_execution", error=message)

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
            add_log(task.id, "stdout", stdout.rstrip())
        if stderr:
            add_log(task.id, "stderr", stderr.rstrip())
        message = f"Gemma task timed out after {timeout_seconds} seconds"
        add_log(task.id, "error", message)
        return ExecutorResult(status="timeout", error=message)
    except Exception as exc:
        add_log(task.id, "error", str(exc))
        return ExecutorResult(status="failed_execution", error=str(exc))

    answer = stdout.strip()
    if answer:
        add_log(task.id, "stdout", answer)
    if stderr:
        add_log(task.id, "stderr", stderr.rstrip())

    rc = proc.returncode
    return ExecutorResult(
        status="completed" if rc == 0 else "failed_execution",
        summary=answer or "Gemma task completed",
        exit_code=rc,
        error=None if rc == 0 else (stderr.strip() or "Gemma task failed"),
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
