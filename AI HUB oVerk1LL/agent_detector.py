"""
Lightweight local AI agent detection for AI Hub Bridge.

One cached pass: process names (psutil), config/data folders, optional localhost ports.
Designed to stay cheap on idle machines — no background threads, no full disk walks.
"""
from __future__ import annotations

import os
import re
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore[assignment,misc]

DETECT_CACHE_TTL = 55.0
PORT_TIMEOUT = 0.22

_detect_cache: dict[str, Any] = {"ts": 0.0, "data": None}


@dataclass(frozen=True)
class AgentSignature:
    id: str
    label: str
    category: str
    processes: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()
    ports: tuple[int, ...] = ()
    hub_id: str | None = None
    note: str = ""


def _compile(patterns: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(p, re.I) for p in patterns)


SIGNATURES: tuple[AgentSignature, ...] = (
    AgentSignature(
        "cursor",
        "Cursor Agent",
        "ide",
        processes=(r"^cursor(\.exe)?$", r"cursor helper", r"cursor\.exe"),
        paths=(".cursor",),
        hub_id="cursor-agent",
        note="IDE + Agent chat transcripts under ~/.cursor/projects",
    ),
    AgentSignature(
        "windsurf",
        "Windsurf",
        "ide",
        processes=(r"^windsurf(\.exe)?$", r"windsurf helper"),
        paths=("Windsurf", ".codeium/windsurf"),
    ),
    AgentSignature(
        "vscode",
        "VS Code",
        "ide",
        processes=(r"^code(\.exe)?$", r"code helper"),
        paths=(".vscode",),
        note="Copilot / Continue / Cline extensions often run here",
    ),
    AgentSignature(
        "vscodium",
        "VSCodium",
        "ide",
        processes=(r"^codium(\.exe)?$", r"vscodium"),
        paths=(".vscode-oss",),
    ),
    AgentSignature(
        "claude-desktop",
        "Claude Desktop",
        "assistant",
        processes=(r"^claude(\.exe)?$", r"claude desktop"),
        paths=(".claude", "Claude"),
        hub_id="claude",
    ),
    AgentSignature(
        "chatgpt",
        "ChatGPT Desktop",
        "assistant",
        processes=(r"chatgpt(\.exe)?$", r"^chatgpt$"),
        paths=("com.openai.chat", "OpenAI/ChatGPT"),
    ),
    AgentSignature(
        "copilot",
        "GitHub Copilot",
        "coding",
        processes=(
            r"copilot",
            r"github copilot",
            r"copilot-language-server",
            r"copilot-agent",
        ),
        paths=(".github-copilot",),
        hub_id="codex",
    ),
    AgentSignature(
        "continue",
        "Continue.dev",
        "coding",
        processes=(r"continue", r"continue-binary"),
        paths=(".continue",),
    ),
    AgentSignature(
        "cline",
        "Cline",
        "coding",
        processes=(r"cline", r"claude-dev"),
        paths=(".cline",),
    ),
    AgentSignature(
        "codeium",
        "Codeium",
        "coding",
        processes=(r"codeium", r"codeium\.exe", r"codesearch"),
        paths=(".codeium",),
    ),
    AgentSignature(
        "roo-code",
        "Roo Code",
        "coding",
        processes=(r"roo-cline", r"roo code"),
        paths=(".roo",),
    ),
    AgentSignature(
        "tabnine",
        "Tabnine",
        "coding",
        processes=(r"tabnine", r"TabNine"),
        paths=(".tabnine",),
    ),
    AgentSignature(
        "supermaven",
        "Supermaven",
        "coding",
        processes=(r"supermaven",),
        paths=(".supermaven",),
    ),
    AgentSignature(
        "open-interpreter",
        "Open Interpreter",
        "coding",
        processes=(r"interpreter", r"open-interpreter"),
        paths=(".open-interpreter",),
    ),
    AgentSignature(
        "ollama",
        "Ollama",
        "local-llm",
        processes=(r"^ollama(\.exe)?$",),
        paths=(".ollama",),
        ports=(11434,),
        hub_id="ollama",
    ),
    AgentSignature(
        "lmstudio",
        "LM Studio",
        "local-llm",
        processes=(r"lm studio", r"lmstudio", r"^lm-studio"),
        paths=("LM Studio", ".lmstudio"),
        ports=(1234,),
    ),
    AgentSignature(
        "jan",
        "Jan",
        "local-llm",
        processes=(r"^jan(\.exe)?$",),
        paths=("Jan", ".jan"),
        ports=(1337,),
    ),
    AgentSignature(
        "open-webui",
        "Open WebUI",
        "local-llm",
        processes=(r"open-webui", r"open_webui"),
        ports=(8080, 3000),
    ),
    AgentSignature(
        "localai",
        "LocalAI",
        "local-llm",
        processes=(r"local-ai", r"localai"),
        ports=(8080,),
    ),
    AgentSignature(
        "tabby",
        "Tabby",
        "local-llm",
        processes=(r"tabby",),
        paths=(".tabby",),
        ports=(8080,),
    ),
    AgentSignature(
        "textgen-webui",
        "Text Generation WebUI",
        "local-llm",
        processes=(r"webui", r"text-generation"),
        ports=(7860, 5000),
    ),
    AgentSignature(
        "sd-webui",
        "Stable Diffusion WebUI",
        "image",
        processes=(r"webui", r"stable-diffusion"),
        ports=(7860,),
    ),
    AgentSignature(
        "comfyui",
        "ComfyUI",
        "image",
        processes=(r"comfyui", r"comfy"),
        ports=(8188,),
    ),
    AgentSignature(
        "koboldcpp",
        "KoboldCpp",
        "local-llm",
        processes=(r"kobold", r"koboldcpp"),
        ports=(5001,),
    ),
    AgentSignature(
        "llama-server",
        "llama.cpp server",
        "local-llm",
        processes=(r"llama-server", r"llama\.cpp"),
        ports=(8080,),
    ),
    AgentSignature(
        "gemini-cli",
        "Gemini CLI",
        "assistant",
        processes=(r"gemini", r"google-gemini"),
        hub_id="gemini",
    ),
    AgentSignature(
        "amazon-q",
        "Amazon Q",
        "coding",
        processes=(r"amazon-q", r"q-cli", r"aws-toolkit"),
        paths=(".aws/amazonq",),
    ),
    AgentSignature(
        "zed",
        "Zed",
        "ide",
        processes=(r"^zed(\.exe)?$",),
        paths=(".zed",),
    ),
)

