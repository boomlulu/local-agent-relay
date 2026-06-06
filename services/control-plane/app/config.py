from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "Local Agent Relay Control Plane"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def service_root() -> Path:
    return Path(__file__).resolve().parents[1]


def db_path() -> Path:
    configured = os.environ.get("LOCAL_AGENT_RELAY_DB")
    if configured:
        return Path(configured).expanduser().resolve()
    return service_root() / "data" / "control_plane.sqlite3"


def default_workdir() -> Path:
    configured = os.environ.get("LOCAL_AGENT_RELAY_WORKDIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return repo_root()

