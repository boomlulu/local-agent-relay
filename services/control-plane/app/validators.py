from __future__ import annotations

import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel

from .config import default_workdir, service_root
from .repository import add_log, add_validation
from .schemas import TaskRecord


class ValidationOutcome(BaseModel):
    name: str = ""
    adapter: str = ""
    status: str
    detail: str = ""
    exit_code: int | None = None


def artifact_dir(task_id: str) -> Path:
    path = service_root() / "data" / "artifacts" / task_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _subst(text: str | None, mapping: dict[str, str]) -> str:
    if text is None:
        return ""
    result = text
    for key, value in mapping.items():
        result = result.replace("${" + key + "}", value)
    return result


def git_diff_check(spec: dict[str, Any], ctx: dict[str, Any]) -> ValidationOutcome:
    proc = subprocess.run(
        ["git", "-C", str(ctx["root"]), "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        return ValidationOutcome(status="skipped", detail="not a git repo", exit_code=proc.returncode)
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    names = [line[3:] if len(line) > 3 else line for line in lines[:10]]
    detail = f"{len(lines)} changed files"
    if names:
        detail += ": " + ", ".join(names)
    return ValidationOutcome(status="passed", detail=detail, exit_code=proc.returncode)


def shell_command(spec: dict[str, Any], ctx: dict[str, Any]) -> ValidationOutcome:
    cmd = _subst(spec.get("command", ""), ctx["map"])
    if not cmd.strip():
        return ValidationOutcome(status="skipped", detail="no command")
    timeout = int(spec.get("timeout_seconds", 600))
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(ctx["root"]),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ValidationOutcome(status="failed", detail="timeout")
    combined = (proc.stdout or "") + (proc.stderr or "")
    log_path = ctx["artifact"] / (ctx["name"] + ".log")
    try:
        log_path.write_text(combined, encoding="utf-8")
    except Exception:
        pass
    status = "passed" if proc.returncode == 0 else "failed"
    detail = combined[-400:]
    return ValidationOutcome(status=status, detail=detail, exit_code=proc.returncode)


def log_error_scan(spec: dict[str, Any], ctx: dict[str, Any]) -> ValidationOutcome:
    path = Path(_subst(spec.get("input", ""), ctx["map"]))
    if not path.is_file():
        return ValidationOutcome(status="skipped", detail=f"input missing: {path}")
    text = path.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(
        r"(?i)\b(error|exception|traceback|fatal|failed|failure)\b", text
    )
    if matches:
        return ValidationOutcome(
            status="failed", detail=f"{len(matches)} error markers"
        )
    return ValidationOutcome(status="passed", detail="no error markers")


def http_smoke_test(spec: dict[str, Any], ctx: dict[str, Any]) -> ValidationOutcome:
    url = _subst(spec.get("url", ""), ctx["map"])
    expected = int(spec.get("expected_status", 200))
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        code = resp.status
        status = "passed" if code == expected else "failed"
        return ValidationOutcome(
            status=status, detail=f"HTTP {code} (want {expected})", exit_code=code
        )
    except urllib.error.HTTPError as exc:
        code = exc.code
        status = "passed" if code == expected else "failed"
        return ValidationOutcome(
            status=status, detail=f"HTTP {code} (want {expected})", exit_code=code
        )
    except Exception as exc:
        return ValidationOutcome(status="failed", detail=f"unreachable: {exc}")


ADAPTERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], ValidationOutcome]] = {
    "git-diff-check": git_diff_check,
    "shell-command": shell_command,
    "log-error-scan": log_error_scan,
    "http-smoke-test": http_smoke_test,
}


def run_validations(task: TaskRecord, pipeline: Any) -> list[ValidationOutcome]:
    root = (
        Path(task.project_root).expanduser().resolve()
        if task.project_root
        else default_workdir()
    )
    art = artifact_dir(task.id)
    mp = {"PROJECT_ROOT": str(root), "ARTIFACT_DIR": str(art)}

    outcomes: list[ValidationOutcome] = []
    for spec in pipeline.validate_steps:
        adapter = spec.get("adapter", "")
        name = spec.get("name", adapter or "step")
        ctx = {
            "root": root,
            "artifact": art,
            "map": mp,
            "name": name,
            "adapter": adapter,
        }
        fn = ADAPTERS.get(adapter)
        if fn:
            outcome = fn(spec, ctx)
        else:
            outcome = ValidationOutcome(
                status="skipped", detail=f"adapter not implemented: {adapter}"
            )
        outcome.name = name
        outcome.adapter = adapter
        add_log(
            task.id,
            "validation",
            f"{name} [{adapter}] -> {outcome.status}: {outcome.detail}",
        )
        add_validation(
            task.id, name, adapter, outcome.status, outcome.detail, outcome.exit_code
        )
        outcomes.append(outcome)
    return outcomes
