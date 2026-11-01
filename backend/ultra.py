"""
ULTRA layer — setup doctor, one-click model install, sessions
=============================================================
The three things that stand between "it has every feature" and "everything
actually works for me":

  1. Doctor      — one honest diagnosis of what is wired up and what is missing,
                   with a concrete fix for each gap, not a vague hint.
  2. Auto-setup  — install local models from inside the app, streamed live, so
                   "no model connected" is one click instead of a docs hunt.
  3. Sessions    — named, persisted chats you can switch between, instead of one
                   endless undifferentiated log.
"""
from __future__ import annotations

import asyncio
import json
import shutil
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend import brain_api as B

router = APIRouter(tags=["ultra"])

SESSIONS_FILE = B.DATA_DIR / "sessions.json"

# What a complete offline brain looks like, and why each piece earns its disk.
RECOMMENDED = [
    {"model": "qwen2.5-coder", "role": "coder", "size": "~4.7 GB",
     "why": "writes and fixes code — the single biggest quality jump"},
    {"model": "llama3.1", "role": "expert", "size": "~4.9 GB",
     "why": "deep reasoning: design questions, critiques, trade-offs"},
    {"model": "llama3.2:1b", "role": "fast", "size": "~1.3 GB",
     "why": "instant replies for short messages, keeps the app snappy"},
]


def _has_ollama() -> bool:
    return shutil.which("ollama") is not None


# ────────────────────────────────────────────────────────── Doctor
@router.get("/api/ultra/doctor")
async def doctor() -> Dict[str, Any]:
    """One honest read of the whole system: what works, what doesn't, how to fix it."""
    st = await B._refresh_local_models(force=True)
    keys = [p for p in B.PROVIDERS if p != "free" and B.KEYS.get(p)]
    checks: List[Dict[str, Any]] = []

    def add(name, ok, detail, fix=None, severity="info", action=None):
        checks.append({"name": name, "ok": ok, "detail": detail, "fix": fix,
                       "severity": severity, "action": action})

    # --- the brain ---
    if st["available"]:
        add("Offline brain", True,
            f"{len(st['models'])} local model(s): {', '.join(st['models'][:4])}")
    elif _has_ollama():
        add("Offline brain", False,
            "Ollama is installed but no models are pulled yet.",
            "Pull the recommended set — one click, no terminal needed.",
            "critical", "install_models")
    else:
        add("Offline brain", False,
            "Ollama is not installed, so there is no offline model to think with.",
            "Install Ollama from ollama.com, then come back and press Install models.",
            "critical", "open_ollama")

    if keys:
        add("Cloud models", True, f"{len(keys)} provider key(s): {', '.join(keys)}")
    else:
        add("Cloud models", False, "No provider keys saved.",
            "Optional once the offline brain is up. Otherwise add one in 🔑.",
            "warn" if st["available"] else "critical", "open_keys")

    # --- the thing users actually feel ---
    can_think = st["available"] or bool(keys)
    add("Can answer real questions", can_think,
        "A model is connected — questions get real answers."
        if can_think else
        "Nothing to reason with. It can still scaffold runnable projects and keep "
        "your history, but it will honestly refuse to answer questions rather "
        "than invent something.",
        None if can_think else "Fix 'Offline brain' or 'Cloud models' above.",
        "info" if can_think else "critical")

    # --- runtimes the verify/repair loop needs ---
    py = shutil.which("python3") or shutil.which("python")
    add("Python runtime", bool(py),
        f"Found at {py}" if py else "Not found — generated Python cannot be verified.",
        None if py else "Install Python 3 and restart the app.",
        "info" if py else "warn")
    node = shutil.which("node")
    add("Node runtime", bool(node),
        f"Found at {node}" if node else "Not found — JS projects cannot be verified.",
        None if node else "Install Node.js if you want JS verification.", "info")

    # --- what it has learned ---
    mem = len(B.MEMORY.get("messages", []))
    add("Memory", True, f"{mem} message(s) remembered"
        + (" — it has barely any history yet." if mem < 20 else "."))

    crit = [c for c in checks if not c["ok"] and c["severity"] == "critical"]
    score = round(100 * sum(1 for c in checks if c["ok"]) / max(1, len(checks)))
    return {
        "ok": not crit, "score": score, "checks": checks,
        "headline": ("Everything is wired up." if not crit else
                     f"{len(crit)} thing(s) need fixing before this works properly."),
        "ollama_installed": _has_ollama(),
        "recommended": RECOMMENDED,
        "installed_models": st["models"],
    }


