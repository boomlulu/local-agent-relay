from __future__ import annotations

import os
import subprocess

from pydantic import BaseModel

from .config import gemma_model_path, python_bin


class GemmaCall(BaseModel):
    status: str  # "completed" | "failed" | "timeout" | "model_missing"
    stdout: str = ""
    stderr: str = ""
    returncode: int | None = None
    error: str | None = None


def _build_cmd(
    model_path,
    prompt: str,
    *,
    max_tokens: int,
    temperature: float,
    image: str | None,
    repetition_penalty: float,
    repetition_context_size: int,
) -> list[str]:
    cmd = [python_bin(), "-m", "mlx_vlm.generate", "--model", str(model_path)]
    if image:
        cmd += ["--image", image]
    cmd += ["--prompt", prompt, "--max-tokens", str(max_tokens), "--temperature", str(temperature)]
    if repetition_penalty and repetition_penalty > 1.0:
        cmd += ["--repetition-penalty", str(repetition_penalty), "--repetition-context-size", str(repetition_context_size)]
    cmd += ["--no-verbose"]
    return cmd


def run_gemma(
    prompt: str,
    max_tokens: int = 512,
    timeout_seconds: int = 240,
    cwd: str | None = None,
    image: str | None = None,
    temperature: float | None = None,
    repetition_penalty: float | None = None,
    repetition_context_size: int | None = None,
) -> GemmaCall:
    model = gemma_model_path()
    if not model.exists():
        return GemmaCall(
            status="model_missing",
            error=f"Gemma model path does not exist: {model}",
        )
    temperature = (
        temperature
        if temperature is not None
        else float(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_TEMP", "0.2"))
    )
    repetition_penalty = (
        repetition_penalty
        if repetition_penalty is not None
        else float(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_REP_PENALTY", "1.3"))
    )
    repetition_context_size = (
        repetition_context_size
        if repetition_context_size is not None
        else int(os.environ.get("LOCAL_AGENT_RELAY_GEMMA_REP_CTX", "64"))
    )
    cmd = _build_cmd(
        model,
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        image=image,
        repetition_penalty=repetition_penalty,
        repetition_context_size=repetition_context_size,
    )
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return GemmaCall(
            status="timeout",
            stdout=out or "",
            stderr=err or "",
            error="gemma timed out",
        )
    except Exception as exc:
        return GemmaCall(status="failed", error=str(exc))
    rc = proc.returncode
    return GemmaCall(
        status="completed" if rc == 0 else "failed",
        stdout=out or "",
        stderr=err or "",
        returncode=rc,
        error=None if rc == 0 else (err.strip() or "gemma failed"),
    )
