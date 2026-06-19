import { brainAuto } from "./brainClient";

const AIHUB_BRIDGE_BASE = "/aihub-bridge";

export const SUMMARIZE_SYSTEM_PROMPT =
  "You summarize a multi-agent AI project chat for the user. The transcript includes the user and various AI assistants (GPT, Claude, Codex, Cursor, Ollama, etc.). Write a clear structured summary in markdown with these sections:\n\n" +
  "## What we worked on\n## Outcomes & decisions\n## Artifacts (files, code, snippets mentioned)\n## Open questions / next steps\n\n" +
  "Be factual — only include what appears in the transcript. Use bullet points. Stay under 700 words unless the thread is very long.";

export interface CursorSession {
  sessionId: string;
  projectSlug: string;
  preview: string;
  modified: string;
  messageCount: number;
  isThisWorkspace?: boolean;
}

export interface ChatMessage {
  role: string;
  text: string;
  source?: string;
}

const STORAGE_KEY = "democore-summaries";

export interface SavedSummary {
  id: string;
  title: string;
  source: string;
  text: string;
  createdAt: number;
}

export async function fetchCursorSessions(): Promise<CursorSession[]> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/bridge/cursor/sessions?limit=40`, {
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return [];
    const data = (await res.json()) as { sessions?: CursorSession[] };
    return data.sessions ?? [];
  } catch {
    return [];
  }
}

export async function fetchSessionMessages(sessionId: string): Promise<ChatMessage[]> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/bridge/cursor/sessions/${sessionId}/messages`, {
      signal: AbortSignal.timeout(15000),
    });
    if (!res.ok) return [];
    const data = (await res.json()) as { messages?: ChatMessage[] };
    return data.messages ?? [];
  } catch {
    return [];
  }
}

export function buildTranscriptFromMessages(
  messages: ChatMessage[],
  title = "Chat",
  maxMessages = 120,
  maxChars = 50000,
): string {
  const filtered = messages.filter((m) => m.role === "user" || m.role === "assistant");
  if (!filtered.length) return "";
  let slice = filtered;
  if (filtered.length > maxMessages) {
    slice = filtered.slice(0, 24).concat(filtered.slice(-(maxMessages - 24)));
  }
  const lines = [`Title: ${title}`, `Messages: ${filtered.length}`, "---"];
  let total = lines.join("\n").length;
  for (const m of slice) {
    const who = m.role === "user" ? "User" : m.source ?? "Assistant";
    let body = (m.text ?? "").trim();
    if (body.length > 1200) body = `${body.slice(0, 1200)}…`;
    const line = `[${who}]: ${body}`;
    if (total + line.length > maxChars) break;
    lines.push(line);
    total += line.length + 1;
  }
  return lines.join("\n");
}

export async function summarizeTranscript(transcript: string): Promise<{ ok: boolean; text?: string; error?: string }> {
  if (!transcript.trim()) {
    return { ok: false, error: "No transcript to summarize" };
  }
  const prompt = `${SUMMARIZE_SYSTEM_PROMPT}\n\nSummarize the following chat transcript:\n\n${transcript}`;
  const result = await brainAuto(prompt, { engineCombo: "multi" });
  if (!result.ok || !result.blended) {
    return { ok: false, error: result.error ?? "Summarization failed — start AI Hub Bridge (port 8765)" };
  }
  return { ok: true, text: result.blended };
}

export function loadSavedSummaries(): SavedSummary[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as SavedSummary[];
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

export function saveSummary(entry: Omit<SavedSummary, "id" | "createdAt">): SavedSummary {
  const list = loadSavedSummaries();
  const row: SavedSummary = {
    ...entry,
    id: `sum-${Date.now()}`,
    createdAt: Date.now(),
  };
  list.unshift(row);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, 30)));
  return row;
}

export function deleteSummary(id: string): void {
  const list = loadSavedSummaries().filter((s) => s.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}
