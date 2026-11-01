"""
Second Brain — core chat API
============================
The honest core. Three rules it never breaks:

  1. It answers the question you actually asked. It never keyword-matches your
     message and dumps an unrelated template at you ("delulu" mode).
  2. It only claims a model is connected when one really is. `_has_model()` is
     the single source of truth, and the UI status dots read from it.
  3. With no model at all it still does the deterministic things well (scaffold
     a project, remember, search) and *says so plainly* for everything else,
     instead of inventing an answer.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import asyncio
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["second-brain"])

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
KEYS_FILE = DATA_DIR / "keys.json"
MEMORY_FILE = DATA_DIR / "memory.json"

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

# ──────────────────────────────────────────────────── providers
# `env` is the variable a key can also arrive in, so a configured machine needs
# no clicking. `local` marks the one provider that needs no key at all.
PROVIDERS: Dict[str, Dict[str, Any]] = {
    "free":      {"label": "Free / Offline", "local": True, "env": None,
                  "note": "Ollama on this machine. No key, no quota, no network."},
    "anthropic": {"label": "Claude", "env": "ANTHROPIC_API_KEY",
                  "url": "https://api.anthropic.com/v1/messages",
                  "model": "claude-sonnet-4-20250514"},
    "openai":    {"label": "OpenAI", "env": "OPENAI_API_KEY",
                  "url": "https://api.openai.com/v1/chat/completions",
                  "model": "gpt-4o-mini"},
    "deepseek":  {"label": "DeepSeek", "env": "DEEPSEEK_API_KEY",
                  "url": "https://api.deepseek.com/v1/chat/completions",
                  "model": "deepseek-chat"},
    "gemini":    {"label": "Gemini", "env": "GEMINI_API_KEY",
                  "url": "https://generativelanguage.googleapis.com/v1beta/models",
                  "model": "gemini-2.0-flash"},
    "groq":      {"label": "Groq", "env": "GROQ_API_KEY",
                  "url": "https://api.groq.com/openai/v1/chat/completions",
                  "model": "llama-3.3-70b-versatile"},
}

SETTINGS: Dict[str, Any] = {
    "engine": "off",          # off | fable5 | fable6
    "reasoning": "think",     # fast | think | ultrathink
    "resource": "mid",        # mid | high | max | ultramax
    "multitask": False,
    "autoselect": True,
}


def _load(path: Path, default: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def _store(path: Path, data: Any) -> None:
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


KEYS: Dict[str, str] = _load(KEYS_FILE, {})
MEMORY: Dict[str, Any] = _load(MEMORY_FILE, {"messages": []})

# a key present in the environment counts as configured — nothing to click
for _p, _m in PROVIDERS.items():
    _env = _m.get("env")
    if _env and not KEYS.get(_p) and os.environ.get(_env):
        KEYS[_p] = os.environ[_env]


def _remember(role: str, text: str, meta: Optional[Dict[str, Any]] = None) -> None:
    MEMORY.setdefault("messages", []).append({
        "role": role, "text": text[:4000], "meta": meta or {},
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    MEMORY["messages"] = MEMORY["messages"][-2000:]
    _store(MEMORY_FILE, MEMORY)


# ─────────────────────────────────────────────────── local models
LOCAL_STATE: Dict[str, Any] = {"available": False, "models": [], "roles": {}, "checked": 0.0}

# Which local model should play which part. Longest match wins, so
# "qwen2.5-coder" beats a bare "qwen".
_ROLE_HINTS: List[Tuple[str, str]] = [
    ("coder", "coder"), ("code", "coder"), ("deepseek-coder", "coder"),
    ("llama3.1", "expert"), ("llama3.3", "expert"), ("mixtral", "expert"),
    ("qwen2.5", "expert"), ("1b", "fast"), ("3b", "fast"), ("mini", "fast"),
    ("phi", "fast"),
]


def _assign_roles(models: List[str]) -> Dict[str, str]:
    """Pick a model per role from what is actually installed."""
    roles: Dict[str, str] = {}
    for role in ("coder", "expert", "fast"):
        for m in models:
            low = m.lower()
            if any(h in low and r == role for h, r in _ROLE_HINTS):
                roles.setdefault(role, m)
                break
    # chat is the general one: prefer an expert, else anything installed
    roles["chat"] = roles.get("expert") or (models[0] if models else "")
    # never leave a role empty while *some* model exists — a missing role would
    # silently disable a feature the user can see advertised
    for role in ("coder", "expert", "fast"):
        if not roles.get(role) and models:
            roles[role] = roles["chat"]
    return {k: v for k, v in roles.items() if v}


def _http_json(url: str, payload: Optional[dict] = None,
               headers: Optional[dict] = None, timeout: float = 120.0) -> dict:
    """Blocking JSON request. Callers wrap it in asyncio.to_thread."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "ignore") or "{}")


