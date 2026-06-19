import { useCallback, useEffect, useState } from "react";
import {
  fetchBridgeStatus,
  fetchNoahubaiHealth,
  noahubaiUiUrl,
  postAgentEvent,
} from "../services/noahubaiClient";
import { syncAllAgents } from "../services/agentSync";

const GITHUB_REPO = "https://github.com/ezsoftwarez/Noahubai";

export default function NoahubaiOG() {
  const [online, setOnline] = useState(false);
  const [bridgeOnline, setBridgeOnline] = useState(false);
  const [hint, setHint] = useState("Checking…");

  const refresh = useCallback(async () => {
    const [health, bridge] = await Promise.all([fetchNoahubaiHealth(), fetchBridgeStatus()]);
    const isOnline = health?.status === "healthy" || health?.status === "ok";
    setOnline(isOnline);
    setBridgeOnline(bridge?.ok === true);
    if (isOnline && bridge?.ok) {
      setHint("OG app + Bridge running");
      await syncAllAgents();
      await postAgentEvent("noahubai-og", "open", { source: "democore" });
    } else if (isOnline) {
      setHint("Noahubai online — start Bridge with NOAHUBAI-OG.bat");
    } else {
      setHint("Run NOAHUBAI-OG.bat or RUN-NOAHUBAI-OG.bat from repo root");
    }
  }, []);

  useEffect(() => {
    void refresh();
    const t = setInterval(() => void refresh(), 12000);
    return () => clearInterval(t);
  }, [refresh]);

  return (
    <div className="app-panel" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <h2>Noahubai OG</h2>
      <p>
        Original app from{" "}
        <a href={GITHUB_REPO} target="_blank" rel="noreferrer" style={{ color: "#7dfff0" }}>
          github.com/ezsoftwarez/Noahubai
        </a>{" "}
        — Windows 7 desktop shell. Bridge starts automatically when you use{" "}
        <code>RUN-NOAHUBAI-OG.bat</code>.
      </p>
      <div className="status-row">
        <span className={`pill ${online ? "online" : "offline"}`}>
          Noahubai {online ? "online" : "offline"}
        </span>
        <span className={`pill ${bridgeOnline ? "online" : "offline"}`}>
          Bridge {bridgeOnline ? "online" : "offline"}
        </span>
        <span className="pill">{hint}</span>
      </div>
      <div className="btn-row">
        <button type="button" className="btn" onClick={() => void refresh()}>
          Refresh
        </button>
        <a className="btn secondary" href={noahubaiUiUrl()} target="_blank" rel="noreferrer">
          Open OG in browser
        </a>
        <a className="btn secondary" href="/aihub-bridge/" target="_blank" rel="noreferrer">
          Open AI Hub Bridge
        </a>
      </div>
      {online ? (
        <iframe className="embed-frame" src={noahubaiUiUrl()} title="Noahubai OG Desktop" />
      ) : (
        <div
          style={{
            flex: 1,
            padding: 24,
            borderRadius: 12,
            border: "1px dashed rgba(255,255,255,0.15)",
            opacity: 0.85,
            fontSize: 13,
            lineHeight: 1.7,
          }}
        >
          <strong>Windows desktop shortcut</strong>
          <ol style={{ marginTop: 8, paddingLeft: 20 }}>
            <li>
              Run <code>CREATE-NOAHUBAI-DESKTOP-SHORTCUT.bat</code> once (creates &quot;Noahubai OG&quot; on
              Desktop)
            </li>
            <li>
              Or double-click <code>RUN-NOAHUBAI-OG.bat</code> in the repo root
            </li>
            <li>Bridge + Noahubai start together automatically</li>
          </ol>
        </div>
      )}
    </div>
  );
}
