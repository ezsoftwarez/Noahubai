"""
Fable Engine — offline reasoning that is genuinely different per level
=====================================================================
Both levels run entirely on local models. The difference is real work, not a
label on the same call:

  Fable 5 — one pass. Fast, direct, good for most questions.
  Fable 6 — five passes: plan → draft → critique → refine → verify. The model
            argues with its own draft before you see it, which is what makes it
            worth the extra wall-clock time.

Every pass is timed and traced, so the UI can show what actually happened
instead of a spinner and a promise.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["fable"])

TRACE: List[Dict[str, Any]] = []   # last run, for /api/fable/trace


async def _timed(label: str, role: str, prompt: str, system: str = "") -> Dict[str, Any]:
    """Run one pass and record what it cost."""
    from backend import brain_api as B
    t0 = time.time()
    out = await B._local(prompt, role, system)
    st = B.LOCAL_STATE
    return {"pass": label, "role": role, "model": st["roles"].get(role, ""),
            "ms": int((time.time() - t0) * 1000), "text": out or "",
            "ok": bool(out)}


_CODE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)


def _extract_code(text: str) -> Optional[str]:
    m = _CODE_RE.search(text or "")
    return m.group(1).strip() if m else None


def _run_code(code: str, timeout: float = 20.0) -> Dict[str, Any]:
    """Execute a Python snippet in a temp dir and report what really happened.

    Used by the verify pass. Isolated interpreter (-I) so nothing is picked up
    from the working directory.
    """
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "snippet.py"
        f.write_text(code, encoding="utf-8")
        try:
            p = subprocess.run([sys.executable, "-I", str(f)], cwd=d,
                               capture_output=True, text=True, timeout=timeout)
            return {"ran": True, "code": p.returncode,
                    "stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:]}
        except subprocess.TimeoutExpired:
            return {"ran": False, "code": -1, "stdout": "",
                    "stderr": f"timed out after {timeout}s"}
        except Exception as e:
            return {"ran": False, "code": -1, "stdout": "", "stderr": str(e)}


async def run_fable(question: str, engine: str = "fable6") -> Optional[str]:
    """Return the final answer, or None when no local model is installed."""
    from backend import brain_api as B
    st = await B._refresh_local_models()
    if not st["available"]:
        return None

    TRACE.clear()

    if engine == "fable5":
        r = await _timed("answer", "chat", question,
                         "Answer directly and concretely. No preamble.")
        TRACE.append(r)
        return r["text"] or None

    # ── Fable 6 ────────────────────────────────────────────────────────────
    plan = await _timed(
        "plan", "fast",
        f"List the 3 things a correct answer to this must get right. "
        f"Terse bullets, no answer yet.\n\nQ: {question}",
        "You plan before answering. Be brief.")
    TRACE.append(plan)

    draft = await _timed(
        "draft", "chat",
        f"Question: {question}\n\nMust get right:\n{plan['text']}\n\n"
        f"Write the best answer you can.",
        "Answer directly and concretely.")
    TRACE.append(draft)
    if not draft["ok"]:
        return None

    critique = await _timed(
        "critique", "expert",
        f"Question: {question}\n\nDraft answer:\n{draft['text']}\n\n"
        f"What is wrong, missing, or overclaimed in this draft? Be specific and "
        f"harsh. If it is actually fine, say CLEAN and nothing else.",
        "You are a strict reviewer. You do not rewrite, you only find faults.")
    TRACE.append(critique)

    if critique["ok"] and "CLEAN" not in critique["text"].upper()[:40]:
        refine = await _timed(
            "refine", "chat",
            f"Question: {question}\n\nYour draft:\n{draft['text']}\n\n"
            f"Review of your draft:\n{critique['text']}\n\n"
            f"Rewrite the answer, fixing every valid point. Keep what was right.",
            "Answer directly. Do not mention the review process.")
        TRACE.append(refine)
        final = refine["text"] if refine["ok"] else draft["text"]
    else:
        final = draft["text"]

    # verify: if the answer contains runnable Python, actually run it
    code = _extract_code(final)
    if code:
        res = _run_code(code)
        TRACE.append({"pass": "verify", "role": "runtime", "model": sys.executable,
                      "ms": 0, "ok": res["code"] == 0,
                      "text": f"exit={res['code']}\n{res['stderr'] or res['stdout']}"[:1500]})
        if res["ran"] and res["code"] != 0:
            fix = await _timed(
                "repair", "coder",
                f"This code was produced for: {question}\n\n"
                f"```python\n{code}\n```\n\n"
                f"Running it failed:\n{res['stderr']}\n\n"
                f"Give the corrected full code and one line on what was wrong.",
                "Fix the real error. Output the complete corrected code.")
            TRACE.append(fix)
            if fix["ok"]:
                final = fix["text"]

    return final or None


class FableRequest(BaseModel):
    question: str
    engine: str = "fable6"


@router.post("/api/fable/run")
async def fable_run(req: FableRequest) -> Dict[str, Any]:
    t0 = time.time()
    out = await run_fable(req.question, req.engine)
    if out is None:
        return {"ok": False,
                "error": "No local model installed. Open 🩺 Setup Doctor to install one.",
                "passes": []}
    return {"ok": True, "answer": out, "engine": req.engine,
            "ms": int((time.time() - t0) * 1000),
            "passes": [{k: v for k, v in p.items() if k != "text"} | {
                "preview": (p.get("text") or "")[:200]} for p in TRACE]}


@router.get("/api/fable/trace")
async def fable_trace() -> Dict[str, Any]:
    """Full trace of the last run — what each pass thought and how long it took."""
    return {"passes": TRACE}