async def _refresh_local_models(force: bool = False) -> Dict[str, Any]:
    """Ask Ollama what it has. Cached for 20s so the UI can poll freely."""
    if not force and time.time() - LOCAL_STATE["checked"] < 20:
        return LOCAL_STATE
    LOCAL_STATE["checked"] = time.time()
    try:
        j = await asyncio.to_thread(_http_json, f"{OLLAMA}/api/tags", None, None, 3.0)
        models = [m["name"] for m in j.get("models", []) if m.get("name")]
        LOCAL_STATE.update(available=bool(models), models=models, roles=_assign_roles(models))
    except Exception:
        LOCAL_STATE.update(available=False, models=[], roles={})
    return LOCAL_STATE


def _has_credentials(provider: str) -> bool:
    """Real availability, not a guess — this is what the status dots show."""
    if provider == "free":
        return LOCAL_STATE["available"]
    return bool(KEYS.get(provider))


def _has_model() -> bool:
    return LOCAL_STATE["available"] or any(_has_credentials(p) for p in PROVIDERS if p != "free")


# ────────────────────────────────────────────────── intent gating
# The bug this exists to kill: a message was keyword-scanned and whichever
# template matched a word got dumped back, so "why is my website slow?" came
# back as a website starter kit. A build request and a question about building
# look similar to a keyword matcher and nothing alike to a person.

_QUESTION_RE = re.compile(
    r"^\s*(why|how|what|whats|what's|when|where|who|which|can|could|should|"
    r"would|will|is|are|am|do|does|did|explain|tell\s+me|help\s+me\s+understand|"
    r"any\s+idea|is\s+there)\b", re.I)

_ABOUT_RE = re.compile(
    r"\b(slow|faster|slower|broken|crash(es|ing)?|error|bug|fails?|failing|"
    r"not\s+working|doesn'?t\s+work|wrong|better|best|vs\.?|versus|difference|"
    r"compare|why|meaning|means)\b", re.I)

_BUILD_VERB_RE = re.compile(
    r"\b(make|build|create|generate|write|scaffold|implement|code|"
    r"give\s+me|set\s+up|start)\b", re.I)

_BUILD_NOUN_RE = re.compile(
    r"\b(app|application|game|site|website|page|landing|script|program|api|"
    r"server|bot|tool|cli|dashboard|clone|project|snake|todo|calculator)\b", re.I)


def _wants_build(text: str) -> bool:
    """True only for an actual 'make me X' request.

    A question keeps priority: "how do I build an api?" is a question about
    building, not an order to build. That single precedence rule is what stops
    the template dumping.
    """
    t = (text or "").strip()
    if not t:
        return False
    if t.endswith("?") or _QUESTION_RE.match(t):
        return False
    if _ABOUT_RE.search(t) and not _BUILD_NOUN_RE.search(t):
        return False
    return bool(_BUILD_VERB_RE.search(t) and _BUILD_NOUN_RE.search(t))


def _offline_notice(text: str) -> str:
    """Say plainly that nothing can answer this, and quote it back so it is
    obvious the message *was* read. Never fake an answer."""
    q = (text or "").strip()
    short = q if len(q) <= 160 else q[:157] + "…"
    return (
        f"I read your message — **“{short}”** — and it needs a model to reason "
        "about, which is exactly what is missing right now.\n\n"
        "I will not guess at an answer and dress it up as one. Here is how to "
        "fix it, cheapest first:\n\n"
        "- **Offline, free, private** — install [Ollama](https://ollama.com), "
        "then open 🩺 **Setup Doctor** and press *Install models*. After that "
        "this question gets a real answer with no network and no key.\n"
        "- **Cloud** — put a key in 🔑 (Claude, OpenAI, DeepSeek, Gemini or Groq).\n\n"
        "What already works with no model at all: scaffolding a runnable project "
        "(*“make an html snake game”*), and your saved chat history."
    )


