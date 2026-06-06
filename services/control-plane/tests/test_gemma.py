from __future__ import annotations

from app.gemma import _build_cmd


def test_cmd_has_repetition_penalty():
    cmd = _build_cmd("M", "hi", max_tokens=1024, temperature=0.2, image=None, repetition_penalty=1.3, repetition_context_size=64)
    assert "--repetition-penalty" in cmd and "1.3" in cmd
    assert "--repetition-context-size" in cmd and "64" in cmd
    assert "--max-tokens" in cmd and "1024" in cmd
    assert "--image" not in cmd


def test_cmd_with_image():
    cmd = _build_cmd("M", "hi", max_tokens=512, temperature=0.2, image="/x/y.png", repetition_penalty=1.3, repetition_context_size=64)
    i = cmd.index("--image"); assert cmd[i + 1] == "/x/y.png"
    assert cmd.index("--image") < cmd.index("--prompt")


def test_cmd_no_penalty_when_one():
    cmd = _build_cmd("M", "hi", max_tokens=512, temperature=0.2, image=None, repetition_penalty=1.0, repetition_context_size=64)
    assert "--repetition-penalty" not in cmd