_COMPILED: dict[str, tuple[re.Pattern[str], ...]] = {
    s.id: _compile(s.processes) for s in SIGNATURES
}


def _expand_path(raw: str) -> list[Path]:
    home = Path.home()
    out: list[Path] = []
    p = Path(raw)
    if raw.startswith("~"):
        out.append(p.expanduser())
    elif p.is_absolute():
        out.append(p)
    else:
        out.append(home / raw)
    if sys.platform == "win32":
        for env_key in ("APPDATA", "LOCALAPPDATA", "PROGRAMFILES"):
            base = os.environ.get(env_key)
            if base:
                out.append(Path(base) / raw)
    elif sys.platform == "darwin":
        out.append(home / "Library" / "Application Support" / raw)
    return out


def _path_exists(sig: AgentSignature) -> list[str]:
    found: list[str] = []
    for raw in sig.paths:
        for candidate in _expand_path(raw):
            try:
                if candidate.exists():
                    found.append(str(candidate))
            except OSError:
                continue
    return found


def _probe_port(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=PORT_TIMEOUT):
            return True
    except OSError:
        return False


def _scan_processes() -> dict[str, list[int]]:
    found: dict[str, list[int]] = {}
    if psutil is None:
        return found
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            info = proc.info
            pid = info.get("pid")
            name = (info.get("name") or "").lower().strip()
            if not name or pid is None:
                continue
            base = name.removesuffix(".exe")
            for sig in SIGNATURES:
                for pat in _COMPILED[sig.id]:
                    if pat.search(name) or pat.search(base):
                        found.setdefault(sig.id, [])
                        if pid not in found[sig.id]:
                            found[sig.id].append(pid)
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return found


