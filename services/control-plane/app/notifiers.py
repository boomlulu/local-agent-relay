from __future__ import annotations

import json
import os
import subprocess

from .repository import add_log, list_validations
from .schemas import TaskRecord


def _enabled() -> bool:
    return os.environ.get("LOCAL_AGENT_RELAY_NOTIFY", "1") != "0"


def _outcome(task):
    vals = list_validations(task.id)
    passed = [v["name"] for v in vals if v["status"] == "passed"]
    failed = [v["name"] for v in vals if v["status"] == "failed"]
    return passed, failed


def _voice_text(task) -> str:
    passed, failed = _outcome(task)
    if task.status == "failed_validation" or failed:
        return f"{task.title}，验收失败，问题在 {'、'.join(failed) or '未知'}"[:200]
    if passed:
        return f"{task.title}，已完成，验收通过"[:200]
    return f"{task.title}，已完成"[:200]


def _macos_body(task) -> str:
    passed, failed = _outcome(task)
    if task.status == "failed_validation" or failed:
        return ("❌ 验收失败：" + ('、'.join(failed) or '未知'))[:200]
    if passed:
        return ("✅ 验收通过 (" + '、'.join(passed) + ")")[:200]
    return "✅ 已完成"


def notify_dashboard(task: TaskRecord) -> None:
    add_log(task.id, "notify", "dashboard updated")


def notify_macos(task: TaskRecord) -> None:
    body = _macos_body(task)
    script = f'display notification {json.dumps(body)} with title {json.dumps("Local Agent Relay")} subtitle {json.dumps(task.title)}'
    subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=15)
    add_log(task.id, "notify", "macos notification sent")


def notify_voice(task: TaskRecord) -> None:
    text = _voice_text(task)
    proc = subprocess.run(["say", "-v", "Tingting", text], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        subprocess.run(["say", text], capture_output=True, text=True, timeout=30)
    add_log(task.id, "notify", "voice played")


NOTIFIERS = {"dashboard": notify_dashboard, "macos": notify_macos, "voice": notify_voice}


def run_notifiers(task: TaskRecord, pipeline) -> None:
    targets = getattr(pipeline, "notify", []) or []
    for target in targets:
        fn = NOTIFIERS.get(target)
        if fn is None:
            add_log(task.id, "notify", f"unknown notifier: {target}")
            continue
        if target in {"macos", "voice"} and not _enabled():
            add_log(task.id, "notify", f"{target} skipped (disabled)")
            continue
        try:
            fn(task)
        except Exception as exc:
            add_log(task.id, "notify", f"{target} failed: {exc}")
