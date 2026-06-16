"""
╔══════════════════════════════════════════════════════╗
║  CODEER PLATFORM  —  v3.0                            ║
║  Kobold Platform × Codeer Brain × Interface AI       ║
╠══════════════════════════════════════════════════════╣
║  Providers  : OpenRouter · Groq · Anthropic ·        ║
║               Mistral · Cohere · Together ·          ║
║               Ollama · Local (LM Studio / llama.cpp) ║
║  Brain      : Long-term memory · Boundary guard ·    ║
║               Self-improvement · Fact extraction     ║
║  Intelligence: Auto-titler · Follow-up suggester ·   ║
║               Error detector · Context advisor ·     ║
║               Smart mode selection                   ║
║                                                      ║
║  Install  : pip install pyqt6 requests               ║
║  Run      : python codeer_platform.py                ║
╚══════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import os, sys, json, time, uuid, base64, mimetypes, hashlib, re, zipfile, subprocess
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import requests
from PyQt6.QtCore    import Qt, QThread, pyqtSignal, QEvent, QUrl, QTimer, QSize
from PyQt6.QtGui     import QAction, QPixmap, QFont, QColor, QDesktopServices, QKeySequence, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QDockWidget, QTabWidget,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QColorDialog,
    QDialogButtonBox, QFormLayout, QToolButton, QSizePolicy,
    QTextEdit, QTextBrowser, QSplitter, QProgressBar, QMenu, QSystemTrayIcon,
    QStatusBar, QGroupBox, QInputDialog
)

# ══════════════════════════════════════════════════════════════════════════════
# APP IDENTITY
# ══════════════════════════════════════════════════════════════════════════════
APP_NAME    = "Codeer Platform"
APP_VERSION = "3.0"
APP_ID      = "codeer_platform"

def _app_dir() -> Path:
    base = Path(os.environ.get("APPDATA") or Path.home())
    d = base / APP_ID
    d.mkdir(parents=True, exist_ok=True)
    return d

APP_DIR  = _app_dir()
CHAT_DIR = APP_DIR / "chats"
ATT_DIR  = APP_DIR / "attachments"
MEM_DIR  = APP_DIR / "memory"
CHAT_DIR.mkdir(exist_ok=True)
ATT_DIR.mkdir(exist_ok=True)
MEM_DIR.mkdir(exist_ok=True)

SETTINGS_PATH = APP_DIR / "settings.json"
INDEX_PATH    = CHAT_DIR / "index.json"
MEMORY_PATH   = MEM_DIR  / "longterm.json"

# ══════════════════════════════════════════════════════════════════════════════
# PROVIDER REGISTRY
# ══════════════════════════════════════════════════════════════════════════════
PROVIDERS: Dict[str, Dict] = {
    "OpenRouter": {
        "base":       "https://openrouter.ai/api/v1",
        "needs_key":  True,
        "protocol":   "openai",
        "free_suffix": ":free",
        "models_url": "/models",
        "key_help":   "https://openrouter.ai/keys",
    },
    "Groq": {
        "base":       "https://api.groq.com/openai/v1",
        "needs_key":  True,
        "protocol":   "openai",
        "free_suffix": None,
        "models_url": "/models",
        "key_help":   "https://console.groq.com/",
    },
    "Anthropic": {
        "base":       "https://api.anthropic.com",
        "needs_key":  True,
        "protocol":   "anthropic",
        "free_suffix": None,
        "models_url": None,
        "key_help":   "https://console.anthropic.com/",
    },
    "Mistral": {
        "base":       "https://api.mistral.ai/v1",
        "needs_key":  True,
        "protocol":   "openai",
        "free_suffix": None,
        "models_url": "/models",
        "key_help":   "https://console.mistral.ai/",
    },
    "Cohere": {
        "base":       "https://api.cohere.com/v2",
        "needs_key":  True,
        "protocol":   "openai",
        "free_suffix": None,
        "models_url": "/models",
        "key_help":   "https://dashboard.cohere.com/",
    },
    "Together": {
        "base":       "https://api.together.xyz/v1",
        "needs_key":  True,
        "protocol":   "openai",
        "free_suffix": None,
        "models_url": "/models",
        "key_help":   "https://api.together.ai/",
    },
    "Ollama": {
        "base":       "http://localhost:11434/v1",
        "needs_key":  False,
        "protocol":   "openai",
        "free_suffix": None,
        "models_url": "/models",
        "key_help":   "https://ollama.com/",
    },
    "Local": {
        "base":       "http://127.0.0.1:1234/v1",
        "needs_key":  False,
        "protocol":   "openai",
        "free_suffix": None,
        "models_url": "/models",
        "key_help":   "https://lmstudio.ai/",
    },
}

ANTHROPIC_MODELS = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]

FALLBACK_MODELS: Dict[str, List[str]] = {
    "OpenRouter": [
        "deepseek/deepseek-chat:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "qwen/qwen-2.5-7b-instruct:free",
    ],
    "Groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "Anthropic": ANTHROPIC_MODELS,
    "Mistral": [
        "mistral-large-latest",
        "mistral-small-latest",
        "codestral-latest",
    ],
    "Cohere": ["command-r-plus", "command-r"],
    "Together": [
        "meta-llama/Llama-3-70b-chat-hf",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
    ],
    "Ollama": ["deepseek-coder-v2:16b", "llama3:latest", "mistral:latest"],
    "Local":  ["local-model"],
}

HELP_LINKS = {
    "OpenRouter keys":       "https://openrouter.ai/keys",
    "OpenRouter models":     "https://openrouter.ai/models",
    "OpenRouter privacy":    "https://openrouter.ai/settings/privacy",
    "Groq console":          "https://console.groq.com/",
    "Anthropic console":     "https://console.anthropic.com/",
    "Mistral console":       "https://console.mistral.ai/",
    "Together AI":           "https://api.together.ai/",
    "Ollama":                "https://ollama.com/",
    "LM Studio":             "https://lmstudio.ai/",
}

# ══════════════════════════════════════════════════════════════════════════════
# CODEER BRAIN — BOUNDARY GUARD
# ══════════════════════════════════════════════════════════════════════════════
KNOWN_DOMAINS = [
    "python","javascript","typescript","c","c++","c#","java","rust","go","lua","php","ruby","swift","kotlin",
    "html","css","sql","bash","powershell","shader","glsl","hlsl",
    "algorithms","data structures","design patterns","architecture",
    "game development","unity","unreal","pygame","godot","three.js","webgl","canvas",
    "software engineering","system design","microservices","api","rest","graphql","websockets",
    "databases","orm","queries","indexing","mongodb","postgres","sqlite","redis",
    "performance","optimization","profiling","memory","multithreading","async",
    "debugging","testing","refactoring","code review","linting",
    "git","version control","ci/cd","devops","docker","kubernetes",
    "web development","backend","frontend","fullstack","react","vue","svelte","node",
    "machine learning","neural networks","numpy","pandas","pytorch","tensorflow",
    "security","cryptography","authentication","oauth","jwt",
    "electron","tauri","desktop apps","mobile","android","ios",
    "regex","parsing","compilers","interpreters","asm",
    "audio","dsp","synthesis","web audio api",
    "file system","os","linux","windows","processes","networking","sockets",
    "ai","llm","prompt","claude","gpt","gemini","mistral",
]

OFF_TOPIC_KW = [
    "recipe","cooking","food","weather","sports","celebrity",
    "relationship","love","marriage","mental health","therapy",
    "politics","election","religion","god","church",
    "stock market","invest in","should i buy","crypto price",
    "symptoms","disease","medicine","doctor","medical diagnosis",
]

CODING_SIGNALS = [
    "function","code","program","script","api","library","algorithm",
    "implement","build","develop","debug","error","bug","class","method","variable",
    "syntax","runtime","compile","deploy","test","refactor","optimize",
]

CODE_PATTERNS = [
    r'\bdef\b|\bclass\b|\bfunction\b|\breturn\b',
    r'\bimport\b|\brequire\b|\binclude\b',
    r'[{}\[\]();]{2,}',
    r'\b\w+\(\)',
    r'```',
    r'\berror\b|\bbug\b|\bdebug\b|\bfix\b|\bcrash\b',
    r'\bwrite\b.*\bcode\b|\bbuild\b.*\bapp\b|\bcreate\b.*\bscript\b',
    r'==|!=|<=|>=|=>|->|\|\|',
]

def boundary_check(query: str, coding_mode: bool = True) -> Tuple[bool, str]:
    """Returns (in_domain, reason). In GENERAL mode always True."""
    if not coding_mode:
        return True, "general mode"
    q = query.lower()
    for kw in OFF_TOPIC_KW:
        if kw in q and not any(c in q for c in CODING_SIGNALS):
            return False, f"off-topic: {kw}"
    for d in KNOWN_DOMAINS:
        if d in q:
            return True, f"domain: {d}"
    if any(re.search(p, q) for p in CODE_PATTERNS):
        return True, "code pattern"
    return True, "benefit of doubt"

BOUNDARY_MSG = (
    "That's outside my specialty as a coding agent. "
    "I focus on software engineering, programming, and technical development. "
    "Switch to General mode (top bar) if you want unrestricted conversation."
)

# ══════════════════════════════════════════════════════════════════════════════
# CODEER BRAIN — LONG-TERM MEMORY
# ══════════════════════════════════════════════════════════════════════════════
class LongTermMemory:
    MAX_FACTS = 80
    MAX_CORRS = 30

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        try:
            if MEMORY_PATH.exists():
                return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "user_name": None,
            "preferred_language": None,
            "preferred_style": "clean, well-commented, production-ready",
            "projects": {},
            "facts": [],
            "corrections_summary": [],
            "total_sessions": 0,
            "total_turns": 0,
        }

    def _save(self):
        try:
            MEMORY_PATH.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass

    def remember_fact(self, fact: str):
        if fact and fact not in self._data["facts"]:
            self._data["facts"].append(fact)
            self._data["facts"] = self._data["facts"][-self.MAX_FACTS:]
            self._save()

    def remember_project(self, name: str, desc: str, lang: str = ""):
        self._data["projects"][name.lower()] = {
            "name": name, "description": desc, "language": lang,
            "last_seen": time.strftime("%Y-%m-%d"),
        }
        self._save()

    def set_user_name(self, name: str):
        self._data["user_name"] = name
        self._save()

    def set_preferred_language(self, lang: str):
        self._data["preferred_language"] = lang
        self._save()

    def log_correction(self, learned: str):
        if learned:
            self._data["corrections_summary"].append(learned)
            self._data["corrections_summary"] = self._data["corrections_summary"][-self.MAX_CORRS:]
            self._save()

    def log_session(self, turns: int):
        self._data["total_sessions"] += 1
        self._data["total_turns"] += turns
        self._save()

    def build_context(self) -> str:
        lines = []
        if self._data["user_name"]:
            lines.append(f"User's name: {self._data['user_name']}")
        if self._data["preferred_language"]:
            lines.append(f"Preferred language: {self._data['preferred_language']}")
        if self._data["preferred_style"]:
            lines.append(f"Code style: {self._data['preferred_style']}")
        if self._data["projects"]:
            for p in list(self._data["projects"].values())[-5:]:
                lines.append(f"Project '{p['name']}': {p['description'][:80]}"
                             + (f" ({p['language']})" if p["language"] else ""))
        for f in self._data["facts"][-10:]:
            lines.append(f"Fact: {f}")
        for c in self._data["corrections_summary"][-5:]:
            lines.append(f"Learned: {c}")
        lines.append(f"Stats: {self._data['total_sessions']} sessions / {self._data['total_turns']} turns")
        return "\n".join(lines)

    def get_stats(self) -> dict:
        return {
            "sessions": self._data["total_sessions"],
            "turns": self._data["total_turns"],
            "facts": len(self._data["facts"]),
            "projects": len(self._data["projects"]),
            "corrections": len(self._data["corrections_summary"]),
            "user_name": self._data.get("user_name"),
        }

    def get_all(self) -> dict:
        return dict(self._data)

    def clear(self):
        self._data = {
            "user_name": None, "preferred_language": None,
            "preferred_style": "clean, well-commented, production-ready",
            "projects": {}, "facts": [], "corrections_summary": [],
            "total_sessions": self._data.get("total_sessions", 0),
            "total_turns":   self._data.get("total_turns", 0),
        }
        self._save()


memory = LongTermMemory()

# ══════════════════════════════════════════════════════════════════════════════
# CODEER BRAIN — SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════════════════
MODE_PROMPTS = {
    "CODING": """You are Codeer, an elite AI coding agent operating at GitHub Copilot / Claude Sonnet quality.
