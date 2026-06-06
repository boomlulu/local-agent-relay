from __future__ import annotations

import json
import os
import subprocess

from .repository import add_log
from .schemas import TaskRecord


def _enabled() -> bool:
    return os.environ.get("LOCAL_AGENT_RELAY_NOTIFY", "1") != "0"


def _message(task: TaskRecord) -> str:
    return (task.summary or task.error or task.title or "task updated")[:200]


def notify_dashboard(task: TaskRecord) -> None:
    add_log(task.id, "notify", "dashboard updated")


def notify_macos(task: TaskRecord) -> None:
    text = _message(task)
    script = f'display notification {json.dumps(text)} with title {json.dumps("Local Agent Relay")} subtitle {json.dumps(task.title)}'
    subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=15)
    add_log(task.id, "notify", "macos notification sent")


def notify_voice(task: TaskRecord) -> None:
    subprocess.run(["say", _message(task)], capture_output=True, text=True, timeout=30)
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