# ─────────────────────────────────────────────────────── scaffolds
_SNAKE = """<!doctype html><meta charset="utf-8"><title>Snake</title>
<style>body{margin:0;background:#0b0e18;display:grid;place-items:center;height:100vh}
canvas{border:1px solid #2a3350}#s{color:#9fb4ff;font:14px system-ui;text-align:center}</style>
<div><canvas id=c width=400 height=400></canvas><div id=s>score 0 — arrows to steer</div></div>
<script>
const g=c.getContext('2d'),G=20,N=20;let sn=[{x:10,y:10}],d={x:1,y:0},f=rnd(),sc=0,dead=false;
function rnd(){return{x:0|Math.random()*N,y:0|Math.random()*N}}
onkeydown=e=>{const m={ArrowUp:[0,-1],ArrowDown:[0,1],ArrowLeft:[-1,0],ArrowRight:[1,0]}[e.key];
 if(!m)return;e.preventDefault();if(m[0]!==-d.x||m[1]!==-d.y)d={x:m[0],y:m[1]}};
setInterval(()=>{if(dead)return;
 const h={x:(sn[0].x+d.x+N)%N,y:(sn[0].y+d.y+N)%N};
 if(sn.some(p=>p.x===h.x&&p.y===h.y)){dead=true;s.textContent='dead — score '+sc+' (reload)';return}
 sn.unshift(h);
 if(h.x===f.x&&h.y===f.y){sc++;s.textContent='score '+sc;f=rnd()}else sn.pop();
 g.fillStyle='#0b0e18';g.fillRect(0,0,400,400);
 g.fillStyle='#ff5d7a';g.fillRect(f.x*G,f.y*G,G-1,G-1);
 g.fillStyle='#6c8bff';sn.forEach(p=>g.fillRect(p.x*G,p.y*G,G-1,G-1));},90);
</script>"""


def _scaffold(text: str) -> str:
    """A real, runnable starting point — deterministic, no model needed.

    Only ever reached when _wants_build() said yes, so it cannot land on top of
    a question.
    """
    low = (text or "").lower()
    if "snake" in low:
        return ("Here is a complete, runnable Snake — save as `snake.html` and open it.\n\n"
                f"```html\n{_SNAKE}\n```\n\n"
                "_Scaffolded offline with no model. Connect one (🩺) and I can extend "
                "it instead: levels, high scores, mobile controls._")
    if re.search(r"\b(api|server|rest|fastapi|backend)\b", low):
        return ("A working FastAPI service — `pip install fastapi uvicorn`, then "
                "`uvicorn app:app --reload`.\n\n"
                "```python\n"
                "from fastapi import FastAPI, HTTPException\n"
                "from pydantic import BaseModel\n\n"
                "app = FastAPI(title=\"API\")\n"
                "DB: dict[int, dict] = {}\n\n"
                "class Item(BaseModel):\n"
                "    name: str\n"
                "    done: bool = False\n\n"
                "@app.get(\"/items\")\n"
                "def list_items():\n"
                "    return [{\"id\": i, **v} for i, v in DB.items()]\n\n"
                "@app.post(\"/items\", status_code=201)\n"
                "def add(item: Item):\n"
                "    i = max(DB, default=0) + 1\n"
                "    DB[i] = item.model_dump()\n"
                "    return {\"id\": i, **DB[i]}\n\n"
                "@app.delete(\"/items/{i}\", status_code=204)\n"
                "def remove(i: int):\n"
                "    if DB.pop(i, None) is None:\n"
                "        raise HTTPException(404, \"no such item\")\n"
                "```\n\n"
                "_Scaffolded offline. Connect a model to have it shaped to your "
                "actual data instead of a generic item._")
    if re.search(r"\b(site|website|page|landing)\b", low):
        return ("A single-file responsive page — save as `index.html`.\n\n"
                "```html\n"
                "<!doctype html><meta charset=\"utf-8\">\n"
                "<meta name=viewport content=\"width=device-width,initial-scale=1\">\n"
                "<title>Project</title>\n"
                "<style>\n"
                "  :root{--bg:#0b0e18;--fg:#e8ecf8;--accent:#6c8bff}\n"
                "  *{box-sizing:border-box}\n"
                "  body{margin:0;font:16px/1.6 system-ui;background:var(--bg);color:var(--fg)}\n"
                "  .wrap{max-width:900px;margin:auto;padding:16px}\n"
                "  h1{font-size:clamp(28px,6vw,52px);margin:18vh 0 8px}\n"
                "  .grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}\n"
                "  .card{padding:18px;border:1px solid #2a3350;border-radius:14px}\n"
                "  a.btn{display:inline-block;margin-top:14px;padding:11px 18px;border-radius:10px;\n"
                "    background:var(--accent);color:#fff;text-decoration:none}\n"
                "</style>\n"
                "<div class=wrap>\n"
                "  <h1>Your project, stated in one line.</h1>\n"
                "  <p>The second line earns the first one.</p>\n"
                "  <a class=btn href=\"#more\">Get started</a>\n"
                "  <div class=grid id=more style=\"margin:14vh 0\">\n"
                "    <div class=card><h3>Fast</h3><p>No build step, one file.</p></div>\n"
                "    <div class=card><h3>Responsive</h3><p>Works at phone width.</p></div>\n"
                "    <div class=card><h3>Yours</h3><p>Edit the two lines above.</p></div>\n"
                "  </div>\n"
                "</div>\n"
                "```\n\n"
                "_Scaffolded offline. Connect a model to write real copy for your project._")
    return ("I can scaffold this offline, but only from a template — with no model "
            "connected I cannot design it around what you actually described.\n\n"
            "Say *snake game*, *api* or *landing page* for a complete runnable "
            "starting point right now, or connect a model (🩺 Setup Doctor) and I "
            "will build this specific thing properly.")


