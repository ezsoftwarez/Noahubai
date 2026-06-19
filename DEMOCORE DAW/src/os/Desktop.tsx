import { useCallback, useEffect, useState } from "react";
import { APPS } from "./apps";
import WindowManager from "./WindowManager";
import Taskbar from "./Taskbar";
import StartMenu from "./StartMenu";
import type { AppId, WindowState } from "./types";

let nextZ = 10;
let windowCounter = 0;

function createWindow(appId: AppId): WindowState {
  const app = APPS.find((a) => a.id === appId)!;
  windowCounter += 1;
  return {
    id: `win-${windowCounter}`,
    appId,
    title: app.title,
    x: 80 + (windowCounter % 5) * 24,
    y: 60 + (windowCounter % 5) * 24,
    width: app.defaultSize.width,
    height: app.defaultSize.height,
    minimized: false,
    zIndex: ++nextZ,
  };
}

export default function Desktop() {
  const [windows, setWindows] = useState<WindowState[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [startOpen, setStartOpen] = useState(false);

  const openApp = useCallback((appId: AppId) => {
    setWindows((prev) => {
      const existing = prev.find((w) => w.appId === appId && !w.minimized);
      if (existing) {
        setActiveId(existing.id);
        return prev.map((w) =>
          w.id === existing.id ? { ...w, minimized: false, zIndex: ++nextZ } : w,
        );
      }
      const win = createWindow(appId);
      setActiveId(win.id);
      return [...prev, win];
    });
    setStartOpen(false);
  }, []);

  const focusWindow = useCallback((id: string) => {
    setActiveId(id);
    setWindows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, minimized: false, zIndex: ++nextZ } : w)),
    );
  }, []);

  const closeWindow = useCallback((id: string) => {
    setWindows((prev) => prev.filter((w) => w.id !== id));
    setActiveId((cur) => (cur === id ? null : cur));
  }, []);

  const minimizeWindow = useCallback((id: string) => {
    setWindows((prev) => prev.map((w) => (w.id === id ? { ...w, minimized: true } : w)));
    setActiveId((cur) => (cur === id ? null : cur));
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setStartOpen(false);
      if ((e.metaKey || e.ctrlKey) && e.key === "Escape") setStartOpen((v) => !v);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="desktop" onClick={() => setStartOpen(false)}>
      <div className="desktop-icons">
        {APPS.filter((a) => ["daw", "noahubai-og", "noahubai", "aihub", "aibrowser", "summarizer", "osbridge", "agentsmanager"].includes(a.id)).map(
          (app) => (
          <button
            key={app.id}
            type="button"
            className="desktop-icon"
            onDoubleClick={() => openApp(app.id)}
            title={app.description}
          >
            <span className="emoji">{app.icon}</span>
            <span>{app.title}</span>
          </button>
        ))}
      </div>

      <WindowManager
        windows={windows}
        activeId={activeId}
        onFocus={focusWindow}
        onClose={closeWindow}
        onMinimize={minimizeWindow}
      />

      {startOpen && (
        <StartMenu
          onOpen={openApp}
          onClose={() => setStartOpen(false)}
        />
      )}

      <Taskbar
        windows={windows}
        activeId={activeId}
        onStart={() => setStartOpen((v) => !v)}
        onFocus={focusWindow}
        onOpen={openApp}
      />
    </div>
  );
}
