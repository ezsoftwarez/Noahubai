import sys
from dataclasses import dataclass
from typing import List, Tuple
from urllib.parse import urlparse, parse_qs

from PySide6.QtCore import QUrl, Qt, QSettings, QStandardPaths
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QTabWidget,
    QWidget, QVBoxLayout, QProgressBar, QDialog, QDialogButtonBox,
    QFormLayout, QComboBox, QCheckBox, QPushButton, QHBoxLayout,
    QMessageBox, QPlainTextEdit, QLabel
)

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings

from extensions import (
    TabVault,
    parse_koboldblock, KoboldBlockInterceptor, build_cosmetic_script,
    VirusTotalChecker
)

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com/?q={q}",
    "Google": "https://www.google.com/search?q={q}",
    "Bing": "https://www.bing.com/search?q={q}",
    "Startpage": "https://www.startpage.com/sp/search?query={q}",
}

TABVAULT_INTERNAL = "about:tabvault"
BOOKMARKS_INTERNAL = "about:bookmarks"

DEFAULT_KOBOLDBLOCK = """# KoboldBlock rules
# exact host: ads.example.com
# domain+subdomain: ||doubleclick.net
# wildcard domain: *.example.com
# url-fragment: /ads?
# cosmetic: ##selector (global) or domain##selector

||doubleclick.net
||googlesyndication.com
||google-analytics.com
||googletagmanager.com
"""

DEFAULT_BOOKMARKS = """# Bookmarks / Quick links (one per line)
# Formats:
#   Label | https://example.com
#   Label = https://example.com
# Comments start with #

Steam | https://store.steampowered.com/
Search | https://duckduckgo.com/
YouTube | https://www.youtube.com/
Reddit | https://www.reddit.com/
"""


@dataclass
class BrowserPrefs:
    home_url: str = "https://store.steampowered.com/"
    search_engine: str = "DuckDuckGo"
    js_enabled: bool = True
    images_enabled: bool = True
    allow_popups: bool = False
    disk_cache: bool = True
    persistent_cookies: bool = True
    custom_user_agent: str = ""
    clear_on_exit: bool = False

    # built-in "extensions" (different names)
    tabvault_enabled: bool = True
    koboldblock_enabled: bool = True
    koboldblock_rules: str = DEFAULT_KOBOLDBLOCK

    # bookmarks page
    bookmarks_text: str = DEFAULT_BOOKMARKS

    # VirusTotal (only HTTP)
    vt_enabled: bool = False
    vt_api_key: str = ""


def percent_encode(s: str) -> str:
    return QUrl.toPercentEncoding(s).data().decode("utf-8")


def normalize_url(text: str, prefs: BrowserPrefs) -> QUrl:
    text = (text or "").strip()
    if not text:
        return QUrl(prefs.home_url)

    if text in (TABVAULT_INTERNAL, BOOKMARKS_INTERNAL):
        return QUrl(text)

    first = text.split()[0]
    if "://" not in text and "." in first and " " not in text:
        text = "https://" + text

    if "://" not in text:
        tmpl = SEARCH_ENGINES.get(prefs.search_engine, SEARCH_ENGINES["DuckDuckGo"])
        q = percent_encode(text)
        return QUrl(tmpl.format(q=q))

    return QUrl(text)


