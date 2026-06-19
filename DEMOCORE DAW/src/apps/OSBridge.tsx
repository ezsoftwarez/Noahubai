import { useCallback, useEffect, useState } from "react";
import {
  fetchRoots,
  fetchVault,
  fetchWinBridgeStatus,
  listPath,
  loadIntoVault,
  openHostPath,
  readPath,
  removeVaultItem,
  type FsEntry,
  type VaultItem,
} from "../services/winBridgeClient";

function fmtSize(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function OSBridge() {
  const [online, setOnline] = useState(false);
  const [platform, setPlatform] = useState("");
  const [currentPath, setCurrentPath] = useState("");
  const [parent, setParent] = useState<string | null>(null);
  const [entries, setEntries] = useState<FsEntry[]>([]);
  const [selected, setSelected] = useState<FsEntry | null>(null);
  const [preview, setPreview] = useState("");
  const [vault, setVault] = useState<VaultItem[]>([]);
  const [status, setStatus] = useState("Connect WinBridge on port 9778");

  const refreshVault = useCallback(async () => {
    const data = await fetchVault();
    setVault(data?.items ?? []);
  }, []);

  const browse = useCallback(async (path: string) => {
    const data = await listPath(path);
    if (!data) {
      setStatus("List failed — check path or permissions");
      return;
    }
    setCurrentPath(data.path);
    setParent(data.parent);
    setEntries(data.entries);
    setSelected(null);
    setPreview("");
    setStatus(data.path);
  }, []);

  const bootstrap = useCallback(async () => {
    const st = await fetchWinBridgeStatus();
    setOnline(st?.ok === true);
    setPlatform(st?.platform ?? "");
    if (!st?.ok) {
      setStatus("Offline — run RUN-WINBRIDGE.bat or START-DEMOCORE.bat");
      return;
    }
    await refreshVault();
    const roots = await fetchRoots();
    if (roots[0]) {
      await browse(roots[0].path);
    }
    setStatus(`Connected · vault ${st.vaultCount ?? 0} items`);
  }, [browse, refreshVault]);

  useEffect(() => {
    void bootstrap();
    const t = setInterval(() => void bootstrap(), 15000);
    return () => clearInterval(t);
  }, [bootstrap]);

  const onSelect = async (entry: FsEntry) => {
    setSelected(entry);
    if (entry.type === "folder") {
      setPreview(`Folder · ${entry.path}`);
      return;
    }
    const data = await readPath(entry.path);
    if (!data) {
      setPreview("(could not read file)");
      return;
    }
    if (data.text && data.content) {
      setPreview(data.truncated ? `${data.content}\n\n… truncated` : data.content);
    } else {
      setPreview(`Binary file · ${fmtSize(data.size)} · ${data.mime}`);
    }
  };

  const onOpen = (entry: FsEntry) => {
    if (entry.type === "folder") {
      void browse(entry.path);
    } else {
      void onSelect(entry);
    }
  };

  const onLoad = async (recursive: boolean) => {
    if (!selected) {
      setStatus("Select a file or folder first");
      return;
    }
    const res = await loadIntoVault(selected.path, recursive);
    if (!res?.ok) {
      setStatus("Load failed");
      return;
    }
    setStatus(`Loaded ${res.loaded?.length ?? 0} item(s) into vault`);
    await refreshVault();
  };

  return (
    <div className="app-panel os-bridge">
      <h2>OS Bridge</h2>
      <p>Host file access via WinBridge — load files and folders into the vault for DEMOCORE apps.</p>

      <div className="status-row">
        <span className={`pill ${online ? "online" : "offline"}`}>
          WinBridge {online ? "online" : "offline"}
        </span>
        {platform && <span className="pill">{platform}</span>}
        <span className="pill">:9778</span>
      </div>

      <p style={{ fontSize: 12, opacity: 0.8 }}>{status}</p>

      <div className="btn-row">
        <button type="button" className="btn" disabled={!online} onClick={() => void bootstrap()}>
          Refresh
        </button>
        <button
          type="button"
          className="btn secondary"
          disabled={!online || !parent}
          onClick={() => parent && void browse(parent)}
        >
          Up
        </button>
        <button type="button" className="btn" disabled={!online || !selected} onClick={() => void onLoad(false)}>
          Load file
        </button>
        <button
          type="button"
          className="btn"
          disabled={!online || !selected || selected.type !== "folder"}
          onClick={() => void onLoad(true)}
        >
          Load folder
        </button>
        {currentPath && (
          <button type="button" className="btn secondary" onClick={() => void openHostPath(currentPath)}>
            Open in Explorer
          </button>
        )}
      </div>

      <div className="bridge-layout">
        <div className="bridge-pane">
          <h4>Host files</h4>
          <div className="bridge-path">{currentPath || "—"}</div>
          <ul className="bridge-list">
            {entries.map((e) => (
              <li key={e.path}>
                <button
                  type="button"
                  className={selected?.path === e.path ? "active" : ""}
                  onClick={() => void onSelect(e)}
                  onDoubleClick={() => onOpen(e)}
                >
                  {e.type === "folder" ? "📁" : "📄"} {e.name}
                  {e.type === "file" && <small> {fmtSize(e.size)}</small>}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="bridge-pane">
          <h4>Preview</h4>
          <pre className="bridge-preview">{preview || "Select a file to preview"}</pre>
        </div>

        <div className="bridge-pane">
          <h4>Loaded vault ({vault.length})</h4>
          <ul className="bridge-list">
            {vault.map((v) => (
              <li key={v.id}>
                <span>
                  [{v.kind}] {v.name}
                </span>
                <button type="button" className="btn secondary small" onClick={() => void removeVaultItem(v.id).then(refreshVault)}>
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {!online && (
        <p style={{ fontSize: 12, marginTop: 12 }}>
          Start <code>RUN-WINBRIDGE.bat</code> from the repo root, or use <code>START-DEMOCORE.bat</code> which
          starts WinBridge automatically.
        </p>
      )}
    </div>
  );
}
