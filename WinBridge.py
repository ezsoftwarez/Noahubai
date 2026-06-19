#!/usr/bin/env python3
"""
WinBridge — OS Bridge for DEMOCORE / brOS.

HTTP API on port 9778 + optional desktop UI (tkinter) to browse and load
files and folders from the host OS into a local vault for DEMOCORE apps.

Run: python WinBridge.py
     RUN-WINBRIDGE.bat
"""
from __future__ import annotations

import json
import mimetypes
import os
import platform
import shutil
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

DEFAULT_PORT = 9778
MAX_READ_BYTES = 512_000
MAX_VAULT_FILE_BYTES = 2_000_000
MAX_VAULT_ITEMS = 200

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "winbridge-data"
VAULT_PATH = DATA_DIR / "vault.json"
VAULT_FILES_DIR = DATA_DIR / "vault-files"

_vault_lock = threading.Lock()
_vault: dict[str, Any] = {"version": 1, "items": []}


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_FILES_DIR.mkdir(parents=True, exist_ok=True)
    if not VAULT_PATH.is_file():
        VAULT_PATH.write_text(json.dumps(_vault, indent=2), encoding="utf-8")


def load_vault() -> dict[str, Any]:
    global _vault
    ensure_dirs()
    if VAULT_PATH.is_file():
        try:
            data = json.loads(VAULT_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("items"), list):
                _vault = data
        except (OSError, json.JSONDecodeError):
            pass
    return _vault


def save_vault() -> None:
    ensure_dirs()
    VAULT_PATH.write_text(json.dumps(_vault, indent=2), encoding="utf-8")


def safe_path(raw: str) -> Path:
    if not raw or not str(raw).strip():
        raise ValueError("Path is required")
    p = Path(unquote(str(raw).strip())).expanduser()
    try:
        resolved = p.resolve(strict=False)
    except OSError as exc:
        raise ValueError(f"Invalid path: {raw}") from exc
    parts = resolved.parts
    if ".." in parts:
        raise ValueError("Path traversal not allowed")
    return resolved


def list_roots() -> list[dict[str, str]]:
    roots: list[dict[str, str]] = []
    if platform.system() == "Windows":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = Path(f"{letter}:/")
            if drive.exists():
                roots.append({"name": f"{letter}:", "path": str(drive)})
    else:
        roots.append({"name": "Home", "path": str(Path.home())})
        roots.append({"name": "Root", "path": "/"})
        if ROOT.is_dir():
            roots.append({"name": "Repo", "path": str(ROOT)})
    return roots


def stat_entry(p: Path) -> dict[str, Any]:
    try:
        st = p.stat()
        is_dir = p.is_dir()
        return {
            "name": p.name,
            "path": str(p),
            "type": "folder" if is_dir else "file",
            "size": 0 if is_dir else st.st_size,
            "mtime": int(st.st_mtime),
        }
    except OSError:
        return {
            "name": p.name,
            "path": str(p),
            "type": "folder" if p.is_dir() else "file",
            "size": 0,
            "mtime": 0,
        }


