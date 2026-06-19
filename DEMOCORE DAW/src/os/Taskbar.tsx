import { useEffect, useState } from "react";
import { APPS } from "./apps";
import type { AppId, WindowState } from "./types";

interface Props {
  windows: WindowState[];
  activeId: string | null;
  onStart: () => void;
  onFocus: (id: string) => void;
  onOpen: (appId: AppId) => void;
}

export default function Taskbar({ windows, activeId, onStart, onFocus, onOpen }: Props) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="taskbar" onClick={(e) => e.stopPropagation()}>
      <button type="button" className="start-btn" onClick={onStart}>
        Start
      </button>
      <div className="taskbar-apps">
        {windows.map((w) => (
          <button
            key={w.id}
            type="button"
            className={`taskbar-app ${activeId === w.id ? "active" : ""}`}
            onClick={() => onFocus(w.id)}
          >
            {APPS.find((a) => a.id === w.appId)?.icon} {w.title}
          </button>
        ))}
      </div>
      <button type="button" className="taskbar-app" onClick={() => onOpen("noahubai-og")} title="Noahubai OG">
        🪟
      </button>
      <button type="button" className="taskbar-app" onClick={() => onOpen("aihub")} title="AI Hub">
        🌉
      </button>
      <div className="taskbar-clock">
        {time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
      </div>
    </div>
  );
}
