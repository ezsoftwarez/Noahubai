import { useCallback, useEffect, useState } from "react";
import {
  fetchNoahubaiAgents,
  fetchNoahubaiHealth,
  fetchNoahubaiStatus,
  noahubaiUiUrl,
  postAgentEvent,
} from "../services/noahubaiClient";
import { syncAllAgents } from "../services/agentSync";

export default function NoahubAI() {
  const [online, setOnline] = useState(false);
  const [agents, setAgents] = useState<Array<{ name: string; state?: string; status?: string }>>([]);
  const [statusText, setStatusText] = useState("Checking…");
  const [view, setView] = useState<"dashboard" | "shell">("dashboard");

  const refresh = useCallback(async () => {
    const [health, agentList, status] = await Promise.all([
      fetchNoahubaiHealth(),
      fetchNoahubaiAgents(),
      fetchNoahubaiStatus(),
    ]);
    const isOnline = health?.status === "healthy" || health?.status === "ok";
    setOnline(isOnline);
    setAgents(agentList);
    setStatusText(
      status
        ? `Agents: ${Object.keys((status.agents as object) ?? {}).length || agentList.length} · Issues tracked`
        : isOnline
          ? "Noahubai online"
          : "Start Noahubai: python main.py (port 8000)",
    );
    if (isOnline) {
      await syncAllAgents();
      await postAgentEvent("noahubai-core", "sync", { agentCount: agentList.length });
    }
  }, []);

  useEffect(() => {
    void refresh();
    const t = setInterval(() => void refresh(), 12000);
    return () => clearInterval(t);
  }, [refresh]);

  return (
    <div className="app-panel" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <h2>NOAHUBAI</h2>
      <p>Unified AI — memory, issue tracking, auto-fix. Synced with AI Hub agents.</p>
      <div className="status-row">
        <span className={`pill ${online ? "online" : "offline"}`}>
          {online ? "ONLINE" : "OFFLINE"}
        </span>
        <span className="pill">{statusText}</span>
      </div>
      <div className="btn-row">
        <button type="button" className="btn" onClick={() => void refresh()}>
          Sync now
        </button>
        <button
          type="button"
          className={`btn ${view === "dashboard" ? "" : "secondary"}`}
          onClick={() => setView("dashboard")}
        >
          Dashboard
        </button>
        <button
          type="button"
          className={`btn ${view === "shell" ? "" : "secondary"}`}
          onClick={() => setView("shell")}
        >
          Full UI
        </button>
      </div>

      {view === "shell" ? (
        <iframe
          className="embed-frame"
          src={noahubaiUiUrl()}
          title="Noahubai Desktop Shell"
        />
      ) : (
        <div className="agent-grid" style={{ flex: 1, overflow: "auto" }}>
          {agents.length === 0 ? (
            <p style={{ opacity: 0.7 }}>
              No backend agents detected. Run Noahubai from the repo root:{" "}
              <code>python main.py</code>
            </p>
          ) : (
            agents.map((a) => (
              <div key={a.name} className="agent-card" style={{ borderLeft: "4px solid #6366f1" }}>
                <h4>{a.name.replace(/_/g, " ")}</h4>
                <small>{a.state ?? a.status ?? "unknown"}</small>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
