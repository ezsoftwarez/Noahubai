#!/usr/bin/env python3
# browser_ai_fixed.py – Works on Python 3.14

import sys
from PySide6.QtCore import QUrl, QThread, Signal, Qt, QEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QTextEdit, QPushButton, QDockWidget, QLabel)
from PySide6.QtWebEngineWidgets import QWebEngineView

# ---------- Mock AI (replace with real API later) ----------
class AIWorker(QThread):
    response = Signal(str)
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
    def run(self):
        # Simple echo – no API key needed for testing
        self.response.emit(f"You said: {self.prompt}\n\n(Replace with OpenRouter/Groq key)")

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser + AI (fixed)")
        self.resize(1200, 800)

        # Central web view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://duckduckgo.com"))
        self.setCentralWidget(self.browser)

        # AI dock
        ai_dock = QDockWidget("AI Assistant", self)
        ai_widget = QWidget()
        layout = QVBoxLayout(ai_widget)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("AI replies will appear here...")

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Ask about the page (Ctrl+Enter to send)")
        self.input_field.setMaximumHeight(100)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        layout.addWidget(QLabel("Context: page title + selected text"))
        layout.addWidget(self.chat_display)
        layout.addWidget(self.input_field)
        layout.addWidget(send_btn)

        ai_widget.setLayout(layout)
        ai_dock.setWidget(ai_widget)

        # CORRECT: use Qt.RightDockWidgetArea, not 1
        self.addDockWidget(Qt.RightDockWidgetArea, ai_dock)

        # Install event filter for Ctrl+Enter
        self.input_field.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            # Check for Ctrl+Enter
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def send_message(self):
        user_text = self.input_field.toPlainText().strip()
        if not user_text:
            return
        self.chat_display.append(f"<b>You:</b> {user_text}")
        self.input_field.clear()

        # Get page title and selected text
        page_title = self.browser.title()
        self.browser.page().runJavaScript("window.getSelection().toString()",
            lambda sel: self.start_ai(user_text, page_title, sel))

    def start_ai(self, user_text, page_title, selected_text):
        context = f"Page: {page_title}\nSelected: {selected_text[:200]}"
        full_prompt = f"{context}\n\nUser: {user_text}"
        self.chat_display.append(f"<i>Context: {page_title[:50]}...</i>")
        self.worker = AIWorker(full_prompt)
        self.worker.response.connect(self.show_ai_reply)
        self.worker.start()

    def show_ai_reply(self, reply):
        self.chat_display.append(f"<b>AI:</b> {reply}")
        self.chat_display.append("<hr>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
