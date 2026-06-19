import type { AppDefinition } from "./types";

export const APPS: AppDefinition[] = [
  {
    id: "daw",
    title: "DEMOCORE DAW",
    icon: "🎹",
    description: "Digital audio workstation",
    defaultSize: { width: 960, height: 620 },
  },
  {
    id: "noahubai",
    title: "NOAHUBAI",
    icon: "🧠",
    description: "Memory, issues, auto-fix agents",
    defaultSize: { width: 1100, height: 720 },
  },
  {
    id: "aihub",
    title: "AI Hub",
    icon: "🌉",
    description: "Bridge between Cursor and AI providers",
    defaultSize: { width: 1200, height: 760 },
  },
  {
    id: "agentsmanager",
    title: "Agents Manager",
    icon: "🤖",
    description: "Unified agent sync dashboard",
    defaultSize: { width: 900, height: 640 },
  },
  {
    id: "agentbuilder",
    title: "Agent Builder",
    icon: "🛠️",
    description: "Build custom agents for AI Hub Brain",
    defaultSize: { width: 820, height: 600 },
  },
  {
    id: "terminal",
    title: "Terminál",
    icon: "⌨️",
    description: "brOS shell",
    defaultSize: { width: 720, height: 420 },
  },
  {
    id: "files",
    title: "Fájlkezelő",
    icon: "📁",
    description: "Project files",
    defaultSize: { width: 680, height: 480 },
  },
  {
    id: "settings",
    title: "Beállítások",
    icon: "⚙️",
    description: "OS and bridge settings",
    defaultSize: { width: 560, height: 480 },
  },
];

export function getApp(id: string): AppDefinition | undefined {
  return APPS.find((a) => a.id === id);
}
