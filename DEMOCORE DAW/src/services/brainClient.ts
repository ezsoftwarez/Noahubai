const AIHUB_BRIDGE_BASE = "/aihub-bridge";

export interface BrainAutoResult {
  ok: boolean;
  blended?: string;
  error?: string;
  route?: string;
  models?: string[];
}

export async function brainAuto(prompt: string, opts?: { engineCombo?: string }): Promise<BrainAutoResult> {
  try {
    const res = await fetch(`${AIHUB_BRIDGE_BASE}/api/brain/auto`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        auto: true,
        engineCombo: opts?.engineCombo ?? "multi",
      }),
      signal: AbortSignal.timeout(120000),
    });
    const data = (await res.json()) as BrainAutoResult & { error?: string };
    if (!res.ok) {
      return { ok: false, error: data.error ?? `HTTP ${res.status}` };
    }
    return data;
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Brain request failed" };
  }
}
