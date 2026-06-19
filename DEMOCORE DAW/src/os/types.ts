export type AppId =
  | "daw"
  | "noahubai"
  | "noahubai-og"
  | "aihub"
  | "agentsmanager"
  | "agentbuilder"
  | "terminal"
  | "files"
  | "osbridge"
  | "settings";

export interface AppDefinition {
  id: AppId;
  title: string;
  icon: string;
  description: string;
  defaultSize: { width: number; height: number };
}

export interface WindowState {
  id: string;
  appId: AppId;
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  minimized: boolean;
  zIndex: number;
}

export interface SyncedAgent {
  id: string;
  name: string;
  source: "noahubai" | "aihub" | "democore";
  status: "online" | "offline" | "busy";
  color: string;
  description: string;
  lastSync: number;
}

export interface AgentSyncState {
  version: number;
  updatedAt: number;
  agents: SyncedAgent[];
  noahubaiOnline: boolean;
  aihubOnline: boolean;
}
