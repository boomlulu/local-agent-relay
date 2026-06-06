from __future__ import annotations

from typing import Any

from .gemma import run_gemma
from .schemas import TaskRecord
from .validators import ValidationOutcome


def _icon(status: str) -> str:
    if status == "passed":
        return "✅"
    if status == "failed":
        return "❌"
    return "⏭️"


def build_deterministic_report(
    task: TaskRecord,
    exec_summary: str | None,
    outcomes: list[ValidationOutcome],
) -> str:
    if outcomes:
        validation_lines = "\n".join(
            f"- {o.name} [{o.adapter}] {_icon(o.status)} {o.status} — {o.detail}"
            for o in outcomes
        )
    else:
        validation_lines = "No validators configured."

    failed = [o.name for o in outcomes if o.status == "failed"]
    if failed:
        outcome_line = "Validation failed: " + ", ".join(failed)
    elif outcomes:
        outcome_line = "All validations passed."
    else:
        outcome_line = "No validation configured."

    return (
        f"# {task.title}\n"
        f"\n"
        f"**Instruction:** {task.instruction}\n"
        f"**Executor:** {task.executor}\n"
        f"\n"
        f"## Execution\n"
        f"{exec_summary or '(no execution summary)'}\n"
        f"\n"
        f"## Validation\n"
        f"{validation_lines}\n"
        f"\n"
        f"## Outcome\n"
        f"{outcome_line}\n"
    )


def make_report(
    task: TaskRecord,
    pipeline: Any,
    exec_summary: str | None,
    outcomes: list[ValidationOutcome],
) -> str:
    deterministic = build_deterministic_report(task, exec_summary, outcomes)
    report_cfg = getattr(pipeline, "report", {}) or {}
    adapter = report_cfg.get("adapter")
    if adapter in {"gemma-summary", "gemma"}:
        prompt = (
            "把下面的任务执行报告浓缩成一段简洁中文小结（不超过120字），"
            "面向开发者，突出是否成功、关键改动、失败项：\n\n" + deterministic
        )
        call = run_gemma(prompt, max_tokens=300, timeout_seconds=180)
        if call.status == "completed" and call.stdout.strip():
            return call.stdout.strip() + "\n\n---\n\n" + deterministic
        return deterministic
    return deterministic
