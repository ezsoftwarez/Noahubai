import json
import threading
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Set

from PySide6.QtCore import QObject, Signal, QSettings, QUrl
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineScript


# =========================
# TabVault (OneTab-szerű)
# =========================

@dataclass
class TabVaultGroup:
    created_iso: str
    title: str
    items: List[Tuple[str, str]]  # (title, url)


class TabVault:
    KEY = "ext/tabvault/groups_json"

    def __init__(self, qs: QSettings):
        self.qs = qs

    def load_groups(self) -> List[TabVaultGroup]:
        raw = self.qs.value(self.KEY, "[]")
        try:
            arr = json.loads(raw) if isinstance(raw, str) else raw
            out: List[TabVaultGroup] = []
            for g in arr:
                out.append(TabVaultGroup(
                    created_iso=g.get("created_iso", ""),
                    title=g.get("title", "Saved Tabs"),
                    items=[(it.get("title", ""), it.get("url", "")) for it in (g.get("items") or []) if it.get("url")]
                ))
            return out
        except Exception:
            return []

    def save_groups(self, groups: List[TabVaultGroup]):
        arr = []
        for g in groups:
            arr.append({
                "created_iso": g.created_iso,
                "title": g.title,
                "items": [{"title": t, "url": u} for (t, u) in g.items],
            })
        self.qs.setValue(self.KEY, json.dumps(arr, ensure_ascii=False))

    def add_group_from_tabs(self, tabs: List[Tuple[str, str]], title: str) -> int:
        groups = self.load_groups()
        g = TabVaultGroup(
            created_iso=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            title=title,
            items=tabs,
        )
        groups.insert(0, g)
        self.save_groups(groups)
        return 0

    def delete_group(self, idx: int):
        groups = self.load_groups()
        if 0 <= idx < len(groups):
            groups.pop(idx)
            self.save_groups(groups)

    def build_html(self) -> str:
        groups = self.load_groups()

        def esc(s: str) -> str:
            return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

        blocks = []
        if not groups:
            blocks.append('<div class="empty">Még nincs mentett csoport. Nyomd: <b>Ctrl+Shift+O</b> (TabVault).</div>')
        else:
            for i, g in enumerate(groups):
                items = []
                for (t, u) in g.items:
                    tt = esc(t) if t else esc(u)
                    uu = esc(u)
                    items.append(f'<div class="it"><a href="{uu}">{tt}</a><div class="u">{uu}</div></div>')
                items_html = "\n".join(items)
                blocks.append(f"""
                <div class="group">
                  <div class="gh">
                    <div>
                      <div class="gt">{esc(g.title)}</div>
                      <div class="gs">{esc(g.created_iso)}</div>
                    </div>
                    <div class="ga">
                      <a class="btn" href="tabvault://restore?g={i}">Restore all</a>
                      <a class="btn danger" href="tabvault://delete?g={i}">Delete</a>
                    </div>
                  </div>
                  <div class="items">{items_html}</div>
                </div>
                """)

        groups_html = "\n".join(blocks)
        return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>TabVault</title>