def parse_bookmarks(text: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "|" in line:
            left, right = line.split("|", 1)
        elif "=" in line:
            left, right = line.split("=", 1)
        else:
            left, right = "", line

        label = left.strip()
        url = right.strip()
        if not url:
            continue

        if "://" not in url and "." in url and not url.startswith("about:"):
            url = "https://" + url

        if not label:
            q = QUrl(url)
            label = q.host() or url

        out.append((label, url))
    return out[:80]


def html_escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_bookmarks_html(prefs: BrowserPrefs) -> str:
    cards = []
    for label, url in parse_bookmarks(prefs.bookmarks_text):
        cards.append(
            f'<a class="card" href="{html_escape(url)}">'
            f'<div class="t">{html_escape(label)}</div>'
            f'<div class="u">{html_escape(url)}</div>'
            f'</a>'
        )
    cards_html = "\n".join(cards) if cards else '<div class="empty">Nincs bookmark. Settingsben add hozzá.</div>'

    tv_btn = f'<a class="btn" href="{TABVAULT_INTERNAL}">Open TabVault</a>' if prefs.tabvault_enabled else ""

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Bookmarks</title>
<style>
  body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#1b2838; color:#c7d5e0; }}
  .top {{ padding:18px 20px; background:#171a21; border-bottom:1px solid #0f141a; display:flex; align-items:center; justify-content:space-between; gap:12px; }}
  .h1 {{ font-size:18px; font-weight:800; letter-spacing:0.4px; }}
  .wrap {{ padding:18px 20px; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap:12px; }}
  .card {{
    display:block; text-decoration:none; color:#c7d5e0;
    background:#2a475e; border:1px solid #0f141a; border-radius:14px;
    padding:12px 14px;
  }}
  .card:hover {{ background:#3b6b8a; }}
  .t {{ font-weight:800; margin-bottom:6px; }}
  .u {{ font-size:12px; opacity:0.85; word-break:break-all; }}
  .btn {{ text-decoration:none; color:#c7d5e0; background:#2a475e; border:1px solid #0f141a; padding:8px 10px; border-radius:12px; }}
  .btn:hover {{ background:#3b6b8a; }}
  .empty {{ opacity:0.8; padding:16px; background:#2a475e; border:1px solid #0f141a; border-radius:14px; }}
</style>
</head>
<body>
  <div class="top">
    <div class="h1">Bookmarks</div>
    <div>{tv_btn}</div>
  </div>
  <div class="wrap">
    <div class="grid">
      {cards_html}
    </div>
  </div>
</body>
</html>
"""


class SteamishPage(QWebEnginePage):
    """target=_blank / window.open -> új TAB, de csak ha engedélyezve van."""
    def __init__(self, profile: QWebEngineProfile, new_tab_page_callback, allow_popups_callable, tabvault_handler, parent=None):
        super().__init__(profile, parent)
        self._new_tab_page_callback = new_tab_page_callback
        self._allow_popups = allow_popups_callable
        self._tabvault_handler = tabvault_handler

    def createWindow(self, _type):
        if not self._allow_popups():
            return None
        return self._new_tab_page_callback()

    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        if url.scheme().lower() == "tabvault":
            try:
                self._tabvault_handler(url)
            except Exception:
                pass
            return False
        return super().acceptNavigationRequest(url, nav_type, isMainFrame)


class SettingsDialog(QDialog):
    def __init__(self, parent, prefs: BrowserPrefs, profile: QWebEngineProfile):
        super().__init__(parent)
        self.setWindowTitle("Beállítások")
        self.setModal(True)
        self._profile = profile

        self.home_edit = QLineEdit(prefs.home_url)

        self.search_combo = QComboBox()
        self.search_combo.addItems(list(SEARCH_ENGINES.keys()))
        if prefs.search_engine in SEARCH_ENGINES:
            self.search_combo.setCurrentText(prefs.search_engine)

        self.js_cb = QCheckBox("JavaScript engedélyezése")
        self.js_cb.setChecked(prefs.js_enabled)

        self.img_cb = QCheckBox("Képek automatikus betöltése")
        self.img_cb.setChecked(prefs.images_enabled)

        self.popups_cb = QCheckBox("Felugró ablakok engedélyezése (window.open / target=_blank)")
        self.popups_cb.setChecked(prefs.allow_popups)

        self.cache_cb = QCheckBox("Lemezes gyorsítótár (cache)")
        self.cache_cb.setChecked(prefs.disk_cache)

        self.cookies_cb = QCheckBox("Sütik megőrzése két indítás között")
        self.cookies_cb.setChecked(prefs.persistent_cookies)

        self.ua_edit = QLineEdit(prefs.custom_user_agent)
        self.ua_edit.setPlaceholderText("Üres = alapértelmezett user-agent")

        self.clear_exit_cb = QCheckBox("Kilépéskor cache + sütik törlése")
        self.clear_exit_cb.setChecked(prefs.clear_on_exit)

        # Built-in extensions
        self.tabvault_cb = QCheckBox("TabVault engedélyezése (beépített OneTab)")
        self.tabvault_cb.setChecked(prefs.tabvault_enabled)

        self.koboldblock_cb = QCheckBox("KoboldBlock engedélyezése (beépített adblock)")
        self.koboldblock_cb.setChecked(prefs.koboldblock_enabled)

        self.koboldblock_edit = QPlainTextEdit(prefs.koboldblock_rules)
        self.koboldblock_edit.setMinimumHeight(130)

        self.bookmarks_edit = QPlainTextEdit(prefs.bookmarks_text)
        self.bookmarks_edit.setMinimumHeight(120)

        # VirusTotal (only HTTP)
        self.vt_enable_cb = QCheckBox("VirusTotal ellenőrzés csak HTTP (nem secured) oldalakra")
        self.vt_enable_cb.setChecked(prefs.vt_enabled)

        self.vt_key_edit = QLineEdit(prefs.vt_api_key)
        self.vt_key_edit.setPlaceholderText("VirusTotal API key (opcionális)")

        # Azonnali törlés gombok
        clear_cookies_btn = QPushButton("Sütik törlése most")
        clear_cache_btn = QPushButton("Cache törlése most")
        clear_cookies_btn.clicked.connect(self._clear_cookies_now)
        clear_cache_btn.clicked.connect(self._clear_cache_now)

        btn_row = QHBoxLayout()
        btn_row.addWidget(clear_cookies_btn)
        btn_row.addWidget(clear_cache_btn)
        btn_row.addStretch(1)

        form = QFormLayout()
        form.addRow("Kezdőlap:", self.home_edit)
        form.addRow("Kereső:", self.search_combo)
        form.addRow("", self.js_cb)
        form.addRow("", self.img_cb)
        form.addRow("", self.popups_cb)
        form.addRow("", self.cache_cb)
        form.addRow("", self.cookies_cb)
        form.addRow("Egyéni user-agent:", self.ua_edit)
        form.addRow("", self.clear_exit_cb)

        form.addRow("", QLabel("Beépített extensionok:"))
        form.addRow("", self.tabvault_cb)
        form.addRow("", self.koboldblock_cb)
        form.addRow("KoboldBlock rules:", self.koboldblock_edit)

        form.addRow("Bookmarks / Quick links:", self.bookmarks_edit)

        form.addRow("", QLabel("VirusTotal:"))
        form.addRow("", self.vt_enable_cb)
        form.addRow("API key:", self.vt_key_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btn_row)
        root.addWidget(buttons)

        self.setStyleSheet("""
            QDialog { background: #1b2838; color: #c7d5e0; }
            QLabel { color: #c7d5e0; }
            QLineEdit, QComboBox, QPlainTextEdit {
                color: #c7d5e0;
                background: #0f141a;
                border: 1px solid #2a475e;
                padding: 6px 10px;
                border-radius: 8px;
            }
            QCheckBox { padding: 4px 0; }
            QPushButton {
                color: #c7d5e0;
                background: #2a475e;
                border: 1px solid #0f141a;
                padding: 6px 10px;
                border-radius: 8px;
            }
            QPushButton:hover { background: #3b6b8a; }
        """)

    def prefs_from_ui(self) -> BrowserPrefs:
        home = self.home_edit.text().strip() or "https://store.steampowered.com/"
        if "://" not in home and "." in home:
            home = "https://" + home

        return BrowserPrefs(
            home_url=home,
            search_engine=self.search_combo.currentText(),
            js_enabled=self.js_cb.isChecked(),
            images_enabled=self.img_cb.isChecked(),
            allow_popups=self.popups_cb.isChecked(),
            disk_cache=self.cache_cb.isChecked(),
            persistent_cookies=self.cookies_cb.isChecked(),
            custom_user_agent=self.ua_edit.text().strip(),
            clear_on_exit=self.clear_exit_cb.isChecked(),

            tabvault_enabled=self.tabvault_cb.isChecked(),
            koboldblock_enabled=self.koboldblock_cb.isChecked(),
            koboldblock_rules=self.koboldblock_edit.toPlainText(),

            bookmarks_text=self.bookmarks_edit.toPlainText(),

            vt_enabled=self.vt_enable_cb.isChecked(),
            vt_api_key=self.vt_key_edit.text().strip(),
        )

    def _clear_cookies_now(self):
        self._profile.cookieStore().deleteAllCookies()
        QMessageBox.information(self, "Kész", "Sütik törölve.")

    def _clear_cache_now(self):
        self._profile.clearHttpCache()
        QMessageBox.information(self, "Kész", "Cache törölve.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steam-ish Browser")
        self.resize(1200, 800)

        self.qsettings = QSettings("Steamish", "SteamishBrowser")
        self.prefs = self.load_prefs()

        # Extensions
        self.tabvault = TabVault(self.qsettings)
        self.kb_interceptor = KoboldBlockInterceptor(self)
        self.kb_rules = parse_koboldblock(self.prefs.koboldblock_rules)
        self.kb_cosmetic_script = build_cosmetic_script(self.kb_rules)

        self.vt = VirusTotalChecker(self.prefs.vt_api_key)
        self.vt.signals.result.connect(self.on_vt_result)

        # Profil (közös cookie/cache/UA az összes TAB között)
        self.profile = self.make_profile()

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_urlbar_with_tab)
        self.setCentralWidget(self.tabs)

        # --- Toolbar ---
        tb = QToolBar()
        tb.setMovable(False)
        tb.setFloatable(False)
        self.addToolBar(tb)

        back = QAction("←", self)
        back.setShortcut(QKeySequence.Back)
        back.triggered.connect(lambda: self.current_view().back())
        tb.addAction(back)

        forward = QAction("→", self)
        forward.setShortcut(QKeySequence.Forward)
        forward.triggered.connect(lambda: self.current_view().forward())
        tb.addAction(forward)

        reload_ = QAction("⟳", self)
        reload_.setShortcut(QKeySequence.Refresh)
        reload_.triggered.connect(lambda: self.current_view().reload())
        tb.addAction(reload_)

        home = QAction("⌂", self)
        home.triggered.connect(lambda: self.open_url(QUrl(self.prefs.home_url)))
        tb.addAction(home)

        tb.addSeparator()

        newtab = QAction("+", self)
        newtab.setShortcut(QKeySequence.AddTab)  # Ctrl+T
        newtab.triggered.connect(lambda: self.add_tab(QUrl(self.prefs.home_url), "New Tab"))
        tb.addAction(newtab)

        bm_act = QAction("⭐", self)
        bm_act.setShortcut(QKeySequence("Ctrl+Shift+B"))
        bm_act.triggered.connect(self.open_bookmarks_page)
        tb.addAction(bm_act)

        tabvault_act = QAction("TabVault", self)
        tabvault_act.setShortcut(QKeySequence("Ctrl+Shift+O"))
        tabvault_act.triggered.connect(self.tabvault_save_all_tabs)
        tb.addAction(tabvault_act)

        settings_act = QAction("⚙", self)
        settings_act.setShortcut(QKeySequence("Ctrl+,"))
        settings_act.triggered.connect(self.open_settings)
        tb.addAction(settings_act)

        tb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Enter URL or search… (Ctrl+L)")
        self.urlbar.returnPressed.connect(self.navigate_to_entered)
        tb.addWidget(self.urlbar)

        # VT badge (csak HTTP oldalnál látszik, ha be van kapcsolva)
        self.vt_label = QLabel("")
        self.vt_label.setMinimumWidth(80)
        self.vt_label.setAlignment(Qt.AlignCenter)
        self.vt_label.setStyleSheet("padding:4px 8px; border-radius:8px; background:#0f141a; border:1px solid #2a475e; color:#c7d5e0;")
        tb.addWidget(self.vt_label)
        self.vt_label.hide()

        self.progress = QProgressBar()
        self.progress.setMaximumHeight(10)
        self.progress.setTextVisible(False)
        self.progress.setMaximumWidth(220)
        self.progress.hide()
        tb.addWidget(self.progress)

        # Shortcuts
        focus_url = QAction(self)
        focus_url.setShortcut(QKeySequence("Ctrl+L"))
        focus_url.triggered.connect(lambda: self.urlbar.setFocus(Qt.ShortcutFocusReason))
        self.addAction(focus_url)

        close_tab = QAction(self)
        close_tab.setShortcut(QKeySequence.Close)  # Ctrl+W
        close_tab.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        self.addAction(close_tab)

        # Steam-ish dark theme
        self.setStyleSheet("""
            QMainWindow { background: #1b2838; }
            QToolBar {
                background: #171a21;
                spacing: 6px;
                padding: 6px;
                border: none;
            }
            QToolButton {
                color: #c7d5e0;
                background: #2a475e;
                border: 1px solid #0f141a;
                padding: 4px 8px;
                border-radius: 6px;
            }
            QToolButton:hover { background: #3b6b8a; }
            QLineEdit {
                color: #c7d5e0;
                background: #0f141a;
                border: 1px solid #2a475e;
                padding: 6px 10px;
                border-radius: 8px;
                min-width: 480px;
                selection-background-color: #2a475e;
            }
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: #171a21;
                color: #9fb3c8;
                padding: 8px 12px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: #2a475e; color:#c7d5e0; }
            QProgressBar {
                background: #0f141a;
                border: 1px solid #2a475e;
                border-radius: 6px;
            }
            QProgressBar::chunk { background: #66c0f4; }
        """)

        # restore window geometry
        geo = self.qsettings.value("window/geometry")
        if geo is not None:
            self.restoreGeometry(geo)

        # Start tab
        self.add_tab(QUrl(self.prefs.home_url), "Home")

    # ---------- prefs ----------
    def load_prefs(self) -> BrowserPrefs:
        p = BrowserPrefs()
        p.home_url = self.qsettings.value("prefs/home_url", p.home_url)
        p.search_engine = self.qsettings.value("prefs/search_engine", p.search_engine)
        p.js_enabled = self.qsettings.value("prefs/js_enabled", p.js_enabled, type=bool)
        p.images_enabled = self.qsettings.value("prefs/images_enabled", p.images_enabled, type=bool)
        p.allow_popups = self.qsettings.value("prefs/allow_popups", p.allow_popups, type=bool)
        p.disk_cache = self.qsettings.value("prefs/disk_cache", p.disk_cache, type=bool)
        p.persistent_cookies = self.qsettings.value("prefs/persistent_cookies", p.persistent_cookies, type=bool)
        p.custom_user_agent = self.qsettings.value("prefs/custom_user_agent", p.custom_user_agent)
        p.clear_on_exit = self.qsettings.value("prefs/clear_on_exit", p.clear_on_exit, type=bool)

        p.tabvault_enabled = self.qsettings.value("ext/tabvault/enabled", p.tabvault_enabled, type=bool)
        p.koboldblock_enabled = self.qsettings.value("ext/koboldblock/enabled", p.koboldblock_enabled, type=bool)
        p.koboldblock_rules = self.qsettings.value("ext/koboldblock/rules", p.koboldblock_rules)

        p.bookmarks_text = self.qsettings.value("prefs/bookmarks_text", p.bookmarks_text)

        p.vt_enabled = self.qsettings.value("vt/enabled", p.vt_enabled, type=bool)
        p.vt_api_key = self.qsettings.value("vt/api_key", p.vt_api_key)

        return p

    def save_prefs(self):
        p = self.prefs
        self.qsettings.setValue("prefs/home_url", p.home_url)
        self.qsettings.setValue("prefs/search_engine", p.search_engine)
        self.qsettings.setValue("prefs/js_enabled", p.js_enabled)
        self.qsettings.setValue("prefs/images_enabled", p.images_enabled)
        self.qsettings.setValue("prefs/allow_popups", p.allow_popups)
        self.qsettings.setValue("prefs/disk_cache", p.disk_cache)
        self.qsettings.setValue("prefs/persistent_cookies", p.persistent_cookies)
        self.qsettings.setValue("prefs/custom_user_agent", p.custom_user_agent)
        self.qsettings.setValue("prefs/clear_on_exit", p.clear_on_exit)

        self.qsettings.setValue("ext/tabvault/enabled", p.tabvault_enabled)
        self.qsettings.setValue("ext/koboldblock/enabled", p.koboldblock_enabled)
        self.qsettings.setValue("ext/koboldblock/rules", p.koboldblock_rules)

        self.qsettings.setValue("prefs/bookmarks_text", p.bookmarks_text)

        self.qsettings.setValue("vt/enabled", p.vt_enabled)
        self.qsettings.setValue("vt/api_key", p.vt_api_key)

    def make_profile(self) -> QWebEngineProfile:
        profile = QWebEngineProfile("steamish_profile", self)
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        profile.setPersistentStoragePath(data_dir)
        profile.setCachePath(data_dir)
        self.apply_profile_prefs(profile, self.prefs)
        return profile

    def apply_profile_prefs(self, profile: QWebEngineProfile, prefs: BrowserPrefs):
        profile.setHttpUserAgent(prefs.custom_user_agent or "")

        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache if prefs.disk_cache else QWebEngineProfile.MemoryHttpCache)

        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies if prefs.persistent_cookies else QWebEngineProfile.NoPersistentCookies
        )

        # KoboldBlock network blocking
        self.kb_rules = parse_koboldblock(prefs.koboldblock_rules)
        self.kb_interceptor.set_rules(prefs.koboldblock_enabled, self.kb_rules)
        profile.setUrlRequestInterceptor(self.kb_interceptor)

        # KoboldBlock cosmetic script
        try:
            profile.scripts().remove(self.kb_cosmetic_script)
        except Exception:
            pass
        self.kb_cosmetic_script = build_cosmetic_script(self.kb_rules)
        if prefs.koboldblock_enabled:
            profile.scripts().insert(self.kb_cosmetic_script)

    def apply_view_prefs(self, view: QWebEngineView, prefs: BrowserPrefs):
        s = view.settings()
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, prefs.js_enabled)
        s.setAttribute(QWebEngineSettings.AutoLoadImages, prefs.images_enabled)
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, prefs.allow_popups)

    # ---------- tabs / view ----------
    def current_view(self) -> QWebEngineView:
        w = self.tabs.currentWidget()
        return w.findChild(QWebEngineView)

    def open_url(self, url: QUrl):
        u = url.toString()
        if u == BOOKMARKS_INTERNAL:
            self.open_bookmarks_page()
            return
        if u == TABVAULT_INTERNAL:
            self.open_tabvault_page()
            return
        self.current_view().setUrl(url)

    def add_tab(self, url: QUrl, label: str, switch: bool = True, return_page: bool = False):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        view = QWebEngineView()

        def new_tab_page():
            return self.add_tab(QUrl("about:blank"), "New Tab", switch=True, return_page=True)

        page = SteamishPage(
            self.profile,
            new_tab_page_callback=new_tab_page,
            allow_popups_callable=lambda: self.prefs.allow_popups,
            tabvault_handler=self.handle_tabvault_action,
            parent=view
        )
        view.setPage(page)

        self.apply_view_prefs(view, self.prefs)

        layout.addWidget(view)

        idx = self.tabs.addTab(container, label)
        if switch:
            self.tabs.setCurrentIndex(idx)

        view.urlChanged.connect(lambda u, v=view: self.on_url_changed(u, v))
        view.titleChanged.connect(lambda t, v=view: self.on_title_changed(t, v))
        view.loadStarted.connect(self.on_load_started)
        view.loadProgress.connect(self.on_load_progress)
        view.loadFinished.connect(lambda ok, v=view: self.on_load_finished(ok, v))

        view.setUrl(url)
        return view.page() if return_page else view

    def close_tab(self, index: int):
        if self.tabs.count() <= 1:
            return
        self.tabs.removeTab(index)

    def tab_index_for_view(self, view: QWebEngineView) -> int:
        for i in range(self.tabs.count()):
            if self.tabs.widget(i).findChild(QWebEngineView) is view:
                return i
        return -1

    def on_title_changed(self, title: str, view: QWebEngineView):
        i = self.tab_index_for_view(view)
        if i >= 0:
            title = title or "New Tab"
            self.tabs.setTabText(i, (title[:18] + "…") if len(title) > 19 else title)

    def on_url_changed(self, url: QUrl, view: QWebEngineView):
        if view is self.current_view():
            self.urlbar.setText(url.toString())
            self.update_vt_visibility(url)

    def sync_urlbar_with_tab(self, _index: int):
        view = self.current_view()
        if view:
            self.urlbar.setText(view.url().toString())
            self.update_vt_visibility(view.url())

    def navigate_to_entered(self):
        url = normalize_url(self.urlbar.text(), self.prefs)
        self.open_url(url)

    def on_load_started(self):
        self.progress.show()
        self.progress.setValue(0)

    def on_load_progress(self, v: int):
        self.progress.setValue(v)

    def on_load_finished(self, ok: bool, view: QWebEngineView):
        self.progress.hide()
        if not ok:
            return

        if not (self.prefs.vt_enabled and (self.prefs.vt_api_key or "").strip()):
            return
        url = view.url()
        if url.scheme().lower() == "http":
            self.vt_label.show()
            self.vt_label.setText("VT: …")
            self.vt.check_http_url_async(url.toString())

    # ---------- bookmarks / tabvault ----------
    def open_bookmarks_page(self):
        html = build_bookmarks_html(self.prefs)
        view = self.add_tab(QUrl("about:blank"), "Bookmarks")
        view.setHtml(html, QUrl("about:blank"))

    def open_tabvault_page(self):
        if not self.prefs.tabvault_enabled:
            QMessageBox.information(self, "TabVault", "TabVault ki van kapcsolva a Settingsben.")
            return
        html = self.tabvault.build_html()
        view = self.add_tab(QUrl("about:blank"), "TabVault")
        view.setHtml(html, QUrl("about:blank"))

    def tabvault_save_all_tabs(self):
        if not self.prefs.tabvault_enabled:
            QMessageBox.information(self, "TabVault", "TabVault ki van kapcsolva a Settingsben.")
            return

        tabs: List[Tuple[str, str]] = []
        for i in range(self.tabs.count()):
            v = self.tabs.widget(i).findChild(QWebEngineView)
            if not v:
                continue
            u = v.url().toString()
            if u.startswith("http://") or u.startswith("https://"):
                title = v.title() or self.tabs.tabText(i) or u
                tabs.append((title, u))

        if not tabs:
            QMessageBox.information(self, "TabVault", "Nincs http/https tab amit menteni lehet.")
            return

        self.tabvault.add_group_from_tabs(tabs, title=f"Saved {len(tabs)} tabs")
        self.open_tabvault_page()

    def handle_tabvault_action(self, url: QUrl):
        u = url.toString()
        pr = urlparse(u)
        q = parse_qs(pr.query or "")
        g = int((q.get("g") or ["-1"])[0])

        if pr.netloc == "restore":
            self.restore_tabvault_group(g)
        elif pr.netloc == "delete":
            self.tabvault.delete_group(g)
            self.open_tabvault_page()

    def restore_tabvault_group(self, idx: int):
        groups = self.tabvault.load_groups()
        if not (0 <= idx < len(groups)):
            return
        g = groups[idx]
        for (t, u) in g.items:
            if u and (u.startswith("http://") or u.startswith("https://")):
                self.add_tab(QUrl(u), t or "Tab")
        self.open_tabvault_page()

    # ---------- VT UI ----------
    def update_vt_visibility(self, url: QUrl):
        if not (self.prefs.vt_enabled and (self.prefs.vt_api_key or "").strip()):
            self.vt_label.hide()
            return
        self.vt_label.setVisible(url.scheme().lower() == "http")

    def on_vt_result(self, s: str):
        self.vt_label.setText(s)

    # ---------- settings ----------
    def open_settings(self):
        dlg = SettingsDialog(self, self.prefs, self.profile)
        if dlg.exec() == QDialog.Accepted:
            self.prefs = dlg.prefs_from_ui()

            self.apply_profile_prefs(self.profile, self.prefs)
            for i in range(self.tabs.count()):
                v = self.tabs.widget(i).findChild(QWebEngineView)
                if v:
                    self.apply_view_prefs(v, self.prefs)

            self.vt = VirusTotalChecker(self.prefs.vt_api_key)
            self.vt.signals.result.connect(self.on_vt_result)

            self.save_prefs()

    # ---------- close ----------
    def closeEvent(self, event):
        self.qsettings.setValue("window/geometry", self.saveGeometry())

        if self.prefs.clear_on_exit:
            try:
                self.profile.clearHttpCache()
                self.profile.cookieStore().deleteAllCookies()
            except Exception:
                pass

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
