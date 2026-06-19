const FILES = [
  { name: "DEMOCORE DAW/", type: "folder" },
  { name: "noahubai/", type: "folder" },
  { name: "AI HUB oVerk1LL/", type: "folder" },
  { name: "main.py", type: "file" },
  { name: "dev.cmd", type: "file" },
  { name: "START-DEMOCORE.bat", type: "file" },
];

export default function Files() {
  return (
    <div className="app-panel">
      <h2>Fájlkezelő</h2>
      <p>Project layout — copy this folder to your OneDrive DEMOCORE DAW path.</p>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {FILES.map((f) => (
          <li
            key={f.name}
            style={{
              padding: "8px 12px",
              marginBottom: 4,
              borderRadius: 8,
              background: "rgba(255,255,255,0.04)",
            }}
          >
            {f.type === "folder" ? "📁" : "📄"} {f.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