<style>
  body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; background:#1b2838; color:#c7d5e0; }}
  .top {{ padding:18px 20px; background:#171a21; border-bottom:1px solid #0f141a; }}
  .h1 {{ font-size:18px; font-weight:800; letter-spacing:0.4px; }}
  .sub {{ opacity:0.85; margin-top:6px; font-size:13px; }}
  .wrap {{ padding:18px 20px; }}
  .group {{ background:#2a475e; border:1px solid #0f141a; border-radius:16px; padding:12px 14px; margin-bottom:14px; }}
  .gh {{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }}
  .gt {{ font-weight:800; }}
  .gs {{ opacity:0.75; font-size:12px; margin-top:4px; }}
  .ga {{ display:flex; gap:8px; flex-wrap:wrap; }}
  .btn {{ text-decoration:none; color:#c7d5e0; background:#171a21; border:1px solid #0f141a; padding:6px 10px; border-radius:10px; font-size:12px; }}
  .btn:hover {{ background:#0f141a; }}
  .danger {{ background:#4a1f2a; }}
  .danger:hover {{ background:#35111a; }}
  .items {{ margin-top:10px; display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:10px; }}
  .it {{ background:#171a21; border:1px solid #0f141a; border-radius:12px; padding:10px 12px; }}
  .it a {{ color:#66c0f4; text-decoration:none; font-weight:700; }}
  .it a:hover {{ text-decoration:underline; }}
  .u {{ font-size:12px; opacity:0.85; word-break:break-all; margin-top:6px; }}
  .empty {{ opacity:0.85; padding:14px; background:#2a475e; border:1px solid #0f141a; border-radius:16px; }}
</style>
</head>
<body>
  <div class="top">
    <div class="h1">TabVault</div>
    <div class="sub">Beépített OneTab-szerű mentés / visszaállítás.</div>
  </div>
  <div class="wrap">
    {groups_html}
  </div>
</body>
</html>
"""


# =========================
# KoboldBlock (saját adblock)
# =========================

@dataclass
class KoboldBlockRules:
    enabled: bool
    exact_hosts: Set[str]
    domain_suffixes: Set[str]
    url_contains: List[str]
    cosmetic_global: List[str]               # ##selector
    cosmetic_by_domain: List[Tuple[str,str]] # domain##selector


def parse_koboldblock(text: str) -> KoboldBlockRules:
    exact_hosts: Set[str] = set()
    domain_suffixes: Set[str] = set()
    url_contains: List[str] = []
    cosmetic_global: List[str] = []
    cosmetic_by_domain: List[Tuple[str, str]] = []

    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        # Cosmetic: domain##selector or ##selector
        if "##" in line and not line.startswith("||"):
            left, sel = line.split("##", 1)
            sel = sel.strip()
            dom = left.strip().lower()
            if not sel:
                continue
            if dom:
                cosmetic_by_domain.append((dom, sel))
            else:
                cosmetic_global.append(sel)
            continue

        # domain+subdomain: ||example.com^
        if line.startswith("||"):
            dom = line[2:].strip().lstrip(".").lower().rstrip("^")
            if dom:
                domain_suffixes.add(dom)
            continue

        # wildcard: *.example.com
        if line.startswith("*."):
            dom = line[2:].strip().lstrip(".").lower().rstrip("^")
            if dom:
                domain_suffixes.add(dom)
            continue

        # url fragment
        if "://" in line or "/" in line:
            url_contains.append(line)
            continue

        # exact host
        exact_hosts.add(line.lower())

    return KoboldBlockRules(
        enabled=True,
        exact_hosts=exact_hosts,
        domain_suffixes=domain_suffixes,
        url_contains=url_contains[:500],
        cosmetic_global=cosmetic_global[:600],
        cosmetic_by_domain=cosmetic_by_domain[:600],
    )


class KoboldBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = False
        self.exact_hosts: Set[str] = set()
        self.domain_suffixes: Set[str] = set()
        self.url_contains: List[str] = []

    def set_rules(self, enabled: bool, rules: KoboldBlockRules):
        self.enabled = bool(enabled)
        self.exact_hosts = set(rules.exact_hosts)
        self.domain_suffixes = set(rules.domain_suffixes)
        self.url_contains = list(rules.url_contains)

    def interceptRequest(self, info):
        if not self.enabled:
            return

        url = info.requestUrl()
        host = (url.host() or "").lower()
        full = url.toString()

        blocked = False
        if host and host in self.exact_hosts:
            blocked = True
        else:
            if host:
                for dom in self.domain_suffixes:
                    if host == dom or host.endswith("." + dom):
                        blocked = True
                        break
            if not blocked:
                for frag in self.url_contains:
                    if frag and frag in full:
                        blocked = True
                        break

        if blocked:
            info.block(True)


def build_cosmetic_script(rules: KoboldBlockRules) -> QWebEngineScript:
    g = json.dumps(rules.cosmetic_global)
    by = json.dumps(rules.cosmetic_by_domain)

    js = f"""
(function() {{
  try {{
    const host = (location.hostname || "").toLowerCase();
    const globalSelectors = {g};
    const byDomain = {by}; // [ [domain, selector], ... ]
    const sels = [];
    for (const s of globalSelectors) sels.push(s);
    for (const pair of byDomain) {{
      const dom = (pair[0] || "").toLowerCase();
      const sel = pair[1];
      if (!dom || !sel) continue;
      if (host === dom || host.endsWith("." + dom)) sels.push(sel);
    }}
    if (!sels.length) return;

    const css = sels.map(s => `${{s}} {{ display: none !important; }}`).join("\n");
    let el = document.getElementById("__koboldblock_style__");
    if (!el) {{
      el = document.createElement("style");
      el.id = "__koboldblock_style__";
      document.documentElement.appendChild(el);
    }}
    el.textContent = css;
  }} catch (e) {{}}
}})();
"""
    script = QWebEngineScript()
    script.setName("KoboldBlockCosmetic")
    script.setSourceCode(js)
    script.setInjectionPoint(QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    script.setWorldId(QWebEngineScript.MainWorld)
    return script


# =========================
# VirusTotal (csak HTTP)
# =========================

class VtSignals(QObject):
    result = Signal(str)


class VirusTotalChecker(QObject):
    """
    Ha van API key és be van kapcsolva, csak a nem secured (http://) oldalakat ellenőrzi.
    """
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = (api_key or "").strip()
        self.signals = VtSignals()

    def check_http_url_async(self, url: str):
        if not self.api_key:
            return
        t = threading.Thread(target=self._worker, args=(url,), daemon=True)
        t.start()

    def _worker(self, url: str):
        try:
            data = urllib.parse.urlencode({"url": url}).encode("utf-8")
            req = urllib.request.Request(
                "https://www.virustotal.com/api/v3/urls",
                data=data,
                method="POST",
                headers={"x-apikey": self.api_key, "Content-Type": "application/x-www-form-urlencoded"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            j = json.loads(raw)
            analysis_id = ((j.get("data") or {}).get("id")) or ""
            if not analysis_id:
                self.signals.result.emit("VT: ?")
                return

            req2 = urllib.request.Request(
                f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                method="GET",
                headers={"x-apikey": self.api_key},
            )
            with urllib.request.urlopen(req2, timeout=8) as resp2:
                raw2 = resp2.read().decode("utf-8", errors="ignore")
            j2 = json.loads(raw2)
            stats = (((j2.get("data") or {}).get("attributes") or {}).get("stats")) or {}
            malicious = int(stats.get("malicious", 0) or 0)
            suspicious = int(stats.get("suspicious", 0) or 0)

            if malicious > 0 or suspicious > 0:
                self.signals.result.emit(f"VT: ⚠ m={malicious} s={suspicious}")
            else:
                self.signals.result.emit("VT: ✓")
        except Exception:
            self.signals.result.emit("VT: (err)")