You are a deeply expert software engineer, game developer, and systems programmer.
RULES:
1. Complete code only — never use placeholders, TODOs, or "..." stubs.
2. Every I/O operation has error handling (try/except or equivalent).
3. Non-obvious logic always has a comment. Complex functions have docstrings.
4. Follow language conventions (PEP 8, ESLint, etc.).
5. Use modern idioms (f-strings, async/await, destructuring, etc.).
6. Never hallucinate APIs — if unsure, say so.
For debugging: Root cause → Fix → Why it happened.
For architecture: Give a concrete recommendation with a code skeleton.
For code review: Critical → Warning → Suggestion severity ordering.""",

    "GENERAL": """You are a helpful, knowledgeable AI assistant.
You are direct, precise, and friendly. You think carefully before answering.
You adapt your communication style to the user's level of expertise.
You acknowledge uncertainty rather than guessing.""",

    "REASONING": """You are an expert reasoning and analysis AI.
When tackling problems:
1. Break down the problem into components.
2. Consider multiple approaches and their trade-offs.
3. Show your reasoning chain step by step.
4. Arrive at a confident conclusion with justification.
5. Flag any assumptions you make.
Think like a senior consultant: structured, rigorous, evidence-based.""",

    "PLAN": """You are a strategic planning and project management AI.
When asked to plan:
1. Define clear goals and success criteria first.
2. Break work into phases with concrete deliverables.
3. Identify dependencies and critical path.
4. Flag risks and propose mitigations.
5. Provide a realistic timeline estimate.
Output structured plans with checkboxes where appropriate.""",

    "CREATIVE": """You are a creative AI collaborator.
You approach creative tasks with originality, depth, and attention to craft.
You help brainstorm, draft, iterate, and refine.
You offer concrete creative choices rather than vague suggestions.
You match the tone and style the user is aiming for.""",
}

SUBMODE_EXTRAS = {
    "(none)":  "",
    "Python":  "Focus on Python idioms, type hints, and PEP 8. Use modern Python 3.10+ features.",
    "JS/TS":   "Prefer TypeScript. Use ESM imports, async/await, modern array methods.",
    "C++":     "Focus on C++17/20. Use RAII, smart pointers, and STL correctly.",
    "C#":      "Target .NET 8+. Use nullable reference types, records, and pattern matching.",
    "Rust":    "Idiomatic Rust: ownership, liflers, no unsafe unless necessary, use cargo idioms.",
    "Go":      "Idiomatic Go: error wrapping, goroutines, context cancellation, clean interfaces.",
    "Godot":   "Use GDScript 2.0 with typed variables. Focus on Godot 4.x patterns.",
    "Unity":   "Focus on C# in Unity 2022+. Use SerializeField, UniTask, ScriptableObjects.",
    "Unreal":  "UE5 C++ and Blueprint patterns. Use GameplayAbilitySystem where relevant.",
    "React":   "Functional components, hooks, no class components. Prefer Vite + TypeScript.",
    "Vue":     "Vue 3 Composition API with <script setup> syntax.",
    "Shader":  "GLSL/HLSL focus. Explain math behind effects. Provide vertex+fragment pairs.",
}

LANG_INSTRUCTIONS = {
    "Auto":    "",
    "English": "Always reply in English.",
    "Magyar":  "Mindig magyarul válaszolj.",
    "Slovak":  "Vždy odpovedaj v slovenčine.",
    "German":  "Antworte immer auf Deutsch.",
    "Japanese": "常に日本語で返答してください。",
    "French":  "Répondez toujours en français.",
}

MEMORY_EXTRACTION_PROMPT = """Extract memorable facts from this conversation turn. Return ONLY valid JSON, no markdown fences.

JSON schema:
{{"facts":["..."],"project":{{"name":"...","description":"...","language":"..."}},"user_name":null,"preferred_language":null,"corrections":["..."]}}

If nothing to extract: {{"facts":[],"project":null,"user_name":null,"preferred_language":null,"corrections":[]}}

Conversation:
User: {user_msg}
Agent: {agent_msg}"""

TITLE_PROMPT = """Generate a short chat title (max 6 words) for this first message. Return ONLY the title, no quotes, no punctuation.

Message: {msg}"""

FOLLOWUP_PROMPT = """Based on this coding conversation, suggest 3 natural follow-up questions the user might want to ask next. 
Return ONLY a JSON array of 3 strings. No markdown fences.
Example: ["How do I test this?", "Can you add type hints?", "What about error handling?"]

