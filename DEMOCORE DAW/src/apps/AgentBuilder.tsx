import { useEffect, useState } from "react";
import {
  fetchBrainAgents,
  fetchBrainConfig,
  saveBrainAgent,
  uploadDevicesToBrain,
} from "../services/noahubaiClient";

const BLOCKBUSTER_MODELS = [
  "deepseek/deepseek-chat:free",
  "meta-llama/llama-3.2-3b-instruct:free",
  "google/gemma-2-9b-it:free",
  "mistralai/mistral-7b-instruct:free",
];

export default function AgentBuilder() {
  const [name, setName] = useState("");
  const [model, setModel] = useState(BLOCKBUSTER_MODELS[0]);
  const [prompt, setPrompt] = useState("You are a specialized DEMOCORE agent.");
  const [agents, setAgents] = useState<Array<Record<string, string>>>([]);
  const [status, setStatus] = useState("Ready");

  const refresh = async () => {
    await fetchBrainConfig();
    const list = await fetchBrainAgents();
    setAgents(list);
  };

  useEffect(() => {
    void refresh();
  }, []);

  const handleSave = async () => {
    if (!name.trim()) {
      setStatus("Name required");
      return;
    }
    const ok = await saveBrainAgent({
      name: name.trim(),
      model,
      systemPrompt: prompt,
      source: "democore-builder",
    });
    setStatus(ok ? `Saved ${name}` : "Save failed — is AI Hub bridge running?");
    if (ok) {
      setName("");
      await refresh();
    }
  };

  const handleUploadDevices = async () => {
    setStatus("Uploading synced devices to brain…");
    const n = await uploadDevicesToBrain();
    setStatus(n >= 0 ? `Uploaded ${n} devices to AI Hub Brain` : "Upload failed");
  };

  return (
    <div className="app-panel">
      <h2>Agent Builder</h2>
      <p>
        Build custom agents with <strong>Blockbuster</strong> free models. Saved agents sync to AI Hub Brain and
        blend with Auto mode.
      </p>
      <p className="pill" style={{ display: "inline-block", marginBottom: 12 }}>
        {status}
      </p>

      <div className="field" style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 12, opacity: 0.7 }}>Agent name</label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="CODEER-01"
          style={{
            width: "100%",
            padding: 8,
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.12)",
            background: "#050810",
            color: "#fff",
          }}
        />
      </div>

      <div className="field" style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 12, opacity: 0.7 }}>Blockbuster model</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          style={{
            width: "100%",
            padding: 8,
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.12)",
            background: "#050810",
            color: "#fff",
          }}
        >
          {BLOCKBUSTER_MODELS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      <div className="field" style={{ marginBottom: 10 }}>
        <label style={{ fontSize: 12, opacity: 0.7 }}>System prompt</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          style={{
            width: "100%",
            padding: 8,
            borderRadius: 8,
            border: "1px solid rgba(255,255,255,0.12)",
            background: "#050810",
            color: "#fff",
          }}
        />
      </div>

      <div className="btn-row">
        <button type="button" className="btn" onClick={() => void handleSave()}>
          Save to Brain
        </button>
        <button type="button" className="btn secondary" onClick={() => void handleUploadDevices()}>
          Upload synced devices
        </button>
        <button type="button" className="btn secondary" onClick={() => void refresh()}>
          Refresh
        </button>
      </div>

      <h3 style={{ fontSize: 13, marginTop: 16, opacity: 0.7 }}>Built agents</h3>
      <div className="agent-grid">
        {agents.length === 0 ? (
          <p style={{ opacity: 0.6, fontSize: 12 }}>No agents in brain yet.</p>
        ) : (
          agents.map((a) => (
            <div key={a.id} className="agent-card" style={{ borderLeft: "4px solid #c084fc" }}>
              <h4>{a.name}</h4>
              <small>{a.model}</small>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
