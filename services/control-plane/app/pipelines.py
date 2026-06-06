from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .config import repo_root


class PipelineTemplate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_type: str = ""
    pipeline_name: str
    execute: dict[str, Any] = Field(default_factory=dict)
    validate_steps: list[dict[str, Any]] = Field(default_factory=list, alias="validate")
    report: dict[str, Any] = Field(default_factory=dict)
    notify: list[str] = Field(default_factory=list)


def pipelines_dir() -> Path:
    configured = os.environ.get("LOCAL_AGENT_RELAY_PIPELINES_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return repo_root() / "configs" / "pipelines"


def load_pipelines() -> dict[str, PipelineTemplate]:
    directory = pipelines_dir()
    if not directory.is_dir():
        return {}

    templates: dict[str, PipelineTemplate] = {}
    for path in sorted(directory.glob("*.yaml")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            if not isinstance(data, dict):
                continue
            template = PipelineTemplate(**data)
        except Exception:
            continue
        key = template.pipeline_name or path.stem
        templates[key] = template
    return templates


def resolve_pipeline(name: str | None) -> PipelineTemplate | None:
    if not name:
        return None
    return load_pipelines().get(name)
