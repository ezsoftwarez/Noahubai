export default function Settings() {
  return (
    <div className="app-panel">
      <h2>Beállítások</h2>
      <p>Service URLs (defaults for local development):</p>
      <ul style={{ fontSize: 13, lineHeight: 1.8 }}>
        <li>
          <strong>DEMOCORE OS</strong> — http://127.0.0.1:5173
        </li>
        <li>
          <strong>NOAHUBAI</strong> — http://127.0.0.1:8000
        </li>
        <li>
          <strong>AI Hub Bridge</strong> — http://127.0.0.1:8765
        </li>
        <li>
          <strong>Ollama</strong> — http://127.0.0.1:11434
        </li>
      </ul>
      <p style={{ fontSize: 12, opacity: 0.7 }}>
        Windows path: C:\Users\krake\OneDrive\Asztali gép\DEMOCORE DAW
      </p>
    </div>
  );
}
