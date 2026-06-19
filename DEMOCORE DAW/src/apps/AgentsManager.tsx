import { useEffect, useState } from "react";
import type { AgentSyncState } from "../os/types";
import { subscribeAgentSync, syncAllAgents } from "../services/agentSync";
import { uploadDevicesToBrain } from "../services/noahubaiClient";

export default function AgentsManager() {
  const [sync, setSync] = useState<AgentSyncState | null>(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => subscribeAgentSync(setSync), []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncAllAgents();
    } finally {
      setSyncing(false);
    }
  };

  const grouped = {
    noahubai: sync?.agents.filter((a) => a.source === "noahubai") ?? [],
    aihub: sync?.agents.filter((a) => a.source === "aihub") ?? [],
    democore: sync?.agents.filter((a) => a.source === "democore") ?? [],
  };

  const [uploading, setUploading] = useState(false);

  const handleUploadBrain = async () => {
    setUploading(true);
    try {
      const n = await uploadDevicesToBrain();
      await syncAllAgents();
      if (n < 0) alert("Upload failed — start AI Hub bridge (port 8765)");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app-panel">
      <h2>Agents Manager</h2>
      <p>Unified sync across NOAHUBAI backend, AI Hub providers, and DEMOCORE OS.</p>
      <div className="status-row">
        <span className={`pill ${sync?.noahubaiOnline ? "online" : "offline"}`}>
          NOAHUBAI {sync?.noahubaiOnline ? "online" : "offline"}
        </span>
        <span className={`pill ${sync?.aihubOnline ? "online" : "offline"}`}>
          AI Hub {sync?.aihubOnline ? "online" : "offline"}
        </span>
        {sync && (
          <span className="pill">
            Last sync {new Date(sync.updatedAt).toLocaleTimeString()}
          </span>
        )}
      </div>
      <div className="btn-row">
        <button type="button" className="btn" disabled={syncing} onClick={() => void handleSync()}>
          {syncing ? "Syncing…" : "Force sync all agents"}
        </button>
        <button type="button" className="btn secondary" disabled={uploading} onClick={() => void handleUploadBrain()}>
          {uploading ? "Uploading…" : "Upload to AI Hub Brain"}
        </button>
      </div>

      {(["noahubai", "aihub", "democore"] as const).map((source) => (
        <section key={source} style={{ marginTop: 16 }}>
          <h3 style={{ fontSize: 13, textTransform: "uppercase", opacity: 0.6 }}>
            {source}
          </h3>
          <div className="agent-grid">
            {grouped[source].length === 0 ? (
              <p style={{ opacity: 0.6, fontSize: 12 }}>No agents — run sync or start services.</p>
            ) : (
              grouped[source].map((a) => (
                <div
                  key={a.id}
                  className="agent-card"
                  style={{ borderLeft: `4px solid ${a.color}` }}
                >
                  <h4>{a.name}</h4>
                  <small>
                    {a.status} · {a.description}
                  </small>
                </div>
              ))
            )}
          </div>
        </section>
      ))}
    </div>
  );
}
