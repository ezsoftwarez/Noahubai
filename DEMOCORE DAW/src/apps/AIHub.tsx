import { syncAllAgents } from "../services/agentSync";

const AIHUB_URL = "/aihub-bridge/";

export default function AIHub() {
  return (
    <div className="app-panel" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <h2>AI Hub — OverDOn Runtime</h2>
      <p>Bridge between you, Cursor Agent, Ollama, and NOAHUBAI.</p>
      <div className="btn-row">
        <button type="button" className="btn" onClick={() => void syncAllAgents()}>
          Sync agents with NOAHUBAI
        </button>
        <a className="btn secondary" href={AIHUB_URL} target="_blank" rel="noreferrer">
          Open in new tab
        </a>
      </div>
      <iframe className="embed-frame" src={AIHUB_URL} title="AI Hub" />
    </div>
  );
}
