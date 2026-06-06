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


def run_gemma(
    prompt: str,
    max_tokens: int = 500,
    timeout_seconds: int = 240,
    cwd: str | None = None,
    image: str | None = None,
) -> GemmaCall:
    model = gemma_model_path()
    if not model.exists():
        return GemmaCall(
            status="model_missing",
            error=f"Gemma model path does not exist: {model}",
        )
    cmd = [
        python_bin(),
        "-m",
        "mlx_vlm.generate",
        "--model",
        str(model),
    ]
    if image:
        cmd += ["--image", image]
    cmd += [
        "--prompt",
        prompt,
        "--max-tokens",
        str(max_tokens),
        "--temperature",
        "0.2",
        "--no-verbose",
    ]
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