Last exchange:
User: {user_msg}
Agent: {agent_msg}"""

def build_system_prompt(mode: str, submode: str, lang: str, mem_ctx: str) -> str:
    base = MODE_PROMPTS.get(mode, MODE_PROMPTS["GENERAL"])
    sub  = SUBMODE_EXTRAS.get(submode, "")
    lng  = LANG_INSTRUCTIONS.get(lang, "")
    mem  = f"\n\n## What I Remember\n{mem_ctx}" if mem_ctx else ""
    parts = [base]
    if sub:  parts.append(f"\nSubmode focus: {sub}")
    if lng:  parts.append(f"\n{lng}")
    parts.append(mem)
    return "\n".join(parts).strip()

# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Settings:
    provider:       str   = "OpenRouter"
    base_url:       str   = PROVIDERS["OpenRouter"]["base"]
    model:          str   = ""
    free_only:      bool  = True
    mode:           str   = "CODING"
    submode:        str   = "(none)"
    reply_lang:     str   = "Auto"
    boundary_guard: bool  = True
    self_improve:   bool  = True
    auto_continue:  bool  = True
    auto_save:      bool  = True
    auto_title:     bool  = True
    show_followups: bool  = True
    max_tokens:     int   = 2048
    temperature:    float = 0.18
    top_p:          float = 1.0
    eur_per_1k:     float = 0.002

    # Keys per provider
    key_openrouter: str = ""
    key_groq:       str = ""
    key_anthropic:  str = ""
    key_mistral:    str = ""
    key_cohere:     str = ""
    key_together:   str = ""
    key_local:      str = ""
    remember_keys:  bool = True

    # Theme
    bg:              str = "#0d0f14"
    panel:           str = "#131620"
    bubble_user:     str = "#1e2235"
    bubble_asst:     str = "#191c2a"
    text_color:      str = "#e8eaf6"
    accent:          str = "#7c6af5"
    accent2:         str = "#5be5c3"
    code_bg:         str = "#0a0c14"
    font_family:     str = "Segoe UI"
    code_font:       str = "Consolas"
    font_size:       int = 13


def _load_settings() -> Settings:
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        return Settings(**{k: v for k, v in raw.items() if k in Settings.__dataclass_fields__})
    except Exception:
        return Settings()

def _save_settings(s: Settings):
    SETTINGS_PATH.write_text(json.dumps(asdict(s), indent=2, ensure_ascii=False), encoding="utf-8")

def _get_api_key(s: Settings) -> str:
    keys = {
        "OpenRouter": s.key_openrouter,
        "Groq":       s.key_groq,
        "Anthropic":  s.key_anthropic,
        "Mistral":    s.key_mistral,
        "Cohere":     s.key_cohere,
        "Together":   s.key_together,
        "Local":      s.key_local,
        "Ollama":     "",
    }
    return keys.get(s.provider, "")

# ══════════════════════════════════════════════════════════════════════════════
# CHAT STORAGE
# ══════════════════════════════════════════════════════════════════════════════
def _now() -> int:
    return int(time.time())

def new_chat(title: str = "New chat", temp: bool = False) -> dict:
    return {
        "id": uuid.uuid4().hex, "title": title,
        "created": _now(), "updated": _now(),
        "temporary": temp,
        "messages": [],
        "pinned_codes": [], "marked_phrases": [], "saved_texts": [],
        "stats": {
            "messages": 0, "answers": 0,
            "approx_tokens": 0, "approx_eur": 0.0,
            "minutes": 0, "provider": "", "model": "",
        },
    }

def _chat_path(cid: str) -> Path:
    return CHAT_DIR / f"{cid}.json"

def save_chat(chat: dict):
    if chat.get("temporary"): return
    chat["updated"] = _now()
    p = _chat_path(chat["id"])
    tmp = str(p) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(chat, f, ensure_ascii=False, indent=2)
    os.replace(tmp, str(p))

def load_chat_file(cid: str) -> Optional[dict]:
    p = _chat_path(cid)
    if not p.exists(): return None
    try: return json.loads(p.read_text(encoding="utf-8"))
    except: return None

def _load_index() -> dict:
    try: return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except: return {"chats": []}

def _save_index(idx: dict):
    tmp = str(INDEX_PATH) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
    os.replace(tmp, str(INDEX_PATH))

def add_to_index(chat: dict):
    if chat.get("temporary"): return
    idx = _load_index()
    chats = idx.get("chats", [])
    for c in chats:
        if c.get("id") == chat["id"]:
            c.update({"title": chat["title"], "updated": chat["updated"], "created": chat["created"]})
            break
    else:
        chats.append({"id": chat["id"], "title": chat["title"],
                      "created": chat["created"], "updated": chat["updated"]})
    chats.sort(key=lambda x: x.get("updated", 0), reverse=True)
    idx["chats"] = chats
    _save_index(idx)

def remove_from_index(cid: str):
    idx = _load_index()
    idx["chats"] = [c for c in idx.get("chats", []) if c.get("id") != cid]
    _save_index(idx)

# ══════════════════════════════════════════════════════════════════════════════
# UTILS
# ══════════════════════════════════════════════════════════════════════════════
def _html_esc(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def _approx_tokens(text: str) -> int:
    return max(1, len(text or "") // 4)

def _sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()

def _detect_img_mime(b: bytes) -> str:
    if b.startswith(b"\x89PNG\r\n\x1a\n"): return "image/png"
    if b.startswith(b"\xff\xd8"):          return "image/jpeg"
    if b[:6] in (b"GIF87a", b"GIF89a"):   return "image/gif"
    if b.startswith(b"RIFF") and b[8:12] == b"WEBP": return "image/webp"
    return "application/octet-stream"

def md_to_html(text: str, s: Settings) -> str:
    text = text or ""
    esc = _html_esc(text)

    # Fenced code blocks
    def repl_code(m):
        lang = _html_esc((m.group(1) or "").strip())
        code = m.group(2) or ""
        lang_tag = f'<div style="font-size:11px;color:#7c6af5;margin-bottom:4px;font-family:{s.code_font};">[{lang}]</div>' if lang else ""
        return (
            f'<div style="background:{s.code_bg};border:1px solid #252840;border-radius:8px;'
            f'padding:12px;margin:8px 0;overflow-x:auto;">'
            f'{lang_tag}<pre style="margin:0;white-space:pre-wrap;'
            f'font-family:{s.code_font};font-size:12px;color:#c8d3f5;">{_html_esc(code)}</pre></div>'
        )

    esc = re.sub(r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```", repl_code, esc, flags=re.S)

    # Inline code
    esc = re.sub(r"`([^`]+)`", lambda m:
        f'<code style="background:{s.code_bg};color:#5be5c3;padding:1px 5px;'
        f'border-radius:4px;font-family:{s.code_font};font-size:11px;">{_html_esc(m.group(1))}</code>', esc)

    # Bold
    esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
    # Italic
    esc = re.sub(r"\*(.+?)\*", r"<em>\1</em>", esc)
    # Headers
    esc = re.sub(r"^### (.+)$", r'<h4 style="color:#7c6af5;margin:8px 0 4px;">\1</h4>', esc, flags=re.M)
    esc = re.sub(r"^## (.+)$",  r'<h3 style="color:#5be5c3;margin:10px 0 5px;">\1</h3>', esc, flags=re.M)
    esc = re.sub(r"^# (.+)$",   r'<h2 style="color:#e8eaf6;margin:12px 0 6px;">\1</h2>', esc, flags=re.M)
    # Bullet lists
    esc = re.sub(r"^[-•]\s+(.+)$", r'<div style="padding-left:16px;">• \1</div>', esc, flags=re.M)
    # Numbered lists
    esc = re.sub(r"^\d+\.\s+(.+)$", r'<div style="padding-left:16px;">\g<0></div>', esc, flags=re.M)

    esc = esc.replace("\n", "<br/>")
    return (f'<div style="font-family:{s.font_family};font-size:{s.font_size}px;'
            f'color:{s.text_color};line-height:1.6;">{esc}</div>')

# ══════════════════════════════════════════════════════════════════════════════
# WORKER THREADS
# ══════════════════════════════════════════════════════════════════════════════
class ModelsWorker(QThread):
    ok   = pyqtSignal(list)
    fail = pyqtSignal(str)

    def __init__(self, provider: str, base_url: str, api_key: str, free_only: bool):
        super().__init__()
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.free_only = free_only

    def run(self):
        # Anthropic: static model list
        if self.provider == "Anthropic":
            self.ok.emit(ANTHROPIC_MODELS)
            return

        models_url = PROVIDERS.get(self.provider, {}).get("models_url")
        if not models_url:
            fallback = FALLBACK_MODELS.get(self.provider, [])
            self.ok.emit(fallback)
            return

        try:
            url = self.base_url + models_url
            headers = {"User-Agent": APP_NAME}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}")
            j = r.json()
            data = j.get("data") or j.get("models") or []
            ids = sorted({str(m.get("id") or m.get("name")) for m in data if m.get("id") or m.get("name")})
            if not ids:
                raise RuntimeError("No models returned")
            free_sfx = PROVIDERS.get(self.provider, {}).get("free_suffix")
            if self.free_only and free_sfx:
                free_ids = [x for x in ids if x.endswith(free_sfx)]
                ids = free_ids if free_ids else ids
            self.ok.emit(ids)
        except Exception as e:
            fallback = FALLBACK_MODELS.get(self.provider, [])
            if fallback:
                self.ok.emit(fallback)
            else:
                self.fail.emit(str(e))


class ChatWorker(QThread):
    delta = pyqtSignal(str)
    done  = pyqtSignal(dict)
    fail  = pyqtSignal(str)

    def __init__(self, provider: str, base_url: str, api_key: str, payload: dict):
        super().__init__()
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.payload  = payload
        self._stop    = False

    def stop(self): self._stop = True

    def run(self):
        try:
            if self.provider == "Anthropic":
                self._run_anthropic()
            else:
                self._run_openai()
        except Exception as e:
            self.fail.emit(str(e))

    def _run_openai(self):
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json", "User-Agent": APP_NAME}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.provider == "OpenRouter":
            headers["X-Title"]      = APP_NAME
            headers["HTTP-Referer"] = "https://localhost"

        full = ""; finish = None; usage = {}
        with requests.post(url, headers=headers, json=self.payload, stream=True, timeout=300) as r:
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}\n{r.text[:2000]}")
            for raw in r.iter_lines(decode_unicode=True):
                if self._stop: break
                if not raw or not raw.strip().startswith("data:"): continue
                data = raw.strip()[5:].strip()
                if data == "[DONE]": break
                try:
                    chunk = json.loads(data)
                    ch0 = (chunk.get("choices") or [{}])[0]
                    fr = ch0.get("finish_reason")
                    if fr: finish = fr
                    if isinstance(chunk.get("usage"), dict):
                        usage = chunk["usage"]
                    delta = (ch0.get("delta") or {}).get("content") or ""
                    if delta:
                        full += delta
                        self.delta.emit(delta)
                except Exception: continue
        self.done.emit({"content": full, "finish_reason": finish or "stop", "usage": usage})

    def _run_anthropic(self):
        """Native Anthropic Messages API (SSE streaming)."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type":            "application/json",
            "x-api-key":               self.api_key,
            "anthropic-version":       "2023-06-01",
            "anthropic-beta":          "messages-2023-12-15",
        }
        # Convert OpenAI payload → Anthropic format
        msgs_in = self.payload.get("messages", [])
        system_parts = [m["content"] for m in msgs_in if m["role"] == "system"]
        conv = [m for m in msgs_in if m["role"] in ("user", "assistant")]
        body = {
            "model":      self.payload["model"],
            "max_tokens": self.payload.get("max_tokens", 2048),
            "stream":     True,
            "messages":   conv,
        }
        if system_parts:
            body["system"] = "\n\n".join(system_parts)
        if "temperature" in self.payload:
            body["temperature"] = self.payload["temperature"]

        full = ""; finish = None
        with requests.post(url, headers=headers, json=body, stream=True, timeout=300) as r:
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}\n{r.text[:2000]}")
            for raw in r.iter_lines(decode_unicode=True):
                if self._stop: break
                if not raw: continue
                line = raw.strip()
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data == "[DONE]": break
                    try:
                        ev = json.loads(data)
                        et = ev.get("type", "")
                        if et == "content_block_delta":
                            delta = ev.get("delta", {}).get("text", "")
                            if delta:
                                full += delta
                                self.delta.emit(delta)
                        elif et == "message_delta":
                            finish = ev.get("delta", {}).get("stop_reason")
                    except Exception: continue
        self.done.emit({"content": full, "finish_reason": finish or "stop", "usage": {}})


class BackgroundWorker(QThread):
    """For memory extraction, title generation, follow-up suggestion."""
    result = pyqtSignal(str, object)  # (task_type, result)

    def __init__(self, task: str, provider: str, base_url: str, api_key: str, model: str, prompt: str):
        super().__init__()
        self.task = task
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.model    = model
        self.prompt   = prompt

    def run(self):
        try:
            resp = self._call()
            self.result.emit(self.task, resp)
        except Exception:
            pass  # background tasks never crash UI

    def _call(self) -> str:
        if self.provider == "Anthropic":
            return self._call_anthropic()
        else:
            return self._call_openai()

    def _call_openai(self) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json", "User-Agent": APP_NAME}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": self.prompt}],
            "max_tokens": 512,
            "temperature": 0.05,
            "stream": False,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _call_anthropic(self) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         self.api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": self.prompt}],
            "max_tokens": 512,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["content"][0]["text"]

# ══════════════════════════════════════════════════════════════════════════════
# UI WIDGETS
# ══════════════════════════════════════════════════════════════════════════════
class ClickLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton: self.clicked.emit()
        super().mousePressEvent(e)


class PromptEdit(QTextEdit):
    sendRequested         = pyqtSignal()
    pasteImageRequested   = pyqtSignal()
    filesDropped          = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def keyPressEvent(self, e):
        if (e.modifiers() & Qt.KeyboardModifier.ControlModifier) and e.key() == Qt.Key.Key_V:
            self.pasteImageRequested.emit()
            return
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.insertPlainText("\n"); return
            cur = self.textCursor(); pos = cur.position(); txt = self.toPlainText()
            if pos > 0 and txt[pos - 1] == " ":
                self.insertPlainText("\n"); return
            self.sendRequested.emit(); return
        super().keyPressEvent(e)

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls() or ev.mimeData().hasImage():
            ev.acceptProposedAction()
        else: super().dragEnterEvent(ev)

    def dropEvent(self, ev):
        paths = []
        if ev.mimeData().hasUrls():
            for u in ev.mimeData().urls():
                p = u.toLocalFile()
                if p and os.path.exists(p): paths.append(p)
        if paths: self.filesDropped.emit(paths); ev.acceptProposedAction(); return
        super().dropEvent(ev)


class MessageBubble(QFrame):
    def __init__(self, role: str, ts: int, s: Settings, msg_id: str):
        super().__init__()
        self.msg_id = msg_id
        self.role   = role
        self._streaming = False
        self.s = s
        obj = {"user": "BubbleUser", "assistant": "BubbleAsst", "system": "BubbleSys"}.get(role, "BubbleSys")
        self.setObjectName(obj)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(4)

        # Role + timestamp header
        role_icon = {"user": "▶", "assistant": "⚡", "system": "⚙"}.get(role, "•")
        ts_str = time.strftime("%H:%M:%S", time.localtime(ts))
        hdr = QLabel(f"{role_icon} {role.upper()}  {ts_str}")
        hdr.setObjectName("BubbleHeader")
        lay.addWidget(hdr)

        self.text = QTextBrowser()
        self.text.setOpenExternalLinks(True)
        self.text.setOpenLinks(False)
        self.text.setObjectName("BubbleText")
        self.text.setFrameShape(QFrame.Shape.NoFrame)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.text.setFont(QFont(s.font_family, s.font_size))
        lay.addWidget(self.text)

        self.img_wrap = QWidget()
        self.img_lay = QHBoxLayout(self.img_wrap)
        self.img_lay.setContentsMargins(0, 4, 0, 0)
        self.img_lay.setSpacing(8)
        lay.addWidget(self.img_wrap)
        self.img_wrap.hide()

    def set_html(self, html: str):
        self._streaming = False
        self.text.setHtml(html)
        self._resize()

    def set_plain(self, txt: str):
        self._streaming = True
        self.text.setPlainText(txt)
        self._resize()

    def append_delta(self, d: str):
        if not self._streaming: self.set_plain("")
        self.text.moveCursor(self.text.textCursor().MoveOperation.End)
        self.text.insertPlainText(d)
        self._resize()

    def add_image(self, path: str):
        if not os.path.exists(path): return
        self.img_wrap.show()
        lbl = ClickLabel()
        pix = QPixmap(path)
        if not pix.isNull():
            lbl.setPixmap(pix.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
        else: lbl.setText(os.path.basename(path))
        lbl.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(path)))
        self.img_lay.addWidget(lbl)

    def _resize(self):
        h = int(self.text.document().size().height()) + 12
        self.text.setFixedHeight(max(h, 24))


