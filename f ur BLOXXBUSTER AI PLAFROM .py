# blockbuster_ai_platform.py
# Blockbuster AI Platform - Complete Working Version with Templates

from __future__ import annotations
import os
import sys
import json
import time
import uuid
import re
import threading
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import requests
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QEvent, QUrl, QProcess, QTimer, QSize
)
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QColor, QDesktopServices, QTextCursor,
    QSyntaxHighlighter, QTextDocument, QTextCharFormat, QFileSystemModel,
    QPalette
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QDockWidget, QTabWidget,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QColorDialog,
    QDialogButtonBox, QFormLayout, QToolButton, QSizePolicy, QTextEdit,
    QTextBrowser, QMenu, QStyleFactory, QSplitter, QTreeView, QPlainTextEdit,
    QSlider, QGridLayout, QGroupBox
)

# Try to import web engine for preview
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("PyQtWebEngine not installed; preview will be simple HTML text.")

# Optional code highlighting
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

# App constants
APP_NAME = "Blockbuster AI Platform"
APP_ID = "blockbuster_ai"
VERSION = "3.0"

def _app_data_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, APP_ID)
    os.makedirs(d, exist_ok=True)
    return d

APP_DIR = _app_data_dir()
CHATS_DIR = os.path.join(APP_DIR, "chats")
ATT_DIR = os.path.join(APP_DIR, "attachments")
PROJECTS_DIR = os.path.join(APP_DIR, "projects")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
os.makedirs(CHATS_DIR, exist_ok=True)
os.makedirs(ATT_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

SETTINGS_PATH = os.path.join(APP_DIR, "settings.json")
INDEX_PATH = os.path.join(CHATS_DIR, "index.json")
TEMPLATES_PATH = os.path.join(APP_DIR, "templates.json")

# Default templates
DEFAULT_TEMPLATES = {
    "Python Script": "Create a Python script that:\n\n",
    "React Component": "Create a React component that:\n\n",
    "Bug Fix": "Fix the following bug:\n\n```\n\n```\n\n",
    "Code Review": "Review this code and suggest improvements:\n\n```\n\n```\n\n",
    "Documentation": "Write documentation for:\n\n",
    "Unit Tests": "Write unit tests for:\n\n```\n\n```\n\n",
    "API Endpoint": "Create an API endpoint that:\n\n",
    "Database Query": "Write a database query that:\n\n",
}

# Defaults for providers
DEFAULTS = {
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
    }
}

# Helper functions
def _safe_read_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _safe_write_json(path: str, data: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def _now_ts() -> int:
    return int(time.time())

def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

def load_templates() -> Dict[str, str]:
    return _safe_read_json(TEMPLATES_PATH, DEFAULT_TEMPLATES)

def save_templates(templates: Dict[str, str]) -> None:
    _safe_write_json(TEMPLATES_PATH, templates)

@dataclass
class Settings:
    provider: str = "OpenRouter"
    base_url: str = DEFAULTS["OpenRouter"]["base"]
    key_openrouter: str = ""
    key_groq: str = ""
    key_local: str = ""
    remember_keys: bool = True
    free_only: bool = True
    model: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    auto_continue: bool = True
    auto_save: bool = True
    forced_reply_language: str = "Auto"
    # Theme
    bg: str = "#0f1117"
    panel: str = "#151b2b"
    bubble_user: str = "#1c2440"
    bubble_assistant: str = "#1a2233"
    text: str = "#d7dae0"
    accent: str = "#4aa3ff"
    code_bg: str = "#0b1220"
    alt_focus: str = "#00ff66"
    font_family: str = "Segoe UI"
    code_font_family: str = "Consolas"
    background_image: str = ""
    eur_per_1k_tokens: float = 0.002
    # Project & AI
    default_project_path: str = PROJECTS_DIR
    show_terminal: bool = True
    ai_actions_enabled: bool = True
    # Multi-AI settings
    num_ai_workers: int = 1
    selected_models: List[str] = None
    # Sliders
    coding_quality: int = 50
    text_length: int = 50
    preview_effort: int = 50

def load_settings() -> Settings:
    raw = _safe_read_json(SETTINGS_PATH, {})
    try:
        s = Settings(**raw)
    except Exception:
        s = Settings()
    if s.provider not in DEFAULTS:
        s.provider = "OpenRouter"
    if not s.base_url:
        s.base_url = DEFAULTS[s.provider]["base"]
    if s.selected_models is None:
        s.selected_models = [s.model] if s.model else []
    return s

def save_settings(s: Settings) -> None:
    _safe_write_json(SETTINGS_PATH, asdict(s))

# --- Simple code highlighter ---
class SimpleCodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument):
        super().__init__(parent)
        self.highlighting_rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 150, 200))
        keywords = ["def", "class", "if", "else", "elif", "for", "while", "return", "import", "from", "try", "except", "with", "as", "None", "True", "False", "and", "or", "not"]
        for kw in keywords:
            self.highlighting_rules.append((rf'\b{kw}\b', keyword_format))
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(200, 150, 100))
        self.highlighting_rules.append((r'".*?"', string_format))
        self.highlighting_rules.append((r"'.*?'", string_format))
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 150, 100))
        self.highlighting_rules.append((r'#.*', comment_format))
        self.highlighting_rules.append((r'//.*', comment_format))

    def highlightBlock(self, text: str):
        for pattern, fmt in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(QFont("Consolas", 10))
        self.highlighter = SimpleCodeHighlighter(self.document())

