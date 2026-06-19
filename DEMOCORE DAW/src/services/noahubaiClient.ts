const NOAHUBAI_BASE = "/noahubai";
const AIHUB_BRIDGE_BASE = "/aihub-bridge";

export interface NoahubaiHealth {
  status: string;
  agents?: Record<string, unknown>;
  timestamp?: string;
}

export interface NoahubaiAgent {
  name: string;
  state?: string;
  status?: string;
  health?: Record<string, unknown>;
}

export async function fetchNoahubaiHealth(): Promise<NoahubaiHealth | null> {
  try {
    const res = await fetch(`${NOAHUBAI_BASE}/api/health`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) return null;
    return (await res.json()) as NoahubaiHealth;
  } catch {
    return null;
  }
}

export async function fetchNoahubaiAgents(): Promise<NoahubaiAgent[]> {
  try {
    const res = await fetch(`${NOAHUBAI_BASE}/api/agents`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) return [];
    const data = (await res.json()) as { agents?: NoahubaiAgent[] };
    return data.agents ?? [];
  } catch {
    return [];
  }
}

export async function fetchNoahubaiStatus(): Promise<Record<string, unknown> | null> {
  try {
    const res = await fetch(`${NOAHUBAI_BASE}/api/status`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) return null;
    return (await res.json()) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export function noahubaiUiUrl(): string {
  return `${NOAHUBAI_BASE}/`;
}

export async function fetchBridgeStatus(): Promise<{ ok: boolean } | null> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/bridge/status`, {
      signal: AbortSignal.timeout(4000),
    });
    if (!res.ok) return null;
    return (await res.json()) as { ok: boolean };
  } catch {
    return null;
  }
}

export async function fetchUnifiedAgentSync(): Promise<Record<string, unknown> | null> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/bridge/agents/sync`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return null;
    return (await res.json()) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export async function postAgentEvent(
  agentId: string,
  event: string,
  payload: Record<string, unknown> = {},
): Promise<boolean> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/bridge/agents/event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agentId, event, payload, source: "democore" }),
    });
    return res.ok;
  } catch {
    return false;
  }
}
