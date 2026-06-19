import type { AgentSyncState, SyncedAgent } from "../os/types";
import {
  fetchBridgeStatus,
  fetchNoahubaiAgents,
  fetchNoahubaiHealth,
  fetchUnifiedAgentSync,
} from "./noahubaiClient";

export const SYNC_STORAGE_KEY = "democore-agent-sync-v1";
export const SYNC_EVENT = "democore-agent-sync";

const NOAHUBAI_COLORS: Record<string, string> = {
  memory_agent: "#6366f1",
  issue_agent: "#ec4899",
  fixer_agent: "#10b981",
};

const AIHUB_AGENTS: SyncedAgent[] = [
  { id: "gpt", name: "GPT", source: "aihub", status: "online", color: "#4ade80", description: "OpenAI", lastSync: 0 },
  { id: "claude", name: "Claude", source: "aihub", status: "online", color: "#f97316", description: "Anthropic", lastSync: 0 },
  { id: "codex", name: "Codex", source: "aihub", status: "online", color: "#15803d", description: "OpenAI Codex", lastSync: 0 },
  { id: "cursor-agent", name: "Cursor Agent", source: "aihub", status: "online", color: "#e5e5e5", description: "Cursor bridge", lastSync: 0 },
  { id: "ollama", name: "Ollama", source: "aihub", status: "offline", color: "#00ff88", description: "Local models", lastSync: 0 },
];

export function loadLocalSync(): AgentSyncState | null {
  try {
    const raw = localStorage.getItem(SYNC_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AgentSyncState) : null;
  } catch {
    return null;
  }
}

export function saveLocalSync(state: AgentSyncState): void {
  localStorage.setItem(SYNC_STORAGE_KEY, JSON.stringify(state));
  window.dispatchEvent(new CustomEvent(SYNC_EVENT, { detail: state }));
}

function mapNoahubaiAgents(agents: Awaited<ReturnType<typeof fetchNoahubaiAgents>>, now: number): SyncedAgent[] {
  return agents.map((a) => ({
    id: `noahubai-${a.name}`,
    name: a.name.replace(/_/g, " "),
    source: "noahubai" as const,
    status: a.status === "running" || a.status === "active" || a.state === "running" || a.state === "ready"
      ? "online"
      : "offline",
    color: NOAHUBAI_COLORS[a.name] ?? "#7367ff",
    description: "Noahubai backend agent",
    lastSync: now,
  }));
}

export async function syncAllAgents(): Promise<AgentSyncState> {
  const now = Date.now();
  const [health, noahAgents, bridge, unified] = await Promise.all([
    fetchNoahubaiHealth(),
    fetchNoahubaiAgents(),
    fetchBridgeStatus(),
    fetchUnifiedAgentSync(),
  ]);

  const noahubaiOnline = health?.status === "healthy" || health?.status === "ok";
  const aihubOnline = bridge?.ok === true;

  let agents: SyncedAgent[] = [];

  if (unified && Array.isArray(unified.agents)) {
    agents = unified.agents as SyncedAgent[];
  } else {
    agents = [
      ...mapNoahubaiAgents(noahAgents, now),
      ...AIHUB_AGENTS.map((a) => ({
        ...a,
        status: aihubOnline ? a.status : "offline",
        lastSync: now,
      })),
      {
        id: "noahubai-core",
        name: "NOAHUBAI Core",
        source: "noahubai",
        status: noahubaiOnline ? "online" : "offline",
        color: "#6366f1",
        description: "Unified memory, issue tracking, auto-fix",
        lastSync: now,
      },
    ];
  }

  const state: AgentSyncState = {
    version: 1,
    updatedAt: now,
    agents,
    noahubaiOnline,
    aihubOnline,
  };

  saveLocalSync(state);
  return state;
}

let pollTimer: ReturnType<typeof setInterval> | null = null;

export function startAgentSyncPoll(intervalMs = 15000): () => void {
  void syncAllAgents();
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => void syncAllAgents(), intervalMs);
  return () => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  };
}

export function subscribeAgentSync(cb: (state: AgentSyncState) => void): () => void {
  const handler = (e: Event) => {
    const detail = (e as CustomEvent<AgentSyncState>).detail;
    if (detail) cb(detail);
  };
  window.addEventListener(SYNC_EVENT, handler);
  const existing = loadLocalSync();
  if (existing) cb(existing);
  return () => window.removeEventListener(SYNC_EVENT, handler);
}