# --- Terminal widget ---
class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 9))
        self.input = QLineEdit()
        self.input.returnPressed.connect(self.run_command)
        layout.addWidget(self.output)
        layout.addWidget(self.input)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        if sys.platform == "win32":
            self.shell = "cmd.exe"
            self.shell_args = []
        else:
            self.shell = "/bin/bash"
            self.shell_args = ["-i"]
        self.process.start(self.shell, self.shell_args)
        self.input.setFocus()

    def run_command(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.input.clear()
        self.output.append(f"> {cmd}")
        self.process.write((cmd + "\n").encode())

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.output.append(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='replace')
        self.output.append(data)

    def process_finished(self):
        self.output.append("Process finished. Restarting...")
        self.process.start(self.shell, self.shell_args)

# --- File tree ---
class FileTree(QTreeView):
    file_activated = pyqtSignal(str)
    def __init__(self, root_path: str):
        super().__init__()
        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(root_path))
        self.setHeaderHidden(True)
        self.doubleClicked.connect(self.on_double_click)

    def on_double_click(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            self.file_activated.emit(path)

# --- AI Worker ---
class AIWorker(QThread):
    delta = pyqtSignal(str, int)  # delta, worker_id
    done = pyqtSignal(dict, int)  # result, worker_id
    fail = pyqtSignal(str, int)   # error, worker_id

    def __init__(self, base_url: str, api_key: str, payload: dict, worker_id: int, extra_headers: Optional[dict] = None):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.payload = payload
        self.worker_id = worker_id
        self.extra_headers = extra_headers or {}
        self._stop = False
        self.response_text = ""

    def stop(self):
        self._stop = True

    def run(self):
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {"Content-Type": "application/json", "User-Agent": "BlockbusterAI"}
            headers.update(self.extra_headers)
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            with requests.post(url, headers=headers, json=self.payload, stream=True, timeout=300) as r:
                if r.status_code >= 400:
                    raise RuntimeError(f"HTTP {r.status_code}\n{r.text[:4000]}")

                full = ""
                finish_reason = None
                usage = {}
                for raw in r.iter_lines(decode_unicode=True):
                    if self._stop:
                        break
                    if not raw:
                        continue
                    line = raw.strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except Exception:
                        continue
                    ch0 = (chunk.get("choices") or [{}])[0]
                    fr = ch0.get("finish_reason")
                    if fr is not None:
                        finish_reason = fr
                    if isinstance(chunk.get("usage"), dict):
                        usage = chunk.get("usage") or usage
                    delta = ((ch0.get("delta") or {}).get("content")) or ""
                    if delta:
                        full += delta
                        self.response_text += delta
                        self.delta.emit(delta, self.worker_id)
                self.done.emit({"content": full, "finish_reason": finish_reason or "stop", "usage": usage}, self.worker_id)
        except Exception as e:
            self.fail.emit(str(e), self.worker_id)

# --- Template Widget (Sticky Template Box) ---
class TemplateWidget(QFrame):
    template_clicked = pyqtSignal(str, str)  # template_name, template_content
    
    def __init__(self, name: str, content: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.content = content
        self.setObjectName("TemplateWidget")
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Title
        title = QLabel(name)
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Preview
        preview = QLabel(content[:60] + ("..." if len(content) > 60 else ""))
        preview.setStyleSheet("font-size: 10px; opacity: 0.7;")
        preview.setWordWrap(True)
        layout.addWidget(preview)
        
        # Buttons
        btn_layout = QHBoxLayout()
        use_btn = QPushButton("Use")
        use_btn.setFixedSize(40, 25)
        use_btn.clicked.connect(self._use_template)
        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(30, 25)
        edit_btn.clicked.connect(self._edit_template)
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 25)
        delete_btn.clicked.connect(self._delete_template)
        
        btn_layout.addWidget(use_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def _use_template(self):
        self.template_clicked.emit(self.name, self.content)
    
    def _edit_template(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Template: {self.name}")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        
        name_edit = QLineEdit(self.name)
        content_edit = QTextEdit()
        content_edit.setPlainText(self.content)
        content_edit.setMinimumHeight(200)
        
        layout.addWidget(QLabel("Template Name:"))
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Template Content:"))
        layout.addWidget(content_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            new_name = name_edit.text().strip()
            new_content = content_edit.toPlainText()
            if new_name and new_content:
                self.name = new_name
                self.content = new_content
                title = self.layout().itemAt(0).widget()
                title.setText(new_name)
                preview = self.layout().itemAt(1).widget()
                preview.setText(new_content[:60] + ("..." if len(new_content) > 60 else ""))
                # Save to global templates
                templates = load_templates()
                templates[new_name] = new_content
                if self.name != new_name and self.name in templates:
                    del templates[self.name]
                save_templates(templates)
    
    def _delete_template(self):
        reply = QMessageBox.question(self, "Delete Template", f"Delete '{self.name}'?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            templates = load_templates()
            if self.name in templates:
                del templates[self.name]
                save_templates(templates)
            self.deleteLater()

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.templates = load_templates()
        self.setWindowTitle(f"{APP_NAME} — Blockbuster Edition")
        self.resize(1800, 1000)

        # Current project
        self.current_project_path = self.settings.default_project_path
        self.current_file_path = None
        self.open_files = {}

        # AI chat state
        self.chat: Dict[str, Any] = self._new_chat_record()
        self.workers = []
        self.worker_responses = {}
        self.current_worker_id = 0

        # Build UI
        self._build_ui()
        self._apply_theme()
        self._load_projects()
        self._load_templates_ui()

        self.refresh_models()

    # --- UI Construction ---
    def _build_ui(self):
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: file tree and editor
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        self.file_tree = FileTree(self.current_project_path)
        self.file_tree.file_activated.connect(self.open_file)
        tree_layout.addWidget(self.file_tree)
        btn_change_project = QPushButton("Change Project")
        btn_change_project.clicked.connect(self.change_project)
        tree_layout.addWidget(btn_change_project)
        left_splitter.addWidget(tree_widget)

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        left_splitter.addWidget(self.editor_tabs)
        left_splitter.setSizes([250, 750])
        main_splitter.addWidget(left_splitter)

        # Right: chat + preview + templates
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top: Chat panel
        chat_panel = self._build_chat_panel()
        right_splitter.addWidget(chat_panel)

        # Middle: Templates panel (sticky boxes)
        templates_panel = self._build_templates_panel()
        right_splitter.addWidget(templates_panel)

        # Bottom: Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_label = QLabel("Live Preview")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)
        if HAS_WEBENGINE:
            self.preview_view = QWebEngineView()
        else:
            self.preview_view = QTextBrowser()
            self.preview_view.setPlaceholderText("HTML preview (simple text)")
        preview_layout.addWidget(self.preview_view)
        right_splitter.addWidget(preview_widget)
        
        right_splitter.setSizes([500, 200, 300])
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([800, 1000])
        self.setCentralWidget(main_splitter)

        # Bottom terminal
        if self.settings.show_terminal:
            self.terminal_dock = QDockWidget("Terminal", self)
            self.terminal_dock.setWidget(TerminalWidget())
            self.terminal_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)

        # Toolbar
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        act_settings = QAction("⚙ Settings", self)
        act_settings.triggered.connect(self.open_settings)
        tb.addAction(act_settings)
        act_new_chat = QAction("＋ New Chat", self)
        act_new_chat.triggered.connect(self._new_chat)
        tb.addAction(act_new_chat)
        act_stop = QAction("⏹ Stop", self)
        act_stop.triggered.connect(self.stop_all_workers)
        tb.addAction(act_stop)
        act_refresh = QAction("⟳ Refresh models", self)
        act_refresh.triggered.connect(self.refresh_models)
        tb.addAction(act_refresh)
        act_add_template = QAction("📝 Add Template", self)
        act_add_template.triggered.connect(self._add_template)
        tb.addAction(act_add_template)

        self.status = self.statusBar()
        self._update_status()

    def _build_chat_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Top controls
        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(8, 8, 8, 8)

        self.provider_box = QComboBox()
        self.provider_box.addItems(["OpenRouter", "Groq", "Local"])
        self.provider_box.setCurrentText(self.settings.provider)
        self.provider_box.currentTextChanged.connect(self._on_provider_changed)

        self.free_box = QCheckBox("FREE")
        self.free_box.setChecked(self.settings.free_only)
        self.free_box.stateChanged.connect(self._on_free_only_changed)

        self.model_box = QComboBox()
        self.model_box.setMinimumWidth(200)
        self.model_box.currentTextChanged.connect(self._on_model_selected)

        self.mode_box = QComboBox()
        self.mode_box.addItems(["CODING", "REASONING", "PLAN", "DEBUG", "EXPLAIN"])
        self.submode_box = QComboBox()
        self.submode_box.addItems(["(none)", "Python", "JavaScript", "C++", "Rust", "Go", "HTML/CSS"])

        top_layout.addWidget(QLabel("Provider"))
        top_layout.addWidget(self.provider_box)
        top_layout.addWidget(self.free_box)
        top_layout.addWidget(QLabel("Model"))
        top_layout.addWidget(self.model_box, 1)
        top_layout.addWidget(QLabel("Mode"))
        top_layout.addWidget(self.mode_box)
        top_layout.addWidget(self.submode_box)

        # Multi-AI selector
        self.num_ai_spin = QSpinBox()
        self.num_ai_spin.setRange(1, 6)
        self.num_ai_spin.setValue(self.settings.num_ai_workers)
        self.num_ai_spin.valueChanged.connect(self._on_num_ai_changed)
        top_layout.addWidget(QLabel("AI Workers"))
        top_layout.addWidget(self.num_ai_spin)

        # Sliders
        sliders_widget = QWidget()
        sliders_layout = QHBoxLayout(sliders_widget)
        sliders_layout.setContentsMargins(8, 0, 8, 8)

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(self.settings.coding_quality)
        self.quality_slider.valueChanged.connect(self._on_quality_changed)
        sliders_layout.addWidget(QLabel("Quality"))
        sliders_layout.addWidget(self.quality_slider)

        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(0, 100)
        self.length_slider.setValue(self.settings.text_length)
        self.length_slider.valueChanged.connect(self._on_length_changed)
        sliders_layout.addWidget(QLabel("Length"))
        sliders_layout.addWidget(self.length_slider)

        self.effort_slider = QSlider(Qt.Orientation.Horizontal)
        self.effort_slider.setRange(0, 100)
        self.effort_slider.setValue(self.settings.preview_effort)
        self.effort_slider.valueChanged.connect(self._on_effort_changed)
        sliders_layout.addWidget(QLabel("Preview Effort"))
        sliders_layout.addWidget(self.effort_slider)

        # Chat display
        self.chat_area = QTextBrowser()
        self.chat_area.setOpenExternalLinks(True)

        # Input area
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(8, 8, 8, 8)

        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("Ask AI or use /explain, /generate, /fix, /refactor...\nEnter to send, Shift+Enter for new line")
        self.prompt.setFixedHeight(100)

        self.btn_send = QPushButton("Send to All AI Workers")
        self.btn_send.clicked.connect(self.send_to_all)

        # AI Action buttons
        action_layout = QHBoxLayout()
        self.btn_explain = QPushButton("Explain")
        self.btn_explain.clicked.connect(lambda: self.ai_action("explain"))
        self.btn_generate = QPushButton("Generate")
        self.btn_generate.clicked.connect(lambda: self.ai_action("generate"))
        self.btn_fix = QPushButton("Fix")
        self.btn_fix.clicked.connect(lambda: self.ai_action("fix"))
        self.btn_refactor = QPushButton("Refactor")
        self.btn_refactor.clicked.connect(lambda: self.ai_action("refactor"))
        action_layout.addWidget(self.btn_explain)
        action_layout.addWidget(self.btn_generate)
        action_layout.addWidget(self.btn_fix)
        action_layout.addWidget(self.btn_refactor)
        action_layout.addStretch()

        input_layout.addWidget(self.prompt)
        input_layout.addWidget(self.btn_send)
        input_layout.addLayout(action_layout)

        layout.addWidget(top)
        layout.addWidget(sliders_widget)
        layout.addWidget(self.chat_area, 1)
        layout.addWidget(input_widget)

        return widget

    def _build_templates_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header = QLabel("📋 Quick Templates (Click to use)")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Scroll area for templates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.templates_container = QWidget()
        self.templates_layout = QGridLayout(self.templates_container)
        self.templates_layout.setSpacing(8)
        scroll.setWidget(self.templates_container)
        layout.addWidget(scroll)
        
        return widget

    def _load_templates_ui(self):
        # Clear existing
        while self.templates_layout.count():
            item = self.templates_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add templates
        row, col = 0, 0
        for name, content in self.templates.items():
            template_widget = TemplateWidget(name, content)
            template_widget.template_clicked.connect(self._use_template)
            self.templates_layout.addWidget(template_widget, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _use_template(self, name: str, content: str):
        self.prompt.setPlainText(content)
        self.status.showMessage(f"Template '{name}' loaded", 2000)

    def _add_template(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Template")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Template name...")
        content_edit = QTextEdit()
        content_edit.setPlaceholderText("Template content...")
        content_edit.setMinimumHeight(200)
        
        layout.addWidget(QLabel("Template Name:"))
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Template Content:"))
        layout.addWidget(content_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            name = name_edit.text().strip()
            content = content_edit.toPlainText()
            if name and content:
                self.templates[name] = content
                save_templates(self.templates)
                self._load_templates_ui()
                self.status.showMessage(f"Template '{name}' added", 2000)

    # --- Slider handlers ---
    def _on_quality_changed(self, value):
        self.settings.coding_quality = value
        save_settings(self.settings)
        temp = 0.2 + (100 - value) * 0.8 / 100.0
        self.settings.temperature = temp
        self._update_status()

    def _on_length_changed(self, value):
        self.settings.text_length = value
        save_settings(self.settings)
        max_tokens = int(256 + (value / 100.0) * 7936)
        self.settings.max_tokens = max_tokens
        self._update_status()

    def _on_effort_changed(self, value):
        self.settings.preview_effort = value
        save_settings(self.settings)
        self._update_status()

    def _on_num_ai_changed(self, value):
        self.settings.num_ai_workers = value
        while len(self.settings.selected_models) < value:
            self.settings.selected_models.append(self.settings.model or self.model_box.currentText())
        while len(self.settings.selected_models) > value:
            self.settings.selected_models.pop()
        save_settings(self.settings)
        self._update_status()

    # --- File handling ---
    def change_project(self):
        new_root = QFileDialog.getExistingDirectory(self, "Select Project Directory", self.current_project_path)
        if new_root:
            self.current_project_path = new_root
            self.file_tree.model.setRootPath(new_root)
            self.file_tree.setRootIndex(self.file_tree.model.index(new_root))
            self.settings.default_project_path = new_root
            save_settings(self.settings)
            self.status.showMessage(f"Project changed to {new_root}")

    def open_file(self, path: str):
        if path in self.open_files:
            self.editor_tabs.setCurrentIndex(self.open_files[path])
            return
        editor = CodeEditor()
        try:
            with open(path, "r", encoding="utf-8") as f:
                editor.setPlainText(f.read())
        except Exception as e:
            editor.setPlainText(f"Error reading file: {e}")
        tab_index = self.editor_tabs.addTab(editor, os.path.basename(path))
        self.open_files[path] = tab_index
        self.editor_tabs.setCurrentIndex(tab_index)
        self.current_file_path = path
        if path.endswith(('.html', '.htm')):
            self.update_preview()

    def close_tab(self, index):
        widget = self.editor_tabs.widget(index)
        if widget:
            for p, idx in list(self.open_files.items()):
                if idx == index:
                    del self.open_files[p]
                    break
            self.editor_tabs.removeTab(index)
            widget.deleteLater()

    def get_current_editor_text(self) -> str:
        if self.editor_tabs.currentWidget():
            return self.editor_tabs.currentWidget().toPlainText()
        return ""

    def update_preview(self):
        if self.current_file_path and self.current_file_path.endswith(('.html', '.htm')):
            try:
                with open(self.current_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception:
                html_content = "<html><body><p>Error loading file</p></body></html>"
        else:
            content = self.get_current_editor_text()
            html_content = f"<html><body><pre>{_html_escape(content)}</pre></body></html>"
        if HAS_WEBENGINE:
            self.preview_view.setHtml(html_content)
        else:
            self.preview_view.setPlainText(html_content)

    # --- AI Actions ---
    def ai_action(self, action_type: str):
        if not self.settings.ai_actions_enabled:
            QMessageBox.warning(self, "AI Actions Disabled", "Enable AI actions in settings.")
            return
        editor = self.editor_tabs.currentWidget()
        if not editor:
            QMessageBox.information(self, "No Editor", "Open a file first.")
            return
        cursor = editor.textCursor()
        selected = cursor.selectedText() if cursor.hasSelection() else ""
        context = selected if selected else editor.toPlainText()
        if not context.strip():
            QMessageBox.information(self, "Empty", "Nothing to act on.")
            return

        if action_type == "explain":
            prompt = f"Explain the following code in detail:\n\n```\n{context}\n```"
        elif action_type == "generate":
            prompt = f"Write code to accomplish the following:\n{context}"
        elif action_type == "fix":
            prompt = f"Fix any bugs in the following code:\n\n```\n{context}\n```"
        elif action_type == "refactor":
            prompt = f"Refactor the following code for better readability and performance:\n\n```\n{context}\n```"
        else:
            return
        self.prompt.setPlainText(prompt)
        self.send_to_all()

    # --- Multi-AI Send ---
    def send_to_all(self):
        if self.workers:
            self.stop_all_workers()
        
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            return
        
        self._append_message("user", prompt)
        self.prompt.clear()

        model_list = self.settings.selected_models[:self.settings.num_ai_workers]
        if not model_list or model_list[0] == "":
            model_list = [self.settings.model or self.model_box.currentText()] * self.settings.num_ai_workers

        # System message
        mode = self.mode_box.currentText()
        sub = self.submode_box.currentText()
        forced = self.settings.forced_reply_language
        sys_parts = [f"MODE: {mode}" + (f" / {sub}" if sub != "(none)" else "")]
        if forced != "Auto":
            sys_parts.append(f"LANGUAGE: Reply in {forced}.")
        if self.current_file_path:
            sys_parts.append(f"Current file: {os.path.basename(self.current_file_path)}")
            file_content = self.get_current_editor_text()
            if file_content:
                sys_parts.append(f"File content:\n```\n{file_content}\n```")
        system_content = "\n".join(sys_parts)

        # History
        history = []
        for m in self.chat["messages"][-10:]:
            if m["role"] in ("user", "assistant"):
                history.append({"role": m["role"], "content": m["content"]})

        self.workers = []
        self.worker_responses = {}
        
        self.chat_area.append(f'<div style="margin-top:10px;"><b style="color:{self.settings.accent}">🤖 AI Workers ({len(model_list)} models):</b></div>')
        
        for i, model in enumerate(model_list):
            quality = self.settings.coding_quality
            temp = 0.2 + (100 - quality) * 0.8 / 100.0
            length = self.settings.text_length
            max_tokens = int(256 + (length / 100.0) * 7936)
            
            messages = [{"role": "system", "content": system_content}] + history + [{"role": "user", "content": prompt}]
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temp,
                "top_p": self.settings.top_p,
                "stream": True,
            }
            
            worker = AIWorker(self.settings.base_url, self._get_api_key(), payload, i)
            worker.delta.connect(self._on_delta_multi)
            worker.done.connect(self._on_done_multi)
            worker.fail.connect(self._on_fail_multi)
            self.workers.append(worker)
            self.worker_responses[i] = ""
            
            self.chat_area.append(f'<div id="ai_response_{i}" style="margin-left:20px; margin-bottom:10px;">'
                                 f'<b style="color:#88ff88;">🤖 AI #{i+1} ({model}):</b> <span id="ai_text_{i}"></span></div>')
            worker.start()
        
        self._update_status()

    def _on_delta_multi(self, delta: str, worker_id: int):
        if worker_id in self.worker_responses:
            self.worker_responses[worker_id] += delta
            # Update the specific AI's response in chat
            cursor = self.chat_area.textCursor()
            # Find and update the specific span
            # For simplicity, we'll just update the whole response when done

    def _on_done_multi(self, result: dict, worker_id: int):
        content = result["content"]
        model = self.settings.selected_models[worker_id] if worker_id < len(self.settings.selected_models) else "Unknown"
        
        formatted_content = self._format_content(content)
        
        self.chat_area.append(f'<div style="margin-left:20px; margin-bottom:15px; border-left: 2px solid {self.settings.accent}; padding-left:10px;">'
                             f'<b style="color:{self.settings.accent};">✅ AI #{worker_id+1} ({model})</b><br/>'
                             f'{formatted_content}</div>')
        
        self.chat["messages"].append({
            "role": "assistant", 
            "content": content, 
            "ts": _now_ts(), 
            "id": uuid.uuid4().hex,
            "model": model,
            "worker_id": worker_id
        })
        
        self.workers[worker_id] = None
        self._update_status()

    def _on_fail_multi(self, err: str, worker_id: int):
        model = self.settings.selected_models[worker_id] if worker_id < len(self.settings.selected_models) else "Unknown"
        self.chat_area.append(f'<div style="margin-left:20px; margin-bottom:10px; color:#ff8888;">'
                             f'❌ AI #{worker_id+1} ({model}) error: {err}</div>')
        self.workers[worker_id] = None
        self._update_status()

    def stop_all_workers(self):
        for worker in self.workers:
            if worker and worker.isRunning():
                worker.stop()
        self.workers = []
        self.status.showMessage("All workers stopped", 2000)

    # --- Chat management ---
    def _new_chat_record(self) -> Dict[str, Any]:
        return {
            "id": uuid.uuid4().hex,
            "title": "New Chat",
            "created": _now_ts(),
            "updated": _now_ts(),
            "temporary": False,
            "stats": {"messages": 0, "answers": 0, "approx_tokens": 0, "approx_eur": 0.0},
            "messages": [],
        }

    def _new_chat(self):
        self.chat = self._new_chat_record()
        self.chat_area.clear()
        self._update_status()

    def _append_message(self, role: str, content: str):
        msg = {"role": role, "content": content, "ts": _now_ts(), "id": uuid.uuid4().hex}
        self.chat["messages"].append(msg)
        self.chat["stats"]["messages"] += 1
        self._render_message(msg)

    def _render_message(self, msg: dict):
        role = msg["role"]
        content = msg["content"]
        ts = time.strftime("%H:%M:%S", time.localtime(msg["ts"]))
        if role == "user":
            html = f'<div style="margin-bottom:12px;"><b style="color:{self.settings.accent}">👤 You ({ts}):</b><br/>{self._format_content(content)}</div>'
        else:
            html = f'<div style="margin-bottom:12px;"><b style="color:{self.settings.accent}">🤖 Assistant ({ts}):</b><br/>{self._format_content(content)}</div>'
        self.chat_area.append(html)

    def _format_content(self, text: str) -> str:
        text = _html_escape(text)
        text = re.sub(r'```([a-zA-Z0-9_\-\+]*)\n(.*?)```', self._code_block_repl, text, flags=re.S)
        text = re.sub(r'`([^`]+)`', r'<code style="background:#2d2d2d; padding:2px 4px; border-radius:3px;">\1</code>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'(https?://[^\s<>"]+)', r'<a href="\1" style="color:#4aa3ff;">\1</a>', text)
        text = text.replace("\n", "<br/>")
        return f'<div style="font-family:{self.settings.font_family}; line-height:1.5;">{text}</div>'

    def _code_block_repl(self, m):
        lang = m.group(1).strip()
        code = m.group(2).strip()
        if HAS_PYGMENTS:
            try:
                lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
                formatter = HtmlFormatter(style='monokai', noclasses=True)
                highlighted = highlight(code, lexer, formatter)
                return f'<div style="background:{self.settings.code_bg}; border-radius:6px; padding:12px; margin:8px 0; overflow:auto;">{highlighted}</div>'
            except:
                pass
        return f'<pre style="background:{self.settings.code_bg}; border-radius:6px; padding:12px; margin:8px 0; overflow:auto; font-family:{self.settings.code_font_family};"><code>{_html_escape(code)}</code></pre>'

    # --- Provider/model handling ---
    def _get_api_key(self) -> str:
        p = self.settings.provider
        if p == "OpenRouter":
            return self.settings.key_openrouter
        if p == "Groq":
            return self.settings.key_groq
        return self.settings.key_local

    def _on_provider_changed(self, p: str):
        self.settings.provider = p
        save_settings(self.settings)
        self.refresh_models()

    def _on_free_only_changed(self):
        self.settings.free_only = self.free_box.isChecked()
        save_settings(self.settings)
        self.refresh_models()

    def _on_model_selected(self, m: str):
        if m and m != "Loading…":
            self.settings.model = m
            save_settings(self.settings)
            self._update_status()

    def refresh_models(self):
        self.model_box.clear()
        self.model_box.addItem("Loading…")
        key = self._get_api_key()
        free = self.free_box.isChecked()
        self.models_worker = ModelsWorker(self.settings.provider, self.settings.base_url, key, free)
        self.models_worker.ok.connect(self._models_ok)
        self.models_worker.fail.connect(self._models_fail)
        self.models_worker.start()

    def _models_ok(self, ids):
        self.model_box.blockSignals(True)
        self.model_box.clear()
        self.model_box.addItems(ids)
        if self.settings.model in ids:
            self.model_box.setCurrentText(self.settings.model)
        else:
            self.model_box.setCurrentIndex(0)
            self.settings.model = self.model_box.currentText()
            save_settings(self.settings)
        self.model_box.blockSignals(False)
        self._update_status()

    def _models_fail(self, err):
        self.model_box.clear()
        self.model_box.addItems(FALLBACK_OPENROUTER_FREE)
        QMessageBox.warning(self, "Model list failed", err)

    # --- Theme ---
    def _apply_theme(self):
        s = self.settings
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {s.bg}; }}
            QWidget {{ color: {s.text}; font-family: {s.font_family}; }}
            QTextEdit, QTextBrowser, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget {{
                background: {s.panel};
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton {{
                background: {s.accent};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{ background: #6cc5ff; }}
            QDockWidget::title {{ background: {s.panel}; padding: 4px; }}
            QTabWidget::pane {{ background: {s.panel}; border: 1px solid rgba(255,255,255,0.1); }}
            QTabBar::tab {{ background: {s.panel}; padding: 6px 12px; margin-right: 2px; }}
            QTabBar::tab:selected {{ background: {s.accent}; color: white; }}
            QFrame#TemplateWidget {{
                background: {s.panel};
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
            }}
            QFrame#TemplateWidget:hover {{
                border: 1px solid {s.accent};
            }}
        """)

    def _update_status(self):
        active = len([w for w in self.workers if w and w.isRunning()])
        self.status.showMessage(f"Provider: {self.settings.provider} | Model: {self.settings.model} | "
                               f"Quality: {self.settings.coding_quality} | Length: {self.settings.text_length} | "
                               f"Active Workers: {active}/{self.settings.num_ai_workers}")

    def _load_projects(self):
        os.makedirs(self.current_project_path, exist_ok=True)

    # --- Settings dialog with easy color selection ---
    def open_settings(self):
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec():
            dlg.apply_to_settings()
            save_settings(self.settings)
            self._apply_theme()
            self.refresh_models()
            if self.settings.show_terminal and not hasattr(self, 'terminal_dock'):
                self.terminal_dock = QDockWidget("Terminal", self)
                self.terminal_dock.setWidget(TerminalWidget())
                self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.terminal_dock)
            elif not self.settings.show_terminal and hasattr(self, 'terminal_dock'):
                self.terminal_dock.close()
                self.terminal_dock.deleteLater()
                del self.terminal_dock

    def closeEvent(self, e):
        self.stop_all_workers()
        save_settings(self.settings)
        super().closeEvent(e)

# --- Models worker ---
class ModelsWorker(QThread):
    ok = pyqtSignal(list)
    fail = pyqtSignal(str)

    def __init__(self, provider: str, base_url: str, api_key: str, free_only: bool):
        super().__init__()
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.free_only = free_only

    def run(self):
        try:
            url = f"{self.base_url}/models"
            headers = {"User-Agent": "BlockbusterAI"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}\n{r.text[:2000]}")
            j = r.json()
            data = j.get("data") or j.get("models") or []
            ids = [str(m.get("id") or m.get("name")) for m in data if m.get("id") or m.get("name")]
            if not ids:
                raise RuntimeError("No models returned")
            if self.provider == "OpenRouter" and self.free_only:
                ids = [x for x in ids if x.endswith(":free")]
            ids = sorted(set(ids))
            self.ok.emit(ids)
        except Exception as e:
            self.fail.emit(str(e))

FALLBACK_OPENROUTER_FREE = [
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
]

# --- Settings Dialog with Easy Color Selection ---
class ColorButton(QPushButton):
    color_changed = pyqtSignal(str)
    
    def __init__(self, initial_color: str):
        super().__init__()
        self.setFixedSize(60, 30)
        self.setStyleSheet(f"background-color: {initial_color}; border: 1px solid white; border-radius: 4px;")
        self.clicked.connect(self.pick_color)
    
    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 4px;")
            self.color_changed.emit(color.name())

class SettingsDialog(QDialog):
    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.s = settings
        self.setWindowTitle("Blockbuster Settings")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget for better organization
        tabs = QTabWidget()
        
        # API Tab
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        
        self.provider = QComboBox()
        self.provider.addItems(["OpenRouter", "Groq", "Local"])
        self.provider.setCurrentText(self.s.provider)
        self.base = QLineEdit(self.s.base_url)
        
        self.key_or = QLineEdit(self.s.key_openrouter)
        self.key_or.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_groq = QLineEdit(self.s.key_groq)
        self.key_groq.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_local = QLineEdit(self.s.key_local)
        self.key_local.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.remember = QCheckBox("Remember keys")
        self.remember.setChecked(self.s.remember_keys)
        
        self.free_only = QCheckBox("FREE only (OpenRouter)")
        self.free_only.setChecked(self.s.free_only)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(16, 32768)
        self.max_tokens.setValue(self.s.max_tokens)
        
        self.temp = QDoubleSpinBox()
        self.temp.setRange(0.0, 2.0)
        self.temp.setSingleStep(0.1)
        self.temp.setValue(self.s.temperature)
        
        self.top_p = QDoubleSpinBox()
        self.top_p.setRange(0.0, 1.0)
        self.top_p.setSingleStep(0.05)
        self.top_p.setValue(self.s.top_p)
        
        self.auto_continue = QCheckBox("Auto-continue")
        self.auto_continue.setChecked(self.s.auto_continue)
        
        self.auto_save = QCheckBox("Auto-save chats")
        self.auto_save.setChecked(self.s.auto_save)
        
        self.forced_lang = QComboBox()
        self.forced_lang.addItems(["Auto", "English", "Magyar", "Slovák", "Német", "Japán"])
        self.forced_lang.setCurrentText(self.s.forced_reply_language)
        
        api_layout.addRow("Provider", self.provider)
        api_layout.addRow("Base URL", self.base)
        api_layout.addRow("OpenRouter key", self.key_or)
        api_layout.addRow("Groq key", self.key_groq)
        api_layout.addRow("Local key", self.key_local)
        api_layout.addRow("", self.remember)
        api_layout.addRow("", self.free_only)
        api_layout.addRow("Max tokens", self.max_tokens)
        api_layout.addRow("Temperature", self.temp)
        api_layout.addRow("Top-p", self.top_p)
        api_layout.addRow("", self.auto_continue)
        api_layout.addRow("", self.auto_save)
        api_layout.addRow("Forced language", self.forced_lang)
        
        # AI Tab
        ai_tab = QWidget()
        ai_layout = QFormLayout(ai_tab)
        
        self.show_terminal = QCheckBox("Show terminal")
        self.show_terminal.setChecked(self.s.show_terminal)
        
        self.ai_actions = QCheckBox("Enable AI actions")
        self.ai_actions.setChecked(self.s.ai_actions_enabled)
        
        self.num_ai = QSpinBox()
        self.num_ai.setRange(1, 6)
        self.num_ai.setValue(self.s.num_ai_workers)
        
        self.model_list = QListWidget()
        self.model_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.model_list.addItems(FALLBACK_OPENROUTER_FREE)
        for i in range(self.model_list.count()):
            if self.model_list.item(i).text() in self.s.selected_models:
                self.model_list.item(i).setSelected(True)
        
        # Sliders
        self.coding_quality = QSlider(Qt.Orientation.Horizontal)
        self.coding_quality.setRange(0, 100)
        self.coding_quality.setValue(self.s.coding_quality)
        self.quality_label = QLabel(f"{self.s.coding_quality}%")
        self.coding_quality.valueChanged.connect(lambda v: self.quality_label.setText(f"{v}%"))
        
        self.text_length = QSlider(Qt.Orientation.Horizontal)
        self.text_length.setRange(0, 100)
        self.text_length.setValue(self.s.text_length)
        self.length_label = QLabel(f"{self.s.text_length}%")
        self.text_length.valueChanged.connect(lambda v: self.length_label.setText(f"{v}%"))
        
        self.preview_effort = QSlider(Qt.Orientation.Horizontal)
        self.preview_effort.setRange(0, 100)
        self.preview_effort.setValue(self.s.preview_effort)
        self.effort_label = QLabel(f"{self.s.preview_effort}%")
        self.preview_effort.valueChanged.connect(lambda v: self.effort_label.setText(f"{v}%"))
        
        ai_layout.addRow("", self.show_terminal)
        ai_layout.addRow("", self.ai_actions)
        ai_layout.addRow("Number of AI workers (1-6)", self.num_ai)
        ai_layout.addRow("Select models for each worker", self.model_list)
        ai_layout.addRow("Coding Quality", self._create_slider_row(self.coding_quality, self.quality_label))
        ai_layout.addRow("Text Length", self._create_slider_row(self.text_length, self.length_label))
        ai_layout.addRow("Preview Effort", self._create_slider_row(self.preview_effort, self.effort_label))
        
        # Theme Tab with easy color selection
        theme_tab = QWidget()
        theme_layout = QFormLayout(theme_tab)
        
        self.bg_btn = ColorButton(self.s.bg)
        self.bg_btn.color_changed.connect(lambda c: setattr(self, 'bg_val', c))
        self.panel_btn = ColorButton(self.s.panel)
        self.panel_btn.color_changed.connect(lambda c: setattr(self, 'panel_val', c))
        self.user_b_btn = ColorButton(self.s.bubble_user)
        self.user_b_btn.color_changed.connect(lambda c: setattr(self, 'user_b_val', c))
        self.asst_b_btn = ColorButton(self.s.bubble_assistant)
        self.asst_b_btn.color_changed.connect(lambda c: setattr(self, 'asst_b_val', c))
        self.accent_btn = ColorButton(self.s.accent)
        self.accent_btn.color_changed.connect(lambda c: setattr(self, 'accent_val', c))
        self.code_bg_btn = ColorButton(self.s.code_bg)
        self.code_bg_btn.color_changed.connect(lambda c: setattr(self, 'code_bg_val', c))
        
        self.font_family = QLineEdit(self.s.font_family)
        self.code_font = QLineEdit(self.s.code_font_family)
        
        theme_layout.addRow("Background", self.bg_btn)
        theme_layout.addRow("Panel Background", self.panel_btn)
        theme_layout.addRow("User Bubble", self.user_b_btn)
        theme_layout.addRow("Assistant Bubble", self.asst_b_btn)
        theme_layout.addRow("Accent Color", self.accent_btn)
        theme_layout.addRow("Code Background", self.code_bg_btn)
        theme_layout.addRow("Font Family", self.font_family)
        theme_layout.addRow("Code Font", self.code_font)
        
        tabs.addTab(api_tab, "API & Chat")
        tabs.addTab(ai_tab, "AI & Performance")
        tabs.addTab(theme_tab, "Theme")
        
        layout.addWidget(tabs)
        
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    
    def _create_slider_row(self, slider, label):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(slider)
        layout.addWidget(label)
        return widget
    
    def apply_to_settings(self):
        self.s.provider = self.provider.currentText()
        self.s.base_url = self.base.text().strip()
        self.s.remember_keys = self.remember.isChecked()
        if self.s.remember_keys:
            self.s.key_openrouter = self.key_or.text().strip()
            self.s.key_groq = self.key_groq.text().strip()
            self.s.key_local = self.key_local.text().strip()
        else:
            self.s.key_openrouter = ""
            self.s.key_groq = ""
            self.s.key_local = ""
        self.s.free_only = self.free_only.isChecked()
        self.s.max_tokens = self.max_tokens.value()
        self.s.temperature = self.temp.value()
        self.s.top_p = self.top_p.value()
        self.s.auto_continue = self.auto_continue.isChecked()
        self.s.auto_save = self.auto_save.isChecked()
        self.s.forced_reply_language = self.forced_lang.currentText()
        self.s.show_terminal = self.show_terminal.isChecked()
        self.s.ai_actions_enabled = self.ai_actions.isChecked()
        self.s.num_ai_workers = self.num_ai.value()
        self.s.selected_models = [item.text() for item in self.model_list.selectedItems()]
        while len(self.s.selected_models) < self.s.num_ai_workers:
            self.s.selected_models.append(self.model_list.item(0).text() if self.model_list.count() else "")
        self.s.coding_quality = self.coding_quality.value()
        self.s.text_length = self.text_length.value()
        self.s.preview_effort = self.preview_effort.value()
        
        # Theme colors
        if hasattr(self, 'bg_val'): self.s.bg = self.bg_val
        if hasattr(self, 'panel_val'): self.s.panel = self.panel_val
        if hasattr(self, 'user_b_val'): self.s.bubble_user = self.user_b_val
        if hasattr(self, 'asst_b_val'): self.s.bubble_assistant = self.asst_b_val
        if hasattr(self, 'accent_val'): self.s.accent = self.accent_val
        if hasattr(self, 'code_bg_val'): self.s.code_bg = self.code_bg_val
        
        self.s.font_family = self.font_family.text().strip() or self.s.font_family
        self.s.code_font_family = self.code_font.text().strip() or self.s.code_font_family

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()