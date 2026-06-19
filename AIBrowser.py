#!/usr/bin/env python3
"""
AIBrowser — merged native browser (Steamish + page-aware AI assistant).

Combines:
  - steamish_browser/main.py  (tabs, bookmarks, TabVault, KoboldBlock)
  - ui for + BROWSER +aicat devforgge +.py  (AI dock with page context)

Run: python AIBrowser.py
     RUN-AI-BROWSER.bat
"""
from __future__ import annotations

import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEAMISH = ROOT / "steamish_browser"
sys.path.insert(0, str(STEAMISH))

from PySide6.QtCore import Qt, QThread, Signal, QEvent  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QDockWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from main import MainWindow  # noqa: E402

BRAIN_URL = "http://127.0.0.1:8765/api/brain/auto"


class BrainWorker(QThread):
    response = Signal(str)
    error = Signal(str)

    def __init__(self, prompt: str) -> None:
        super().__init__()
        self.prompt = prompt

    def run(self) -> None:
        payload = json.dumps({"prompt": self.prompt, "auto": True, "engineCombo": "multi"}).encode("utf-8")
        req = urllib.request.Request(
            BRAIN_URL,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "AIBrowser/1.0"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok") and data.get("blended"):
                self.response.emit(str(data["blended"]))
            else:
                self.error.emit(str(data.get("error") or "Brain returned no blended text"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            self.error.emit(f"AI Hub Brain offline or error: {exc}\nStart AI Hub Bridge on port 8765.")


class AIBrowserWindow(MainWindow):
    """Steamish browser with AI assistant dock (merged aicat browser)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI Browser — Steamish + AI Assistant")
        self._ai_worker: BrainWorker | None = None
        self._build_ai_dock()

    def _build_ai_dock(self) -> None:
        dock = QDockWidget("AI Assistant", self)
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Context: page title + selected text + AI Hub Brain"))
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("AI replies appear here…")

        self.ai_input = QTextEdit()
        self.ai_input.setPlaceholderText("Ask about the page (Ctrl+Enter to send)")
        self.ai_input.setMaximumHeight(100)

        send_btn = QPushButton("Send to Brain")
        send_btn.clicked.connect(self.send_ai_message)
        self.ai_input.installEventFilter(self)

        layout.addWidget(self.chat_display)
        layout.addWidget(self.ai_input)
        layout.addWidget(send_btn)
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def eventFilter(self, obj, event):  # noqa: N802
        if obj == self.ai_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.send_ai_message()
                return True
        return super().eventFilter(obj, event)

    def send_ai_message(self) -> None:
        user_text = self.ai_input.toPlainText().strip()
        if not user_text:
            return
        self.chat_display.append(f"<b>You:</b> {user_text}")
        self.ai_input.clear()

        view = self.current_view()
        if not view:
            self._start_brain(user_text, "", "")
            return

        page_title = view.title()

        def on_selection(selected: str) -> None:
            self._start_brain(user_text, page_title, selected or "")

        view.page().runJavaScript("window.getSelection().toString()", on_selection)

    def _start_brain(self, user_text: str, page_title: str, selected_text: str) -> None:
        context = f"Page: {page_title}\nSelected: {(selected_text or '')[:500]}"
        full_prompt = (
            "You are the AI assistant inside DEMOCORE AI Browser (merged Steamish + page-aware browser).\n"
            f"{context}\n\nUser: {user_text}"
        )
        self.chat_display.append(f"<i>Context: {(page_title or 'page')[:50]}…</i>")
        if self._ai_worker and self._ai_worker.isRunning():
            return
        self._ai_worker = BrainWorker(full_prompt)
        self._ai_worker.response.connect(self._show_ai_reply)
        self._ai_worker.error.connect(self._show_ai_error)
        self._ai_worker.start()

    def _show_ai_reply(self, reply: str) -> None:
        self.chat_display.append(f"<b>AI:</b> {reply}")
        self.chat_display.append("<hr>")

    def _show_ai_error(self, msg: str) -> None:
        self.chat_display.append(f"<b style='color:#f88'>Error:</b> {msg}")
        self.chat_display.append("<hr>")


def main() -> None:
    app = QApplication(sys.argv)
    win = AIBrowserWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
