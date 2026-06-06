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


def uploads_dir() -> Path:
    configured = os.environ.get("LOCAL_AGENT_RELAY_UPLOADS")
    base = Path(configured).expanduser().resolve() if configured else service_root() / "data" / "uploads"
    base.mkdir(parents=True, exist_ok=True)
    return base


def default_workdir() -> Path:
    configured = os.environ.get("LOCAL_AGENT_RELAY_WORKDIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return repo_root()


def gemma_model_path() -> Path:
    configured = os.environ.get("LOCAL_AGENT_RELAY_GEMMA_MODEL")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(
        "/Users/boom/.cache/huggingface/hub/"
        "models--mlx-community--gemma-4-12B-it-4bit/"
        "snapshots/8de8ab4d40f6b95a76ffa491e23dd430e1f725b5"
    )


def python_bin() -> str:
    return os.environ.get("LOCAL_AGENT_RELAY_PYTHON", "/opt/homebrew/bin/python3.10")
