import { useEffect, useState } from "react";
import { fetchBridgeStatus } from "../services/noahubaiClient";
import {
  buildTranscriptFromMessages,
  deleteSummary,
  fetchCursorSessions,
  fetchSessionMessages,
  loadSavedSummaries,
  saveSummary,
  summarizeTranscript,
  type CursorSession,
  type SavedSummary,
} from "../services/summarizerClient";

type SourceMode = "paste" | "cursor";

export default function Summarizer() {
  const [online, setOnline] = useState(false);
  const [mode, setMode] = useState<SourceMode>("paste");
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("Paste a chat or load a Cursor session");
  const [sessions, setSessions] = useState<CursorSession[]>([]);
  const [selectedSession, setSelectedSession] = useState("");
  const [saved, setSaved] = useState<SavedSummary[]>([]);

  const refresh = async () => {
    const bridge = await fetchBridgeStatus();
    setOnline(bridge?.ok === true);
    if (bridge?.ok) {
      const list = await fetchCursorSessions();
      setSessions(list);
    }
    setSaved(loadSavedSummaries());
  };

  useEffect(() => {
    void refresh();
  }, []);

  const loadSession = async (sessionId: string) => {
    setSelectedSession(sessionId);
    setBusy(true);
    setStatus("Loading Cursor transcript…");
    const session = sessions.find((s) => s.sessionId === sessionId);
    const messages = await fetchSessionMessages(sessionId);
    const text = buildTranscriptFromMessages(
      messages,
      session?.preview?.slice(0, 60) || sessionId,
    );
    setTranscript(text);
    setBusy(false);
    setStatus(text ? `Loaded ${messages.length} messages` : "Session empty or unavailable");
  };

  const runSummarize = async () => {
    if (!transcript.trim()) {
      setStatus("Add transcript text first");
      return;
    }
    setBusy(true);
    setSummary("");
    setStatus("Summarizing with AI Hub Brain…");
    const result = await summarizeTranscript(transcript);
    setBusy(false);
    if (!result.ok || !result.text) {
      setStatus(result.error ?? "Failed");
      return;
    }
    setSummary(result.text);
    setStatus("Summary ready");
  };

  const handleSave = () => {
    if (!summary) return;
    const title =
      mode === "cursor" && selectedSession
        ? `Cursor ${selectedSession.slice(0, 8)}`
        : `Paste ${new Date().toLocaleDateString()}`;
    saveSummary({ title, source: mode, text: summary });
    setSaved(loadSavedSummaries());
    setStatus("Saved to local history");
  };

  return (
    <div className="app-panel summarizer-app">
      <h2>Summarizer</h2>
      <p>Summarize multi-agent chats — paste a transcript or load from Cursor via AI Hub Bridge.</p>

      <div className="status-row">
        <span className={`pill ${online ? "online" : "offline"}`}>
          AI Hub {online ? "online" : "offline"}
        </span>
      </div>

      <div className="btn-row">
        <button type="button" className={`btn ${mode === "paste" ? "" : "secondary"}`} onClick={() => setMode("paste")}>
          Paste chat
        </button>
        <button
          type="button"
          className={`btn ${mode === "cursor" ? "" : "secondary"}`}
          onClick={() => setMode("cursor")}
          disabled={!online}
        >
          Cursor sessions
        </button>
        <button type="button" className="btn" disabled={busy || !transcript.trim()} onClick={() => void runSummarize()}>
          {busy ? "Summarizing…" : "Summarize"}
        </button>
        <button type="button" className="btn secondary" disabled={!summary} onClick={handleSave}>
          Save
        </button>
        <button type="button" className="btn secondary" disabled={!summary} onClick={() => void navigator.clipboard.writeText(summary)}>
          Copy
        </button>
      </div>

      <p style={{ fontSize: 12, opacity: 0.75 }}>{status}</p>

      <div className="summarizer-layout">
        <div className="summarizer-pane">
          {mode === "cursor" && (
            <select
              value={selectedSession}
              onChange={(e) => void loadSession(e.target.value)}
              style={{
                width: "100%",
                marginBottom: 8,
                padding: 8,
                borderRadius: 8,
                background: "#050810",
                color: "#fff",
                border: "1px solid rgba(255,255,255,0.12)",
              }}
            >
              <option value="">Select Cursor session…</option>
              {sessions.map((s) => (
                <option key={s.sessionId} value={s.sessionId}>
                  {s.preview.slice(0, 50) || s.sessionId} ({s.messageCount})
                </option>
              ))}
            </select>
          )}
          <textarea
            className="summarizer-textarea"
            placeholder="Paste chat transcript here (User / Assistant lines)…"
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
          />
        </div>
        <div className="summarizer-pane">
          <h4>Summary</h4>
          <pre className="bridge-preview summarizer-output">{summary || (busy ? "Working…" : "Summary appears here")}</pre>
        </div>
      </div>

      {saved.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <h4 style={{ fontSize: 12, opacity: 0.7, margin: "0 0 8px" }}>Saved summaries</h4>
          <ul className="bridge-list">
            {saved.slice(0, 8).map((s) => (
              <li key={s.id}>
                <button type="button" onClick={() => setSummary(s.text)}>
                  {s.title} · {new Date(s.createdAt).toLocaleString()}
                </button>
                <button type="button" className="btn secondary small" onClick={() => { deleteSummary(s.id); setSaved(loadSavedSummaries()); }}>
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