# ──────────────────────────────────────────────────── model calls
async def _local(prompt: str, role: str = "chat", system: str = "") -> Optional[str]:
    """One pass through a local Ollama model. None if nothing is installed."""
    st = await _refresh_local_models()
    model = st["roles"].get(role) or st["roles"].get("chat")
    if not model:
        return None
    body: Dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
    if system:
        body["system"] = system
    try:
        j = await asyncio.to_thread(_http_json, f"{OLLAMA}/api/generate", body, None, 300.0)
        return (j.get("response") or "").strip() or None
    except Exception:
        return None


async def _cloud(provider: str, prompt: str, system: str = "") -> Optional[str]:
    """One pass through a cloud provider. None if unkeyed or the call fails."""
    key = KEYS.get(provider)
    meta = PROVIDERS.get(provider) or {}
    if not key or not meta.get("url"):
        return None
    try:
        if provider == "anthropic":
            j = await asyncio.to_thread(
                _http_json, meta["url"],
                {"model": meta["model"], "max_tokens": 2048,
                 "system": system or "Be direct and concrete.",
                 "messages": [{"role": "user", "content": prompt}]},
                {"x-api-key": key, "anthropic-version": "2023-06-01"})
            return "".join(b.get("text", "") for b in j.get("content", [])).strip() or None
        if provider == "gemini":
            url = f"{meta['url']}/{meta['model']}:generateContent?key={key}"
            j = await asyncio.to_thread(
                _http_json, url,
                {"contents": [{"parts": [{"text": (system + "\n\n" + prompt).strip()}]}]}, {})
            cands = j.get("candidates") or []
            if not cands:
                return None
            return "".join(p.get("text", "") for p in
                           cands[0].get("content", {}).get("parts", [])).strip() or None
        # everything else speaks the OpenAI chat shape
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
        j = await asyncio.to_thread(
            _http_json, meta["url"], {"model": meta["model"], "messages": msgs},
            {"Authorization": f"Bearer {key}"})
        return (j["choices"][0]["message"]["content"] or "").strip() or None
    except Exception:
        return None


async def _best_provider() -> Optional[str]:
    """Autoselect: the best model that is genuinely reachable right now."""
    for p in ("anthropic", "openai", "deepseek", "groq", "gemini"):
        if _has_credentials(p):
            return p
    st = await _refresh_local_models()
    return "free" if st["available"] else None


