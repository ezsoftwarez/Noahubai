"""
Unified Noahubai launcher.

Default behavior:
- start the AI Hub main menu UI
- try to start the Noahubai FastAPI core in the background

Run `python3 main.py --help` for mode/port options.
"""
from __future__ import annotations

import argparse
import importlib.util
import logging
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
from types import ModuleType
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
AI_HUB_PATH = PROJECT_ROOT / "AI HUB oVerk1LL" / "bridge_server.py"
LOG_PATH = PROJECT_ROOT / "noahubai.log"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_PATH),
    ],
)
logger = logging.getLogger(__name__)


def print_banner() -> None:
    """Print the unified launcher banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                        🤖 NOAHUBAI 🤖                        ║
    ║            One launcher for the main menu + core            ║
    ║                                                            ║
    ║  • AI Hub main menu UI                                     ║
    ║  • Memory / Issue / Fixer agent core                       ║
    ║  • Cursor bridge + pinned code workspace                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def parse_args() -> argparse.Namespace:
    """Parse launcher flags."""
    parser = argparse.ArgumentParser(description="Launch Noahubai and/or the AI Hub UI")
    parser.add_argument(
        "--mode",
        choices=("all", "ui", "backend"),
        default="all",
        help="What to run. 'all' starts the UI and attempts the backend.",
    )
    parser.add_argument("--api-host", default="127.0.0.1", help="Noahubai API host")
    parser.add_argument("--api-port", default=8000, type=int, help="Noahubai API port")
    parser.add_argument("--ui-host", default="127.0.0.1", help="AI Hub UI host")
    parser.add_argument("--ui-port", default=8765, type=int, help="AI Hub UI port")
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the main menu in the default browser after startup.",
    )
    return parser.parse_args()


def normalized_local_host(host: str) -> str:
    """Return a connectable local address for status checks."""
    return "127.0.0.1" if host in {"0.0.0.0", "::"} else host


def can_bind_port(host: str, port: int) -> bool:
    """Check whether a host/port can be bound right now."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def choose_port(host: str, preferred_port: int, span: int = 20) -> int:
    """Return the preferred port or the next available one."""
    if can_bind_port(host, preferred_port):
        return preferred_port

    for candidate in range(preferred_port + 1, preferred_port + span + 1):
        if can_bind_port(host, candidate):
            logger.warning("Port %s is busy; using %s instead.", preferred_port, candidate)
            return candidate

    raise OSError(f"No free port found near {preferred_port} on {host}")


def wait_for_port(host: str, port: int, timeout_seconds: float = 4.0) -> bool:
    """Wait until a TCP port starts accepting connections."""
    deadline = time.time() + timeout_seconds
    target_host = normalized_local_host(host)
    while time.time() < deadline:
        try:
            with socket.create_connection((target_host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def load_module_from_path(module_name: str, module_path: Path) -> ModuleType:
    """Import a Python module from an arbitrary file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def start_backend(api_host: str, api_port: int) -> tuple[Any, threading.Thread, int] | None:
    """Start the FastAPI backend if dependencies are installed."""
    try:
        from backend.server import app
        import uvicorn
    except ModuleNotFoundError as exc:
        logger.warning(
            "Backend dependencies are unavailable (%s). "
            "The main menu will still run. Install them with: python3 -m pip install -r requirements.txt",
            exc.name or str(exc),
        )
        return None

    actual_port = choose_port(api_host, api_port)
    config = uvicorn.Config(app, host=api_host, port=actual_port, log_level="info")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name="noahubai-api")
    thread.start()

    if wait_for_port(api_host, actual_port):
        logger.info("Noahubai core ready at http://%s:%s", normalized_local_host(api_host), actual_port)
        logger.info("API docs: http://%s:%s/docs", normalized_local_host(api_host), actual_port)
    else:
        logger.warning("Noahubai core did not confirm startup during the initial wait window.")

    return server, thread, actual_port


def start_ui(ui_host: str, ui_port: int, api_host: str, api_port: int, open_browser: bool) -> None:
    """Start the AI Hub bridge/UI server in the foreground."""
    if not AI_HUB_PATH.is_file():
        raise FileNotFoundError(f"AI Hub bridge server not found: {AI_HUB_PATH}")

    actual_port = choose_port(ui_host, ui_port)
    os.environ["AIHUB_HOST"] = ui_host
    os.environ["AIHUB_PORT"] = str(actual_port)
    os.environ["NOAHUBAI_API_URL"] = f"http://{normalized_local_host(api_host)}:{api_port}"

    ui_url = f"http://{normalized_local_host(ui_host)}:{actual_port}/index.html"
    logger.info("AI Hub main menu: %s", ui_url)

    if open_browser:
        threading.Timer(1.0, lambda: webbrowser.open(ui_url)).start()

    bridge_module = load_module_from_path("ai_hub_bridge_server", AI_HUB_PATH)
    bridge_module.main()


def main() -> None:
    """Main entry point for the unified launcher."""
    args = parse_args()
    print_banner()

    logger.info("Noahubai launcher starting...")
    logger.info("Project root: %s", PROJECT_ROOT)
    logger.info("Requested mode: %s", args.mode)

    backend_server: Any | None = None

    try:
        api_port = args.api_port
        if args.mode in {"all", "backend"}:
            backend_result = start_backend(args.api_host, args.api_port)
            if args.mode == "backend" and backend_result is None:
                sys.exit(1)
            if backend_result is not None:
                backend_server, _, api_port = backend_result

        if args.mode in {"all", "ui"}:
            start_ui(args.ui_host, args.ui_port, args.api_host, api_port, args.open_browser)
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Launcher interrupted by user.")
    except Exception as exc:
        logger.error("Launcher failed: %s", exc, exc_info=True)
        sys.exit(1)
    finally:
        if backend_server is not None:
            backend_server.should_exit = True


if __name__ == "__main__":
    main()
