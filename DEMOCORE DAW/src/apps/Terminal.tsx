import { useState } from "react";

const LINES = [
  "DEMOCORE OS Terminal v1.0",
  "Type 'help' for commands.",
  "",
];

export default function Terminal() {
  const [lines, setLines] = useState<string[]>(LINES);
  const [input, setInput] = useState("");

  const run = (cmd: string) => {
    const c = cmd.trim().toLowerCase();
    let out = "";
    if (c === "help") {
      out = "Commands: help, clear, sync, noahubai, aihub, bridge, daw";
    } else if (c === "clear") {
      setLines([]);
      return;
    } else if (c === "sync") {
      out = "Agent sync triggered — check Agents Manager.";
    } else if (c === "noahubai") {
      out = "NOAHUBAI → http://127.0.0.1:8000 (memory, issues, fixer agents)";
    } else if (c === "aihub") {
      out = "AI Hub → http://127.0.0.1:8765 (Cursor bridge + providers)";
    } else if (c === "bridge" || c === "osbridge") {
      out = "OS Bridge (WinBridge) → http://127.0.0.1:9778 (host files + vault)";
    } else if (c === "daw") {
      out = "DEMOCORE DAW — audio workstation app loaded.";
    } else if (c) {
      out = `Unknown command: ${cmd}`;
    }
    setLines((prev) => [...prev, `$ ${cmd}`, out].filter(Boolean));
  };

  return (
    <div className="app-panel">
      <h2>Terminál</h2>
      <div className="terminal-box">{lines.join("\n")}</div>
      <input
        style={{
          width: "100%",
          marginTop: 8,
          padding: 8,
          borderRadius: 8,
          border: "1px solid rgba(255,255,255,0.12)",
          background: "#050810",
          color: "#fff",
        }}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            run(input);
            setInput("");
          }
        }}
        placeholder="Enter command…"
      />
    </div>
  );
}
