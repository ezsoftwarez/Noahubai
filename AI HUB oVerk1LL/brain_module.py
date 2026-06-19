"""AI Hub Brain — auto-routing, Blockbuster model blending, device + agent builder registry."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Blockbuster AI Platform defaults (f ur BLOXXBUSTER AI PLAFROM .py)
BLOCKBUSTER_PROVIDERS: dict[str, dict[str, Any]] = {
    "OpenRouter": {
        "base": "https://openrouter.ai/api/v1",
        "needs_key": True,
        "free_filter_suffix": ":free",
    },
    "Groq": {
        "base": "https://api.groq.com/openai/v1",
        "needs_key": True,
        "free_filter_suffix": None,
    },
    "Local": {
        "base": "http://127.0.0.1:1234/v1",
        "needs_key": False,
        "free_filter_suffix": None,
    },
}

BLOCKBUSTER_FREE_MODELS: list[str] = [
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
]

ENGINE_MODEL_MAP: dict[str, list[str]] = {
    "general": ["deepseek/deepseek-chat:free", "google/gemma-2-9b-it:free"],
    "coding": ["deepseek/deepseek-chat:free", "meta-llama/llama-3.2-3b-instruct:free"],
    "ui": ["google/gemma-2-9b-it:free", "mistralai/mistral-7b-instruct:free"],
    "research": ["deepseek/deepseek-chat:free", "mistralai/mistral-7b-instruct:free"],
    "fast": ["meta-llama/llama-3.2-3b-instruct:free", "deepseek/deepseek-chat:free"],
    "multi": list(BLOCKBUSTER_FREE_MODELS),
    "local": ["llama3.2"],
}

BLEND_SYSTEM = (
    "You are the AI Hub Brain synthesizer. Merge multiple AI worker outputs into one "
    "clear, non-redundant answer. Keep the best facts, code, and structure. "
    "Do not mention that you blended models unless asked."
)


def _default_brain_config() -> dict[str, Any]:
    return {
        "version": 1,
        "autoMode": True,
        "provider": "OpenRouter",
        "numWorkers": 3,
        "selectedModels": BLOCKBUSTER_FREE_MODELS[:3],
        "blenderModel": "deepseek/deepseek-chat:free",
        "codingQuality": 50,
        "textLength": 50,
        "customAgents": [],
        "updatedAt": int(time.time() * 1000),
    }


class BrainStore:
    def __init__(self, bridge_dir: Path) -> None:
        self.bridge_dir = bridge_dir
        self.config_path = bridge_dir / "brain-config.json"
        self.devices_path = bridge_dir / "brain-devices.json"

    def load_config(self) -> dict[str, Any]:
        if self.config_path.is_file():
            try:
                data = json.loads(self.config_path.read_text(encoding="utf-8"))
                for k, v in _default_brain_config().items():
                    data.setdefault(k, v)
                return data
            except (OSError, json.JSONDecodeError):
                pass
        return _default_brain_config()

    def save_config(self, data: dict[str, Any]) -> dict[str, Any]:
        data["updatedAt"] = int(time.time() * 1000)
        self.config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def load_devices(self) -> dict[str, Any]:
        if self.devices_path.is_file():
            try:
                return json.loads(self.devices_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        return {"version": 1, "devices": [], "updatedAt": 0}

    def upload_devices(self, devices: list[dict[str, Any]], source: str = "agents-manager") -> dict[str, Any]:
        store = self.load_devices()
        existing = {d.get("id"): d for d in store.get("devices", []) if d.get("id")}
        for dev in devices:
            did = str(dev.get("id") or dev.get("name") or f"dev-{len(existing)}")
            existing[did] = {
                **dev,
                "id": did,
                "source": dev.get("source", source),
                "uploadedAt": int(time.time() * 1000),
            }
        payload = {
            "version": 1,
            "devices": list(existing.values()),
            "updatedAt": int(time.time() * 1000),
            "source": source,
        }
        self.devices_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def save_custom_agent(self, agent: dict[str, Any]) -> dict[str, Any]:
        cfg = self.load_config()
        agents: list[dict[str, Any]] = list(cfg.get("customAgents") or [])
        aid = str(agent.get("id") or f"agent-{int(time.time())}")
        agent["id"] = aid
        agent["updatedAt"] = int(time.time() * 1000)
        replaced = False
        for i, a in enumerate(agents):
            if a.get("id") == aid:
                agents[i] = agent
                replaced = True
                break
        if not replaced:
            agents.append(agent)
        cfg["customAgents"] = agents
        self.save_config(cfg)
        return agent

    def delete_custom_agent(self, agent_id: str) -> bool:
        cfg = self.load_config()
        before = len(cfg.get("customAgents") or [])
        cfg["customAgents"] = [a for a in (cfg.get("customAgents") or []) if a.get("id") != agent_id]
        self.save_config(cfg)
        return len(cfg["customAgents"]) < before


def classify_task(prompt: str) -> str:
    p = prompt.lower()
    if re.search(r"\b(html|css|react|vue|ui|layout|design|frontend)\b", p):
        return "ui"
    if re.search(r"\b(research|analyze|compare|explain|why|study)\b", p):
        return "research"
    if re.search(r"\b(code|bug|fix|python|javascript|api|function|refactor)\b", p):
        return "coding"
    return "general"


def pick_models(engine_combo: str, config: dict[str, Any], prompt: str, auto: bool) -> list[str]:
    if auto:
        route = classify_task(prompt)
        models = ENGINE_MODEL_MAP.get(route, ENGINE_MODEL_MAP["general"])
    else:
        models = ENGINE_MODEL_MAP.get(engine_combo, ENGINE_MODEL_MAP["general"])

    selected = config.get("selectedModels") or BLOCKBUSTER_FREE_MODELS
    num = max(1, min(6, int(config.get("numWorkers") or 3)))
    pool = selected if selected else models
    out: list[str] = []
    for m in models:
        if m in pool and m not in out:
            out.append(m)
    for m in pool:
        if m not in out:
            out.append(m)
        if len(out) >= num:
            break
    return out[:num]


def _chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "AIHubBrain/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = Request(f"{base_url.rstrip('/')}/chat/completions", data=payload, headers=headers, method="POST")
    with urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str((data.get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()


def _ollama_chat(url: str, model: str, messages: list[dict[str, str]]) -> str:
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode("utf-8")
    req = Request(
        f"{url.rstrip('/')}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data.get("message", {}).get("content") or "").strip()


def run_workers(
    prompt: str,
    history: list[dict[str, str]],
    models: list[str],
    conn: dict[str, Any],
) -> list[dict[str, Any]]:
    quality = int(conn.get("codingQuality") or 50)
    length = int(conn.get("textLength") or 50)
    temp = 0.2 + (100 - quality) * 0.8 / 100.0
    max_tokens = int(256 + (length / 100.0) * 7936)
    system = f"You are an AI Hub worker. MODE: {conn.get('engineCombo', 'auto')}. Be helpful and concise."
    messages = [{"role": "system", "content": system}]
    messages.extend(history[-8:])
    messages.append({"role": "user", "content": prompt})

    workers: list[dict[str, Any]] = []
    conn_mode = conn.get("connMode") or "openai"

    for model in models:
        try:
            if conn_mode == "ollama":
                out = _ollama_chat(str(conn.get("ollamaUrl") or "http://127.0.0.1:11434"), model, messages)
            else:
                base = str(conn.get("apiBase") or BLOCKBUSTER_PROVIDERS["OpenRouter"]["base"])
                key = str(conn.get("apiKey") or "")
                out = _chat_completion(base, key, model, messages, max_tokens=max_tokens, temperature=temp)
            workers.append({"model": model, "output": out, "ok": True})
        except (URLError, HTTPError, OSError, json.JSONDecodeError, TimeoutError) as exc:
            workers.append({"model": model, "output": "", "ok": False, "error": str(exc)})
    return workers


def blend_heuristic(prompt: str, workers: list[dict[str, Any]]) -> str:
    ok = [w for w in workers if w.get("ok") and (w.get("output") or "").strip()]
    if not ok:
        errs = "; ".join(w.get("error", "failed") for w in workers)
        return f"Brain auto-blend failed: {errs or 'no worker responses'}"

    parts = [w["output"].strip() for w in ok]
    if len(parts) == 1:
        header = f"**Auto** · {ok[0]['model']}\n\n"
        return header + parts[0]

    parts.sort(key=len, reverse=True)
    base = parts[0]
    extras: list[str] = []
    for p in parts[1:]:
        snippet = p[:400]
        if snippet and snippet not in base:
            extras.append(snippet)
    models = ", ".join(w["model"] for w in ok)
    header = f"**Auto-blended** · {len(ok)} Blockbuster models ({models})\n\n"
    if extras:
        return header + base + "\n\n---\n**Merged insights:**\n\n" + "\n\n".join(extras)
    return header + base


def blend_with_api(prompt: str, workers: list[dict[str, Any]], conn: dict[str, Any]) -> str:
    ok = [w for w in workers if w.get("ok") and w.get("output")]
    if not ok:
        return blend_heuristic(prompt, workers)

    blender = str(conn.get("blenderModel") or ok[0]["model"])
    body = "\n\n".join(f"## Worker: {w['model']}\n{w['output']}" for w in ok)
    messages = [
        {"role": "system", "content": BLEND_SYSTEM},
        {
            "role": "user",
            "content": f"User prompt:\n{prompt}\n\nWorker outputs:\n{body}\n\nProduce one merged answer.",
        },
    ]
    try:
        if conn.get("connMode") == "ollama":
            out = _ollama_chat(str(conn.get("ollamaUrl") or "http://127.0.0.1:11434"), blender, messages)
        else:
            base = str(conn.get("apiBase") or BLOCKBUSTER_PROVIDERS["OpenRouter"]["base"])
            key = str(conn.get("apiKey") or "")
            out = _chat_completion(base, key, blender, messages)
        if out:
            return f"**Brain blend** · synthesizer `{blender}`\n\n{out}"
    except (URLError, HTTPError, OSError, json.JSONDecodeError, TimeoutError):
        pass
    return blend_heuristic(prompt, workers)


def brain_auto_execute(store: BrainStore, body: dict[str, Any]) -> dict[str, Any]:
    cfg = store.load_config()
    auto = bool(body.get("auto", cfg.get("autoMode", True)))
    prompt = str(body.get("prompt") or "").strip()
    if not prompt:
        return {"ok": False, "error": "empty prompt"}

    engine_combo = str(body.get("engineCombo") or "multi")
    devices = store.load_devices().get("devices") or []
    synced_agents = body.get("syncedAgents") or []
    models = pick_models(engine_combo, cfg, prompt, auto)

    conn = {
        "connMode": body.get("connMode"),
        "apiBase": body.get("apiBase"),
        "apiKey": body.get("apiKey"),
        "ollamaUrl": body.get("ollamaUrl"),
        "ollamaModel": body.get("ollamaModel"),
        "blenderModel": body.get("blenderModel") or cfg.get("blenderModel"),
        "codingQuality": body.get("codingQuality") or cfg.get("codingQuality"),
        "textLength": body.get("textLength") or cfg.get("textLength"),
        "engineCombo": engine_combo,
    }

    history = body.get("history") or []
    workers = run_workers(prompt, history, models, conn)
    use_api_blend = bool(conn.get("apiKey")) or conn.get("connMode") == "ollama"
    blended = blend_with_api(prompt, workers, conn) if use_api_blend else blend_heuristic(prompt, workers)

    return {
        "ok": True,
        "auto": auto,
        "route": classify_task(prompt) if auto else engine_combo,
        "models": models,
        "workers": workers,
        "blended": blended,
        "deviceCount": len(devices),
        "syncedAgentCount": len(synced_agents),
        "customAgentCount": len(cfg.get("customAgents") or []),
        "provider": cfg.get("provider", "OpenRouter"),
        "blockbusterModels": BLOCKBUSTER_FREE_MODELS,
    }


def brain_get_config(store: BrainStore) -> dict[str, Any]:
    cfg = store.load_config()
    devices = store.load_devices()
    return {
        "ok": True,
        "config": cfg,
        "devices": devices.get("devices") or [],
        "providers": BLOCKBUSTER_PROVIDERS,
        "freeModels": BLOCKBUSTER_FREE_MODELS,
        "engineModelMap": ENGINE_MODEL_MAP,
    }
