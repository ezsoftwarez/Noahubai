import { useCallback, useEffect, useMemo, useState } from "react";
import { brainAuto } from "../services/brainClient";
import {
  loadBookmarks,
  loadBrowserChat,
  loadPrefs,
  loadTabVault,
  loadTabs,
  newTabId,
  normalizeUrl,
  saveBrowserChat,
  savePrefs,
  saveTabVault,
  saveTabs,
  SEARCH_ENGINES,
  type Bookmark,
  type BrowserTab,
  type ChatLine,
  type TabVaultGroup,
} from "../services/aiBrowserStorage";

const INTERNAL_BOOKMARKS = "democore://bookmarks";
const INTERNAL_VAULT = "democore://tabvault";

function isInternalPage(url: string): boolean {
  return url.startsWith("democore://");
}

function isEmbeddable(url: string): boolean {
  if (isInternalPage(url)) return false;
  return url.startsWith("http://") || url.startsWith("https://");
}

export default function AIBrowser() {
  const [prefs, setPrefs] = useState(loadPrefs);
  const [tabs, setTabs] = useState<BrowserTab[]>(loadTabs);
  const [activeTabId, setActiveTabId] = useState(tabs[0]?.id ?? "");
  const [urlInput, setUrlInput] = useState(tabs[0]?.url ?? prefs.homeUrl);
  const [bookmarks] = useState<Bookmark[]>(loadBookmarks);
  const [vault, setVault] = useState<TabVaultGroup[]>(loadTabVault);
  const [chat, setChat] = useState<ChatLine[]>(loadBrowserChat);
  const [aiInput, setAiInput] = useState("");
  const [aiBusy, setAiBusy] = useState(false);
  const [pageNote, setPageNote] = useState("");
  const [showAi, setShowAi] = useState(true);

  const activeTab = tabs.find((t) => t.id === activeTabId) ?? tabs[0];

  useEffect(() => {
    saveTabs(tabs);
  }, [tabs]);

  useEffect(() => {
    savePrefs(prefs);
  }, [prefs]);

  useEffect(() => {
    saveBrowserChat(chat);
  }, [chat]);

  useEffect(() => {
    if (activeTab) setUrlInput(activeTab.url);
  }, [activeTab?.id, activeTab?.url]);

  const navigate = useCallback(
    (raw: string) => {
      const url = normalizeUrl(raw, prefs);
      setTabs((prev) =>
        prev.map((t) => (t.id === activeTabId ? { ...t, url, title: titleFromUrl(url) } : t)),
      );
      setUrlInput(url);
    },
    [activeTabId, prefs],
  );

  const addTab = (url?: string) => {
    const u = url ?? prefs.homeUrl;
    const tab: BrowserTab = { id: newTabId(), url: u, title: titleFromUrl(u) };
    setTabs((prev) => [...prev, tab]);
    setActiveTabId(tab.id);
  };

  const closeTab = (id: string) => {
    if (tabs.length <= 1) return;
    setTabs((prev) => {
      const next = prev.filter((t) => t.id !== id);
      if (activeTabId === id && next[0]) setActiveTabId(next[0].id);
      return next;
    });
  };

  const saveAllToVault = () => {
    const httpTabs = tabs.filter((t) => t.url.startsWith("http"));
    if (!httpTabs.length) return;
    const group: TabVaultGroup = {
      id: `vault-${Date.now()}`,
      title: `Saved ${httpTabs.length} tabs`,
      createdAt: Date.now(),
      tabs: httpTabs.map((t) => ({ title: t.title, url: t.url })),
    };
    const next = [group, ...vault];
    setVault(next);
    saveTabVault(next);
    navigate(INTERNAL_VAULT);
  };

  const sendAi = async () => {
    const text = aiInput.trim();
    if (!text || aiBusy) return;
    const ctx = `Page URL: ${activeTab?.url ?? ""}\nPage note: ${pageNote || "(none)"}\n`;
    const userLine: ChatLine = { role: "user", text, ts: Date.now() };
    setChat((prev) => [...prev, userLine]);
    setAiInput("");
    setAiBusy(true);
    const result = await brainAuto(
      `You are the AI assistant inside DEMOCORE AI Browser (merged Steamish + page-aware browser).\n${ctx}\nUser question:\n${text}`,
    );
    const reply = result.ok && result.blended ? result.blended : result.error ?? "AI unavailable — start AI Hub Bridge on :8765";
    setChat((prev) => [...prev, { role: "assistant", text: reply, ts: Date.now() }]);
    setAiBusy(false);
  };

  const internalHtml = useMemo(() => {
    if (activeTab?.url === INTERNAL_BOOKMARKS) return renderBookmarksHtml(bookmarks);
    if (activeTab?.url === INTERNAL_VAULT) return renderVaultHtml(vault);
    return "";
  }, [activeTab?.url, bookmarks, vault]);

  return (
    <div className="ai-browser">
      <div className="ai-browser-toolbar">
        <button type="button" className="btn secondary small" onClick={() => addTab()} title="New tab">
          +
        </button>
        <button type="button" className="btn secondary small" onClick={() => navigate(INTERNAL_BOOKMARKS)}>
          ★
        </button>
        <button type="button" className="btn secondary small" onClick={saveAllToVault} title="TabVault">
          Vault
        </button>
        <select
          value={prefs.searchEngine}
          onChange={(e) => setPrefs({ ...prefs, searchEngine: e.target.value })}
          className="ai-browser-select"
        >
          {Object.keys(SEARCH_ENGINES).map((k) => (
            <option key={k} value={k}>
              {k}
            </option>
          ))}
        </select>
        <input
          className="ai-browser-url"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && navigate(urlInput)}
          placeholder="URL or search…"
        />
        <button type="button" className="btn" onClick={() => navigate(urlInput)}>
          Go
        </button>
        <button type="button" className="btn secondary" onClick={() => window.open(activeTab?.url, "_blank")}>
          New tab ↗
        </button>
        <button type="button" className="btn secondary small" onClick={() => setShowAi((v) => !v)}>
          AI
        </button>
      </div>

      <div className="ai-browser-tabs">
        {tabs.map((t) => (
          <div key={t.id} className={`ai-browser-tab ${t.id === activeTabId ? "active" : ""}`}>
            <button type="button" onClick={() => setActiveTabId(t.id)}>
              {t.title.slice(0, 18)}
            </button>
            {tabs.length > 1 && (
              <button type="button" className="close" onClick={() => closeTab(t.id)}>
                ×
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="ai-browser-body">
        <div className="ai-browser-main">
          {isInternalPage(activeTab?.url ?? "") ? (
            <iframe title="internal" className="ai-browser-frame" srcDoc={internalHtml} sandbox="allow-popups allow-popups-to-escape-sandbox" />
          ) : isEmbeddable(activeTab?.url ?? "") ? (
            <iframe title="browser" className="ai-browser-frame" src={activeTab?.url} sandbox="allow-scripts allow-same-origin allow-forms allow-popups" />
          ) : (
            <div className="ai-browser-fallback">
              <p>Cannot embed this URL in the web shell.</p>
              <button type="button" className="btn" onClick={() => window.open(activeTab?.url, "_blank")}>
                Open externally
              </button>
              <p style={{ fontSize: 12, opacity: 0.7, marginTop: 12 }}>
                For full Chromium browsing + adblock, run <code>RUN-AI-BROWSER.bat</code> (native merged app).
              </p>
            </div>
          )}
        </div>

        {showAi && (
          <div className="ai-browser-sidebar">
            <h4>AI Assistant</h4>
            <p className="ai-browser-hint">Page context + your notes (Steamish + aicat merge)</p>
            <input
              className="ai-browser-note"
              value={pageNote}
              onChange={(e) => setPageNote(e.target.value)}
              placeholder="Paste selected text / page notes…"
            />
            <div className="ai-browser-chat">
              {chat.slice(-12).map((line, i) => (
                <div key={`${line.ts}-${i}`} className={`chat-line ${line.role}`}>
                  <strong>{line.role === "user" ? "You" : "AI"}:</strong> {line.text.slice(0, 800)}
                </div>
              ))}
            </div>
            <textarea
              className="ai-browser-input"
              value={aiInput}
              onChange={(e) => setAiInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) void sendAi();
              }}
              placeholder="Ask about the page (Ctrl+Enter)"
            />
            <button type="button" className="btn" disabled={aiBusy} onClick={() => void sendAi()}>
              {aiBusy ? "…" : "Send"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function titleFromUrl(url: string): string {
  if (url === INTERNAL_BOOKMARKS) return "Bookmarks";
  if (url === INTERNAL_VAULT) return "TabVault";
  try {
    return new URL(url).hostname || "Tab";
  } catch {
    return url.slice(0, 20) || "Tab";
  }
}

function renderBookmarksHtml(bookmarks: Bookmark[]): string {
  const cards = bookmarks
    .map(
      (b) =>
        `<a class="card" href="${escapeHtml(b.url)}" target="_blank"><div class="t">${escapeHtml(b.label)}</div><div class="u">${escapeHtml(b.url)}</div></a>`,
    )
    .join("");
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    body{margin:0;font-family:system-ui;background:#1b2838;color:#c7d5e0}
    .wrap{padding:18px;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
    .card{display:block;text-decoration:none;color:#c7d5e0;background:#2a475e;border:1px solid #0f141a;border-radius:14px;padding:12px}
    .card:hover{background:#3b6b8a}.t{font-weight:800;margin-bottom:6px}.u{font-size:12px;opacity:.85;word-break:break-all}
  </style></head><body><div class="wrap">${cards}</div></body></html>`;
}

function renderVaultHtml(groups: TabVaultGroup[]): string {
  if (!groups.length) {
    return `<!doctype html><html><body style="font-family:system-ui;background:#1b2838;color:#c7d5e0;padding:20px">No saved tab groups yet. Use <b>Vault</b> in the toolbar.</body></html>`;
  }
  const blocks = groups
    .map(
      (g) =>
        `<div class="group"><div class="gt">${escapeHtml(g.title)}</div><div class="gs">${new Date(g.createdAt).toLocaleString()}</div><ul>${g.tabs
          .map((t) => `<li><a href="${escapeHtml(t.url)}" target="_blank">${escapeHtml(t.title || t.url)}</a></li>`)
          .join("")}</ul></div>`,
    )
    .join("");
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    body{margin:0;font-family:system-ui;background:#1b2838;color:#c7d5e0;padding:16px}
    .group{background:#2a475e;border:1px solid #0f141a;border-radius:14px;padding:12px;margin-bottom:12px}
    .gt{font-weight:800}.gs{font-size:12px;opacity:.75;margin:4px 0 8px}
    a{color:#66c0f4}
  </style></head><body>${blocks}</body></html>`;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}