def list_directory(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError("Path does not exist")
    if not path.is_dir():
        raise ValueError("Not a directory")
    entries: list[dict[str, Any]] = []
    try:
        children = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError as exc:
        raise ValueError("Permission denied") from exc
    for child in children:
        entries.append(stat_entry(child))
    parent = str(path.parent) if path.parent != path else None
    return {"path": str(path), "parent": parent, "entries": entries}


def read_text_file(path: Path, max_bytes: int = MAX_READ_BYTES) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("Not a file")
    size = path.stat().st_size
    truncated = size > max_bytes
    with path.open("rb") as fh:
        raw = fh.read(max_bytes)
    mime, _ = mimetypes.guess_type(str(path))
    text_like = (mime or "").startswith("text/") or path.suffix.lower() in {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".html", ".css",
        ".bat", ".cmd", ".xml", ".yaml", ".yml", ".toml", ".ini", ".env", ".csv",
    }
    content: str | None = None
    if text_like:
        content = raw.decode("utf-8", errors="replace")
    return {
        "path": str(path),
        "size": size,
        "truncated": truncated,
        "mime": mime or "application/octet-stream",
        "text": text_like,
        "content": content,
    }


def copy_into_vault(src: Path, recursive: bool) -> list[dict[str, Any]]:
    loaded: list[dict[str, Any]] = []
    with _vault_lock:
        if len(_vault["items"]) >= MAX_VAULT_ITEMS:
            raise ValueError(f"Vault limit reached ({MAX_VAULT_ITEMS} items)")

        if src.is_file():
            item = _vault_add_file(src)
            if item:
                loaded.append(item)
        elif src.is_dir():
            if recursive:
                for root, _dirs, files in os.walk(src):
                    for name in files:
                        fp = Path(root) / name
                        if len(_vault["items"]) >= MAX_VAULT_ITEMS:
                            break
                        item = _vault_add_file(fp, label_prefix=str(src.name))
                        if item:
                            loaded.append(item)
            else:
                item = _vault_add_folder_meta(src)
                if item:
                    loaded.append(item)
        else:
            raise ValueError("Path is not a file or folder")
        save_vault()
    return loaded


def _vault_add_folder_meta(folder: Path) -> dict[str, Any] | None:
    entries: list[dict[str, Any]] = []
    try:
        for child in sorted(folder.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))[:500]:
            entries.append(stat_entry(child))
    except OSError:
        pass
    item_id = str(uuid.uuid4())
    manifest = {
        "id": item_id,
        "kind": "folder",
        "name": folder.name,
        "sourcePath": str(folder),
        "loadedAt": _utc_iso(),
        "entries": entries,
    }
    dest = VAULT_FILES_DIR / f"{item_id}.json"
    dest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    row = {
        "id": item_id,
        "kind": "folder",
        "name": folder.name,
        "sourcePath": str(folder),
        "loadedAt": manifest["loadedAt"],
        "entryCount": len(entries),
    }
    _vault["items"].append(row)
    return row


def _vault_add_file(src: Path, label_prefix: str | None = None) -> dict[str, Any] | None:
    try:
        size = src.stat().st_size
    except OSError:
        return None
    if size > MAX_VAULT_FILE_BYTES:
        return {
            "id": "",
            "kind": "file",
            "name": src.name,
            "sourcePath": str(src),
            "skipped": True,
            "reason": f"Too large ({size} bytes)",
        }
    item_id = str(uuid.uuid4())
    dest = VAULT_FILES_DIR / item_id
    shutil.copy2(src, dest)
    display_name = f"{label_prefix}/{src.name}" if label_prefix else src.name
    row = {
        "id": item_id,
        "kind": "file",
        "name": display_name,
        "sourcePath": str(src),
        "loadedAt": _utc_iso(),
        "size": size,
        "mime": mimetypes.guess_type(str(src))[0] or "application/octet-stream",
    }
    _vault["items"].append(row)
    return row


def vault_list() -> dict[str, Any]:
    with _vault_lock:
        return {"count": len(_vault["items"]), "items": list(_vault["items"])}


def vault_remove(item_id: str) -> bool:
    with _vault_lock:
        items = _vault.get("items", [])
        found = None
        for i, row in enumerate(items):
            if row.get("id") == item_id:
                found = i
                break
        if found is None:
            return False
        row = items.pop(found)
        fp = VAULT_FILES_DIR / item_id
        meta = VAULT_FILES_DIR / f"{item_id}.json"
        if fp.is_file():
            fp.unlink(missing_ok=True)
        if meta.is_file():
            meta.unlink(missing_ok=True)
        save_vault()
        return True


def vault_read(item_id: str) -> dict[str, Any]:
    with _vault_lock:
        row = next((r for r in _vault["items"] if r.get("id") == item_id), None)
    if not row:
        raise ValueError("Vault item not found")
    if row.get("kind") == "folder":
        meta = VAULT_FILES_DIR / f"{item_id}.json"
        if meta.is_file():
            return json.loads(meta.read_text(encoding="utf-8"))
        return row
    fp = VAULT_FILES_DIR / item_id
    if not fp.is_file():
        raise ValueError("Vault file missing on disk")
    return read_text_file(fp)


