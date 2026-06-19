export const SEARCH_ENGINES: Record<string, string> = {
  DuckDuckGo: "https://duckduckgo.com/?q={q}",
  Google: "https://www.google.com/search?q={q}",
  Bing: "https://www.bing.com/search?q={q}",
  Startpage: "https://www.startpage.com/sp/search?query={q}",
};

export interface BrowserTab {
  id: string;
  url: string;
  title: string;
}

export interface Bookmark {
  label: string;
  url: string;
}

export interface TabVaultGroup {
  id: string;
  title: string;
  createdAt: number;
  tabs: Array<{ title: string; url: string }>;
}

export interface BrowserPrefs {
  homeUrl: string;
  searchEngine: string;
}

const TABS_KEY = "democore-ai-browser-tabs";
const VAULT_KEY = "democore-ai-browser-tabvault";
const BOOKMARKS_KEY = "democore-ai-browser-bookmarks";
const PREFS_KEY = "democore-ai-browser-prefs";
const CHAT_KEY = "democore-ai-browser-chat";

export const DEFAULT_BOOKMARKS: Bookmark[] = [
  { label: "Steam", url: "https://store.steampowered.com/" },
  { label: "Search", url: "https://duckduckgo.com/" },
  { label: "YouTube", url: "https://www.youtube.com/" },
  { label: "Reddit", url: "https://www.reddit.com/" },
  { label: "AI Hub", url: "http://127.0.0.1:8765/" },
];

export function loadPrefs(): BrowserPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (raw) return { homeUrl: "https://duckduckgo.com/", searchEngine: "DuckDuckGo", ...JSON.parse(raw) };
  } catch {
    /* ignore */
  }
  return { homeUrl: "https://duckduckgo.com/", searchEngine: "DuckDuckGo" };
}

export function savePrefs(prefs: BrowserPrefs): void {
  localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
}

export function loadTabs(): BrowserTab[] {
  try {
    const raw = localStorage.getItem(TABS_KEY);
    if (raw) {
      const arr = JSON.parse(raw) as BrowserTab[];
      if (Array.isArray(arr) && arr.length) return arr;
    }
  } catch {
    /* ignore */
  }
  return [{ id: "tab-1", url: "https://duckduckgo.com/", title: "New Tab" }];
}

export function saveTabs(tabs: BrowserTab[]): void {
  localStorage.setItem(TABS_KEY, JSON.stringify(tabs));
}

export function loadBookmarks(): Bookmark[] {
  try {
    const raw = localStorage.getItem(BOOKMARKS_KEY);
    if (raw) {
      const arr = JSON.parse(raw) as Bookmark[];
      if (Array.isArray(arr) && arr.length) return arr;
    }
  } catch {
    /* ignore */
  }
  return DEFAULT_BOOKMARKS;
}

export function saveBookmarks(bookmarks: Bookmark[]): void {
  localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
}

export function loadTabVault(): TabVaultGroup[] {
  try {
    const raw = localStorage.getItem(VAULT_KEY);
    if (raw) {
      const arr = JSON.parse(raw) as TabVaultGroup[];
      return Array.isArray(arr) ? arr : [];
    }
  } catch {
    /* ignore */
  }
  return [];
}

export function saveTabVault(groups: TabVaultGroup[]): void {
  localStorage.setItem(VAULT_KEY, JSON.stringify(groups));
}

export interface ChatLine {
  role: "user" | "assistant";
  text: string;
  ts: number;
}

export function loadBrowserChat(): ChatLine[] {
  try {
    const raw = localStorage.getItem(CHAT_KEY);
    if (raw) {
      const arr = JSON.parse(raw) as ChatLine[];
      return Array.isArray(arr) ? arr : [];
    }
  } catch {
    /* ignore */
  }
  return [];
}

export function saveBrowserChat(lines: ChatLine[]): void {
  localStorage.setItem(CHAT_KEY, JSON.stringify(lines.slice(-100)));
}

export function normalizeUrl(input: string, prefs: BrowserPrefs): string {
  const text = (input || "").trim();
  if (!text) return prefs.homeUrl;
  if (text.startsWith("democore://")) return text;

  const first = text.split(/\s+/)[0] ?? text;
  if (!text.includes("://") && first.includes(".") && !text.includes(" ")) {
    return `https://${text}`;
  }
  if (!text.includes("://")) {
    const tmpl = SEARCH_ENGINES[prefs.searchEngine] ?? SEARCH_ENGINES.DuckDuckGo;
    return tmpl.replace("{q}", encodeURIComponent(text));
  }
  return text;
}

export function newTabId(): string {
  return `tab-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}
