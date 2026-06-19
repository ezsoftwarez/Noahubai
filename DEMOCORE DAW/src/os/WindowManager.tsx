import type { ReactNode } from "react";
import DAW from "../apps/DAW";
import NoahubAI from "../apps/NoahubAI";
import NoahubaiOG from "../apps/NoahubaiOG";
import AIHub from "../apps/AIHub";
import AgentsManager from "../apps/AgentsManager";
import AgentBuilder from "../apps/AgentBuilder";
import Terminal from "../apps/Terminal";
import Files from "../apps/Files";
import OSBridge from "../apps/OSBridge";
import AIBrowser from "../apps/AIBrowser";
import Summarizer from "../apps/Summarizer";
import Settings from "../apps/Settings";
import { APPS } from "./apps";
import type { AppId, WindowState } from "./types";

interface Props {
  windows: WindowState[];
  activeId: string | null;
  onFocus: (id: string) => void;
  onClose: (id: string) => void;
  onMinimize: (id: string) => void;
}

function renderApp(appId: AppId): ReactNode {
  switch (appId) {
    case "daw":
      return <DAW />;
    case "noahubai":
      return <NoahubAI />;
    case "noahubai-og":
      return <NoahubaiOG />;
    case "aihub":
      return <AIHub />;
    case "agentsmanager":
      return <AgentsManager />;
    case "agentbuilder":
      return <AgentBuilder />;
    case "terminal":
      return <Terminal />;
    case "files":
      return <Files />;
    case "osbridge":
      return <OSBridge />;
    case "aibrowser":
      return <AIBrowser />;
    case "summarizer":
      return <Summarizer />;
    case "settings":
      return <Settings />;
    default:
      return null;
  }
}

export default function WindowManager({ windows, onFocus, onClose, onMinimize }: Props) {
  return (
    <div className="window-layer">
      {windows.map((win) => (
        <div
          key={win.id}
          className={`os-window ${win.minimized ? "minimized" : ""}`}
          style={{
            left: win.x,
            top: win.y,
            width: win.width,
            height: win.height,
            zIndex: win.zIndex,
          }}
          onMouseDown={() => onFocus(win.id)}
        >
          <div className="window-titlebar">
            <span className="title">
              {APPS.find((a) => a.id === win.appId)?.icon} {win.title}
            </span>
            <div className="window-controls">
              <button type="button" onClick={() => onMinimize(win.id)} title="Minimize">
                −
              </button>
              <button type="button" onClick={() => onClose(win.id)} title="Close">
                ×
              </button>
            </div>
          </div>
          <div className="window-content">{renderApp(win.appId)}</div>
        </div>
      ))}
    </div>
  );
}
