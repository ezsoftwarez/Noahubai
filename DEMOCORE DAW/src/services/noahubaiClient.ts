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

export async function fetchBrainConfig(): Promise<Record<string, unknown> | null> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/brain/config`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return null;
    return (await res.json()) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export async function fetchBrainAgents(): Promise<Array<Record<string, string>>> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/brain/agents`, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return [];
    const data = (await res.json()) as { agents?: Array<Record<string, string>> };
    return data.agents ?? [];
  } catch {
    return [];
  }
}

export async function saveBrainAgent(agent: Record<string, string>): Promise<boolean> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/brain/agents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function uploadDevicesToBrain(): Promise<number> {
  try {
    const syncRes = await fetch(`${AIHUB_BRIDGE_BASE}/api/bridge/agents/sync`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!syncRes.ok) return -1;
    const sync = (await syncRes.json()) as { agents?: Array<Record<string, unknown>> };
    const devices = (sync.agents ?? []).map((a) => ({
      id: String(a.id ?? ""),
      name: String(a.name ?? ""),
      source: String(a.source ?? "sync"),
      status: String(a.status ?? "online"),
      color: String(a.color ?? "#6366f1"),
      description: String(a.description ?? ""),
    }));
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/brain/devices/upload`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ devices, source: "democore-agents-manager" }),
    });
    if (!res.ok) return -1;
    const data = (await res.json()) as { devices?: unknown[] };
    return data.devices?.length ?? devices.length;
  } catch {
    return -1;
  }
}
