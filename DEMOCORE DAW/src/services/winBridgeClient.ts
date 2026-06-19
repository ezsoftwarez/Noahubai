const WIN_BRIDGE_BASE = "/win-bridge";

export interface WinBridgeStatus {
  ok: boolean;
  service?: string;
  platform?: string;
  port?: number;
  vaultCount?: number;
  pyautogui?: boolean;
  repo?: string;
}

export interface FsEntry {
  name: string;
  path: string;
  type: "file" | "folder";
  size: number;
  mtime: number;
}

export interface FsListResult {
  path: string;
  parent: string | null;
  entries: FsEntry[];
}

export interface VaultItem {
  id: string;
  kind: "file" | "folder";
  name: string;
  sourcePath: string;
  loadedAt: string;
  size?: number;
  entryCount?: number;
  mime?: string;
  skipped?: boolean;
  reason?: string;
}

export interface VaultListResult {
  count: number;
  items: VaultItem[];
}

export interface ReadFileResult {
  path: string;
  size: number;
  truncated: boolean;
  mime: string;
  text: boolean;
  content: string | null;
}

async function bridgeFetch<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(`${WIN_BRIDGE_BASE}${path}`, {
      ...init,
      signal: AbortSignal.timeout(8000),
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchWinBridgeStatus(): Promise<WinBridgeStatus | null> {
  return bridgeFetch<WinBridgeStatus>("/api/os-bridge/status");
}

export async function fetchRoots(): Promise<{ name: string; path: string }[]> {
  const data = await bridgeFetch<{ roots: { name: string; path: string }[] }>(
    "/api/os-bridge/roots",
  );
  return data?.roots ?? [];
}

export async function listPath(path: string): Promise<FsListResult | null> {
  const q = encodeURIComponent(path);
  return bridgeFetch<FsListResult>(`/api/os-bridge/list?path=${q}`);
}

export async function readPath(path: string): Promise<ReadFileResult | null> {
  const q = encodeURIComponent(path);
  return bridgeFetch<ReadFileResult>(`/api/os-bridge/read?path=${q}`);
}

export async function loadIntoVault(
  path: string,
  recursive = false,
): Promise<{ ok: boolean; loaded?: VaultItem[] } | null> {
  return bridgeFetch("/api/os-bridge/load", {
    method: "POST",
    body: JSON.stringify({ path, recursive }),
  });
}

export async function fetchVault(): Promise<VaultListResult | null> {
  return bridgeFetch<VaultListResult>("/api/os-bridge/vault");
}

export async function removeVaultItem(id: string): Promise<boolean> {
  const data = await bridgeFetch<{ ok: boolean }>("/api/os-bridge/vault/remove", {
    method: "POST",
    body: JSON.stringify({ id }),
  });
  return data?.ok === true;
}

export async function openHostPath(path: string): Promise<boolean> {
  const data = await bridgeFetch<{ ok: boolean }>("/api/os-bridge/open", {
    method: "POST",
    body: JSON.stringify({ path }),
  });
  return data?.ok === true;
}

export function winBridgeUrl(): string {
  return `${WIN_BRIDGE_BASE}/`;
}
