#!/usr/bin/env python3
"""
AI SWARM FOR CURSOR PRO+ (prototype)
Python 3.11+

  pip install -r requirements.txt
  py ai_swarm.py

Optional: start AI Hub bridge first (RUN-AI-HUB.bat) for Cursor ↔ Hub sync on port 8765.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from copy import deepcopy

from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
)

# =========================
# CONFIG
# =========================

BRIDGE_URL = "http://127.0.0.1:8765"

SYSTEM_PROMPT = """
Szia Cursor Pro+ Agent.

Te egy specializált alrendszer vagy egy több-agentes orchestration hálózatban.

Feladat:
- problémamegoldás
- kooperáció
- optimalizált végrehajtás
- rövid output
- kontextus figyelés

Minden üzenet magas prioritású.
"""

DEFAULT_AGENTS = [
    {
        "name": "UI_AGENT",
        "model": "DeepSeek Instant",
        "status": "idle",
        "x": 180,
        "y": 150,
        "color": "#4cc9f0",
    },
    {
        "name": "CODE_AGENT",
        "model": "DeepSeek Expert",
        "status": "working",
        "x": 420,
        "y": 120,
        "color": "#f72585",
    },
    {
        "name": "DEBUG_AGENT",
        "model": "GPT-5",
        "status": "thinking",
        "x": 320,
        "y": 300,
        "color": "#7209b7",
    },
    {
        "name": "MEMORY_AGENT",
        "model": "Claude",
        "status": "idle",
        "x": 540,
        "y": 260,
        "color": "#43aa8b",
    },
    {
        "name": "BRIDGE_AGENT",
        "model": "Cursor Agent",
        "status": "idle",
        "x": 260,
        "y": 220,
        "color": "#00ffee",
    },
]


def bridge_get(path: str) -> dict | None:
    try:
        req = urllib.request.Request(BRIDGE_URL + path)
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def bridge_post(path: str, payload: dict) -> dict | None:
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            BRIDGE_URL + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


# =========================
# NODE GRAPH
# =========================


class AgentCanvas(QFrame):
    def __init__(self, agents: list[dict]):
        super().__init__()
        self.agents = agents
        self.setMinimumSize(800, 500)
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
        self.pulse = 0

    def animate(self) -> None:
        self.pulse += 1
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0f0f13"))

        for i in range(len(self.agents) - 1):
            a = self.agents[i]
            b = self.agents[i + 1]
            pen = QPen(QColor("#2a2a35"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(int(a["x"]), int(a["y"]), int(b["x"]), int(b["y"]))

        for agent in self.agents:
            radius = 42
            glow_size = (
                radius + (self.pulse % 15)
                if agent["status"] in ("working", "thinking")
                else radius
            )
            painter.setBrush(QBrush(QColor(agent["color"])))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(agent["x"], agent["y"]), glow_size, glow_size)
            painter.setBrush(QBrush(QColor("#111")))
            painter.drawEllipse(
                QPointF(agent["x"], agent["y"]), radius - 8, radius - 8
            )
            painter.setPen(QColor("white"))
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(agent["x"] - 40, agent["y"] + 65, agent["name"])
            painter.drawText(agent["x"] - 45, agent["y"] + 80, agent["model"])


# =========================
# MAIN WINDOW
# =========================


class SwarmUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.agents = deepcopy(DEFAULT_AGENTS)
        self.setWindowTitle("Cursor Pro+ Swarm — AI Hub")
        self.resize(1280, 720)
        self.setStyleSheet(
            """
            QWidget {
                background: #111116;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background: #272733;
                border: 1px solid #444;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover { background: #3a3a4f; }
            QTextEdit {
                background: #181820;
                border: 1px solid #333;
                border-radius: 10px;
            }
            QListWidget {
                background: #181820;
                border-radius: 10px;
            }
            """
        )
        self.build_ui()
        self.bridge_timer = QTimer()
        self.bridge_timer.timeout.connect(self.poll_bridge)
        self.bridge_timer.start(6000)
        self.poll_bridge()

    def build_ui(self) -> None:
        root = QHBoxLayout()

        left = QVBoxLayout()
        title = QLabel("AI SWARM")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        left.addWidget(title)
        sub = QLabel("Bridge ↔ Cursor Agent ↔ Hub")
        sub.setStyleSheet("font-size: 11px; color: #888;")
        left.addWidget(sub)

        self.agent_list = QListWidget()
        self.refresh_agent_list()
        left.addWidget(self.agent_list)

        self.auto_mode = QCheckBox("AUTO MODE")
        self.auto_mode.setChecked(True)
        self.shared_memory = QCheckBox("SHARED MEMORY")
        self.shared_memory.setChecked(True)
        self.parallel_exec = QCheckBox("PARALLEL EXEC")
        self.parallel_exec.setChecked(True)
        self.bridge_sync = QCheckBox("BRIDGE SYNC (Cursor)")
        self.bridge_sync.setChecked(True)
        for w in (
            self.auto_mode,
            self.shared_memory,
            self.parallel_exec,
            self.bridge_sync,
        ):
            left.addWidget(w)

        self.apply_btn = QPushButton("APPLY")
        self.apply_btn.clicked.connect(self.apply_config)
        left.addWidget(self.apply_btn)

        self.hub_btn = QPushButton("Open AI Hub (browser)")
        self.hub_btn.clicked.connect(self.open_hub)
        left.addWidget(self.hub_btn)

        self.sync_btn = QPushButton("Sync Cursor → Hub")
        self.sync_btn.clicked.connect(self.sync_cursor)
        left.addWidget(self.sync_btn)

        self.prompt_box = QTextEdit()
        self.prompt_box.setPlainText(SYSTEM_PROMPT.strip())
        left.addWidget(self.prompt_box)

        self.canvas = AgentCanvas(self.agents)

        right = QVBoxLayout()
        status_title = QLabel("LIVE OUTPUT")
        status_title.setStyleSheet("font-size: 22px;")
        right.addWidget(status_title)

        self.output = QTextEdit()
        self.output.setPlainText(
            "[SYSTEM]\nSwarm initialized.\n\n"
            "[INFO]\nDeepSeek Instant active.\n"
            "DeepSeek Expert standby.\n"
            "BRIDGE_AGENT waits for AI Hub (RUN-AI-HUB.bat).\n"
        )
        right.addWidget(self.output)

        self.instant_btn = QPushButton("DeepSeek Instant")
        self.instant_btn.clicked.connect(
            lambda: self.switch_model("DeepSeek Instant")
        )
        self.expert_btn = QPushButton("DeepSeek Expert")
        self.expert_btn.clicked.connect(lambda: self.switch_model("DeepSeek Expert"))
        right.addWidget(self.instant_btn)
        right.addWidget(self.expert_btn)

        root.addLayout(left, 1)
        root.addWidget(self.canvas, 2)
        root.addLayout(right, 1)
        self.setLayout(root)

    def refresh_agent_list(self) -> None:
        self.agent_list.clear()
        for a in self.agents:
            self.agent_list.addItem(
                QListWidgetItem(f"{a['name']}  |  {a['model']}  |  {a['status']}")
            )

    def log(self, text: str) -> None:
        self.output.append(text)

    def apply_config(self) -> None:
        self.log(
            "[APPLY]\n"
            f"Auto Mode: {self.auto_mode.isChecked()}\n"
            f"Shared Memory: {self.shared_memory.isChecked()}\n"
            f"Parallel Exec: {self.parallel_exec.isChecked()}\n"
            f"Bridge Sync: {self.bridge_sync.isChecked()}\n"
        )

    def switch_model(self, model_name: str) -> None:
        for a in self.agents:
            if "UI" in a["name"]:
                a["model"] = model_name
        self.log(f"[MODEL SWITCH]\nUI_AGENT -> {model_name}\n")
        self.refresh_agent_list()
        self.canvas.update()

    def set_bridge_agent_status(self, status: str) -> None:
        for a in self.agents:
            if a["name"] == "BRIDGE_AGENT":
                a["status"] = status
                break
        self.refresh_agent_list()
        self.canvas.update()

    def poll_bridge(self) -> None:
        if not self.bridge_sync.isChecked():
            return
        st = bridge_get("/api/bridge/status")
        if not st:
            self.set_bridge_agent_status("idle")
            return
        self.set_bridge_agent_status("working")
        poll = bridge_get("/api/bridge/cursor/poll")
        if poll and poll.get("newBatches"):
            n = sum(len(b.get("messages", [])) for b in poll["newBatches"])
            self.log(f"[BRIDGE]\nSynced {n} new Cursor line(s) into Hub.\n")

    def sync_cursor(self) -> None:
        self.set_bridge_agent_status("thinking")
        poll = bridge_get("/api/bridge/cursor/poll")
        if poll is None:
            self.log("[BRIDGE]\nOffline — run RUN-AI-HUB.bat first.\n")
            self.set_bridge_agent_status("idle")
            return
        batches = poll.get("newBatches") or []
        if not batches:
            self.log("[BRIDGE]\nCursor already up to date.\n")
        else:
            n = sum(len(b.get("messages", [])) for b in batches)
            self.log(f"[BRIDGE]\nPulled {n} message(s) from Cursor Agent.\n")
        self.set_bridge_agent_status("idle")

    def open_hub(self) -> None:
        import webbrowser

        webbrowser.open(f"{BRIDGE_URL}/index.html")
        self.log("[HUB]\nOpened AI Hub in browser.\n")


def main() -> int:
    app = QApplication(sys.argv)
    window = SwarmUI()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