def open_in_explorer(path: Path) -> None:
    if platform.system() == "Windows":
        os.startfile(str(path))  # noqa: S606
    elif platform.system() == "Darwin":
        os.system(f'open "{path}"')  # noqa: S605
    else:
        os.system(f'xdg-open "{path}"')  # noqa: S605


def pyautogui_available() -> bool:
    try:
        import pyautogui  # noqa: F401

        return True
    except ImportError:
        return False


def json_response(handler: BaseHTTPRequestHandler, code: int, payload: Any) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def read_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


class WinBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[WinBridge] {self.address_string()} - {fmt % args}")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        try:
            if path == "/api/os-bridge/status":
                json_response(
                    self,
                    200,
                    {
                        "ok": True,
                        "service": "WinBridge",
                        "platform": platform.system(),
                        "port": DEFAULT_PORT,
                        "vaultCount": len(_vault.get("items", [])),
                        "pyautogui": pyautogui_available(),
                        "repo": str(ROOT),
                    },
                )
                return

            if path == "/api/os-bridge/roots":
                json_response(self, 200, {"roots": list_roots()})
                return

            if path == "/api/os-bridge/list":
                raw_path = (qs.get("path") or [""])[0]
                data = list_directory(safe_path(raw_path))
                json_response(self, 200, data)
                return

            if path == "/api/os-bridge/read":
                raw_path = (qs.get("path") or [""])[0]
                max_bytes = int((qs.get("maxBytes") or [str(MAX_READ_BYTES)])[0])
                data = read_text_file(safe_path(raw_path), max_bytes=max_bytes)
                json_response(self, 200, data)
                return

            if path == "/api/os-bridge/vault":
                json_response(self, 200, vault_list())
                return

            if path.startswith("/api/os-bridge/vault/"):
                item_id = path.split("/")[-1]
                data = vault_read(item_id)
                json_response(self, 200, data)
                return

            if path == "/" or path == "/index.html":
                html = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    "<title>WinBridge</title></head><body style='font-family:sans-serif;background:#0a1020;color:#e8ecf4;padding:24px'>"
                    "<h1>WinBridge OS Bridge</h1>"
                    "<p>API running on port {port}. Use DEMOCORE OS Bridge app or <code>RUN-WINBRIDGE.bat</code> UI.</p>"
                    "<ul>"
                    "<li>GET /api/os-bridge/status</li>"
                    "<li>GET /api/os-bridge/roots</li>"
                    "<li>GET /api/os-bridge/list?path=...</li>"
                    "<li>POST /api/os-bridge/load</li>"
                    "<li>GET /api/os-bridge/vault</li>"
                    "</ul></body></html>"
                ).format(port=DEFAULT_PORT)
                body = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            json_response(self, 404, {"ok": False, "error": "Not found"})
        except ValueError as exc:
            json_response(self, 400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            json_response(self, 500, {"ok": False, "error": str(exc)})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = read_body(self)
        try:
            if path == "/api/os-bridge/load":
                raw_path = body.get("path") or ""
                recursive = bool(body.get("recursive", False))
                loaded = copy_into_vault(safe_path(str(raw_path)), recursive=recursive)
                json_response(self, 200, {"ok": True, "loaded": loaded})
                return

            if path == "/api/os-bridge/open":
                raw_path = body.get("path") or ""
                p = safe_path(str(raw_path))
                open_in_explorer(p)
                json_response(self, 200, {"ok": True, "path": str(p)})
                return

            if path == "/api/os-bridge/vault/remove":
                item_id = str(body.get("id") or "")
                ok = vault_remove(item_id)
                json_response(self, 200, {"ok": ok})
                return

            if path == "/api/os-bridge/mouse" and pyautogui_available():
                import pyautogui

                action = body.get("action", "position")
                if action == "position":
                    pos = pyautogui.position()
                    json_response(self, 200, {"ok": True, "x": pos.x, "y": pos.y})
                elif action == "move":
                    pyautogui.moveTo(int(body.get("x", 0)), int(body.get("y", 0)), duration=0.2)
                    json_response(self, 200, {"ok": True})
                else:
                    json_response(self, 400, {"ok": False, "error": "Unknown mouse action"})
                return

            json_response(self, 404, {"ok": False, "error": "Not found"})
        except ValueError as exc:
            json_response(self, 400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            json_response(self, 500, {"ok": False, "error": str(exc)})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        try:
            if path.startswith("/api/os-bridge/vault/"):
                item_id = path.split("/")[-1]
                ok = vault_remove(item_id)
                json_response(self, 200, {"ok": ok})
                return
            json_response(self, 404, {"ok": False, "error": "Not found"})
        except Exception as exc:  # noqa: BLE001
            json_response(self, 500, {"ok": False, "error": str(exc)})


def run_http_server(port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    load_vault()
    server = ThreadingHTTPServer(("127.0.0.1", port), WinBridgeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"WinBridge API: http://127.0.0.1:{port}/")
    return server


# --- Tkinter UI (same app family as DEMOCORE dark theme) ---

class WinBridgeUI:
    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        self.tk = tk
        self.filedialog = filedialog
        self.messagebox = messagebox
        self.ttk = ttk

        self.root = tk.Tk()
        self.root.title("WinBridge — OS Bridge")
        self.root.geometry("1024x640")
        self.root.configure(bg="#0a1020")

        self.current_path = Path.home()
        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        tk = self.tk
        top = tk.Frame(self.root, bg="#121828", pady=8, padx=10)
        top.pack(fill="x")

        tk.Label(top, text="WinBridge", fg="#7dfff0", bg="#121828", font=("Segoe UI", 14, "bold")).pack(side="left")
        self.status_lbl = tk.Label(top, text="API :9778", fg="#9ca3af", bg="#121828", font=("Segoe UI", 10))
        self.status_lbl.pack(side="right")

        bar = tk.Frame(self.root, bg="#0a1020", padx=10, pady=6)
        bar.pack(fill="x")
        for text, cmd in [
            ("Roots", self.go_home),
            ("Up", self.go_up),
            ("Refresh", self.refresh_list),
            ("Pick folder…", self.pick_folder),
            ("Pick file…", self.pick_file),
            ("Load folder", lambda: self.load_selected(recursive=True)),
            ("Load file", lambda: self.load_selected(recursive=False)),
            ("Open vault folder", self.open_vault_dir),
        ]:
            tk.Button(
                bar,
                text=text,
                command=cmd,
                bg="#1e293b",
                fg="#e8ecf4",
                activebackground="#334155",
                relief="flat",
                padx=8,
                pady=4,
            ).pack(side="left", padx=3)

        self.path_var = tk.StringVar(value=str(self.current_path))
        tk.Entry(self.root, textvariable=self.path_var, bg="#0f172a", fg="#e8ecf4", insertbackground="#fff").pack(
            fill="x", padx=10, pady=(0, 6)
        )

        body = tk.PanedWindow(self.root, orient="horizontal", bg="#0a1020", sashwidth=4)
        body.pack(fill="both", expand=True, padx=10, pady=6)

        left = tk.Frame(body, bg="#0f172a")
        self.file_list = tk.Listbox(left, bg="#0f172a", fg="#e8ecf4", selectbackground="#334155", width=42)
        self.file_list.pack(fill="both", expand=True, side="left")
        self.file_list.bind("<Double-Button-1>", self.on_open_entry)
        scroll = tk.Scrollbar(left, command=self.file_list.yview)
        scroll.pack(side="right", fill="y")
        self.file_list.config(yscrollcommand=scroll.set)
        body.add(left, stretch="always")

        right = tk.Frame(body, bg="#0f172a")
        tk.Label(right, text="Loaded vault", fg="#7dfff0", bg="#0f172a").pack(anchor="w", padx=6, pady=4)
        self.vault_list = tk.Listbox(right, bg="#0f172a", fg="#e8ecf4", selectbackground="#334155", width=36)
        self.vault_list.pack(fill="both", expand=True, padx=6, pady=4)
        tk.Button(right, text="Remove selected", command=self.remove_vault_item, bg="#1e293b", fg="#e8ecf4").pack(
            pady=6
        )
        body.add(right)

        self.preview = tk.Text(self.root, height=8, bg="#050810", fg="#cbd5e1", wrap="word")
        self.preview.pack(fill="x", padx=10, pady=(0, 10))

    def go_home(self) -> None:
        roots = list_roots()
        self.current_path = Path(roots[0]["path"]) if roots else Path.home()
        self.refresh_list()

    def go_up(self) -> None:
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            self.refresh_list()

    def pick_folder(self) -> None:
        chosen = self.filedialog.askdirectory(initialdir=str(self.current_path))
        if chosen:
            self.current_path = Path(chosen)
            self.refresh_list()

    def pick_file(self) -> None:
        chosen = self.filedialog.askopenfilename(initialdir=str(self.current_path))
        if chosen:
            self.current_path = Path(chosen).parent
            self.refresh_list()
            self.load_path(Path(chosen), recursive=False)

    def on_open_entry(self, _event: Any = None) -> None:
        idx = self.file_list.curselection()
        if not idx:
            return
        label = self.file_list.get(idx[0])
        if label.startswith("📁 "):
            name = label[2:]
            self.current_path = self.current_path / name
            self.refresh_list()
        elif label.startswith("📄 "):
            self.load_path(self.current_path / label[2:], recursive=False)

    def refresh_list(self) -> None:
        self.path_var.set(str(self.current_path))
        self.file_list.delete(0, "end")
        self.preview.delete("1.0", "end")
        try:
            data = list_directory(self.current_path)
        except ValueError as exc:
            self.preview.insert("end", str(exc))
            return
        for entry in data["entries"]:
            icon = "📁" if entry["type"] == "folder" else "📄"
            self.file_list.insert("end", f"{icon} {entry['name']}")
        self.refresh_vault()

    def refresh_vault(self) -> None:
        self.vault_list.delete(0, "end")
        data = vault_list()
        self.status_lbl.config(text=f"API :{DEFAULT_PORT} · vault {data['count']}")
        for row in data["items"]:
            kind = row.get("kind", "?")
            self.vault_list.insert("end", f"[{kind}] {row.get('name', row.get('id'))}")

    def refresh_all(self) -> None:
        self.refresh_list()

    def load_selected(self, recursive: bool) -> None:
        idx = self.file_list.curselection()
        if not idx:
            self.messagebox.showinfo("WinBridge", "Select a file or folder first.")
            return
        label = self.file_list.get(idx[0])
        name = label[2:]
        path = self.current_path / name
        self.load_path(path, recursive=recursive and path.is_dir())

    def load_path(self, path: Path, recursive: bool) -> None:
        try:
            loaded = copy_into_vault(path, recursive=recursive)
            self.preview.delete("1.0", "end")
            self.preview.insert("end", f"Loaded {len(loaded)} item(s) from {path}\n")
            for row in loaded:
                self.preview.insert("end", f"  - {row.get('name')} ({row.get('kind')})\n")
            self.refresh_vault()
        except ValueError as exc:
            self.messagebox.showerror("WinBridge", str(exc))

    def remove_vault_item(self) -> None:
        idx = self.vault_list.curselection()
        if not idx:
            return
        data = vault_list()
        row = data["items"][idx[0]]
        vault_remove(str(row["id"]))
        self.refresh_vault()

    def open_vault_dir(self) -> None:
        open_in_explorer(VAULT_FILES_DIR)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    port = DEFAULT_PORT
    no_ui = "--no-ui" in sys.argv
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])

    ensure_dirs()
    load_vault()
    run_http_server(port)

    if no_ui:
        print("WinBridge running headless (--no-ui). Ctrl+C to stop.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
        return

    try:
        ui = WinBridgeUI()
        ui.run()
    except Exception as exc:  # noqa: BLE001
        print(f"UI unavailable ({exc}) — API still running headless.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