async def answer(text: str, provider: str = "free", system: str = "") -> Tuple[str, str]:
    """Produce one reply. Returns (reply, model_label).

    The whole honesty contract lives here: a model answers, or a scaffold is
    offered for a genuine build request, or we say we cannot — never a template
    dumped over a question.
    """
    await _refresh_local_models()
    if provider == "auto" or (SETTINGS.get("autoselect") and not _has_credentials(provider)):
        provider = await _best_provider() or provider

    engine = SETTINGS.get("engine", "off")
    if engine in ("fable5", "fable6") and LOCAL_STATE["available"]:
        from backend.fable_engine import run_fable
        out = await run_fable(text, engine)
        if out:
            return out, f"🖥 {engine} · {LOCAL_STATE['roles'].get('chat', '')}"

    if provider == "free":
        reply = await _local(text, "coder" if _wants_build(text) else "chat", system)
        if reply:
            return reply, f"🖥 {LOCAL_STATE['roles'].get('chat', 'local')}"
    else:
        reply = await _cloud(provider, text, system)
        if reply:
            return reply, f"{PROVIDERS[provider]['label']} · {PROVIDERS[provider]['model']}"
        # a keyed provider that failed must not silently become a scaffold
        if _has_credentials(provider):
            return (f"**{PROVIDERS[provider]['label']} did not answer.** The key is saved, "
                    "so this is the provider or the network, not your setup. Try again, "
                    "pick another provider, or run 🩺 Setup Doctor."), "error"

    # nothing could reason. Deterministic help, or an honest no.
    if _wants_build(text):
        return _scaffold(text), "offline scaffold"
    return _offline_notice(text), "no model"


# ────────────────────────────────────────────────────── endpoints
class ChatRequest(BaseModel):
    message: str
    provider: str = "free"
    model: Optional[str] = None
    system: Optional[str] = None


@router.post("/api/chat")
async def chat(req: ChatRequest) -> Dict[str, Any]:
    _remember("me", req.message, {"provider": req.provider})
    reply, model = await answer(req.message, req.provider, req.system or "")
    _remember("ai", reply, {"model": model})
    return {"reply": reply, "model": model, "provider": req.provider,
            "engine": SETTINGS.get("engine"), "timestamp": time.time()}


@router.get("/api/local/models")
async def local_models() -> Dict[str, Any]:
    st = await _refresh_local_models(force=True)
    return {"available": st["available"], "models": st["models"], "roles": st["roles"],
            "host": OLLAMA}


@router.get("/api/providers")
async def providers() -> Dict[str, Any]:
    """Every provider with its real connected state — drives the status dots."""
    await _refresh_local_models()
    return {"providers": [
        {"id": p, "label": m["label"], "connected": _has_credentials(p),
         "local": bool(m.get("local")), "note": m.get("note", ""),
         "model": m.get("model", "")}
        for p, m in PROVIDERS.items()]}


class KeysRequest(BaseModel):
    keys: Dict[str, str]


@router.get("/api/settings/keys")
async def get_keys() -> Dict[str, Any]:
    # never return the secrets themselves, only whether each is set
    return {"configured": {p: bool(KEYS.get(p)) for p in PROVIDERS if p != "free"}}


@router.post("/api/settings/keys")
async def set_keys(req: KeysRequest) -> Dict[str, Any]:
    for p, v in req.keys.items():
        if p not in PROVIDERS:
            continue
        if v:
            KEYS[p] = v
        else:
            KEYS.pop(p, None)
    _store(KEYS_FILE, KEYS)
    return {"ok": True, "configured": {p: bool(KEYS.get(p)) for p in PROVIDERS if p != "free"}}


class SettingsRequest(BaseModel):
    engine: Optional[str] = None
    reasoning: Optional[str] = None
    resource: Optional[str] = None
    multitask: Optional[bool] = None
    autoselect: Optional[bool] = None


@router.post("/api/settings")
async def set_settings(req: SettingsRequest) -> Dict[str, Any]:
    for k, v in req.model_dump().items():
        if v is not None:
            SETTINGS[k] = v
    return {"ok": True, "settings": SETTINGS}


@router.get("/api/settings")
async def get_settings() -> Dict[str, Any]:
    return {"settings": SETTINGS}


@router.get("/api/memory/recent")
async def recent(limit: int = 50) -> Dict[str, Any]:
    msgs = MEMORY.get("messages", [])
    return {"total": len(msgs), "messages": msgs[-max(1, min(limit, 500)):]}
