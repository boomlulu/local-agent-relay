from __future__ import annotations

import os

from app.pipelines import load_pipelines, resolve_pipeline


def test_load_real_pipelines() -> None:
    os.environ.pop("LOCAL_AGENT_RELAY_PIPELINES_DIR", None)
    pipelines = load_pipelines()

    assert "web-basic" in pipelines

    web = resolve_pipeline("web-basic")
    assert web is not None
    assert web.project_type == "web"
    assert len(web.validate_steps) >= 1


def test_resolve_none() -> None:
    os.environ.pop("LOCAL_AGENT_RELAY_PIPELINES_DIR", None)
    assert resolve_pipeline(None) is None
    assert resolve_pipeline("") is None
    assert resolve_pipeline("nope") is None


def test_pipelines_dir_override(tmp_path) -> None:
    yaml_content = """\
project_type: custom
pipeline_name: custom-basic

execute:
  adapter: claude-code

validate:
  - name: smoke
    adapter: shell-command
    command: echo hi

report:
  adapter: gemma-summary

notify:
  - dashboard
"""
    (tmp_path / "custom.yaml").write_text(yaml_content, encoding="utf-8")

    previous = os.environ.get("LOCAL_AGENT_RELAY_PIPELINES_DIR")
    os.environ["LOCAL_AGENT_RELAY_PIPELINES_DIR"] = str(tmp_path)
    try:
        pipelines = load_pipelines()
        assert "custom-basic" in pipelines

        template = resolve_pipeline("custom-basic")
        assert template is not None
        assert template.project_type == "custom"
        assert len(template.validate_steps) == 1
        assert template.notify == ["dashboard"]
    finally:
        if previous is None:
            os.environ.pop("LOCAL_AGENT_RELAY_PIPELINES_DIR", None)
        else:
            os.environ["LOCAL_AGENT_RELAY_PIPELINES_DIR"] = previous
