import { useCallback, useEffect, useState } from "react";
import {
  fetchRoots,
  fetchWinBridgeStatus,
  listPath,
  type FsEntry,
} from "../services/winBridgeClient";

export default function Files() {
  const [online, setOnline] = useState(false);
  const [path, setPath] = useState("");
  const [parent, setParent] = useState<string | null>(null);
  const [entries, setEntries] = useState<FsEntry[]>([]);
  const [hint, setHint] = useState("Loading…");

  const loadDir = useCallback(async (dir: string) => {
    const data = await listPath(dir);
    if (!data) {
      setHint("Could not list folder — is WinBridge running?");
      return;
    }
    setPath(data.path);
    setParent(data.parent);
    setEntries(data.entries);
    setHint(data.path);
  }, []);

  useEffect(() => {
    void (async () => {
      const st = await fetchWinBridgeStatus();
      setOnline(st?.ok === true);
      if (!st?.ok) {
        setHint("WinBridge offline — run RUN-WINBRIDGE.bat (port 9778)");
        return;
      }
      const roots = await fetchRoots();
      if (roots[0]) await loadDir(roots[0].path);
    })();
  }, [loadDir]);

  return (
    <div className="app-panel">
      <h2>Fájlkezelő</h2>
      <p>Host filesystem via OS Bridge (WinBridge :9778).</p>

      <div className="status-row">
        <span className={`pill ${online ? "online" : "offline"}`}>
          WinBridge {online ? "online" : "offline"}
        </span>
      </div>

      <div className="btn-row">
        <button type="button" className="btn secondary" disabled={!parent} onClick={() => parent && void loadDir(parent)}>
          Up
        </button>
        <button type="button" className="btn secondary" disabled={!online} onClick={() => path && void loadDir(path)}>
          Refresh
        </button>
      </div>

      <p style={{ fontSize: 11, opacity: 0.7, wordBreak: "break-all" }}>{hint}</p>

      {online ? (
        <ul className="bridge-list files-only">
          {entries.map((f) => (
            <li key={f.path}>
              <button
                type="button"
                onClick={() => f.type === "folder" && void loadDir(f.path)}
                onDoubleClick={() => f.type === "folder" && void loadDir(f.path)}
              >
                {f.type === "folder" ? "📁" : "📄"} {f.name}
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, opacity: 0.6 }}>
          <li>📁 DEMOCORE DAW/</li>
          <li>📁 AI HUB oVerk1LL/</li>
          <li>📄 main.py</li>
          <li style={{ fontSize: 12, marginTop: 8 }}>Static preview — start WinBridge for live host files.</li>
        </ul>
      )}
    </div>
  );
}
