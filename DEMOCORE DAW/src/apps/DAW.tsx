export default function DAW() {
  return (
    <div className="app-panel">
      <h2>DEMOCORE DAW</h2>
      <p>Web-alapú digitális audio munkaállomás — integrálva az AI agent hálózattal.</p>
      <div className="daw-grid">
        <div className="daw-tracks">
          <strong>Tracks</strong>
          {["Drums", "Bass", "Synth", "Vox"].map((t) => (
            <div key={t} className="track-row">
              {t}
            </div>
          ))}
        </div>
        <div className="daw-timeline" />
        <div className="daw-mixer">
          <strong>Mixer</strong>
          {["Kick", "Snare", "Hat", "Master"].map((c) => (
            <div key={c} style={{ marginTop: 10 }}>
              <div style={{ fontSize: 11, marginBottom: 4 }}>{c}</div>
              <div
                style={{
                  height: 80,
                  width: 24,
                  background: "linear-gradient(180deg, #6366f1, #00ffee)",
                  borderRadius: 4,
                  opacity: 0.7,
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