def count_cursor_sessions(cursor_root: Path) -> int:
    if not cursor_root.is_dir():
        return 0
    total = 0
    try:
        for project_dir in cursor_root.iterdir():
            if not project_dir.is_dir():
                continue
            at = project_dir / "agent-transcripts"
            if not at.is_dir():
                continue
            for session_dir in at.iterdir():
                if not session_dir.is_dir():
                    continue
                sid = session_dir.name
                if (session_dir / f"{sid}.jsonl").is_file():
                    total += 1
    except OSError:
        return total
    return total


def detect_machine_agents(
    *,
    cursor_root: Path | None = None,
    force: bool = False,
    include_offline: bool = False,
    session_counter: Callable[[], int] | None = None,
) -> dict[str, Any]:
    now = time.time()
    if (
        not force
        and _detect_cache["data"] is not None
        and now - float(_detect_cache["ts"]) < DETECT_CACHE_TTL
    ):
        cached = _detect_cache["data"]
        if include_offline or cached.get("presentCount", 0) > 0:
            return cached

    t0 = time.perf_counter()
    proc_map = _scan_processes()
    port_cache: dict[int, bool] = {}

    def port_open(port: int) -> bool:
        if port not in port_cache:
            port_cache[port] = _probe_port(port)
        return port_cache[port]

    agents: list[dict[str, Any]] = []
    for sig in SIGNATURES:
        pids = proc_map.get(sig.id, [])
        paths = _path_exists(sig)
        open_ports = [p for p in sig.ports if port_open(p)]
        signals: list[str] = []
        if pids:
            signals.append("process")
        if paths:
            signals.append("data")
        if open_ports:
            signals.append("port")

        extra: dict[str, Any] = {}
        if sig.id == "cursor" and cursor_root is not None:
            sessions = session_counter() if session_counter else count_cursor_sessions(cursor_root)
            if sessions:
                signals.append("sessions")
                extra["cursorSessions"] = sessions

        if pids:
            status = "running"
        elif open_ports:
            status = "available"
        elif paths:
            status = "installed"
        else:
            status = "offline"

        if status == "offline" and not include_offline:
            continue

        detail_parts: list[str] = []
        if pids:
            detail_parts.append(f"{len(pids)} process")
        if paths:
            detail_parts.append("config/data found")
        if open_ports:
            detail_parts.append("port " + ", ".join(str(p) for p in open_ports))
        if extra.get("cursorSessions"):
            detail_parts.append(f"{extra['cursorSessions']} Cursor session(s)")

        agents.append({
            "id": sig.id,
            "label": sig.label,
            "hubId": sig.hub_id or sig.id,
            "category": sig.category,
            "status": status,
            "signals": signals,
            "detail": " · ".join(detail_parts) if detail_parts else sig.note or "—",
            "pids": pids[:8],
            "paths": paths[:3],
            "ports": open_ports,
            "note": sig.note,
            **extra,
        })

    agents.sort(
        key=lambda a: (
            0 if a["status"] == "running" else 1 if a["status"] == "available" else 2,
            a["label"].lower(),
        )
    )

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
    present = [a for a in agents if a["status"] != "offline"]
    payload: dict[str, Any] = {
        "ok": True,
        "scannedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cacheTtlSec": int(DETECT_CACHE_TTL),
        "scanMs": elapsed_ms,
        "platform": sys.platform,
        "psutil": psutil is not None,
        "agents": agents,
        "presentCount": len(present),
        "runningCount": sum(1 for a in agents if a["status"] == "running"),
    }
    _detect_cache["ts"] = now
    _detect_cache["data"] = payload
    return payload
