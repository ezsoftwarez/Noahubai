#!/usr/bin/env python3
"""
AI Hub Bridge — local server: static UI + API to Cursor Agent transcripts on Windows.
Run via RUN-AI-HUB.bat (single entry point).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from agent_detector import count_cursor_sessions, detect_machine_agents

def _resolve_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


ROOT = _resolve_root()
BRIDGE_DIR = ROOT / "bridge-data"
OUTBOX_DIR = BRIDGE_DIR / "outbox"
CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"
WORKSPACE = ROOT
SESSION_LIST_TTL = 45.0
_session_list_cache: dict[str, Any] = {"ts": 0.0, "data": []}
_linked_project_cache: dict[str, Any] = {"ts": 0.0, "path": None}


CODES_CONFIG_PATH = BRIDGE_DIR / "codes-config.json"
DEFAULT_PINNED_CODES_DIR = ROOT / "pinned-codes"


def ensure_dirs() -> None:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    (BRIDGE_DIR / "sync-state.json").touch(exist_ok=True)
    DEFAULT_PINNED_CODES_DIR.mkdir(parents=True, exist_ok=True)


def load_codes_config() -> dict[str, Any]:
    if CODES_CONFIG_PATH.is_file():
        try:
            return json.loads(CODES_CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_codes_config(cfg: dict[str, Any]) -> None:
    CODES_CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def resolve_codes_dir(custom: str | None = None) -> Path:
    raw = (custom or load_codes_config().get("saveLocation") or "").strip()
    if raw:
        p = Path(raw).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()
    DEFAULT_PINNED_CODES_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_PINNED_CODES_DIR.resolve()


def safe_code_filename(tag: str, item_id: str) -> str:
    base = re.sub(r"[^\w\-]+", "_", (tag or item_id or "pin").strip())[:48] or "pin"
    return base + ".txt"


def read_pins_store() -> dict[str, Any]:
    folder = resolve_codes_dir()
    manifest = folder / "pins.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["saveLocation"] = str(folder)
            return data
        except (OSError, json.JSONDecodeError):
            pass
    return {"version": 1, "saveLocation": str(folder), "items": []}


def write_pins_store(items: list[dict[str, Any]], save_location: str | None = None) -> dict[str, Any]:
    folder = resolve_codes_dir(save_location)
    cfg = load_codes_config()
    cfg["saveLocation"] = str(folder)
    save_codes_config(cfg)
    clean_items: list[dict[str, Any]] = []
    for item in items:
        if not item.get("pinned"):
            continue
        tag = str(item.get("tag") or "PIN").strip()[:32]
        text = str(item.get("text") or "")
        title = str(item.get("title") or "")
        iid = str(item.get("id") or f"pin-{len(clean_items)}")
        fname = safe_code_filename(tag, iid)
        file_path = folder / fname
        file_path.write_text(text, encoding="utf-8")
        clean_items.append({
            "id": iid,
            "tag": tag,
            "title": title,
            "text": text,
            "pinned": True,
            "file": fname,
            "updated": datetime.now(timezone.utc).isoformat(),
        })
    payload = {"version": 1, "saveLocation": str(folder), "items": clean_items}
    (folder / "pins.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def open_local_path(target: str) -> dict[str, Any]:
    p = Path(target).expanduser().resolve()
    if not p.exists():
        return {"ok": False, "error": f"not found: {p}"}
    if sys.platform == "win32":
        os.startfile(str(p))  # noqa: S606 — intentional: open folder/file in Explorer
    elif sys.platform == "darwin":
        os.system(f'open "{p}"')  # noqa: S605
    else:
        os.system(f'xdg-open "{p}"')  # noqa: S605
    return {"ok": True, "path": str(p)}


def json_response(handler: SimpleHTTPRequestHandler, data: Any, status: int = 200) -> None:
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_body(handler: SimpleHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", 0))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def extract_user_queries(record: dict[str, Any]) -> list[str]:
    if record.get("role") != "user":
        return []
    out: list[str] = []
    for block in record.get("message", {}).get("content", []):
        if block.get("type") != "text":
            continue
        text = block.get("text", "")
        m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", text, re.DOTALL)
        out.append(m.group(1).strip() if m else text.strip())
    return out


def extract_assistant_text(record: dict[str, Any]) -> list[str]:
    if record.get("role") != "assistant":
        return []
    texts: list[str] = []
    for block in record.get("message", {}).get("content", []):
        if block.get("type") == "text":
            t = block.get("text", "").strip()
            if t and t != "[REDACTED]":
                texts.append(t)
    return texts


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def flatten_session(jsonl_path: Path, include_tools: bool = False) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for rec in iter_jsonl(jsonl_path):
        for q in extract_user_queries(rec):
            messages.append({"role": "user", "text": q, "source": "cursor"})
        for t in extract_assistant_text(rec):
            messages.append({"role": "assistant", "text": t, "source": "cursor"})
        if include_tools and rec.get("role") == "assistant":
            for block in rec.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    messages.append({
                        "role": "system",
                        "text": f"[tool] {block.get('name')}",
                        "source": "cursor",
                    })
    return messages


def find_project_slug_for_workspace(*, force: bool = False) -> Path | None:
    now = time.time()
    if not force and now - _linked_project_cache["ts"] < 300 and _linked_project_cache["path"] is not None:
        p = _linked_project_cache["path"]
        return p if isinstance(p, Path) and p.is_dir() else None
    ws = str(WORKSPACE.resolve()).lower()
    if not CURSOR_PROJECTS.is_dir():
        return None
    best: Path | None = None
    for project_dir in CURSOR_PROJECTS.iterdir():
        at = project_dir / "agent-transcripts"
        if not at.is_dir():
            continue
        for jsonl in at.rglob("*.jsonl"):
            try:
                head = jsonl.read_text(encoding="utf-8", errors="replace")[:12000].lower()
            except OSError:
                continue
            if ws in head or "ai hub" in head:
                _linked_project_cache["ts"] = now
                _linked_project_cache["path"] = project_dir
                return project_dir
        if "ai-hub" in project_dir.name.lower() or "g-p-ai-hub" in project_dir.name:
            best = project_dir
    if best:
        _linked_project_cache["ts"] = now
        _linked_project_cache["path"] = best
        return best
    known = CURSOR_PROJECTS / "c-Users-krake-OneDrive-Asztali-g-p-ai-hub"
    result = known if known.is_dir() else None
    _linked_project_cache["ts"] = now
    _linked_project_cache["path"] = result
    return result


def preview_from_jsonl(path: Path, max_chars: int = 120) -> str:
    if not path.is_file():
        return ""
    try:
        size = path.stat().st_size
        with path.open("rb") as f:
            f.seek(max(0, size - 65536))
            tail = f.read().decode("utf-8", errors="replace")
    except OSError:
        return ""
    for line in reversed(tail.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        for q in extract_user_queries(rec):
            return q[:max_chars]
        for t in extract_assistant_text(rec):
            if t:
                return t[:max_chars]
    return ""


def count_jsonl_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    n = 0
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.strip():
                    n += 1
    except OSError:
        return 0
    return n


def list_sessions_in_project(project_dir: Path, limit: int = 50) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    at = project_dir / "agent-transcripts"
    if not at.is_dir():
        return sessions
    for session_dir in at.iterdir():
        if not session_dir.is_dir():
            continue
        sid = session_dir.name
        main = session_dir / f"{sid}.jsonl"
        if not main.is_file():
            continue
        st = main.stat()
        linked = find_project_slug_for_workspace()
        is_here = linked is not None and project_dir.resolve() == linked.resolve()
        sessions.append({
            "sessionId": sid,
            "projectSlug": project_dir.name,
            "projectPath": str(project_dir),
            "isThisWorkspace": is_here,
            "modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
            "preview": preview_from_jsonl(main),
            "messageCount": count_jsonl_lines(main),
            "jsonlPath": str(main),
        })
    sessions.sort(key=lambda s: s["modified"], reverse=True)
    return sessions[:limit]


def list_all_cursor_sessions(limit: int = 50, *, force: bool = False) -> list[dict[str, Any]]:
    now = time.time()
    if not force and _session_list_cache["data"] and now - _session_list_cache["ts"] < SESSION_LIST_TTL:
        return _session_list_cache["data"][:limit]
    sessions: list[dict[str, Any]] = []
    if not CURSOR_PROJECTS.is_dir():
        return sessions
    linked = find_project_slug_for_workspace()
    if linked:
        sessions = list_sessions_in_project(linked, max(limit, 80))
    else:
        for project_dir in CURSOR_PROJECTS.iterdir():
            sessions.extend(list_sessions_in_project(project_dir, 30))
        sessions.sort(key=lambda s: s["modified"], reverse=True)
        sessions = sessions[: max(limit, 80)]
    _session_list_cache["ts"] = now
    _session_list_cache["data"] = sessions
    return sessions[:limit]


def sessions_for_poll(sync: dict[str, Any]) -> list[dict[str, Any]]:
    linked = find_project_slug_for_workspace()
    if linked:
        return list_sessions_in_project(linked, 80)
    out: list[dict[str, Any]] = []
    for sid, meta in sync.get("sessions", {}).items():
        path_s = meta.get("jsonlPath")
        if not path_s:
            continue
        path = Path(path_s)
        if not path.is_file():
            continue
        st = path.stat()
        out.append({
            "sessionId": sid,
            "projectSlug": meta.get("projectSlug", ""),
            "preview": meta.get("preview", ""),
            "jsonlPath": path_s,
            "modified": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        })
    return out


def load_sync_state() -> dict[str, Any]:
    path = BRIDGE_DIR / "sync-state.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"sessions": {}}


def save_sync_state(data: dict[str, Any]) -> None:
    path = BRIDGE_DIR / "sync-state.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def cursor_poll(since_session: str | None = None) -> dict[str, Any]:
    sync = load_sync_state()
    sessions = sessions_for_poll(sync)
    new_messages: list[dict[str, Any]] = []
    for s in sessions:
        sid = s["sessionId"]
        path = Path(s["jsonlPath"])
        mtime = path.stat().st_mtime if path.is_file() else 0
        prev = sync.get("sessions", {}).get(sid, {})
        if mtime <= prev.get("mtime", 0):
            continue
        flat = flatten_session(path)
        start_idx = prev.get("messageCount", 0)
        chunk = flat[start_idx:]
        if chunk:
            new_messages.append({
                "sessionId": sid,
                "projectSlug": s["projectSlug"],
                "preview": s.get("preview") or preview_from_jsonl(path),
                "messages": chunk,
            })
        sync.setdefault("sessions", {})[sid] = {
            "mtime": mtime,
            "messageCount": len(flat),
            "jsonlPath": str(path),
            "projectSlug": s.get("projectSlug", ""),
            "preview": s.get("preview", ""),
        }
    save_sync_state(sync)
    return {"sessions": sessions, "newBatches": new_messages, "cursorRoot": str(CURSOR_PROJECTS)}


def write_cursor_outbox(text: str, project_name: str = "AI Hub") -> dict[str, Any]:
    ensure_dirs()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    fname = OUTBOX_DIR / "cursor-inbox.md"
    block = f"\n\n---\n## AI Hub → Cursor · {ts}\n**Project:** {project_name}\n\n{text.strip()}\n"
    if fname.is_file():
        existing = fname.read_text(encoding="utf-8")
    else:
        existing = "# Cursor Bridge Inbox\n\nPaste this block into **Cursor Agent** (Ctrl+L) or open this file in Cursor.\n"
    fname.write_text(existing + block, encoding="utf-8")
    queue_path = OUTBOX_DIR / "queue.jsonl"
    entry = {"ts": ts, "text": text, "project": project_name}
    with queue_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"ok": True, "file": str(fname), "ts": ts}


class HubHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        if str(args[0]).startswith("GET /api/"):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/bridge/status":
            proj = find_project_slug_for_workspace()
            qs = parse_qs(parsed.query)
            force_agents = qs.get("refresh", ["0"])[0] in ("1", "true", "yes")
            machine = detect_machine_agents(
                cursor_root=CURSOR_PROJECTS,
                force=force_agents,
                session_counter=lambda: count_cursor_sessions(CURSOR_PROJECTS),
            )
            return json_response(self, {
                "ok": True,
                "workspace": str(WORKSPACE),
                "cursorProjectsRoot": str(CURSOR_PROJECTS),
                "cursorProjectsRootExists": CURSOR_PROJECTS.is_dir(),
                "linkedProject": proj.name if proj else None,
                "linkedProjectPath": str(proj) if proj else None,
                "outboxFile": str(OUTBOX_DIR / "cursor-inbox.md"),
                "machineAgents": {
                    "presentCount": machine.get("presentCount", 0),
                    "runningCount": machine.get("runningCount", 0),
                    "scanMs": machine.get("scanMs"),
                    "scannedAt": machine.get("scannedAt"),
                },
            })

        if path == "/api/bridge/agents/machine":
            qs = parse_qs(parsed.query)
            force = qs.get("refresh", ["0"])[0] in ("1", "true", "yes")
            include_offline = qs.get("all", ["0"])[0] in ("1", "true", "yes")
            return json_response(
                self,
                detect_machine_agents(
                    cursor_root=CURSOR_PROJECTS,
                    force=force,
                    include_offline=include_offline,
                    session_counter=lambda: count_cursor_sessions(CURSOR_PROJECTS),
                ),
            )

        if path == "/api/bridge/cursor/sessions":
            qs = parse_qs(parsed.query)
            limit = int(qs.get("limit", ["40"])[0])
            force = qs.get("refresh", ["0"])[0] in ("1", "true", "yes")
            scan_all = qs.get("all", ["0"])[0] in ("1", "true", "yes")
            if scan_all and CURSOR_PROJECTS.is_dir():
                sessions: list[dict[str, Any]] = []
                for project_dir in CURSOR_PROJECTS.iterdir():
                    sessions.extend(list_sessions_in_project(project_dir, 25))
                sessions.sort(key=lambda s: s["modified"], reverse=True)
                return json_response(self, {"sessions": sessions[:limit]})
            return json_response(self, {"sessions": list_all_cursor_sessions(limit, force=force)})

        if path.startswith("/api/bridge/cursor/sessions/") and path.endswith("/messages"):
            sid = path.split("/")[-2]
            for s in list_all_cursor_sessions(200):
                if s["sessionId"] == sid:
                    msgs = flatten_session(Path(s["jsonlPath"]), include_tools=False)
                    return json_response(self, {"sessionId": sid, "messages": msgs})
            return json_response(self, {"error": "session not found"}, 404)

        if path == "/api/bridge/cursor/poll":
            return json_response(self, cursor_poll())

        if path == "/api/bridge/outbox":
            ensure_dirs()
            inbox = OUTBOX_DIR / "cursor-inbox.md"
            text = inbox.read_text(encoding="utf-8") if inbox.is_file() else ""
            return json_response(self, {"file": str(inbox), "content": text})

        if path == "/api/bridge/codes":
            store = read_pins_store()
            return json_response(self, {"ok": True, **store})

        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        body = read_body(self)

        if path == "/api/bridge/outbox":
            text = body.get("text", "")
            project = body.get("project", "AI Hub")
            if not text.strip():
                return json_response(self, {"error": "empty text"}, 400)
            return json_response(self, write_cursor_outbox(text, project))

        if path == "/api/bridge/relay":
            text = body.get("text", "").strip()
            targets = body.get("targets", {})
            project = body.get("project", "AI Hub")
            results: dict[str, Any] = {}
            if targets.get("cursor"):
                results["cursor"] = write_cursor_outbox(text, project)
            results["hub"] = {"ok": True, "note": "append on client"}
            return json_response(self, {"ok": True, "results": results})

        if path.startswith("/api/bridge/cursor/sessions/") and path.endswith("/import"):
            sid = path.split("/")[-2]
            for s in list_all_cursor_sessions(200):
                if s["sessionId"] == sid:
                    msgs = flatten_session(Path(s["jsonlPath"]))
                    return json_response(self, {"sessionId": sid, "messages": msgs, "imported": len(msgs)})
            return json_response(self, {"error": "session not found"}, 404)

        if path == "/api/bridge/open":
            target = body.get("path", "")
            if not target:
                return json_response(self, {"error": "path required"}, 400)
            return json_response(self, open_local_path(target))

        if path == "/api/bridge/codes":
            items = body.get("items")
            if not isinstance(items, list):
                return json_response(self, {"error": "items array required"}, 400)
            loc = body.get("saveLocation")
            store = write_pins_store(items, str(loc).strip() if loc else None)
            return json_response(self, {"ok": True, **store})

        if path == "/api/bridge/codes/location":
            loc = (body.get("path") or body.get("saveLocation") or "").strip()
            cfg = load_codes_config()
            if loc:
                cfg["saveLocation"] = str(resolve_codes_dir(loc))
            else:
                cfg["saveLocation"] = str(resolve_codes_dir())
            save_codes_config(cfg)
            return json_response(self, {"ok": True, "saveLocation": cfg["saveLocation"]})

        return json_response(self, {"error": "not found"}, 404)


def main() -> None:
    ensure_dirs()
    port = int(os.environ.get("AIHUB_PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), HubHandler)
    print(f"AI Hub Bridge: http://127.0.0.1:{port}/index.html")
    print(f"Cursor transcripts: {CURSOR_PROJECTS}")
    print(f"Outbox (paste into Cursor): {OUTBOX_DIR / 'cursor-inbox.md'}")
    print(f"Pinned codes folder: {DEFAULT_PINNED_CODES_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