class ChatArea(QWidget):
    def __init__(self, s: Settings):
        super().__init__()
        self.s = s
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.v = QVBoxLayout(self.container)
        self.v.setContentsMargins(12, 12, 12, 24)
        self.v.setSpacing(8)
        self.v.addStretch(1)

        self.scroll.setWidget(self.container)
        outer.addWidget(self.scroll)

        self.bubbles: List[MessageBubble] = []
        self.by_id:   Dict[str, MessageBubble] = {}
        self._stream_id: Optional[str] = None

    def clear(self):
        for b in self.bubbles: b.setParent(None)
        self.bubbles = []
        self.by_id   = {}
        self._stream_id = None
        while self.v.count():
            item = self.v.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.v.addStretch(1)

    def add_bubble(self, role: str, html: str, ts: int, msg_id: str, attachments: List[dict] = None) -> MessageBubble:
        b = MessageBubble(role, ts, self.s, msg_id)
        b.set_html(html)
        self.v.insertWidget(self.v.count() - 1, b)
        self.bubbles.append(b)
        self.by_id[msg_id] = b
        if attachments:
            for a in attachments:
                if a.get("type") == "image": b.add_image(a.get("path",""))
        self.scroll_bottom()
        return b

    def start_stream(self, ts: int, msg_id: str) -> MessageBubble:
        b = self.add_bubble("assistant", "", ts, msg_id)
        b.set_plain("")
        self._stream_id = msg_id
        return b

    def append_stream(self, d: str):
        if not self._stream_id: return
        b = self.by_id.get(self._stream_id)
        if b: b.append_delta(d); self.scroll_bottom()

    def finalize_stream(self, msg_id: str, html: str):
        b = self.by_id.get(msg_id)
        if b: b.set_html(html)
        if self._stream_id == msg_id: self._stream_id = None
        self.scroll_bottom()

    def scroll_bottom(self):
        QTimer.singleShot(30, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))

    def scroll_to(self, msg_id: str):
        b = self.by_id.get(msg_id)
        if b: self.scroll.ensureWidgetVisible(b, 0, 40)


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class SettingsDialog(QDialog):
    def __init__(self, parent, s: Settings):
        super().__init__(parent)
        self.setWindowTitle("Codeer Platform — Settings")
        self.setMinimumWidth(700)
        self.s = s
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        tabs = QTabWidget()

        # ── Provider tab ──
        prov_w = QWidget()
        pf = QFormLayout(prov_w)

        self.provider = QComboBox()
        self.provider.addItems(list(PROVIDERS.keys()))
        self.provider.setCurrentText(self.s.provider)
        self.provider.currentTextChanged.connect(self._on_provider)

        self.base_url = QLineEdit(self.s.base_url)

        self.free_only = QCheckBox("Free only (OpenRouter :free suffix)")
        self.free_only.setChecked(self.s.free_only)

        pf.addRow("Provider:", self.provider)
        pf.addRow("Base URL:", self.base_url)
        pf.addRow("", self.free_only)

        keys_g = QGroupBox("API Keys")
        kf = QFormLayout(keys_g)
        self.k_or   = self._key_field(self.s.key_openrouter)
        self.k_groq = self._key_field(self.s.key_groq)
        self.k_ant  = self._key_field(self.s.key_anthropic)
        self.k_mis  = self._key_field(self.s.key_mistral)
        self.k_coh  = self._key_field(self.s.key_cohere)
        self.k_tog  = self._key_field(self.s.key_together)
        kf.addRow("OpenRouter:", self.k_or)
        kf.addRow("Groq:", self.k_groq)
        kf.addRow("Anthropic:", self.k_ant)
        kf.addRow("Mistral:", self.k_mis)
        kf.addRow("Cohere:", self.k_coh)
        kf.addRow("Together:", self.k_tog)
        self.remember = QCheckBox("Remember keys (stored in settings.json)")
        self.remember.setChecked(self.s.remember_keys)
        kf.addRow("", self.remember)
        pf.addRow(keys_g)

        tabs.addTab(prov_w, "Providers")

        # ── Agent tab ──
        agent_w = QWidget()
        af = QFormLayout(agent_w)

        self.boundary = QCheckBox("Enable boundary guard (coding-only filter in CODING mode)")
        self.boundary.setChecked(self.s.boundary_guard)
        self.self_impr = QCheckBox("Self-improvement (extract facts after each response)")
        self.self_impr.setChecked(self.s.self_improve)
        self.auto_cont = QCheckBox("Auto-continue if response cut (finish_reason=length)")
        self.auto_cont.setChecked(self.s.auto_continue)
        self.auto_save = QCheckBox("Auto-save chats after each message")
        self.auto_save.setChecked(self.s.auto_save)
        self.auto_title = QCheckBox("Auto-generate chat titles from first message")
        self.auto_title.setChecked(self.s.auto_title)
        self.show_fu = QCheckBox("Show follow-up suggestions after each response")
        self.show_fu.setChecked(self.s.show_followups)

        self.reply_lang = QComboBox()
        self.reply_lang.addItems(list(LANG_INSTRUCTIONS.keys()))
        self.reply_lang.setCurrentText(self.s.reply_lang)

        af.addRow("", self.boundary)
        af.addRow("", self.self_impr)
        af.addRow("", self.auto_cont)
        af.addRow("", self.auto_save)
        af.addRow("", self.auto_title)
        af.addRow("", self.show_fu)
        af.addRow("Reply language:", self.reply_lang)

        tabs.addTab(agent_w, "Agent Brain")

        # ── Generation tab ──
        gen_w = QWidget()
        gf = QFormLayout(gen_w)

        self.max_tokens = QSpinBox(); self.max_tokens.setRange(16, 32768)
        self.max_tokens.setValue(self.s.max_tokens)
        self.temp = QDoubleSpinBox(); self.temp.setRange(0.0, 2.0); self.temp.setSingleStep(0.01)
        self.temp.setValue(self.s.temperature); self.temp.setDecimals(2)
        self.top_p = QDoubleSpinBox(); self.top_p.setRange(0.0, 1.0); self.top_p.setSingleStep(0.05)
        self.top_p.setValue(self.s.top_p)
        self.eur = QDoubleSpinBox(); self.eur.setRange(0.0, 10.0); self.eur.setSingleStep(0.001)
        self.eur.setDecimals(6); self.eur.setValue(self.s.eur_per_1k)

        gf.addRow("Max tokens:", self.max_tokens)
        gf.addRow("Temperature:", self.temp)
        gf.addRow("Top-p:", self.top_p)
        gf.addRow("EUR/1k tokens:", self.eur)
        tabs.addTab(gen_w, "Generation")

        # ── Theme tab ──
        theme_w = QWidget()
        tf = QFormLayout(theme_w)

        def cr(label, val, attr):
            row = QHBoxLayout()
            le = QLineEdit(val); le.setObjectName(attr)
            btn = QPushButton("Pick"); btn.setFixedWidth(60)
            def pick(le=le, label=label):
                c = QColorDialog.getColor(QColor(le.text()), self, label)
                if c.isValid(): le.setText(c.name())
            btn.clicked.connect(pick)
            row.addWidget(le); row.addWidget(btn)
            w = QWidget(); w.setLayout(row); return le, w

        self.c_bg,     w_bg     = cr("Background",     self.s.bg,          "c_bg")
        self.c_panel,  w_panel  = cr("Panel",          self.s.panel,       "c_panel")
        self.c_buser,  w_buser  = cr("Bubble user",    self.s.bubble_user, "c_buser")
        self.c_basst,  w_basst  = cr("Bubble asst",    self.s.bubble_asst, "c_basst")
        self.c_text,   w_text   = cr("Text",           self.s.text_color,  "c_text")
        self.c_accent, w_accent = cr("Accent",         self.s.accent,      "c_accent")
        self.c_code,   w_code   = cr("Code bg",        self.s.code_bg,     "c_code")

        self.font      = QLineEdit(self.s.font_family)
        self.code_font = QLineEdit(self.s.code_font)
        self.font_size = QSpinBox(); self.font_size.setRange(8,24); self.font_size.setValue(self.s.font_size)

        tf.addRow("Background:",    w_bg)
        tf.addRow("Panel:",         w_panel)
        tf.addRow("Bubble user:",   w_buser)
        tf.addRow("Bubble asst:",   w_basst)
        tf.addRow("Text:",          w_text)
        tf.addRow("Accent:",        w_accent)
        tf.addRow("Code bg:",       w_code)
        tf.addRow("UI font:",       self.font)
        tf.addRow("Code font:",     self.code_font)
        tf.addRow("Font size:",     self.font_size)
        tabs.addTab(theme_w, "Theme")

        lay.addWidget(tabs)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _key_field(self, val: str) -> QLineEdit:
        f = QLineEdit(val)
        f.setEchoMode(QLineEdit.EchoMode.Password)
        return f

    def _on_provider(self, prov: str):
        info = PROVIDERS.get(prov, {})
        self.base_url.setText(info.get("base",""))

    def apply(self):
        s = self.s
        s.provider  = self.provider.currentText()
        s.base_url  = self.base_url.text().strip()
        s.free_only = self.free_only.isChecked()

        if self.remember.isChecked():
            s.key_openrouter = self.k_or.text().strip()
            s.key_groq       = self.k_groq.text().strip()
            s.key_anthropic  = self.k_ant.text().strip()
            s.key_mistral    = self.k_mis.text().strip()
            s.key_cohere     = self.k_coh.text().strip()
            s.key_together   = self.k_tog.text().strip()
        else:
            s.key_openrouter = s.key_groq = s.key_anthropic = ""
            s.key_mistral = s.key_cohere = s.key_together = ""
        s.remember_keys = self.remember.isChecked()

        s.boundary_guard = self.boundary.isChecked()
        s.self_improve   = self.self_impr.isChecked()
        s.auto_continue  = self.auto_cont.isChecked()
        s.auto_save      = self.auto_save.isChecked()
        s.auto_title     = self.auto_title.isChecked()
        s.show_followups = self.show_fu.isChecked()
        s.reply_lang     = self.reply_lang.currentText()

        s.max_tokens  = self.max_tokens.value()
        s.temperature = self.temp.value()
        s.top_p       = self.top_p.value()
        s.eur_per_1k  = self.eur.value()

        s.bg          = self.c_bg.text().strip()     or s.bg
        s.panel       = self.c_panel.text().strip()  or s.panel
        s.bubble_user = self.c_buser.text().strip()  or s.bubble_user
        s.bubble_asst = self.c_basst.text().strip()  or s.bubble_asst
        s.text_color  = self.c_text.text().strip()   or s.text_color
        s.accent      = self.c_accent.text().strip() or s.accent
        s.code_bg     = self.c_code.text().strip()   or s.code_bg
        s.font_family = self.font.text().strip()      or s.font_family
        s.code_font   = self.code_font.text().strip() or s.code_font
        s.font_size   = self.font_size.value()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.s        = _load_settings()
        self.chat     = new_chat()
        self.worker:  Optional[ChatWorker]     = None
        self.bg_workers: List[BackgroundWorker] = []
        self._stream_id: Optional[str] = None
        self.draft_atts: List[dict] = []
        self._session_turns: int = 0

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1520, 920)

        self._build_ui()
        self._apply_theme()
        self._load_chat_list()
        self._start_new_chat()
        self.refresh_models()

    # ──────────────────────────────────────────────────────────────────────────
    # BUILD UI
    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Toolbar
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))

        def tba(text, slot, shortcut=None, tip=""):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if shortcut: a.setShortcut(QKeySequence(shortcut))
            if tip: a.setToolTip(tip)
            tb.addAction(a)
            return a

        tba("⚙ Settings",        self.open_settings,     "Ctrl+,")
        tba("＋ New chat",        self._start_new_chat,   "Ctrl+N")
        tba("⌛ Temp",            self._new_temp_chat)
        tba("⏹ Stop",            self.stop_stream,        "Escape")
        tba("⟳ Models",          self.refresh_models,     "Ctrl+R")
        tba("🧠 Memory",          self.show_memory_dialog)
        tba("🗑 Clear memory",    self.clear_memory)
        tba("✅ Test connection", self.test_connection)
        tb.addSeparator()
        tba("📋 Help links",      self.show_help)

        # ── Top control bar ──
        top = QWidget()
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(10, 6, 10, 6)
        top_l.setSpacing(10)

        self.provider_box = QComboBox()
        self.provider_box.addItems(list(PROVIDERS.keys()))
        self.provider_box.setCurrentText(self.s.provider)
        self.provider_box.currentTextChanged.connect(self._on_provider_changed)
        self.provider_box.setToolTip("Select AI provider")

        self.free_box = QCheckBox("FREE")
        self.free_box.setChecked(self.s.free_only)
        self.free_box.stateChanged.connect(self._on_free_changed)
        self.free_box.setToolTip("Filter to free models (OpenRouter)")

        self.model_box = QComboBox()
        self.model_box.setMinimumWidth(400)
        self.model_box.setEditable(True)
        self.model_box.currentTextChanged.connect(self._on_model_changed)
        self.model_box.setToolTip("Active model — editable for custom model IDs")

        self.mode_box = QComboBox()
        self.mode_box.addItems(["CODING", "GENERAL", "REASONING", "PLAN", "CREATIVE"])
        self.mode_box.setCurrentText(self.s.mode)
        self.mode_box.currentTextChanged.connect(self._on_mode_changed)
        self.mode_box.setToolTip("Agent mode — changes system prompt and boundary rules")

        self.submode_box = QComboBox()
        self.submode_box.addItems(list(SUBMODE_EXTRAS.keys()))
        self.submode_box.setCurrentText(self.s.submode)
        self.submode_box.setToolTip("Sub-specialization within the current mode")

        self.max_tok_spin = QSpinBox()
        self.max_tok_spin.setRange(16, 32768)
        self.max_tok_spin.setValue(self.s.max_tokens)
        self.max_tok_spin.setFixedWidth(80)
        self.max_tok_spin.setToolTip("Max tokens per response")

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0); self.temp_spin.setSingleStep(0.01)
        self.temp_spin.setDecimals(2); self.temp_spin.setValue(self.s.temperature)
        self.temp_spin.setFixedWidth(70)
        self.temp_spin.setToolTip("Temperature (0=deterministic, 1=creative)")

        top_l.addWidget(QLabel("Provider:")); top_l.addWidget(self.provider_box)
        top_l.addWidget(self.free_box)
        top_l.addWidget(QLabel("Model:"));   top_l.addWidget(self.model_box, 1)
        top_l.addWidget(QLabel("Mode:"));    top_l.addWidget(self.mode_box)
        top_l.addWidget(self.submode_box)
        top_l.addWidget(QLabel("Tokens:"));  top_l.addWidget(self.max_tok_spin)
        top_l.addWidget(QLabel("Temp:"));    top_l.addWidget(self.temp_spin)

        # ── Central chat + prompt ──
        central = QWidget()
        cl = QVBoxLayout(central)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        cl.addWidget(top)

        self.chat_area = ChatArea(self.s)
        cl.addWidget(self.chat_area, 1)

        # Draft attachment bar
        self.att_bar = QWidget()
        al = QHBoxLayout(self.att_bar)
        al.setContentsMargins(10, 4, 10, 0)
        al.setSpacing(8)
        self.att_wrap = QWidget()
        self.att_lay  = QHBoxLayout(self.att_wrap)
        self.att_lay.setContentsMargins(0,0,0,0); self.att_lay.setSpacing(6)
        al.addWidget(self.att_wrap, 1)
        btn_af = QPushButton("Attach files"); btn_af.clicked.connect(self._attach_files)
        btn_ad = QPushButton("Attach folder"); btn_ad.clicked.connect(self._attach_folder)
        btn_ac = QPushButton("Clear attachments"); btn_ac.clicked.connect(self._clear_atts)
        al.addWidget(btn_af); al.addWidget(btn_ad); al.addWidget(btn_ac)
        cl.addWidget(self.att_bar)

        # Prompt area
        pw = QWidget()
        pl = QHBoxLayout(pw)
        pl.setContentsMargins(10, 6, 10, 10)
        pl.setSpacing(10)

        self.prompt = PromptEdit()
        self.prompt.setPlaceholderText(
            "Type here… (Enter=Send | Shift+Enter=New line | Ctrl+V paste image | drag & drop files)")
        self.prompt.setFixedHeight(110)
        self.prompt.sendRequested.connect(self.send)
        self.prompt.pasteImageRequested.connect(self._paste_image)
        self.prompt.filesDropped.connect(self._files_dropped)

        self.btn_send = QPushButton("Send ⚡")
        self.btn_send.clicked.connect(self.send)
        self.btn_send.setFixedWidth(100)
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.clicked.connect(self.stop_stream)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setFixedWidth(100)

        rr = QVBoxLayout()
        rr.addWidget(self.btn_send)
        rr.addWidget(self.btn_stop)
        rr.addStretch()
        pl.addWidget(self.prompt, 1)
        pl.addLayout(rr)
        cl.addWidget(pw)

        # Follow-up suggestions bar
        self.fu_bar = QWidget()
        fl = QHBoxLayout(self.fu_bar)
        fl.setContentsMargins(10, 0, 10, 6)
        fl.setSpacing(6)
        fl.addWidget(QLabel("💡 Try:"))
        self.fu_btns: List[QPushButton] = []
        for i in range(3):
            b = QPushButton("")
            b.setObjectName("FollowUpBtn")
            b.setVisible(False)
            b.clicked.connect(lambda _, i=i: self._use_followup(i))
            fl.addWidget(b, 1)
            self.fu_btns.append(b)
        cl.addWidget(self.fu_bar)
        self.fu_bar.hide()

        # Status / progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(3)
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        cl.addWidget(self.progress)

        self.setCentralWidget(central)

        # ── LEFT DOCK: chat list ──
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self._load_chat)
        self.chat_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chat_list.customContextMenuRequested.connect(self._chat_list_ctx)

        lw = QWidget()
        ll = QVBoxLayout(lw)
        ll.setContentsMargins(8, 8, 8, 8)
        ll.setSpacing(6)
        btn_nc = QPushButton("＋ New chat"); btn_nc.clicked.connect(self._start_new_chat)
        btn_tc = QPushButton("⌛ Temp chat"); btn_tc.clicked.connect(self._new_temp_chat)

        # Memory stats
        self.mem_label = QLabel()
        self.mem_label.setObjectName("MemLabel")
        self.mem_label.setWordWrap(True)
        self._refresh_mem_label()

        ll.addWidget(btn_nc); ll.addWidget(btn_tc)
        ll.addWidget(self.chat_list, 1)
        ll.addWidget(self.mem_label)

        dock_l = QDockWidget("Chats", self)
        dock_l.setWidget(lw)
        dock_l.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock_l.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_l)

        # ── RIGHT DOCK: panels ──
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # Pinned codes
        self.list_pins = QListWidget()
        self.list_pins.itemDoubleClicked.connect(lambda i: self._copy_item_text(i))
        pp = QWidget(); pl2 = QVBoxLayout(pp); pl2.setContentsMargins(6,6,6,6)
        btn_pin = QPushButton("Pin selection (Alt+A)"); btn_pin.clicked.connect(self.pin_selection)
        btn_cp  = QPushButton("Copy selected"); btn_cp.clicked.connect(lambda: self._copy_item_text(self.list_pins.currentItem()))
        pl2.addWidget(self.list_pins, 1); pl2.addWidget(btn_pin); pl2.addWidget(btn_cp)
        tabs.addTab(pp, "📌 Pinned")

        # Marked phrases
        self.list_marks = QListWidget()
        self.list_marks.itemClicked.connect(lambda i: self.chat_area.scroll_to(
            (i.data(Qt.ItemDataRole.UserRole) or {}).get("msg_id","")))
        mp = QWidget(); ml2 = QVBoxLayout(mp); ml2.setContentsMargins(6,6,6,6)
        btn_mk = QPushButton("Mark selection (Alt+M)"); btn_mk.clicked.connect(self.mark_selection)
        ml2.addWidget(self.list_marks, 1); ml2.addWidget(btn_mk)
        tabs.addTab(mp, "🔖 Marks")

        # Saved texts
        self.list_saved = QListWidget()
        sp2 = QWidget(); sl2 = QVBoxLayout(sp2); sl2.setContentsMargins(6,6,6,6)
        btn_sv  = QPushButton("Save selection (Ctrl+S)"); btn_sv.clicked.connect(self.save_selection)
        btn_csv = QPushButton("Copy selected"); btn_csv.clicked.connect(lambda: self._copy_item_text(self.list_saved.currentItem()))
        sl2.addWidget(self.list_saved, 1); sl2.addWidget(btn_sv); sl2.addWidget(btn_csv)
        tabs.addTab(sp2, "💾 Saved")

        # Chat info
        self.info_browser = QTextBrowser()
        self.info_browser.setOpenExternalLinks(True)
        iw = QWidget(); il = QVBoxLayout(iw); il.setContentsMargins(6,6,6,6)
        il.addWidget(self.info_browser, 1)
        tabs.addTab(iw, "ℹ Info")

        # Memory viewer
        self.mem_browser = QTextBrowser()
        self.mem_browser.setOpenExternalLinks(False)
        mv = QWidget(); mvl = QVBoxLayout(mv); mvl.setContentsMargins(6,6,6,6)
        btn_rm = QPushButton("Clear all memory"); btn_rm.clicked.connect(self.clear_memory)
        mvl.addWidget(self.mem_browser, 1); mvl.addWidget(btn_rm)
        tabs.addTab(mv, "🧠 Memory")

        dock_r = QDockWidget("Panels", self)
        dock_r.setWidget(tabs)
        dock_r.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        dock_r.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_r)

        self.status_bar = self.statusBar()
        self._update_status()

        # Keyboard shortcuts
        QAction("Pin",  self, shortcut=QKeySequence("Alt+A"), triggered=self.pin_selection).setParent(self)
        QAction("Mark", self, shortcut=QKeySequence("Alt+M"), triggered=self.mark_selection).setParent(self)

        # Install event filter for Alt+A / Alt+M  
        QApplication.instance().installEventFilter(self)

    # ──────────────────────────────────────────────────────────────────────────
    # THEME
    # ──────────────────────────────────────────────────────────────────────────
    def _apply_theme(self):
        s = self.s
        qss = f"""
        QMainWindow, QDialog, QWidget {{ background:{s.bg}; color:{s.text_color}; font-family:{s.font_family}; font-size:{s.font_size}px; }}
        QDockWidget {{ background:{s.panel}; color:{s.text_color}; }}
        QDockWidget::title {{ background:{s.panel}; padding:4px 8px; font-weight:bold; }}
        QToolBar {{ background:{s.panel}; border:none; spacing:4px; padding:4px; }}
        QToolButton, QAction {{ color:{s.text_color}; }}
        QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {{
            background:{s.panel}; color:{s.text_color}; border:1px solid #252840;
            border-radius:5px; padding:4px 8px; selection-background-color:{s.accent};
        }}
        QComboBox::drop-down {{ border:none; }}
        QComboBox QAbstractItemView {{ background:{s.panel}; color:{s.text_color}; selection-background-color:{s.accent}; }}
        QPushButton {{
            background:{s.accent}; color:#fff; border:none; border-radius:6px;
            padding:6px 14px; font-weight:600;
        }}
        QPushButton:hover {{ background:#9585f7; }}
        QPushButton:pressed {{ background:#6050d0; }}
        QPushButton:disabled {{ background:#252840; color:#6b7299; }}
        QPushButton#FollowUpBtn {{
            background:{s.panel}; color:{s.accent}; border:1px solid {s.accent};
            font-size:{s.font_size - 2}px; font-weight:400; padding:4px 8px;
        }}
        QPushButton#FollowUpBtn:hover {{ background:{s.accent}; color:#fff; }}
        QCheckBox {{ color:{s.text_color}; spacing:6px; }}
        QCheckBox::indicator {{ width:16px; height:16px; border:2px solid #252840; border-radius:3px; background:{s.panel}; }}
        QCheckBox::indicator:checked {{ background:{s.accent}; }}
        QListWidget {{ background:{s.panel}; color:{s.text_color}; border:none; outline:none; }}
        QListWidget::item {{ padding:6px 8px; border-radius:4px; }}
        QListWidget::item:selected {{ background:{s.accent}; color:#fff; }}
        QListWidget::item:hover:!selected {{ background:#1e2235; }}
        QTabWidget::pane {{ border:1px solid #252840; background:{s.panel}; }}
        QTabBar::tab {{ background:{s.bg}; color:#6b7299; padding:7px 14px; border:1px solid #252840; border-bottom:none; border-radius:5px 5px 0 0; }}
        QTabBar::tab:selected {{ background:{s.panel}; color:{s.text_color}; border-bottom:1px solid {s.panel}; }}
        QScrollBar:vertical {{ background:{s.bg}; width:6px; border-radius:3px; }}
        QScrollBar::handle:vertical {{ background:#252840; border-radius:3px; min-height:30px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        QFrame#BubbleUser {{ background:{s.bubble_user}; border-radius:10px; margin:2px 60px 2px 0px; }}
        QFrame#BubbleAsst {{ background:{s.bubble_asst}; border-radius:10px; margin:2px 0px 2px 0px; }}
        QFrame#BubbleSys  {{ background:#0d1020; border-radius:6px; margin:2px 20px; }}
        QLabel#BubbleHeader {{ font-size:{s.font_size - 2}px; color:{s.accent}; font-weight:600; }}
        QTextBrowser#BubbleText {{ background:transparent; color:{s.text_color}; selection-background-color:{s.accent}; }}
        QLabel#MemLabel {{ color:#6b7299; font-size:{s.font_size - 2}px; padding:6px; }}
        QProgressBar {{ background:{s.bg}; border:none; }}
        QProgressBar::chunk {{ background:{s.accent}; }}
        QGroupBox {{ border:1px solid #252840; border-radius:6px; margin-top:8px; padding-top:8px; color:{s.text_color}; }}
        QGroupBox::title {{ subcontrol-origin:margin; left:10px; color:{s.accent}; font-weight:600; }}
        QStatusBar {{ background:{s.panel}; color:#6b7299; font-size:{s.font_size - 1}px; }}
        """
        self.setStyleSheet(qss)
        self._update_info()
        self._refresh_mem_browser()

    # ──────────────────────────────────────────────────────────────────────────
    # PROVIDER / MODEL
    # ──────────────────────────────────────────────────────────────────────────
    def _on_provider_changed(self, prov: str):
        self.s.provider = prov
        info = PROVIDERS.get(prov, {})
        self.s.base_url = info.get("base", self.s.base_url)
        self.free_box.setVisible(bool(info.get("free_suffix")))
        self.refresh_models()
        self._update_status()

    def _on_free_changed(self):
        self.s.free_only = self.free_box.isChecked()
        self.refresh_models()

    def _on_model_changed(self, model: str):
        self.s.model = model

    def _on_mode_changed(self, mode: str):
        self.s.mode = mode
        guard_visible = (mode == "CODING")
        # Update UI hint

    def refresh_models(self):
        self.model_box.clear()
        self.model_box.addItem("Loading…")
        key = _get_api_key(self.s)
        w = ModelsWorker(self.s.provider, self.s.base_url, key, self.s.free_only)
        w.ok.connect(self._on_models_ok)
        w.fail.connect(self._on_models_fail)
        w.finished.connect(w.deleteLater)
        w.start()

    def _on_models_ok(self, ids: List[str]):
        self.model_box.clear()
        self.model_box.addItems(ids)
        if self.s.model and self.s.model in ids:
            self.model_box.setCurrentText(self.s.model)
        elif ids:
            self.s.model = ids[0]
            self.model_box.setCurrentText(ids[0])
        self._update_status()

    def _on_models_fail(self, err: str):
        self.model_box.clear()
        self.model_box.addItem("(fetch failed — type manually)")
        self.status_bar.showMessage(f"Model fetch failed: {err}", 3000)

    def test_connection(self):
        key = _get_api_key(self.s)
        pinfo = PROVIDERS.get(self.s.provider, {})
        mu = pinfo.get("models_url")
        if not mu:
            QMessageBox.information(self, "Info", "No models endpoint for this provider.")
            return
        url = self.s.base_url.rstrip("/") + mu
        headers = {"User-Agent": APP_NAME}
        if key: headers["Authorization"] = f"Bearer {key}"
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}\n{r.text[:1000]}")
            QMessageBox.information(self, "Connected ✅", "Connection successful!")
        except Exception as e:
            QMessageBox.critical(self, "Failed ❌", str(e))

    # ──────────────────────────────────────────────────────────────────────────
    # CHAT MANAGEMENT
    # ──────────────────────────────────────────────────────────────────────────
    def _start_new_chat(self):
        if self.s.auto_save and self.chat["messages"]:
            save_chat(self.chat); add_to_index(self.chat)
        memory.log_session(self._session_turns)
        self._session_turns = 0
        self.chat = new_chat()
        save_chat(self.chat); add_to_index(self.chat)
        self._load_chat_list()
        self._render_chat()
        self._load_side_panels()
        self._update_info()
        self._update_status()
        self.fu_bar.hide()
        self.prompt.setFocus()

    def _new_temp_chat(self):
        self.chat = new_chat("Temp chat", temp=True)
        self._render_chat()
        self._load_side_panels()
        self._update_info()
        self._update_status()

    def _load_chat_list(self):
        self.chat_list.clear()
        for c in _load_index().get("chats", []):
            item = QListWidgetItem(c.get("title", "chat"))
            item.setData(Qt.ItemDataRole.UserRole, c.get("id"))
            self.chat_list.addItem(item)

    def _load_chat(self, item: QListWidgetItem):
        cid = item.data(Qt.ItemDataRole.UserRole)
        chat = load_chat_file(cid)
        if not chat:
            QMessageBox.warning(self, "Missing", "Chat file not found."); return
        if self.s.auto_save and self.chat["messages"]:
            save_chat(self.chat); add_to_index(self.chat)
        self.chat = chat
        self._render_chat()
        self._load_side_panels()
        self._update_info()
        self._update_status()

    def _chat_list_ctx(self, pos):
        item = self.chat_list.itemAt(pos)
        if not item: return
        menu = QMenu(self)
        act_del = menu.addAction("🗑 Delete chat")
        act_ren = menu.addAction("✏ Rename")
        act = menu.exec(self.chat_list.mapToGlobal(pos))
        cid = item.data(Qt.ItemDataRole.UserRole)
        if act == act_del:
            p = _chat_path(cid)
            if p.exists(): p.unlink()
            remove_from_index(cid)
            self._load_chat_list()
            if self.chat.get("id") == cid:
                self._start_new_chat()
        elif act == act_ren:
            new_title, ok = QInputDialog.getText(self, "Rename", "New title:", text=item.text())
            if ok and new_title.strip():
                c = load_chat_file(cid)
                if c:
                    c["title"] = new_title.strip()
                    save_chat(c); add_to_index(c)
                    self._load_chat_list()
                    if self.chat.get("id") == cid:
                        self.chat["title"] = new_title.strip()

    def _render_chat(self):
        self.chat_area.clear()
        for m in self.chat.get("messages", []):
            role = m.get("role", "user")
            if role == "system": continue
            html = md_to_html(m.get("content", ""), self.s)
            self.chat_area.add_bubble(role, html, m.get("ts", _now()),
                                      m.get("id", uuid.uuid4().hex),
                                      m.get("attachments"))

    def _load_side_panels(self):
        self.list_pins.clear()
        for p in self.chat.get("pinned_codes", []):
            it = QListWidgetItem(p.get("label","Pin"))
            it.setData(Qt.ItemDataRole.UserRole, p)
            self.list_pins.addItem(it)
        self.list_marks.clear()
        for mk in self.chat.get("marked_phrases", []):
            it = QListWidgetItem(mk.get("label","Mark"))
            it.setData(Qt.ItemDataRole.UserRole, mk)
            self.list_marks.addItem(it)
        self.list_saved.clear()
        for sv in self.chat.get("saved_texts", []):
            it = QListWidgetItem(sv.get("label","Saved"))
            it.setData(Qt.ItemDataRole.UserRole, sv)
            self.list_saved.addItem(it)

    # ──────────────────────────────────────────────────────────────────────────
    # SEND
    # ──────────────────────────────────────────────────────────────────────────
    def send(self):
        if self.worker and self.worker.isRunning(): return

        text = self.prompt.toPlainText().strip()
        if not text and not self.draft_atts: return

        model = self.model_box.currentText().strip()
        if not model or model in ("Loading…", "(fetch failed — type manually)"):
            QMessageBox.warning(self, "No model", "Select or type a model ID."); return

        # FREE enforcement
        if self.s.provider == "OpenRouter" and self.free_box.isChecked():
            if not model.endswith(":free"):
                model += ":free"

        # Key check
        key = _get_api_key(self.s)
        pinfo = PROVIDERS.get(self.s.provider, {})
        if pinfo.get("needs_key") and not key:
            QMessageBox.warning(self, "No API key",
                f"{self.s.provider} requires an API key.\n"
                f"Open Settings (Ctrl+,) and enter your key.\n\n"
                f"Get one at: {pinfo.get('key_help','')}"); return

        # Boundary guard
        if self.s.boundary_guard and self.s.mode == "CODING":
            ok, reason = boundary_check(text, coding_mode=True)
            if not ok:
                self._show_boundary_msg(); return

        # Build user message
        uid = uuid.uuid4().hex
        user_msg = {
            "id": uid, "role": "user",
            "content": text if text else "[attachments]",
            "ts": _now(),
            "attachments": [a for a in self.draft_atts if a.get("type") in ("image","file","folder")] or None,
        }
        self.chat.setdefault("messages", []).append(user_msg)

        # Render user bubble
        html = md_to_html(user_msg["content"], self.s)
        self.chat_area.add_bubble("user", html, user_msg["ts"], uid, user_msg.get("attachments"))

        self.prompt.clear()
        self._clear_atts()
        self.fu_bar.hide()

        # Build API messages
        mem_ctx = memory.build_context()
        system  = build_system_prompt(
            self.s.mode, self.submode_box.currentText(),
            self.s.reply_lang, mem_ctx
        )
        api_msgs = [{"role": "system", "content": system}]

        # File context from attachments
        file_ctx = self._build_file_ctx(user_msg.get("attachments") or [])
        if file_ctx:
            api_msgs.append({"role": "system", "content": "FILE CONTEXT:\n" + file_ctx})

        # Conversation history (last 40 messages)
        for m in self.chat["messages"][-40:]:
            if m["role"] in ("user","assistant"):
                api_msgs.append({"role": m["role"], "content": m.get("content","")})

        payload = {
            "model":       model,
            "messages":    api_msgs,
            "max_tokens":  self.max_tok_spin.value(),
            "temperature": self.temp_spin.value(),
            "top_p":       self.s.top_p,
            "stream":      True,
        }

        # Start streaming
        aid = uuid.uuid4().hex
        self._stream_id = aid
        self.chat_area.start_stream(_now(), aid)

        self.worker = ChatWorker(self.s.provider, self.s.base_url, key, payload)
        self.worker.delta.connect(self._on_delta)
        self.worker.done.connect(lambda obj: self._on_done(obj, model, text))
        self.worker.fail.connect(self._on_fail)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

        self.btn_send.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setVisible(True)

        # Update stats
        self.chat["stats"].update({"provider": self.s.provider, "model": model})
        self._session_turns += 1
        self._update_status()

        # Auto-title on first message
        if self.s.auto_title and len(self.chat["messages"]) == 1 and text:
            self._bg_task("title", TITLE_PROMPT.format(msg=text[:300]))

    def _show_boundary_msg(self):
        mid = uuid.uuid4().hex
        self.chat_area.add_bubble("system",
            md_to_html(BOUNDARY_MSG, self.s), _now(), mid)
        self.chat.setdefault("messages",[]).append({
            "id": mid, "role": "assistant",
            "content": BOUNDARY_MSG, "ts": _now(),
        })

    def _on_delta(self, d: str):
        if self._stream_id:
            self.chat_area.append_stream(d)

    def _on_done(self, obj: dict, model: str, user_text: str):
        content       = obj.get("content", "")
        finish_reason = obj.get("finish_reason", "stop")
        usage         = obj.get("usage") or {}

        html = md_to_html(content, self.s)
        if self._stream_id:
            self.chat_area.finalize_stream(self._stream_id, html)

        aid = self._stream_id or uuid.uuid4().hex
        asst_msg = {
            "id": aid, "role": "assistant",
            "content": content, "ts": _now(),
            "finish_reason": finish_reason, "usage": usage,
        }
        self.chat.setdefault("messages",[]).append(asst_msg)

        # Update stats
        st = self.chat.setdefault("stats",{})
        st["messages"]     = st.get("messages", 0) + 1
        st["answers"]      = st.get("answers", 0) + 1
        tok = usage.get("total_tokens") or _approx_tokens(content)
        st["approx_tokens"] = st.get("approx_tokens", 0) + tok
        st["approx_eur"]    = (st["approx_tokens"] / 1000.0) * self.s.eur_per_1k
        st["minutes"]       = max(0, int((_now() - self.chat.get("created", _now())) / 60))

        if self.s.auto_save:
            save_chat(self.chat); add_to_index(self.chat); self._load_chat_list()

        self._stream_id = None
        self.btn_send.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setVisible(False)
        self._update_status()
        self._update_info()

        # Auto-continue
        if self.s.auto_continue and str(finish_reason).lower() == "length":
            self.prompt.setPlainText("Continue.")
            QTimer.singleShot(400, self.send)
            return

        # Background: memory extraction
        if self.s.self_improve and content:
            self._bg_task("memory",
                MEMORY_EXTRACTION_PROMPT.format(
                    user_msg=user_text[:600], agent_msg=content[:400]))

        # Background: follow-up suggestions
        if self.s.show_followups and content and len(content) > 50:
            self._bg_task("followup",
                FOLLOWUP_PROMPT.format(
                    user_msg=user_text[:300], agent_msg=content[:500]))

    def _on_fail(self, err: str):
        html = md_to_html(f"**Error:** {err}", self.s)
        if self._stream_id:
            self.chat_area.finalize_stream(self._stream_id, html)
        self._stream_id = None
        self.btn_send.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setVisible(False)
        self._update_status()

        self.chat.setdefault("messages",[]).append({
            "id": uuid.uuid4().hex, "role": "assistant",
            "content": f"[error] {err}", "ts": _now(),
        })

        low = err.lower()
        if "10061" in err or "connection refused" in err or "failed to establish" in err:
            QMessageBox.warning(self, "Connection refused",
                f"Cannot reach {self.s.provider}.\n"
                f"Base URL: {self.s.base_url}\n\n"
                f"If using Ollama/Local, make sure the server is running.")
        elif "data policy" in low or "privacy" in low:
            QMessageBox.information(self, "OpenRouter privacy",
                "This is common with OpenRouter FREE models.\n"
                "Configure your data policy at: https://openrouter.ai/settings/privacy")
        elif "401" in err or "unauthorized" in err.lower():
            QMessageBox.warning(self, "API key error",
                f"Authentication failed for {self.s.provider}.\n"
                "Check your API key in Settings (Ctrl+,).")

    def stop_stream(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.btn_send.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.progress.setVisible(False)
            self.status_bar.showMessage("Stopped.", 2000)

    # ──────────────────────────────────────────────────────────────────────────
    # BACKGROUND INTELLIGENCE
    # ──────────────────────────────────────────────────────────────────────────
    def _bg_task(self, task: str, prompt: str):
        model = self.model_box.currentText().strip()
        key   = _get_api_key(self.s)
        w = BackgroundWorker(task, self.s.provider, self.s.base_url, key, model, prompt)
        w.result.connect(self._on_bg_result)
        w.finished.connect(w.deleteLater)
        self.bg_workers.append(w)
        w.start()

    def _on_bg_result(self, task: str, result: Any):
        if task == "memory":
            self._process_memory_extraction(result)
        elif task == "title":
            self._apply_auto_title(result)
        elif task == "followup":
            self._show_followups(result)

    def _process_memory_extraction(self, raw: str):
        try:
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n",1)[1].rsplit("```",1)[0].strip()
            data = json.loads(raw)
            for fact in data.get("facts", []):
                if fact and len(fact) > 8: memory.remember_fact(fact)
            if data.get("user_name"): memory.set_user_name(data["user_name"])
            if data.get("preferred_language"): memory.set_preferred_language(data["preferred_language"])
            proj = data.get("project")
            if proj and proj.get("name"):
                memory.remember_project(proj["name"], proj.get("description",""), proj.get("language",""))
            for corr in data.get("corrections", []):
                if corr: memory.log_correction(corr)
            self._refresh_mem_label()
            self._refresh_mem_browser()
        except Exception:
            pass

    def _apply_auto_title(self, raw: str):
        title = raw.strip().strip('"\'').strip()[:60]
        if title:
            self.chat["title"] = title
            if self.s.auto_save:
                save_chat(self.chat); add_to_index(self.chat); self._load_chat_list()

    def _show_followups(self, raw: str):
        try:
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n",1)[1].rsplit("```",1)[0].strip()
            suggestions = json.loads(raw)
            if not isinstance(suggestions, list): return
            self._followups = suggestions[:3]
            for i, btn in enumerate(self.fu_btns):
                if i < len(self._followups):
                    label = self._followups[i][:50] + ("…" if len(self._followups[i]) > 50 else "")
                    btn.setText(label); btn.setVisible(True)
                else:
                    btn.setVisible(False)
            self.fu_bar.show()
        except Exception:
            pass

    def _use_followup(self, idx: int):
        sugg = getattr(self, "_followups", [])[idx] if idx < len(getattr(self, "_followups", [])) else ""
        if sugg:
            self.prompt.setPlainText(sugg)
            self.fu_bar.hide()
            self.prompt.setFocus()

    # ──────────────────────────────────────────────────────────────────────────
    # FILE ATTACHMENTS
    # ──────────────────────────────────────────────────────────────────────────
    def _save_img_bytes(self, b: bytes, ext: str = "") -> str:
        mime = _detect_img_mime(b)
        if not ext:
            ext = (mimetypes.guess_extension(mime) or ".png").strip(".")
        h = _sha1(b)
        p = ATT_DIR / f"{h}.{ext}"
        if not p.exists(): p.write_bytes(b)
        return str(p)

    def _paste_image(self):
        cb = QApplication.clipboard()
        md = cb.mimeData()
        if not md.hasImage():
            self.prompt.paste(); return
        img = cb.image()
        if img.isNull(): self.prompt.paste(); return
        from PyQt6.QtCore import QBuffer, QByteArray
        ba = QByteArray(); buf = QBuffer(ba)
        buf.open(QBuffer.OpenModeFlag.WriteOnly)
        QPixmap.fromImage(img).save(buf, "PNG")
        path = self._save_img_bytes(bytes(ba), "png")
        self.draft_atts.append({"type":"image","path":path})
        self._refresh_atts_ui()
        self.prompt.insertPlainText(" [pasted image] ")

    def _files_dropped(self, paths: List[str]):
        for p in paths:
            if not os.path.exists(p): continue
            mt, _ = mimetypes.guess_type(p)
            if (mt or "").startswith("image/") or p.lower().endswith((".png",".jpg",".jpeg",".gif",".webp")):
                b = Path(p).read_bytes()
                saved = self._save_img_bytes(b, os.path.splitext(p)[1].strip("."))
                self.draft_atts.append({"type":"image","path":saved})
            else:
                self.draft_atts.append({"type":"file","path":p})
        self._refresh_atts_ui()

    def _attach_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Attach files")
        if files: self._files_dropped(files)

    def _attach_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Attach folder")
        if d: self.draft_atts.append({"type":"folder","path":d}); self._refresh_atts_ui()

    def _clear_atts(self):
        self.draft_atts = []; self._refresh_atts_ui()

    def _refresh_atts_ui(self):
        while self.att_lay.count():
            it = self.att_lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        for a in self.draft_atts:
            p = a.get("path","")
            if a.get("type") == "image" and os.path.exists(p):
                lbl = ClickLabel(); pix = QPixmap(p)
                if not pix.isNull():
                    lbl.setPixmap(pix.scaled(64,64,Qt.AspectRatioMode.KeepAspectRatio,
                                             Qt.TransformationMode.SmoothTransformation))
                else: lbl.setText(os.path.basename(p))
                self.att_lay.addWidget(lbl)
            else:
                lbl = QLabel(f"📄 {os.path.basename(p)}"); self.att_lay.addWidget(lbl)
        self.att_lay.addStretch(1)

    def _build_file_ctx(self, atts: List[dict]) -> str:
        parts = []
        TEXT_EXT = {".txt",".md",".py",".js",".ts",".json",".yaml",".yml",".ini",".cfg",
                    ".cpp",".c",".h",".cs",".java",".go",".rs",".sh",".bat",".html",".css"}
        for a in (atts or []):
            t = a.get("type"); p = a.get("path","")
            if not p: continue
            if t == "file" and os.path.exists(p):
                if os.path.getsize(p) > 200_000:
                    parts.append(f"- {p} (too large, not inlined)"); continue
                if os.path.splitext(p)[1].lower() in TEXT_EXT:
                    try: parts.append(f"FILE: {os.path.basename(p)}\n---\n{Path(p).read_text('utf-8','ignore')[:50000]}\n---")
                    except: parts.append(f"- {p} (unreadable)")
                else: parts.append(f"- {p} (binary, not inlined)")
            elif t == "folder" and os.path.isdir(p):
                entries = os.listdir(p)[:200]
                parts.append(f"FOLDER: {p}\n{chr(10).join(entries)}")
        return "\n\n".join(parts)

    # ──────────────────────────────────────────────────────────────────────────
    # SELECTION TOOLS
    # ──────────────────────────────────────────────────────────────────────────
    def _selected_text(self) -> str:
        w = QApplication.focusWidget()
        if isinstance(w, (QTextEdit, QTextBrowser)):
            t = w.textCursor().selectedText()
            return t.replace("\u2029","\n").strip()
        return ""

    def _focused_msg_id(self) -> Optional[str]:
        w = QApplication.focusWidget()
        while w:
            if isinstance(w, MessageBubble): return w.msg_id
            w = w.parentWidget()
        return None

    def pin_selection(self):
        sel = self._selected_text()
        if not sel: QMessageBox.information(self, "No selection", "Select text in a bubble first."); return
        vnum = len(self.chat.get("pinned_codes",[])) + 1
        label = f"V{vnum} — " + sel.replace("\n"," ")[:60] + ("…" if len(sel) > 60 else "")
        entry = {"label": label, "text": sel, "ts": _now(), "msg_id": self._focused_msg_id()}
        self.chat.setdefault("pinned_codes",[]).append(entry)
        it = QListWidgetItem(label)
        it.setData(Qt.ItemDataRole.UserRole, entry)
        self.list_pins.addItem(it)
        if self.s.auto_save: save_chat(self.chat); add_to_index(self.chat)
        self.status_bar.showMessage("Pinned!", 1500)

    def mark_selection(self):
        sel = self._selected_text()
        if not sel: QMessageBox.information(self, "No selection", "Select text first."); return
        label = sel.replace("\n"," ")[:80] + ("…" if len(sel) > 80 else "")
        entry = {"label": label, "msg_id": self._focused_msg_id(), "ts": _now()}
        self.chat.setdefault("marked_phrases",[]).append(entry)
        it = QListWidgetItem(label)
        it.setData(Qt.ItemDataRole.UserRole, entry)
        self.list_marks.addItem(it)
        if self.s.auto_save: save_chat(self.chat); add_to_index(self.chat)
        self.status_bar.showMessage("Marked!", 1500)

    def save_selection(self):
        sel = self._selected_text()
        if not sel: QMessageBox.information(self, "No selection", "Select text first."); return
        label = sel.replace("\n"," ")[:80] + ("…" if len(sel) > 80 else "")
        entry = {"label": label, "text": sel, "msg_id": self._focused_msg_id(), "ts": _now()}
        self.chat.setdefault("saved_texts",[]).append(entry)
        it = QListWidgetItem(label)
        it.setData(Qt.ItemDataRole.UserRole, entry)
        self.list_saved.addItem(it)
        if self.s.auto_save: save_chat(self.chat); add_to_index(self.chat)
        self.status_bar.showMessage("Saved!", 1500)

    def _copy_item_text(self, it: Optional[QListWidgetItem]):
        if not it: return
        d = it.data(Qt.ItemDataRole.UserRole) or {}
        QApplication.clipboard().setText(d.get("text","") or it.text())
        self.status_bar.showMessage("Copied!", 1200)

    # ──────────────────────────────────────────────────────────────────────────
    # MEMORY
    # ──────────────────────────────────────────────────────────────────────────
    def show_memory_dialog(self):
        data = memory.get_all()
        dlg = QDialog(self)
        dlg.setWindowTitle("Long-term Memory")
        dlg.resize(560, 500)
        lay = QVBoxLayout(dlg)
        browser = QTextBrowser()
        lines = []
        lines.append(f"<h3 style='color:#7c6af5'>Codeer Long-term Memory</h3>")
        lines.append(f"<b>User:</b> {data.get('user_name') or '(unknown)'}<br>")
        lines.append(f"<b>Language:</b> {data.get('preferred_language') or '(auto)'}<br>")
        lines.append(f"<b>Style:</b> {data.get('preferred_style','')}<br><br>")
        lines.append(f"<b>Facts ({len(data.get('facts',[]))}):</b><br>")
        for f in data.get("facts", []): lines.append(f"• {_html_esc(f)}<br>")
        lines.append(f"<br><b>Projects ({len(data.get('projects',{}))}):</b><br>")
        for p in data.get("projects",{}).values():
            lines.append(f"• <b>{_html_esc(p['name'])}</b>: {_html_esc(p.get('description',''))} "
                         f"({_html_esc(p.get('language',''))})<br>")
        lines.append(f"<br><b>Corrections ({len(data.get('corrections_summary',[]))}):</b><br>")
        for c in data.get("corrections_summary",[]): lines.append(f"• {_html_esc(c)}<br>")
        lines.append(f"<br><b>Sessions:</b> {data.get('total_sessions',0)} | "
                     f"<b>Turns:</b> {data.get('total_turns',0)}")
        browser.setHtml("".join(lines))
        lay.addWidget(browser)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns)
        dlg.exec()

    def clear_memory(self):
        r = QMessageBox.question(self, "Clear memory?",
            "This deletes all facts, projects, and corrections Codeer has learned.\n"
            "Session stats are preserved. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            memory.clear()
            self._refresh_mem_label()
            self._refresh_mem_browser()
            self.status_bar.showMessage("Memory cleared.", 2000)

    def _refresh_mem_label(self):
        st = memory.get_stats()
        self.mem_label.setText(
            f"🧠 {st['facts']} facts · {st['projects']} projects · "
            f"{st['sessions']} sessions\n"
            f"User: {st['user_name'] or 'unknown'}")

    def _refresh_mem_browser(self):
        try:
            ctx = memory.build_context()
            self.mem_browser.setPlainText(ctx if ctx else "(no memory yet)")
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    # STATUS / INFO
    # ──────────────────────────────────────────────────────────────────────────
    def _update_status(self):
        prov  = self.s.provider
        model = self.s.model or "(none)"
        st    = self.chat.get("stats",{})
        tok   = int(st.get("approx_tokens", 0))
        eur   = float(st.get("approx_eur", 0.0))
        turns = self._session_turns
        mode  = self.s.mode
        free  = "·FREE" if (prov=="OpenRouter" and self.s.free_only) else ""
        self.status_bar.showMessage(
            f"{prov}{free} | {model} | mode:{mode} | turns:{turns} | ~{tok} tokens | ~€{eur:.4f}")

    def _update_info(self):
        st = self.chat.get("stats",{})
        ct = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.chat.get("created",_now())))
        ut = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.chat.get("updated",_now())))
        mem_st = memory.get_stats()
        html = (
            f"<h3 style='color:#7c6af5'>{_html_esc(self.chat.get('title',''))}</h3>"
            f"<b>Created:</b> {ct}<br><b>Updated:</b> {ut}<br><br>"
            f"<b>Provider:</b> {st.get('provider','')}<br>"
            f"<b>Model:</b> {_html_esc(str(st.get('model','')))}<br>"
            f"<b>Mode:</b> {self.s.mode}<br><br>"
            f"<b>Messages:</b> {st.get('messages',0)}<br>"
            f"<b>Answers:</b> {st.get('answers',0)}<br>"
            f"<b>Session turns:</b> {self._session_turns}<br>"
            f"<b>Approx tokens:</b> {int(st.get('approx_tokens',0))}<br>"
            f"<b>Approx EUR:</b> {float(st.get('approx_eur',0)):.4f}<br><br>"
            f"<h4 style='color:#5be5c3'>Memory</h4>"
            f"Facts: {mem_st['facts']} | Projects: {mem_st['projects']}<br>"
            f"Sessions: {mem_st['sessions']} | Turns: {mem_st['turns']}<br>"
            f"User: {mem_st['user_name'] or 'unknown'}<br><br>"
            f"<h4 style='color:#5be5c3'>Help</h4>"
            + "".join(f"<a href='{v}' style='color:#7c6af5'>{k}</a><br>" for k,v in HELP_LINKS.items())
        )
        try: self.info_browser.setHtml(html)
        except Exception: pass

    # ──────────────────────────────────────────────────────────────────────────
    # SETTINGS / HELP
    # ──────────────────────────────────────────────────────────────────────────
    def open_settings(self):
        dlg = SettingsDialog(self, self.s)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dlg.apply()
            _save_settings(self.s)
            self.provider_box.setCurrentText(self.s.provider)
            self.free_box.setChecked(self.s.free_only)
            self.mode_box.setCurrentText(self.s.mode)
            self.max_tok_spin.setValue(self.s.max_tokens)
            self.temp_spin.setValue(self.s.temperature)
            self._apply_theme()
            self._render_chat()
            self._update_status()
            self.refresh_models()

    def show_help(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Help & Links")
        dlg.resize(400, 300)
        lay = QVBoxLayout(dlg)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        html = "<h3>Codeer Platform — Help</h3>"
        for k, v in HELP_LINKS.items():
            html += f"<p><a href='{v}'>{k}</a></p>"
        html += f"<p><b>Data stored at:</b> {APP_DIR}</p>"
        html += f"<p><b>Memory file:</b> {MEMORY_PATH}</p>"
        browser.setHtml(html)
        lay.addWidget(browser)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btns.accepted.connect(dlg.accept)
        lay.addWidget(btns)
        dlg.exec()

    # ──────────────────────────────────────────────────────────────────────────
    # EVENT FILTER (Alt+A, Alt+M, Ctrl+S)
    # ──────────────────────────────────────────────────────────────────────────
    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Type.KeyPress:
            mods = ev.modifiers()
            key  = ev.key()
            if mods & Qt.KeyboardModifier.AltModifier:
                if key == Qt.Key.Key_A: self.pin_selection();  return True
                if key == Qt.Key.Key_M: self.mark_selection(); return True
            if mods & Qt.KeyboardModifier.ControlModifier:
                if key == Qt.Key.Key_S:
                    # Don't intercept Ctrl+S inside text widgets (let them pass)
                    w = QApplication.focusWidget()
                    if not isinstance(w, (QTextEdit,)):
                        self.save_selection(); return True
        return super().eventFilter(obj, ev)

    # ──────────────────────────────────────────────────────────────────────────
    # CLOSE
    # ──────────────────────────────────────────────────────────────────────────
    def closeEvent(self, e):
        if self.s.auto_save and self.chat.get("messages"):
            save_chat(self.chat); add_to_index(self.chat)
        memory.log_session(self._session_turns)
        _save_settings(self.s)
        super().closeEvent(e)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
