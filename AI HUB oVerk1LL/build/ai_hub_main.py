#!/usr/bin/env python3
"""AI HUB.exe entry — Bridge server + browser (PyInstaller)."""
from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen

# Run from repo root so bridge_server resolves
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)

import bridge_server  # noqa: E402


def open_browser_when_ready(port: int, timeout: int = 15) -> None:
    base = f"http://127.0.0.1:{port}"
    status = base + "/api/bridge/status"
    ui = base + "/index.html"
    for _ in range(timeout):
        try:
            with urlopen(status, timeout=2) as r:
                if r.status == 200:
                    webbrowser.open(ui)
                    return
        except OSError:
            time.sleep(1)
    webbrowser.open(ui)


def main() -> None:
    port = int(os.environ.get("AIHUB_PORT", "8765"))
    server_thread = threading.Thread(target=bridge_server.main, daemon=True)
    server_thread.start()
    open_browser_when_ready(port)
    print(f"AI Hub: http://127.0.0.1:{port}/index.html")
    print("Close this window to stop the server.")
    try:
        while server_thread.is_alive():
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
