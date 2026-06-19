import { useEffect, useState } from "react";
import Desktop from "./os/Desktop";
import { startAgentSyncPoll } from "./services/agentSync";

export default function App() {
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setBooting(false), 1900);
    const stopSync = startAgentSyncPoll(15000);
    return () => {
      clearTimeout(t);
      stopSync();
    };
  }, []);

  return (
    <>
      {booting && (
        <div className={`boot-screen ${booting ? "" : "done"}`}>
          <div className="boot-logo">DEMOCORE OS</div>
          <p style={{ opacity: 0.7, marginBottom: 16 }}>Loading NOAHUBAI + AI Hub sync…</p>
          <div className="boot-bar">
            <span />
          </div>
        </div>
      )}
      <Desktop />
    </>
  );
}