# ─────────────────────────────────────────────── one-click install
class InstallRequest(BaseModel):
    models: Optional[List[str]] = None


@router.post("/api/ultra/install")
async def install_models(req: InstallRequest):
    """Stream `ollama pull` for each model so the UI shows real progress."""
    models = req.models or [m["model"] for m in RECOMMENDED]

    async def gen():
        if not _has_ollama():
            yield ("data: " + json.dumps({
                "error": "Ollama is not installed. Get it from https://ollama.com, "
                         "then press this again."}) + "\n\n")
            return
        for m in models:
            yield "data: " + json.dumps({"model": m, "status": "starting"}) + "\n\n"
            try:
                proc = await asyncio.create_subprocess_exec(
                    "ollama", "pull", m,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT)
                assert proc.stdout
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    txt = line.decode("utf-8", "ignore").strip()
                    if txt:
                        yield "data: " + json.dumps({"model": m, "line": txt[:200]}) + "\n\n"
                rc = await proc.wait()
                yield ("data: " + json.dumps({
                    "model": m, "status": "done" if rc == 0 else "failed"}) + "\n\n")
            except Exception as e:
                yield ("data: " + json.dumps({
                    "model": m, "status": "failed", "line": str(e)}) + "\n\n")
        st = await B._refresh_local_models(force=True)
        yield ("data: " + json.dumps({
            "done": True, "models": st["models"], "roles": st["roles"]}) + "\n\n")

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


# ────────────────────────────────────────────────────────── sessions
def _load_sessions() -> Dict[str, Any]:
    return B._load(SESSIONS_FILE, {"sessions": []})


def _save_sessions(d: Dict[str, Any]) -> None:
    B._store(SESSIONS_FILE, d)


class SessionSave(BaseModel):
    name: Optional[str] = None
    messages: List[Dict[str, Any]]


@router.get("/api/ultra/sessions")
async def list_sessions() -> Dict[str, Any]:
    d = _load_sessions()
    return {"sessions": [
        {k: v for k, v in s.items() if k != "messages"} | {"count": len(s.get("messages", []))}
        for s in reversed(d["sessions"])]}


@router.post("/api/ultra/sessions")
async def save_session(req: SessionSave) -> Dict[str, Any]:
    d = _load_sessions()
    first = next((m.get("text", "") for m in req.messages if m.get("role") == "me"), "")
    sid = uuid.uuid4().hex[:10]
    d["sessions"].append({
        "id": sid,
        "name": (req.name or first[:48] or "Untitled session"),
        "ts": time.strftime("%Y-%m-%d %H:%M"),
        "messages": req.messages[-400:],
    })
    d["sessions"] = d["sessions"][-100:]
    _save_sessions(d)
    return {"ok": True, "id": sid, "total": len(d["sessions"])}


@router.get("/api/ultra/sessions/{sid}")
async def get_session(sid: str) -> Dict[str, Any]:
    d = _load_sessions()
    s = next((x for x in d["sessions"] if x["id"] == sid), None)
    return {"ok": True, "session": s} if s else {"ok": False, "error": "not found"}


@router.delete("/api/ultra/sessions/{sid}")
async def del_session(sid: str) -> Dict[str, Any]:
    d = _load_sessions()
    before = len(d["sessions"])
    d["sessions"] = [x for x in d["sessions"] if x["id"] != sid]
    _save_sessions(d)
    return {"ok": True, "deleted": before - len(d["sessions"])}
