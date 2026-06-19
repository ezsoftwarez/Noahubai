const STORAGE_KEY = 'aihub-state-v1';
const NAV = [
  { id: 'bridge', icon: '🌉', label: 'Bridge' },
  { id: 'chats', icon: '💬', label: 'Chats' },
  { id: 'brain', icon: '🧠', label: 'Brain' },
  { id: 'pins', icon: '📌', label: 'Pins' },
  { id: 'agents', icon: '🤖', label: 'Agents' },
  { id: 'files', icon: '📄', label: 'Files' },
  { id: 'codes', icon: '🧊', label: 'Codes' },
  { id: 'build', icon: '🏗', label: 'Builder' },
  { id: 'pictures', icon: '🖼️', label: 'Pictures' }
];
/** Picture / image generator services (opensource-friendly where possible) */
const PICTURE_GENERATORS = [
  {
    id: 'pollinations',
    name: 'Pollinations',
    badge: 'FREE',
    desc: 'Instant URL images — no API key. Great for quick drafts.',
    openUrl: 'https://pollinations.ai/',
    buildUrl: p =>
      'https://image.pollinations.ai/prompt/' +
      encodeURIComponent(p) +
      '?width=1024&height=1024&nologo=true'
  },
  {
    id: 'openai',
    name: 'DALL·E 3',
    badge: 'API',
    desc: 'OpenAI image API — uses your key from Settings.',
    api: 'openai'
  },
  {
    id: 'sd-webui',
    name: 'Stable Diffusion WebUI',
    badge: 'LOCAL',
    desc: 'A1111 / Forge — run locally (typical port 7860).',
    openUrl: 'http://127.0.0.1:7860'
  },
  {
    id: 'comfyui',
    name: 'ComfyUI',
    badge: 'LOCAL',
    desc: 'Node-based SD workflows — localhost:8188.',
    openUrl: 'http://127.0.0.1:8188'
  },
  {
    id: 'hf-spaces',
    name: 'Hugging Face Spaces',
    badge: 'OSS',
    desc: 'Community text-to-image demos & models.',
    openUrl: 'https://huggingface.co/spaces?sort=trending&search=text-to-image'
  },
  {
    id: 'civitai',
    name: 'Civitai',
    badge: 'MODELS',
    desc: 'SD checkpoints, LoRAs, and example galleries.',
    openUrl: 'https://civitai.com/'
  },
  {
    id: 'leonardo',
    name: 'Leonardo.ai',
    badge: 'WEB',
    desc: 'Web UI with free tier for image generation.',
    openUrl: 'https://app.leonardo.ai/'
  },
  {
    id: 'ideogram',
    name: 'Ideogram',
    badge: 'WEB',
    desc: 'Strong text-in-image and logo layouts.',
    openUrl: 'https://ideogram.ai/'
  },
  {
    id: 'bing',
    name: 'Bing Image Creator',
    badge: 'WEB',
    desc: 'Microsoft Copilot image creation.',
    openUrl: 'https://www.bing.com/images/create'
  }
];
const LIBRARY_TABS = ['agents', 'folders', 'groups'];
const PROVIDERS = ['gpt', 'gemini', 'claude', 'codex', 'deepseek', 'grok'];
/** Agents with custom color pickers in Settings */
const COLORABLE_AGENTS = [
  'gpt',
  'gemini',
  'claude',
  'codex',
  'deepseek',
  'grok',
  'cursor-agent',
  'cursor-import',
  'you',
  'combined',
  'assistant',
  'ollama'
];
/** Default rainbow stops for Combined AIs (customizable in Settings) */
const DEFAULT_RAINBOW_STOPS = ['#4ade80', '#facc15', '#fb923c', '#f472b6', '#60a5fa', '#c084fc'];
/** Shown in chat color legend + quick filter chips */
const CHAT_LEGEND_AGENTS = [
  'you',
  'gpt',
  'claude',
  'codex',
  'gemini',
  'deepseek',
  'grok',
  'ollama',
  'cursor-import',
  'cursor-agent',
  'combined'
];
/** Detect AI brand from message metadata or text */
const BRAND_TEXT_HINTS = [
  ['gpt', /\b(gpt-4|gpt-3\.5|gpt-3|chatgpt|openai|o1-|o3-)\b/i],
  ['claude', /\b(claude|anthropic|sonnet|opus|haiku)\b/i],
  ['gemini', /\b(gemini|google ai|bard)\b/i],
  ['codex', /\b(codex|github copilot)\b/i],
  ['deepseek', /\b(deepseek|deep seek)\b/i],
  ['grok', /\b(grok|x\.ai|xai)\b/i],
  ['ollama', /\b(ollama|llama\s*\d|mistral|qwen|phi-)\b/i]
];
const AGENT_ROUTES = { coding: ['gpt', 'deepseek', 'claude'], ui: ['gemini', 'gpt'], research: ['claude', 'gemini'] };
/** Named provider stacks — shown on project cards and in Settings */
const ENGINE_COMBOS = [
  { id: 'general', name: 'General', meta: 'GPT + Claude', providers: ['gpt', 'claude'], route: 'coding' },
  { id: 'coding', name: 'Coding', meta: 'Claude + GPT', providers: ['claude', 'gpt'], route: 'coding' },
  { id: 'ui', name: 'UI & Web', meta: 'Gemini + GPT', providers: ['gemini', 'gpt'], route: 'ui' },
  { id: 'research', name: 'Research', meta: 'Claude + Gemini', providers: ['claude', 'gemini'], route: 'research' },
  { id: 'fast', name: 'Fast', meta: 'GPT + DeepSeek', providers: ['gpt', 'deepseek'], route: 'coding' },
  { id: 'multi', name: 'Multi', meta: 'GPT + Claude + Gemini', providers: ['gpt', 'claude', 'gemini'], route: 'coding' },
  { id: 'local', name: 'Local', meta: 'Ollama', providers: [], route: 'coding' }
];
const LEGACY_PROJECT_FIXES = {
  'p-beebox': { name: 'Web & UI', desc: 'Websites, layouts, and front-end work.', meta: 'Gemini + GPT', engineCombo: 'ui' },
  'p-odo': { name: 'Coding', desc: 'Features, bugs, and code review.', meta: 'Claude + GPT', engineCombo: 'coding' },
  'p-bitmap': { name: 'Media', desc: 'Images, animation, and visual work.', meta: 'GPT + Gemini', engineCombo: 'ui' }
};
const ALT_COPY = {
  pins: ['Pins', 'Pinned items appear here when you pin a project (double-click a project card).'],
  build: ['Agent Builder', 'Create custom agents with Blockbuster models. Use the Brain tab for the main orchestrator and device upload.'],
  brain: ['Brain', 'Main AI Hub brain — auto mode blends Blockbuster models.']
};
const PICTURES_HISTORY_MAX = 24;
const CODE_SNIPPETS = {
  PY: '# Python\nprint("AI Hub ready")',
  JS: '// JavaScript\nconsole.log("AI Hub ready");',
  CPP: '#include <iostream>\nint main() {\n  std::cout << "AI Hub\\n";\n  return 0;\n}',
  WEB: '<!DOCTYPE html>\n<html lang="en">\n<body>\n  <h1>AI Hub</h1>\n</body>\n</html>',
  AI: '# Prompt\nYou are a helpful assistant in AI Hub.',
  SYS: 'REM Run: RUN-AI-HUB.bat',
  BOT: '# Connect Ollama or API in Settings → Providers',
  UI: ':root {\n  --accent: #00ffee;\n}',
  BLDR: '# Local server\n# RUN-AI-HUB.bat → http://127.0.0.1:8765'
};
const CODE_META = {
  PY: 'Python starter',
  JS: 'JavaScript',
  CPP: 'C++',
  WEB: 'HTML shell',
  AI: 'AI prompt',
  SYS: 'Windows batch',
  BOT: 'Bot hook',
  UI: 'CSS tokens',
  BLDR: 'Build / run'
};
const ICON_COPY =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>';
const ICON_PREVIEW =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>';

let codePreviewKey = null;
let codeStageBlobUrl = null;
const DEFAULT_PROJECTS = [
  { id: 'p-general', name: 'General', desc: 'Everyday questions, notes, and planning.', meta: 'GPT + Claude', engineCombo: 'general' },
  { id: 'p-aihub', name: 'AI Hub', desc: 'Bridge between you, Cursor, and your AI providers.', meta: 'Multi Provider', engineCombo: 'multi' },
  { id: 'p-noahubai', name: 'NOAHUBAI', desc: 'Memory, issue tracking, and auto-fix agents synced with AI Hub.', meta: 'NOAHUBAI + Multi', engineCombo: 'multi' },
  { id: 'p-coding', name: 'Coding', desc: 'Build features, fix bugs, review code.', meta: 'Claude + GPT', engineCombo: 'coding' },
  { id: 'p-web', name: 'Web & UI', desc: 'Sites, dashboards, and interface design.', meta: 'Gemini + GPT', engineCombo: 'ui' }
];

let state = loadState();
let sending = false;
let summarizing = false;
let summaryTargetProjectId = null;
let saveStateTimer = null;
let navInitialized = false;
let bridgePanelAt = 0;
let cursorSessionsCache = null;
let chatRenderKey = '';
const CHAT_RENDER_LIMIT = 150;
const SUMMARIZE_MAX_MESSAGES = 120;
const SUMMARIZE_MSG_CHARS = 1200;
const SUMMARIZE_TOTAL_CHARS = 50000;
const SUMMARIZE_SYSTEM_PROMPT =
  'You summarize a multi-agent AI project chat for the user. The transcript includes the user and various AI assistants (GPT, Claude, Codex, Cursor, Ollama, etc.). Write a clear structured summary in markdown with these sections:\n\n' +
  '## What we worked on\n## Outcomes & decisions\n## Artifacts (files, code, snippets mentioned)\n## Open questions / next steps\n\n' +
  'Be factual — only include what appears in the transcript. Use bullet points. Stay under 700 words unless the thread is very long.';
const TIMELINE_RENDER_LIMIT = 400;
const BRIDGE_POLL_MS = 20000;
const AGENTS_SYNC_MS = 30000;
let agentsSyncTimer = null;
const perf = window.HubPerf || { debounce: (fn, ms) => fn, visible: () => true };
const AGENT_META = {
  you: { label: 'You', color: '#00ffee', border: '#00ffee', bg: 'rgba(0,255,238,.08)' },
  'cursor-agent': { label: 'Cursor Agent', color: '#f5f5f5', border: 'rgba(255,255,255,.45)', bg: 'rgba(255,255,255,.07)' },
  'cursor-import': { label: 'Cursor', color: '#9ca3af', border: '#4b5563', bg: 'rgba(75,85,99,.28)' },
  cursor: { label: 'Cursor', color: '#9ca3af', border: '#4b5563', bg: 'rgba(75,85,99,.28)' },
  gpt: { label: 'GPT', color: '#86efac', border: '#4ade80', bg: 'rgba(74,222,128,.14)' },
  codex: { label: 'Codex', color: '#22c55e', border: '#15803d', bg: 'rgba(22,163,74,.22)' },
  gemini: { label: 'Gemini', color: '#4285f4', border: '#4285f4', bg: 'rgba(66,133,244,.12)' },
  claude: { label: 'Claude', color: '#fb923c', border: '#f97316', bg: 'rgba(249,115,22,.16)' },
  deepseek: { label: 'DeepSeek', color: '#4d9fff', border: '#4d9fff', bg: 'rgba(77,159,255,.12)' },
  grok: { label: 'Grok', color: '#e5e5e5', border: '#a3a3a3', bg: 'rgba(255,255,255,.06)' },
  assistant: { label: 'Assistant', color: '#7367ff', border: '#7367ff', bg: 'rgba(115,103,255,.1)' },
  system: { label: 'System', color: '#888', border: '#666', bg: 'rgba(255,255,255,.04)' },
  ollama: { label: 'Ollama', color: '#00ff88', border: '#00ff88', bg: 'rgba(0,255,136,.1)' },
  noahubai: { label: 'NOAHUBAI', color: '#a5b4fc', border: '#6366f1', bg: 'rgba(99,102,241,.18)' },
  'noahubai-core': { label: 'NOAHUBAI Core', color: '#a5b4fc', border: '#6366f1', bg: 'rgba(99,102,241,.18)' },
  'memory_agent': { label: 'Memory Agent', color: '#a5b4fc', border: '#6366f1', bg: 'rgba(99,102,241,.14)' },
  'issue_agent': { label: 'Issue Agent', color: '#f472b6', border: '#ec4899', bg: 'rgba(236,72,153,.14)' },
  'fixer_agent': { label: 'Fixer Agent', color: '#6ee7b7', border: '#10b981', bg: 'rgba(16,185,129,.14)' },
  combined: {
    label: 'Combined AIs',
    color: '#f5d0fe',
    border: '#c084fc',
    bg: 'linear-gradient(135deg,rgba(74,222,128,.12),rgba(251,146,60,.12),rgba(96,165,250,.14),rgba(192,132,252,.14))',
    rainbow: true
  }
};
let timelineRenderKey = '';

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const s = JSON.parse(raw);
      if (!s.settings) s.settings = {};
      if (!s.settings.agentColors) s.settings.agentColors = {};
      if (s.settings.combinedRainbow === undefined) s.settings.combinedRainbow = true;
      if (!Array.isArray(s.settings.combinedRainbowStops) || s.settings.combinedRainbowStops.length < 2) {
        s.settings.combinedRainbowStops = [...DEFAULT_RAINBOW_STOPS];
      }
      if (!s.settings.startMode) s.settings.startMode = 'whole';
      if (s.workspaceOpen === undefined) s.workspaceOpen = s.settings.startMode === 'odd';
      if (!s.bridge) {
        s.bridge = { relayHub: true, relayCursor: true, relayOllama: false, autoSync: true, linkedSessionId: null };
      }
      if (!s.ui) s.ui = { chatView: 'timeline', filterAgent: 'all', filterProject: 'all' };
      if (s.activeNav === 'groups') s.activeNav = 'agents';
      if (s.activeNav === 'vision') s.activeNav = 'pictures';
      if (!s.ui.libraryTab) s.ui.libraryTab = s.activeNav === 'files' ? 'folders' : 'agents';
      if (!s.ui.libraryFilter) s.ui.libraryFilter = { date: 'all', size: 'all', location: 'all' };
      if (s.ui.showOriginalsInMain === undefined) s.ui.showOriginalsInMain = false;
      if (!s.codes) s.codes = { saveLocation: '', items: [] };
      if (!s.noahubai) s.noahubai = { online: false, agents: [], updatedAt: 0 };
      if (!s.brain) s.brain = { devices: [], customAgents: [], lastBlend: null };
      if (s.settings.brainAuto === undefined) s.settings.brainAuto = true;
      ensurePicturesState(s);
      PROVIDERS.forEach(p => {
        if (s.providers && s.providers[p] === undefined) s.providers[p] = true;
      });
      migrateAllMessages(s);
      migrateProjectCatalog(s);
      return s;
    }
  } catch (_) {}
  return {
    projects: DEFAULT_PROJECTS.map(p => ({ ...p, messages: [], pinned: false })),
    activeProjectId: 'p-aihub',
    activeNav: 'bridge',
    providers: Object.fromEntries(PROVIDERS.map(p => [p, true])),
    settings: {
      startMode: 'whole',
      agentColors: {},
      combinedRainbow: true,
      combinedRainbowStops: [...DEFAULT_RAINBOW_STOPS],
      brainAuto: true,
      connMode: 'ollama',
      ollamaUrl: 'http://127.0.0.1:11434',
      ollamaModel: 'llama3.2',
      apiBase: 'https://api.openai.com/v1',
      apiKey: '',
      apiModel: 'gpt-4o-mini'
    },
    workspaceOpen: false,
    bridge: {
      relayHub: true,
      relayCursor: true,
      relayOllama: false,
      autoSync: true,
      linkedSessionId: null
    },
    ui: { chatView: 'timeline', filterAgent: 'all', filterProject: 'all', filterSource: 'all' },
    codes: { saveLocation: '', items: [] },
    pictures: { prompt: '', activeId: 'pollinations', history: [] },
    brain: { devices: [], customAgents: [], lastBlend: null },
    noahubai: { online: false, agents: [], updatedAt: 0 }
  };
}

function ensureCodesState() {
  if (!state.codes) state.codes = { saveLocation: '', items: [], activeKey: null };
  if (!Array.isArray(state.codes.items)) state.codes.items = [];
  if (state.codes.activeKey === undefined) state.codes.activeKey = null;
}

function codeEntryKey(entry) {
  if (!entry) return '';
  return entry.builtin ? entry.tag : entry.id;
}

function isCodePinned(card) {
  return card.builtin ? !!findPinnedForBuiltin(card.tag) : !!card.pinned;
}

function detectCodePreviewKind(entry) {
  const tag = String(entry.tag || '').toUpperCase();
  const file = String(entry.file || '').toLowerCase();
  const text = (getCodeText(codeEntryKey(entry)) || entry.text || '').trim();
  if (file.endsWith('.html') || tag === 'WEB' || /^<!DOCTYPE/i.test(text) || /^<html[\s>]/i.test(text)) return 'html';
  if (tag === 'UI' || (/--[\w-]+:/.test(text) && text.includes('{') && !/<html/i.test(text))) return 'css';
  if (tag === 'JS' && !/<html/i.test(text)) return 'js';
  return 'code';
}

function buildRunnablePreviewHtml(entry, kind) {
  const text = (getCodeText(codeEntryKey(entry)) || entry.text || '').trim();
  const title = esc(entry.title || CODE_META[entry.tag] || entry.tag || 'Preview');
  if (kind === 'html') {
    if (/^<!DOCTYPE/i.test(text) || /^<html[\s>]/i.test(text)) return text;
    return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>' + title + '</title></head><body>' + text + '</body></html>';
  }
  if (kind === 'css') {
    return (
      '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>' +
      title +
      '</title><style>' +
      text +
      '</style></head><body><div style="padding:28px;font-family:Inter,sans-serif"><h1 style="color:var(--accent,#00ffee)">' +
      esc(entry.tag || 'UI') +
      '</h1><p style="opacity:.7">' +
      title +
      '</p><button type="button" style="margin-top:16px;padding:10px 18px;border-radius:12px;border:1px solid var(--accent,#00ffee);background:transparent;color:inherit;cursor:pointer">Demo control</button></div></body></html>'
    );
  }
  if (kind === 'js') {
    const safe = text.replace(/<\/script/gi, '<\\/script');
    return (
      '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>' +
      title +
      '</title></head><body><pre id="aihub-js-out" style="font:12px monospace;padding:16px;white-space:pre-wrap"></pre><script>\n' +
      'const log=(...a)=>{const el=document.getElementById("aihub-js-out");el.textContent+=(el.textContent?"\\n":"")+a.join(" ");};\n' +
      'try{\n' +
      safe +
      '\n}catch(e){log("Error:",e.message);}\n</script></body></html>'
    );
  }
  return null;
}

function pinnedCodeFileUrl(entry) {
  if (!entry?.file) return null;
  return '/pinned-codes/' + encodeURIComponent(entry.file);
}

function revokeCodeStageBlob() {
  if (codeStageBlobUrl) {
    URL.revokeObjectURL(codeStageBlobUrl);
    codeStageBlobUrl = null;
  }
}

function closeCodeWorkspace() {
  ensureCodesState();
  state.codes.activeKey = null;
  saveState();
  revokeCodeStageBlob();
  renderCodeStage();
  renderCodes();
}

function renderCodeStage() {
  const empty = $('codeStageEmpty');
  const active = $('codeStageActive');
  const frame = $('codeStageFrame');
  const pre = $('codeStagePre');
  if (!empty || !active) return;
  ensureCodesState();
  const key = state.codes.activeKey;
  const entry = key ? getCodeEntry(key) : null;
  if (!entry) {
    empty.classList.remove('hidden');
    active.classList.add('hidden');
    if (frame) {
      frame.hidden = true;
      frame.removeAttribute('src');
      frame.removeAttribute('srcdoc');
    }
    if (pre) pre.hidden = true;
    const badge = $('codeStageBadge');
    if (badge) badge.textContent = 'WORKSPACE';
    return;
  }
  empty.classList.add('hidden');
  active.classList.remove('hidden');
  const kind = detectCodePreviewKind(entry);
  const runnable = buildRunnablePreviewHtml(entry, kind);
  $('codeStageTitle').textContent = entry.tag || key;
  $('codeStageMeta').textContent = (entry.title || CODE_META[entry.tag] || '') + (entry.file ? ' · ' + entry.file : '');
  const badge = $('codeStageBadge');
  if (badge) badge.textContent = kind === 'code' ? 'CODE' : 'LIVE PREVIEW';
  const btnTab = $('btnCodeStageTab');
  const btnFile = $('btnCodeStageFile');
  if (btnTab) btnTab.hidden = !runnable;
  if (btnFile) btnFile.hidden = !entry.file;
  revokeCodeStageBlob();
  if (runnable && frame) {
    const fileUrl = pinnedCodeFileUrl(entry);
    frame.hidden = false;
    if (pre) pre.hidden = true;
    if (fileUrl && kind === 'html') {
      frame.removeAttribute('srcdoc');
      frame.src = fileUrl;
    } else {
      frame.removeAttribute('src');
      frame.srcdoc = runnable;
      codeStageBlobUrl = null;
    }
  } else if (pre) {
    if (frame) {
      frame.hidden = true;
      frame.removeAttribute('src');
      frame.removeAttribute('srcdoc');
    }
    pre.hidden = false;
    pre.textContent = getCodeText(codeEntryKey(entry)) || entry.text || '';
  }
}

function openCodeWorkspace(key) {
  const entry = getCodeEntry(key);
  if (!entry) return;
  ensureCodesState();
  state.codes.activeKey = key;
  saveState();
  renderCodeStage();
  document.querySelectorAll('.code-bubble').forEach(el => {
    el.classList.toggle('stage-active', el.dataset.codeKey === key);
  });
}

function pinAndOpenCode(previewId, card) {
  const entry = getCodeEntry(previewId);
  if (!entry) return;
  if (!isCodePinned(card)) {
    togglePinCode(card.id, card.tag, card.text, card.title, card.builtin);
  }
  openCodeWorkspace(previewId);
  if (state.activeNav !== 'codes') switchNav('codes');
  else {
    renderCodes();
    renderCodeStage();
  }
  if (getStartMode() === 'whole') enterWorkspace();
  const kind = detectCodePreviewKind(entry);
  setStatus('Pinned & opened ' + (entry.tag || previewId) + (kind !== 'code' ? ' · live preview' : ''), true);
}

function initCombinedRainbowSettings() {
  $('combinedRainbowToggle')?.addEventListener('change', e => {
    state.settings.combinedRainbow = e.target.checked;
    timelineRenderKey = '';
    chatRenderKey = '';
    saveState();
    renderChatHub();
    setStatus(e.target.checked ? 'Combined rainbow on' : 'Combined rainbow off — single AI colors', true);
  });
  $('btnResetRainbow')?.addEventListener('click', () => {
    state.settings.combinedRainbowStops = [...DEFAULT_RAINBOW_STOPS];
    delete state.settings.agentColors.combined;
    timelineRenderKey = '';
    chatRenderKey = '';
    saveState();
    renderCombinedRainbowUI();
    renderChatLegend();
    renderAgentFilterChips();
    renderEngineComboPicker();
    renderChatHub();
    setStatus('Rainbow colors reset', true);
  });
}

function initCodeStage() {
  $('btnCodeStageClose')?.addEventListener('click', closeCodeWorkspace);
  $('btnCodeStageFolder')?.addEventListener('click', () => openCodesSaveFolder());
  $('btnCodeStageFile')?.addEventListener('click', async () => {
    const key = state.codes?.activeKey;
    if (!key) return;
    const entry = getCodeEntry(key);
    if (!entry?.file) return;
    try {
      const data = await bridgeFetch('/api/bridge/codes');
      const folder = (data.saveLocation || state.codes.saveLocation || '').trim();
      if (!folder) return;
      const sep = folder.includes('\\') ? '\\' : '/';
      const tail = folder.endsWith(sep) ? '' : sep;
      openLocalPath(folder + tail + entry.file);
    } catch (e) {
      setStatus('Open file failed: ' + e.message, false);
    }
  });
  $('btnCodeStageTab')?.addEventListener('click', () => {
    const key = state.codes?.activeKey;
    if (!key) return;
    const entry = getCodeEntry(key);
    if (!entry) return;
    const html = buildRunnablePreviewHtml(entry, detectCodePreviewKind(entry));
    if (!html) return;
    revokeCodeStageBlob();
    const blob = new Blob([html], { type: 'text/html' });
    codeStageBlobUrl = URL.createObjectURL(blob);
    window.open(codeStageBlobUrl, '_blank', 'noopener');
  });
}

function updateCodesLocationField() {
  const inp = $('codesSaveLocation');
  if (!inp) return;
  const loc = (state.codes?.saveLocation || '').trim();
  inp.value = loc || '(default) ai hub/pinned-codes';
  inp.title = loc || 'Default: pinned-codes next to RUN-AI-HUB.bat';
}

function findPinnedForBuiltin(tag) {
  return (state.codes?.items || []).find(i => i.pinned && i.builtinKey === tag);
}

function getCodeEntry(id) {
  if (CODE_SNIPPETS[id]) {
    return { id: 'builtin-' + id, tag: id, title: CODE_META[id] || '', text: CODE_SNIPPETS[id], builtin: true };
  }
  return (state.codes?.items || []).find(i => i.id === id) || null;
}

function getCodeText(idOrEntry) {
  if (typeof idOrEntry === 'object' && idOrEntry) return idOrEntry.text || '';
  const e = getCodeEntry(idOrEntry);
  if (e) return e.text;
  return CODE_SNIPPETS[idOrEntry] || '';
}

function listCodeCards() {
  ensureCodesState();
  const pinned = (state.codes.items || []).filter(i => i.pinned);
  const pinnedBuiltinTags = new Set(pinned.map(i => i.builtinKey).filter(Boolean));
  const builtins = Object.keys(CODE_SNIPPETS)
    .filter(k => !pinnedBuiltinTags.has(k))
    .map(k => ({ id: 'builtin-' + k, tag: k, title: CODE_META[k] || '', text: CODE_SNIPPETS[k], builtin: true }));
  return { pinned, builtins };
}

function togglePinCode(cardId, tag, text, title, builtin) {
  ensureCodesState();
  if (builtin) {
    const existing = findPinnedForBuiltin(tag);
    if (existing) {
      state.codes.items = state.codes.items.filter(i => i.id !== existing.id);
      if (state.codes.activeKey === tag || state.codes.activeKey === existing.id) closeCodeWorkspace();
      saveState();
      renderCodes();
      setStatus('Unpinned ' + tag, true);
      return;
    }
    state.codes.items.push({
      id: 'pin-' + Date.now(),
      builtinKey: tag,
      tag,
      title: title || CODE_META[tag] || '',
      text: text || CODE_SNIPPETS[tag] || '',
      pinned: true
    });
  } else {
    const item = state.codes.items.find(i => i.id === cardId);
    if (item) {
      item.pinned = !item.pinned;
      if (!item.pinned) {
        if (state.codes.activeKey === cardId) closeCodeWorkspace();
        state.codes.items = state.codes.items.filter(i => i.pinned);
      }
    }
  }
  saveState();
  renderCodes();
  setStatus('Pinned codes updated', true);
}

function addNewCodePin() {
  const tag = prompt('Pin tag (short label, e.g. API):', 'PIN');
  if (!tag?.trim()) return;
  const title = prompt('Description:', 'Pinned snippet') || 'Pinned snippet';
  const text = prompt('Code text:', '') || '';
  ensureCodesState();
  state.codes.items.push({
    id: 'pin-' + Date.now(),
    tag: tag.trim().toUpperCase().slice(0, 24),
    title: title.trim(),
    text,
    pinned: true
  });
  saveState();
  renderCodes();
}

async function loadPinsFromFolder() {
  try {
    const data = await bridgeFetch('/api/bridge/codes');
    ensureCodesState();
    state.codes.saveLocation = data.saveLocation || state.codes.saveLocation;
    if (Array.isArray(data.items) && data.items.length) {
      const custom = state.codes.items.filter(i => !i.builtinKey && i.pinned);
      state.codes.items = [...data.items, ...custom.filter(c => !data.items.some(d => d.id === c.id))];
    }
    saveState();
    updateCodesLocationField();
    renderCodes();
    if (state.codes.activeKey) renderCodeStage();
    setStatus('Loaded pins from ' + (data.saveLocation || 'folder'), true);
  } catch (e) {
    setStatus('Load pins failed: ' + e.message, false);
  }
}

async function savePinsToFolder() {
  ensureCodesState();
  const items = state.codes.items.filter(i => i.pinned);
  if (!items.length) {
    setStatus('Pin at least one code bubble first', false);
    return;
  }
  try {
    const body = { items };
    if (state.codes.saveLocation) body.saveLocation = state.codes.saveLocation;
    const data = await bridgeFetch('/api/bridge/codes', { method: 'POST', body });
    state.codes.saveLocation = data.saveLocation || state.codes.saveLocation;
    if (Array.isArray(data.items)) state.codes.items = data.items;
    saveState();
    updateCodesLocationField();
    renderCodeStage();
    setStatus('Saved ' + data.items.length + ' pin(s) to folder', true);
  } catch (e) {
    setStatus('Save pins failed: ' + e.message, false);
  }
}

async function setCodesSaveLocation() {
  const cur = (state.codes?.saveLocation || '').trim();
  const path = prompt('Full folder path for pinned codes (blank = default pinned-codes):', cur);
  if (path === null) return;
  ensureCodesState();
  try {
    const data = await bridgeFetch('/api/bridge/codes/location', {
      method: 'POST',
      body: { path: path.trim() }
    });
    state.codes.saveLocation = data.saveLocation || '';
    saveState();
    updateCodesLocationField();
    setStatus('Save location set', true);
  } catch (e) {
    setStatus('Set path failed: ' + e.message, false);
  }
}

async function openCodesSaveFolder() {
  ensureCodesState();
  let loc = (state.codes?.saveLocation || '').trim();
  if (!loc) {
    try {
      const data = await bridgeFetch('/api/bridge/codes');
      loc = (data.saveLocation || '').trim();
      if (loc) {
        state.codes.saveLocation = loc;
        saveState();
        updateCodesLocationField();
      }
    } catch (_) {}
  }
  if (!loc) {
    switchNav('codes');
    setStatus('Set path in Codes, or Save pins to create the default folder', false);
    return;
  }
  openLocalPath(loc);
}

function initCodesPanel() {
  $('btnCodesSavePins')?.addEventListener('click', () => savePinsToFolder());
  $('btnCodesReloadPins')?.addEventListener('click', () => loadPinsFromFolder());
  $('btnCodesAddPin')?.addEventListener('click', addNewCodePin);
  $('btnCodesSetLocation')?.addEventListener('click', () => setCodesSaveLocation());
  $('btnCodesOpenFolder')?.addEventListener('click', () => openCodesSaveFolder());
  $('btnSavePinsTop')?.addEventListener('click', () => {
    switchNav('codes');
    savePinsToFolder();
  });
  $('btnPinFolder')?.addEventListener('click', e => {
    if (e.shiftKey) setCodesSaveLocation();
    else openCodesSaveFolder();
  });
}

function ensureUi() {
  if (!state.ui) state.ui = { chatView: 'timeline', filterAgent: 'all', filterProject: 'all' };
  if (state.ui.groupsSelected === undefined) state.ui.groupsSelected = null;
  if (!state.ui.navBeforeGroups) state.ui.navBeforeGroups = 'chats';
  if (!state.ui.libraryTab) state.ui.libraryTab = 'agents';
  if (!state.ui.libraryFilter) state.ui.libraryFilter = { date: 'all', size: 'all', location: 'all' };
  if (!state.ui.filterSource) state.ui.filterSource = 'all';
  if (state.ui.showOriginalsInMain === undefined) state.ui.showOriginalsInMain = false;
}

function isOriginalHiddenFromMain(p) {
  return !!(p && p.hiddenFromMain && !state.ui?.showOriginalsInMain);
}

function isVisibleInMainUi(p) {
  if (!p) return false;
  if (isOriginalHiddenFromMain(p)) return false;
  return true;
}

function getMainProjects() {
  return state.projects.filter(isVisibleInMainUi);
}

function getHiddenOriginalCount() {
  return state.projects.filter(p => p.hiddenFromMain).length;
}

function getOriginalProject(remixProject) {
  if (!remixProject?.remixOf) return null;
  return state.projects.find(p => p.id === remixProject.remixOf) || null;
}

function cloneProjectData(source, overrides = {}) {
  const combo = getProjectEngineCombo(source);
  return {
    id: overrides.id || 'p-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7),
    name: overrides.name || source.name,
    desc: overrides.desc || source.desc,
    meta: overrides.meta ?? source.meta,
    engineCombo: overrides.engineCombo ?? combo.id,
    messages: (source.messages || []).map(m => ({ ...m })),
    pinned: !!overrides.pinned,
    hiddenFromMain: !!overrides.hiddenFromMain,
    remixOf: overrides.remixOf || null,
    isRemix: !!overrides.isRemix
  };
}

function updateShowOriginalsButton() {
  const btn = $('btnShowOriginals');
  if (!btn) return;
  const n = getHiddenOriginalCount();
  btn.hidden = n === 0;
  btn.classList.toggle('active', !!state.ui.showOriginalsInMain);
  btn.textContent = state.ui.showOriginalsInMain ? 'Hide originals' : 'Originals (' + n + ')';
}

function saveProjectAsCopy() {
  const source = getActiveProject();
  if (!source) return;
  const name = prompt('Save as — new project name:', source.name + ' (copy)');
  if (!name?.trim()) return;
  const copy = cloneProjectData(source, {
    name: name.trim(),
    desc: (source.desc || '') + ' · copy',
    pinned: false,
    hiddenFromMain: false,
    isRemix: false,
    remixOf: null
  });
  state.projects.unshift(copy);
  state.activeProjectId = copy.id;
  chatRenderKey = '';
  timelineRenderKey = '';
  saveState();
  switchNav('chats');
  selectProject(copy.id);
  updateShowOriginalsButton();
  setStatus('Saved as: ' + copy.name, true);
}

function remixActiveProject() {
  const source = getActiveProject();
  if (!source) return;
  if (source.isRemix) {
    setStatus('Open the original project to remix again, or use Save as.', false);
    return;
  }
  const name = prompt('Remix name (fork of original):', source.name + ' Remix');
  if (!name?.trim()) return;
  const remix = cloneProjectData(source, {
    name: name.trim(),
    desc: 'Remix of “' + source.name + '”. Original is hidden from main UI.',
    pinned: source.pinned,
    hiddenFromMain: false,
    isRemix: true,
    remixOf: source.id
  });
  source.hiddenFromMain = true;
  state.projects.unshift(remix);
  state.activeProjectId = remix.id;
  chatRenderKey = '';
  timelineRenderKey = '';
  saveState();
  switchNav('chats');
  selectProject(remix.id);
  updateShowOriginalsButton();
  setStatus('Remix created. Original hidden from main UI.', true);
}

function toggleShowOriginalsInMain() {
  ensureUi();
  state.ui.showOriginalsInMain = !state.ui.showOriginalsInMain;
  saveState();
  renderProjects();
  renderChatHub();
  updateShowOriginalsButton();
  setStatus(
    state.ui.showOriginalsInMain ? 'Showing originals in project lists' : 'Originals hidden from main UI',
    true
  );
}

function projectCardBadges(p) {
  const badges = [];
  if (p.isRemix) badges.push('<span class="project-badge remix">Remix</span>');
  if (p.hiddenFromMain) badges.push('<span class="project-badge original-hidden">Original</span>');
  if (!badges.length) return '';
  return '<div class="project-badges">' + badges.join('') + '</div>';
}

function isCursorImportedMessage(m) {
  if (!m) return false;
  if (m.source === 'cursor' || m.imported) return true;
  return (m.text || '').startsWith('[Cursor]');
}

function messageDisplayText(m) {
  const t = m?.text || '';
  if (t.startsWith('[Cursor] ')) return t.slice(9);
  return t;
}

function messageFingerprint(m) {
  const role = m.role || '';
  const src = isCursorImportedMessage(m) ? 'cursor' : 'hub';
  const body = messageDisplayText(m).trim().slice(0, 800);
  return role + '\0' + src + '\0' + body;
}

function clearCursorImportsForProject(projectId) {
  const p = state.projects.find(x => x.id === (projectId || state.activeProjectId));
  if (!p) return 0;
  const before = (p.messages || []).length;
  p.messages = (p.messages || []).filter(m => !isCursorImportedMessage(m));
  const removed = before - p.messages.length;
  if (removed) {
    chatRenderKey = '';
    timelineRenderKey = '';
    saveState();
    renderChatHub();
  }
  return removed;
}

function isLibraryNav(id) {
  return id === 'agents' || id === 'files';
}

function sessionTs(s) {
  if (!s) return 0;
  if (s.modified) {
    const t = Date.parse(s.modified);
    if (!Number.isNaN(t)) return t;
  }
  if (s.mtime) return s.mtime > 1e12 ? s.mtime : s.mtime * 1000;
  return 0;
}

function projectStats(p) {
  const msgs = p.messages || [];
  let lastTs = 0;
  let totalChars = 0;
  msgs.forEach(m => {
    totalChars += (m.text || '').length;
    if (m.ts > lastTs) lastTs = m.ts;
  });
  return { msgCount: msgs.length, lastTs, totalChars };
}

function shortLocation(loc) {
  const s = String(loc || 'Unknown').trim();
  if (s.length <= 48) return s;
  return '…' + s.slice(-45);
}

function matchesLibraryDate(ts, filter) {
  if (!filter || filter === 'all' || !ts) return true;
  const now = Date.now();
  const day = 86400000;
  if (filter === 'today') return now - ts < day;
  if (filter === 'week') return now - ts < 7 * day;
  if (filter === 'month') return now - ts < 30 * day;
  if (filter === 'older') return now - ts >= 30 * day;
  return true;
}

function matchesLibrarySize(size, filter) {
  if (!filter || filter === 'all') return true;
  const n = size || 0;
  if (filter === 'small') return n < 10;
  if (filter === 'medium') return n >= 10 && n < 100;
  if (filter === 'large') return n >= 100;
  return true;
}

function applyLibraryFilters(items) {
  ensureUi();
  const f = state.ui.libraryFilter;
  return items.filter(
    it =>
      matchesLibraryDate(it.date, f.date) &&
      matchesLibrarySize(it.size, f.size) &&
      (f.location === 'all' || !f.location || it.location === f.location)
  );
}

function populateLibraryLocationFilter(items) {
  const sel = $('libraryFilterLocation');
  if (!sel) return;
  const cur = state.ui.libraryFilter.location || 'all';
  const locs = [...new Set(items.map(it => it.location).filter(Boolean))].sort((a, b) => a.localeCompare(b));
  sel.innerHTML = '<option value="all">Location · All</option>';
  locs.forEach(loc => {
    const o = document.createElement('option');
    o.value = loc;
    o.textContent = shortLocation(loc);
    if (loc === cur) o.selected = true;
    sel.appendChild(o);
  });
  if (cur !== 'all' && !locs.includes(cur)) {
    state.ui.libraryFilter.location = 'all';
    sel.value = 'all';
  }
}

function collectLibraryAgentItems() {
  return collectAgentStats().map(s => ({
    kind: 'agent',
    id: 'agent-' + s.id,
    agentId: s.id,
    title: agentLabel(s.id),
    subtitle: s.lastText || 'No messages yet',
    location: s.lastProject || 'Hub',
    date: s.lastTs,
    size: s.count,
    sizeLabel: s.count + ' msgs'
  }));
}

function collectLibraryFolderItems() {
  const items = [];
  getMainProjects().forEach(p => {
    const st = projectStats(p);
    items.push({
      kind: 'folder',
      id: 'proj-' + p.id,
      projectId: p.id,
      title: p.name,
      subtitle: p.desc || 'Project folder',
      location: (p.meta || 'AI Hub').trim(),
      date: st.lastTs,
      size: st.msgCount,
      sizeLabel: st.msgCount + ' msgs'
    });
  });
  const sessions = Array.isArray(cursorSessionsCache) ? cursorSessionsCache : [];
  sessions.forEach(s => {
    const loc = s.projectPath || s.projectSlug || 'Cursor workspace';
    items.push({
      kind: 'folder',
      id: 'sess-' + s.sessionId,
      sessionId: s.sessionId,
      path: s.projectPath,
      title: s.preview || s.projectSlug || 'Cursor session',
      subtitle: (s.projectSlug || '') + ' · Cursor Agent',
      location: loc,
      date: sessionTs(s),
      size: s.messageCount || 0,
      sizeLabel: (s.messageCount || 0) + ' msgs'
    });
  });
  return items;
}

function collectLibraryGroupItems() {
  ensureUi();
  const selected = state.ui.groupsSelected;
  if (selected) {
    return state.projects
      .filter(p => (p.meta || 'Other').trim() === selected)
      .map(p => {
        const st = projectStats(p);
        return {
          kind: 'group-project',
          id: 'gp-' + p.id,
          projectId: p.id,
          groupKey: selected,
          title: p.name,
          subtitle: p.desc || '',
          location: selected,
          date: st.lastTs,
          size: st.msgCount,
          sizeLabel: st.msgCount + ' msgs'
        };
      });
  }
  return getProjectsByGroup().map(([key, list]) => {
    let lastTs = 0;
    let total = 0;
    list.forEach(p => {
      const st = projectStats(p);
      total += st.msgCount;
      if (st.lastTs > lastTs) lastTs = st.lastTs;
    });
    return {
      kind: 'group',
      id: 'grp-' + key,
      groupKey: key,
      title: key,
      subtitle: list.length + ' project' + (list.length === 1 ? '' : 's'),
      location: key,
      date: lastTs,
      size: total,
      sizeLabel: list.length + ' projects'
    };
  });
}

function paintLibraryRow(it) {
  const dateStr = it.date ? formatTimeLabel(it.date) : '—';
  const gk = it.groupKey ? ' data-group-key="' + esc(it.groupKey) + '"' : '';
  return (
    '<button type="button" class="library-row" data-lib-id="' +
    esc(it.id) +
    '" data-lib-kind="' +
    esc(it.kind) +
    '"' +
    gk +
    '>' +
    '<div><h4>' +
    esc(it.title) +
    '</h4><p>' +
    esc(it.subtitle) +
    '</p></div>' +
    '<span class="lib-meta"><span class="loc" title="' +
    esc(it.location) +
    '">' +
    esc(shortLocation(it.location)) +
    '</span><span>' +
    esc(it.sizeLabel) +
    '</span><span>' +
    esc(dateStr) +
    '</span></span></button>'
  );
}

function setLibraryTab(tab) {
  ensureUi();
  if (!LIBRARY_TABS.includes(tab)) tab = 'agents';
  const prev = state.ui.libraryTab;
  state.ui.libraryTab = tab;
  if (tab === 'groups' && prev !== 'groups') state.ui.navBeforeGroups = state.activeNav;
  if (tab !== 'groups') state.ui.groupsSelected = null;
  saveState();
  renderLibraryView();
}

function renderLibraryView() {
  ensureUi();
  const tab = state.ui.libraryTab || 'agents';
  const list = $('libraryList');
  const badge = $('libraryBadge');
  const hint = $('libraryGroupsHint');
  if (!list) return;

  document.querySelectorAll('#libraryTabs button[data-library-tab]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.libraryTab === tab);
  });

  const dateSel = $('libraryFilterDate');
  const sizeSel = $('libraryFilterSize');
  if (dateSel) dateSel.value = state.ui.libraryFilter.date || 'all';
  if (sizeSel) sizeSel.value = state.ui.libraryFilter.size || 'all';

  let raw = [];
  if (tab === 'agents') raw = collectLibraryAgentItems();
  else if (tab === 'folders') raw = collectLibraryFolderItems();
  else raw = collectLibraryGroupItems();

  populateLibraryLocationFilter(raw);
  const items = applyLibraryFilters(raw).sort((a, b) => (b.date || 0) - (a.date || 0));

  if (badge) badge.textContent = items.length ? items.length + ' SHOWN' : 'EMPTY';
  if (hint) {
    const show = tab === 'groups';
    hint.hidden = !show;
    if (show) {
      hint.innerHTML =
        '<kbd>Esc</kbd> · <kbd>Backspace</kbd> — ' +
        (state.ui.groupsSelected ? 'back to all groups' : 'leave library');
    }
  }

  if (tab === 'groups' && state.ui.groupsSelected) {
    list.innerHTML =
      '<button type="button" class="btn btn-ghost groups-back-btn" style="margin-bottom:12px">← All groups</button>' +
      (items.length ? items.map(paintLibraryRow).join('') : '<p class="empty">No projects in this group.</p>');
    return;
  }

  if (!items.length) {
    const empty =
      tab === 'agents'
        ? 'No agent activity yet. Use Chats or Bridge.'
        : tab === 'folders'
          ? 'No folders. Add a project or scan Cursor sessions in Bridge.'
          : 'No groups yet. Create projects with a meta tag (group name).';
    list.innerHTML = '<p class="empty">' + empty + '</p>';
    return;
  }
  list.innerHTML = items.map(paintLibraryRow).join('');
}

function initLibraryPanel() {
  $('libraryTabs')?.addEventListener('click', e => {
    const btn = e.target.closest('button[data-library-tab]');
    if (btn) setLibraryTab(btn.dataset.libraryTab);
  });
  const onFilter = () => {
    ensureUi();
    if ($('libraryFilterDate')) state.ui.libraryFilter.date = $('libraryFilterDate').value;
    if ($('libraryFilterSize')) state.ui.libraryFilter.size = $('libraryFilterSize').value;
    if ($('libraryFilterLocation')) state.ui.libraryFilter.location = $('libraryFilterLocation').value;
    saveState();
    renderLibraryView();
  };
  $('libraryFilterDate')?.addEventListener('change', onFilter);
  $('libraryFilterSize')?.addEventListener('change', onFilter);
  $('libraryFilterLocation')?.addEventListener('change', onFilter);
  $('libraryList')?.addEventListener('click', onLibraryListClick);
}

function onLibraryListClick(e) {
  if (e.target.closest('.groups-back-btn')) {
    groupsGoBack();
    return;
  }
  const row = e.target.closest('.library-row');
  if (!row) return;
  ensureUi();
  const kind = row.dataset.libKind;
  const id = row.dataset.libId;

  if (kind === 'agent') {
    const agentId = id.replace(/^agent-/, '');
    state.ui.filterAgent = agentId;
    timelineRenderKey = '';
    saveState();
    switchNav('chats');
    setChatView('timeline');
    setStatus('Timeline filtered: ' + agentLabel(agentId), true);
    return;
  }
  if (kind === 'folder') {
    if (id.startsWith('proj-')) {
      selectProject(id.slice(5));
      switchNav('chats');
      setChatView('thread');
      return;
    }
    if (id.startsWith('sess-')) {
      const sid = id.slice(5);
      const s = (Array.isArray(cursorSessionsCache) ? cursorSessionsCache : []).find(x => x.sessionId === sid);
      if (s?.projectPath) openLocalPath(s.projectPath);
      switchNav('bridge');
      setStatus('Cursor session · open workspace from Bridge', true);
      return;
    }
  }
  if (kind === 'group') {
    state.ui.groupsSelected = row.dataset.groupKey || id.replace(/^grp-/, '');
    saveState();
    renderLibraryView();
    return;
  }
  if (kind === 'group-project') {
    const pid = id.replace(/^gp-/, '');
    if (pid) selectProject(pid);
    switchNav('chats');
    setChatView('thread');
  }
}

function migrateAllMessages(s) {
  const base = Date.now();
  const ctx = { projects: s.projects, providers: s.providers };
  let i = 0;
  (s.projects || []).forEach(p => {
    (p.messages || []).forEach(m => {
      normalizeMessage(m, base - i++ * 1000, p.id, ctx);
      if (m.role === 'assistant' && m.source === 'hub') {
        const brand = inferBrandAgent(m, p.id, ctx);
        if (brand) {
          m.provider = brand;
          m.agent = brand;
        }
      }
    });
  });
}

function normalizeProjectMeta(p) {
  if (!p) return;
  const map = {
    'GPT + DS': 'GPT + DeepSeek',
    'Bridge + Multi': 'Multi Provider',
    'GPT + Gemini + DeepSeek': 'GPT + DeepSeek'
  };
  if (map[p.meta]) p.meta = map[p.meta];
  if (!p.engineCombo) {
    const combo = ENGINE_COMBOS.find(c => c.meta === p.meta);
    if (combo) p.engineCombo = combo.id;
  }
}

function migrateProjectCatalog(s) {
  (s.projects || []).forEach(p => {
    const fix = LEGACY_PROJECT_FIXES[p.id];
    if (fix) Object.assign(p, fix);
    normalizeProjectMeta(p);
    if (p.hiddenFromMain === undefined) p.hiddenFromMain = false;
    if (p.isRemix === undefined) p.isRemix = !!p.remixOf;
  });
}

function inferBrandAgent(msg, projectId, ctx) {
  const m = msg || {};
  if (m.provider && AGENT_META[m.provider]) return m.provider;
  const a = m.agent;
  if (a && AGENT_META[a] && a !== 'assistant' && a !== 'combined') return a;
  const text = (m.text || '').slice(0, 400);
  for (const id of PROVIDERS) {
    if (new RegExp('\\[' + id + '\\]', 'i').test(text)) return id;
  }
  for (const [id, re] of BRAND_TEXT_HINTS) {
    if (re.test(text)) return id;
  }
  if (m.role === 'assistant' && projectId) {
    const projects = ctx?.projects || state.projects;
    const providers = ctx?.providers || state.providers;
    const p = (projects || []).find(x => x.id === projectId);
    if (p) {
      const combo = getProjectEngineCombo(p);
      for (const pr of combo.providers) {
        if (AGENT_META[pr] && providers?.[pr] !== false) return pr;
      }
    }
  }
  return null;
}

function normalizeMessage(m, fallbackTs, projectId, ctx) {
  if (!m.ts) m.ts = fallbackTs;
  if (!m.agent) {
    if (m.source === 'cursor' || m.imported || (m.text || '').startsWith('[Cursor]')) m.agent = 'cursor-import';
    else if (m.role === 'user') m.agent = 'you';
    else if (m.role === 'system') m.agent = 'system';
    else m.agent = 'assistant';
  }
  if (m.agent === 'cursor' && (m.source === 'cursor' || m.imported)) m.agent = 'cursor-import';
  const brand = inferBrandAgent(m, projectId, ctx);
  if (brand) {
    m.provider = brand;
    if (m.role === 'assistant' && m.source === 'hub') m.agent = brand;
    else if (m.role === 'assistant' && !AGENT_META[m.agent]) m.agent = brand;
  }
  if (!m.source) m.source = m.agent === 'cursor-import' || m.agent === 'cursor' ? 'cursor' : 'hub';
  if (projectId && !m.projectId) m.projectId = projectId;
  return m;
}

function makeMessage(role, text, extra = {}) {
  return {
    role,
    text,
    ts: extra.ts || Date.now(),
    agent: extra.agent || (role === 'user' ? 'you' : role === 'system' ? 'system' : 'assistant'),
    source: extra.source || 'hub',
    ...extra
  };
}

function ensureAgentColors() {
  if (!state.settings) state.settings = {};
  if (!state.settings.agentColors || typeof state.settings.agentColors !== 'object') state.settings.agentColors = {};
  if (state.settings.combinedRainbow === undefined) state.settings.combinedRainbow = true;
  if (!Array.isArray(state.settings.combinedRainbowStops) || state.settings.combinedRainbowStops.length < 2) {
    state.settings.combinedRainbowStops = [...DEFAULT_RAINBOW_STOPS];
  }
}

function shouldUseCombinedRainbow(project) {
  if (state.settings?.combinedRainbow === false) return false;
  const combo = getProjectEngineCombo(project);
  return combo.providers.length >= 2;
}

function getCombinedRainbowStops(projectId) {
  ensureAgentColors();
  const custom = state.settings.combinedRainbowStops || [];
  const parsed = custom.map(parseHexColor).filter(Boolean);
  if (parsed.length >= 2) return parsed;
  const p = projectId ? state.projects.find(x => x.id === projectId) : getActiveProject();
  if (p) {
    const combo = getProjectEngineCombo(p);
    const fromCombo = combo.providers.map(pr => parseHexColor(agentMeta(pr).border || agentMeta(pr).color)).filter(Boolean);
    if (fromCombo.length >= 2) return fromCombo;
  }
  return [...DEFAULT_RAINBOW_STOPS];
}

function buildRainbowGradient(stops) {
  const list = (stops || DEFAULT_RAINBOW_STOPS).filter(Boolean);
  if (list.length < 2) return 'linear-gradient(135deg,#4ade80,#60a5fa,#c084fc)';
  return 'linear-gradient(135deg,' + list.join(',') + ')';
}

function buildRainbowBg(stops) {
  const list = (stops || DEFAULT_RAINBOW_STOPS).map(h => colorWithAlpha(parseHexColor(h) || '#c084fc', 0.14));
  if (list.length < 2) return 'linear-gradient(135deg,rgba(74,222,128,.12),rgba(96,165,250,.14),rgba(192,132,252,.14))';
  return 'linear-gradient(135deg,' + list.join(',') + ')';
}

function parseHexColor(hex) {
  const s = String(hex || '').trim();
  if (/^#[0-9a-fA-F]{6}$/.test(s)) return s.toLowerCase();
  const m = s.match(/^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
  if (m) {
    const r = Math.min(255, +m[1]).toString(16).padStart(2, '0');
    const g = Math.min(255, +m[2]).toString(16).padStart(2, '0');
    const b = Math.min(255, +m[3]).toString(16).padStart(2, '0');
    return '#' + r + g + b;
  }
  return null;
}

function colorWithAlpha(hex, alpha) {
  const h = parseHexColor(hex);
  if (!h) return 'rgba(255,255,255,.08)';
  const n = h.slice(1);
  const r = parseInt(n.slice(0, 2), 16);
  const g = parseInt(n.slice(2, 4), 16);
  const b = parseInt(n.slice(4, 6), 16);
  return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
}

function lightenHex(hex, amount) {
  const h = parseHexColor(hex);
  if (!h) return '#ffffff';
  const n = h.slice(1);
  const clamp = v => Math.min(255, Math.max(0, v));
  const r = clamp(parseInt(n.slice(0, 2), 16) + amount);
  const g = clamp(parseInt(n.slice(2, 4), 16) + amount);
  const b = clamp(parseInt(n.slice(4, 6), 16) + amount);
  return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
}

function defaultAgentHex(id) {
  if (id === 'combined') return getCombinedRainbowStops(null)[0] || '#c084fc';
  const m = AGENT_META[id] || AGENT_META.assistant;
  return parseHexColor(m.border) || parseHexColor(m.color) || '#7367ff';
}

function getCustomAgentOverride(id) {
  ensureAgentColors();
  const raw = state.settings.agentColors[id];
  if (!raw) return null;
  if (id === 'combined' && Array.isArray(raw.stops) && raw.stops.length >= 2) {
    const stops = raw.stops.map(parseHexColor).filter(Boolean);
    if (stops.length >= 2) {
      return {
        color: parseHexColor(raw.color) || lightenHex(stops[Math.floor(stops.length / 2)], 40),
        border: buildRainbowGradient(stops),
        bg: buildRainbowBg(stops),
        rainbow: true,
        gradient: buildRainbowGradient(stops),
        stops
      };
    }
  }
  const hex = parseHexColor(raw.color || raw.border || raw);
  if (!hex) return null;
  return {
    color: raw.text ? parseHexColor(raw.text) || lightenHex(hex, 48) : lightenHex(hex, 48),
    border: hex,
    bg: raw.bg || colorWithAlpha(hex, 0.18)
  };
}

function agentMeta(id, projectId) {
  const base = AGENT_META[id] || AGENT_META.assistant;
  if (id === 'combined' || base.rainbow) {
    const stops = getCombinedRainbowStops(projectId);
    const grad = buildRainbowGradient(stops);
    const custom = getCustomAgentOverride('combined');
    return {
      label: base.label,
      color: custom?.color || base.color,
      border: grad,
      bg: buildRainbowBg(stops),
      rainbow: true,
      gradient: grad,
      stops
    };
  }
  const custom = getCustomAgentOverride(id);
  if (!custom) return { ...base };
  return { label: base.label, color: custom.color, border: custom.border, bg: custom.bg };
}

function setAgentCustomColor(id, hex) {
  ensureAgentColors();
  const h = parseHexColor(hex);
  if (!h) return;
  state.settings.agentColors[id] = { color: h };
  saveState();
  timelineRenderKey = '';
  chatRenderKey = '';
}

function resetAgentCustomColor(id) {
  ensureAgentColors();
  delete state.settings.agentColors[id];
  saveState();
  timelineRenderKey = '';
  chatRenderKey = '';
}

function agentLabel(id, projectId) {
  return agentMeta(id, projectId).label;
}

function agentColor(id, projectId) {
  return agentMeta(id, projectId).color;
}

function agentSlug(id) {
  return String(id || 'assistant').replace(/[^a-z0-9-]/gi, '-');
}

/** Resolve display agent — every chat uses its AI brand color when possible. */
function resolveAgentId(msg, projectId) {
  const m = msg || {};
  if (m.role === 'user') return 'you';
  if (m.role === 'system') return m.agent || 'system';
  if (m.agent === 'cursor' && (m.source === 'cursor' || m.imported || isCursorImportedMessage(m))) return 'cursor-import';
  if (m.agent === 'cursor') return 'cursor-agent';
  const brand = inferBrandAgent(m, projectId);
  if (brand) return brand;
  const id = m.agent || 'assistant';
  if (AGENT_META[id] && id !== 'assistant') return id;
  return 'assistant';
}

function displayAgentLabel(msg, projectId) {
  if (msg?.kind === 'summary') return 'Summary';
  return agentLabel(resolveAgentId(msg, projectId));
}

function agentColorsRevision() {
  return (
    JSON.stringify(state.settings?.agentColors || {}) +
    ':' +
    (state.settings?.combinedRainbow ? '1' : '0') +
    ':' +
    (state.settings?.combinedRainbowStops || []).join(',')
  );
}

function replyAgentId(route) {
  if (state.settings?.connMode === 'ollama') return 'ollama';
  return route && AGENT_META[route] ? route : 'assistant';
}

function applyAgentChatClasses(el, msg, projectId) {
  if (!el) return;
  const id = resolveAgentId(msg, projectId);
  const slug = agentSlug(id);
  const st = agentMeta(id, id === 'combined' ? projectId : null);
  const borderHex = parseHexColor(st.border || st.color) || defaultAgentHex(id);
  el.classList.add('agent-chat', 'agent-' + slug);
  el.dataset.agent = id;
  el.style.setProperty('--agent-color', st.color);
  el.style.setProperty('--agent-border', st.border || st.color);
  el.style.setProperty('--agent-bg', st.bg || 'rgba(255,255,255,.03)');
  if (st.rainbow && st.gradient) {
    el.classList.add('agent-rainbow');
    el.style.setProperty('--agent-gradient', st.gradient);
    el.style.setProperty('--agent-ring', 'rgba(192,132,252,.28)');
  } else {
    el.style.setProperty('--agent-ring', colorWithAlpha(borderHex, 0.22));
  }
}

function agentPillStyle(id, projectId) {
  const st = agentMeta(id, id === 'combined' ? projectId : null);
  if (st.rainbow && st.gradient) {
    return 'color:#fff;border:1px solid rgba(255,255,255,.2);background:' + st.gradient + ';font-weight:800';
  }
  return (
    'border-color:' +
    (st.border || st.color) +
    ';color:' +
    st.color +
    ';background:' +
    (st.bg || 'transparent')
  );
}

function buildChatFrameHtml(metaHtml, bodyHtml) {
  return (
    '<div class="chat-frame">' +
    '<div class="chat-frame-accent" aria-hidden="true"></div>' +
    '<div class="chat-frame-inner">' +
    metaHtml +
    bodyHtml +
    '</div></div>'
  );
}

function renderAgentFilterChips() {
  const host = $('agentFilterChips');
  if (!host) return;
  const cur = state.ui.filterAgent || 'all';
  const frag = document.createDocumentFragment();
  const allBtn = document.createElement('button');
  allBtn.type = 'button';
  allBtn.className = 'agent-chip' + (cur === 'all' ? ' active' : '');
  allBtn.dataset.agent = 'all';
  allBtn.textContent = 'All';
  frag.appendChild(allBtn);
  CHAT_LEGEND_AGENTS.forEach(id => {
    const st = agentMeta(id, null);
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'agent-chip agent-' + agentSlug(id) + (cur === id ? ' active' : '');
    b.dataset.agent = id;
    b.style.setProperty('--chip-color', st.color);
    b.style.setProperty('--chip-border', st.border || st.color);
    const dotStyle = st.rainbow && st.gradient ? 'background:' + esc(st.gradient) : 'background:' + esc(st.border || st.color);
    b.innerHTML = '<span class="chip-dot' + (st.rainbow ? ' chip-rainbow' : '') + '" style="' + dotStyle + '"></span>' + esc(agentLabel(id));
    frag.appendChild(b);
  });
  host.innerHTML = '';
  host.appendChild(frag);
}

function renderChatLegend() {
  const host = $('chatColorLegend');
  if (!host) return;
  host.innerHTML = CHAT_LEGEND_AGENTS.map(id => {
    const st = agentMeta(id, null);
    const dotBg = st.rainbow && st.gradient ? st.gradient : st.border || st.color;
    return (
      '<span class="legend-item agent-' +
      agentSlug(id) +
      (st.rainbow ? ' legend-rainbow' : '') +
      '" title="' +
      esc(agentLabel(id)) +
      '"><span class="legend-dot' +
      (st.rainbow ? ' legend-dot-rainbow' : '') +
      '" style="background:' +
      esc(dotBg) +
      '"></span>' +
      esc(agentLabel(id)) +
      '</span>'
    );
  }).join('');
}

function updateChatViewHint() {
  const el = $('chatViewHint');
  if (!el) return;
  const mode = state.ui.chatView || 'timeline';
  if (mode === 'thread') {
    const p = getActiveProject();
    el.textContent = p
      ? shouldUseCombinedRainbow(p)
        ? 'Thread · ' +
          p.name +
          ' — each message uses its AI brand color; rainbow glow on the panel (' +
          getProjectEngineCombo(p).meta +
          ').'
        : 'Thread · ' + p.name + ' — each message framed in its AI brand color (see legend).'
      : 'Pick a project chip below to open its thread.';
  } else {
    const f = state.ui.filterAgent;
    el.textContent =
      f && f !== 'all'
        ? 'Timeline filtered to ' + agentLabel(f) + '. Click a card to open that project thread.'
        : 'Timeline — click an agent chip to filter, or a message to open its project.';
  }
}

function updateThreadPanelHead() {
  const head = $('threadPanelHead');
  if (!head) return;
  const mode = state.ui.chatView || 'timeline';
  const p = getActiveProject();
  if (mode !== 'thread' || !p) {
    head.classList.add('hidden');
    return;
  }
  head.classList.remove('hidden');
  const title = $('threadProjectTitle');
  const badge = $('threadNextAgentBadge');
  if (title) title.textContent = p.name;
  const nextId = replyAgentId(pickProvider());
  const st = agentMeta(nextId, null);
  if (badge) {
    badge.textContent = 'Next reply · ' + agentLabel(nextId);
    badge.classList.remove('thread-next-rainbow');
    badge.style.borderColor = st.border || st.color;
    badge.style.color = st.color;
    badge.style.background = st.bg || 'transparent';
  }
  updateSummarizeButton();
}

function countSummarizableMessages(project) {
  return (project?.messages || []).filter(m => m.role === 'user' || m.role === 'assistant').length;
}

function summarizeTitleForProject(p) {
  if (!p) return 'No project selected';
  const n = countSummarizableMessages(p);
  const hint = p.chatSummary?.ts ? ' · last summary ' + formatTimeLabel(p.chatSummary.ts) : '';
  return n
    ? 'Summarize “' + p.name + '” (' + n + ' message' + (n === 1 ? '' : 's') + ')' + hint
    : '“' + p.name + '” has no messages yet';
}

function updateSummarizeButton() {
  const active = getActiveProject();
  const busy = summarizing || sending;
  document.querySelectorAll('.btn-summarize-chat').forEach(btn => {
    const pid = btn.dataset.pid || state.activeProjectId;
    const p = pid ? state.projects.find(x => x.id === pid) : active;
    const n = p ? countSummarizableMessages(p) : 0;
    btn.disabled = busy || !n;
    btn.title = summarizeTitleForProject(p);
  });
  const main = $('btnSummarizeChat');
  if (main && active) main.dataset.pid = active.id;
  const threadBtn = $('btnSummarizeChatThread');
  if (threadBtn && active) threadBtn.dataset.pid = active.id;
}

function updateChatWrapTheme() {
  const wrap = $('chatSection');
  if (!wrap) return;
  const p = getActiveProject();
  let id = replyAgentId(pickProvider());
  if (p?.messages?.length) {
    const last = [...p.messages].reverse().find(m => m.role === 'assistant' || m.role === 'user');
    if (last) id = resolveAgentId(last, p?.id);
  }
  if (p && shouldUseCombinedRainbow(p)) {
    wrap.classList.add('agent-rainbow-wrap');
    const grad = buildRainbowGradient(getCombinedRainbowStops(p?.id));
    wrap.style.setProperty('--thread-accent', '#c084fc');
    wrap.style.setProperty('--thread-bg', buildRainbowBg(getCombinedRainbowStops(p?.id)));
    wrap.style.setProperty('--agent-gradient', grad);
  } else {
    wrap.classList.remove('agent-rainbow-wrap');
    const st = agentMeta(id, null);
    wrap.style.setProperty('--thread-accent', st.border || st.color);
    wrap.style.setProperty('--thread-bg', st.bg || 'rgba(115,103,255,.08)');
  }
}

function formatDayLabel(ts) {
  const d = new Date(ts);
  const today = new Date();
  const y = new Date(today);
  y.setDate(y.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === y.toDateString()) return 'Yesterday';
  return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: d.getFullYear() !== today.getFullYear() ? 'numeric' : undefined });
}

function formatTimeLabel(ts) {
  return new Date(ts).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function collectFeedItems() {
  ensureUi();
  const q = getSearchQuery();
  const agentF = state.ui.filterAgent || 'all';
  const projF = state.ui.filterProject || 'all';
  const srcF = state.ui.filterSource || 'all';
  const items = [];
  state.projects.forEach(p => {
    if (projF !== 'all' && p.id !== projF) return;
    if (projF === 'all' && !isVisibleInMainUi(p)) return;
    (p.messages || []).forEach((m, idx) => {
      normalizeMessage(m, Date.now() - idx, p.id);
      const text = messageDisplayText(m).trim();
      if (!text) return;
      const imported = isCursorImportedMessage(m);
      if (srcF === 'hub' && imported) return;
      if (srcF === 'cursor' && !imported) return;
      if (agentF !== 'all' && resolveAgentId(m, p.id) !== agentF && m.agent !== agentF) return;
      if (q && !text.toLowerCase().includes(q) && !p.name.toLowerCase().includes(q)) return;
      items.push({
        projectId: p.id,
        projectName: p.name,
        msg: m,
        ts: m.ts
      });
    });
  });
  items.sort((a, b) => b.ts - a.ts);
  return items;
}

function collectAgentStats() {
  const stats = {};
  collectFeedItems().forEach(it => {
    const id = resolveAgentId(it.msg, it.projectId);
    if (!stats[id]) stats[id] = { id, count: 0, lastTs: 0, lastText: '', lastProject: '' };
    stats[id].count++;
    if (it.ts >= stats[id].lastTs) {
      stats[id].lastTs = it.ts;
      stats[id].lastText = (it.msg.text || '').slice(0, 80);
      stats[id].lastProject = it.projectName;
    }
  });
  return Object.values(stats).sort((a, b) => b.lastTs - a.lastTs);
}

let bridgePollTimer = null;
const BRIDGE_API = '';

async function bridgeFetch(path, opts = {}) {
  const o = { ...opts };
  if (o.body && typeof o.body === 'object') o.body = JSON.stringify(o.body);
  const r = await fetch(BRIDGE_API + path, {
    headers: { 'Content-Type': 'application/json', ...(o.headers || {}) },
    ...o
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || 'Bridge HTTP ' + r.status);
  return data;
}

function ensureBridgeState() {
  if (!state.bridge) {
    state.bridge = {
      relayHub: true,
      relayCursor: true,
      relayOllama: false,
      autoSync: true,
      linkedSessionId: null
    };
  }
}

function readBridgeUI() {
  ensureBridgeState();
  if ($('relayHub')) state.bridge.relayHub = $('relayHub').checked;
  if ($('relayCursor')) state.bridge.relayCursor = $('relayCursor').checked;
  if ($('relayOllama')) state.bridge.relayOllama = $('relayOllama').checked;
  if ($('bridgeAutoSync')) state.bridge.autoSync = $('bridgeAutoSync').checked;
  saveState();
}

function applyBridgeUI() {
  ensureBridgeState();
  const b = state.bridge;
  if ($('relayHub')) $('relayHub').checked = b.relayHub !== false;
  if ($('relayCursor')) $('relayCursor').checked = b.relayCursor !== false;
  if ($('relayOllama')) $('relayOllama').checked = !!b.relayOllama;
  if ($('bridgeAutoSync')) $('bridgeAutoSync').checked = b.autoSync !== false;
}

async function openLocalPath(path) {
  if (!path) return;
  try {
    await bridgeFetch('/api/bridge/open', { method: 'POST', body: { path } });
    setStatus('Opened: ' + path, true);
  } catch (e) {
    setStatus('Open failed: ' + e.message, false);
  }
}

function paintBridgeWorkspaceLinks(st) {
  const box = $('bridgeWorkspaceLinks');
  if (!box) return;
  if (!st) {
    box.innerHTML = '';
    return;
  }
  const linkedPath =
    st.linkedProjectPath ||
    (st.linkedProject && st.cursorProjectsRoot
      ? st.cursorProjectsRoot.replace(/\/$/, '') + '\\' + st.linkedProject
      : null);
  const rows = [
    { label: 'AI Hub folder', path: st.workspace },
    { label: 'Cursor projects root', path: st.cursorProjectsRoot },
    { label: 'Linked Cursor workspace', path: linkedPath, sub: st.linkedProject }
  ];
  box.innerHTML = rows
    .filter(r => r.path)
    .map(
      r =>
        '<div class="bridge-link-row"><span title="' +
        esc(r.path) +
        '">' +
        esc(r.label) +
        (r.sub ? ' · ' + esc(r.sub) : '') +
        '</span><div class="link-actions"><button type="button" class="btn" data-open-path="' +
        esc(r.path) +
        '">Open</button></div></div>'
    )
    .join('');
}

async function goToBridge() {
  if (getStartMode() === 'whole') enterWorkspace();
  switchNav('bridge');
  location.hash = 'bridge';
  await initBridgePanel(true);
}

async function syncNoahubaiAgents() {
  try {
    const data = await bridgeFetch('/api/bridge/agents/sync');
    window._agentsSync = data;
    if (!state.noahubai) state.noahubai = {};
    state.noahubai.online = !!data.noahubaiOnline;
    state.noahubai.agents = data.agents || [];
    state.noahubai.updatedAt = data.updatedAt;
    saveState();
    const box = $('bridgeStatusBox');
    if (box && window._bridgeStatus) {
      const noah = data.noahubaiOnline
        ? '<span style="color:#a5b4fc">NOAHUBAI online</span> · ' +
          (data.agents || []).filter(a => a.source === 'noahubai').length +
          ' agent(s)'
        : '<span style="opacity:.65">NOAHUBAI offline</span> (run python main.py :8000)';
      const extra = box.querySelector('.noahubai-sync-line');
      if (extra) extra.innerHTML = noah;
      else {
        const p = document.createElement('p');
        p.className = 'noahubai-sync-line';
        p.style.marginTop = '8px';
        p.style.fontSize = '12px';
        p.innerHTML = noah;
        box.appendChild(p);
      }
    }
    renderAgentsLive();
    return data;
  } catch (_) {
    return null;
  }
}

function startAgentsSyncPoll() {
  if (agentsSyncTimer) clearInterval(agentsSyncTimer);
  syncNoahubaiAgents().catch(() => {});
  agentsSyncTimer = setInterval(() => {
    if (!perf.visible()) return;
    syncNoahubaiAgents().catch(() => {});
  }, AGENTS_SYNC_MS);
}

async function loadBrainConfig() {
  try {
    const data = await bridgeFetch('/api/brain/config');
    if (!state.brain) state.brain = { devices: [], customAgents: [], lastBlend: null };
    state.brain.config = data.config || {};
    state.brain.devices = data.devices || [];
    state.brain.customAgents = (data.config && data.config.customAgents) || [];
    state.brain.freeModels = data.freeModels || [];
    if (data.config && data.config.autoMode !== undefined) {
      state.settings.brainAuto = !!data.config.autoMode;
    }
    saveState();
    renderBrainView();
    return data;
  } catch (e) {
    return null;
  }
}

function renderBrainView() {
  const box = $('brainStatusBox');
  const badge = $('brainBadge');
  const autoT = $('brainAutoToggle');
  if (autoT) autoT.checked = state.settings?.brainAuto !== false;
  if (badge) badge.textContent = state.settings?.brainAuto !== false ? 'AUTO ON' : 'MANUAL';
  if (box) {
    const devN = (state.brain?.devices || []).length;
    const agN = (state.brain?.customAgents || []).length;
    const modN = (state.brain?.freeModels || []).length;
    box.innerHTML =
      '<h3>Brain ready</h3><p>' +
      devN +
      ' synced device(s) · ' +
      agN +
      ' custom agent(s) · ' +
      modN +
      ' Blockbuster models</p>';
  }
  const ml = $('brainModelList');
  if (ml) {
    const models = state.brain?.freeModels || [];
    ml.innerHTML = models.length
      ? models
          .map(
            m =>
              '<div class="agent-row" style="border-left-color:#6366f1"><span class="dot" style="background:#6366f1"></span><span class="info"><h4>' +
              esc(m) +
              '</h4><p>OpenRouter free · Blockbuster</p></span></div>'
          )
          .join('')
      : '<p class="empty">No models loaded</p>';
  }
  const dl = $('brainDeviceList');
  if (dl) {
    const devices = state.brain?.devices || [];
    dl.innerHTML = devices.length
      ? devices
          .map(
            d =>
              '<div class="agent-row" style="border-left-color:#00ffee"><span class="dot" style="background:#00ffee"></span><span class="info"><h4>' +
              esc(d.name || d.id) +
              '</h4><p>' +
              esc(d.source || 'device') +
              ' · ' +
              esc(d.status || 'synced') +
              '</p></span></div>'
          )
          .join('')
      : '<p class="empty">No devices — click Upload synced devices</p>';
  }
  const bl = $('brainBuiltAgents');
  if (bl) {
    const agents = state.brain?.customAgents || [];
    bl.innerHTML = agents.length
      ? agents
          .map(
            a =>
              '<div class="agent-row" style="border-left-color:#c084fc"><span class="dot" style="background:#c084fc"></span><span class="info"><h4>' +
              esc(a.name || a.id) +
              '</h4><p>' +
              esc(a.model || '') +
              '</p></span></div>'
          )
          .join('')
      : '<p class="empty">No custom agents yet</p>';
  }
}

async function uploadSyncedDevicesToBrain() {
  try {
    const sync = await bridgeFetch('/api/bridge/agents/sync');
    const agents = sync.agents || state.noahubai?.agents || [];
    const devices = agents.map(a => ({
      id: a.id,
      name: a.name,
      source: a.source,
      status: a.status,
      color: a.color,
      description: a.description
    }));
    const data = await bridgeFetch('/api/brain/devices/upload', {
      method: 'POST',
      body: JSON.stringify({ devices, source: 'agents-manager' })
    });
    state.brain = state.brain || {};
    state.brain.devices = data.devices || devices;
    saveState();
    renderBrainView();
    setStatus('Uploaded ' + (data.devices || devices).length + ' synced devices to brain', true);
    return data;
  } catch (e) {
    setStatus(e.message, false);
    return null;
  }
}

async function saveBuiltAgent() {
  const name = ($('builderAgentName')?.value || '').trim();
  const model = $('builderAgentModel')?.value || 'deepseek/deepseek-chat:free';
  const prompt = ($('builderAgentPrompt')?.value || '').trim();
  if (!name) {
    setStatus('Agent name required', false);
    return;
  }
  try {
    const data = await bridgeFetch('/api/brain/agents', {
      method: 'POST',
      body: JSON.stringify({
        agent: { name, model, systemPrompt: prompt, source: 'agent-builder' }
      })
    });
    await loadBrainConfig();
    setStatus('Saved agent: ' + name, true);
    if ($('builderAgentName')) $('builderAgentName').value = '';
    if ($('builderAgentPrompt')) $('builderAgentPrompt').value = '';
  } catch (e) {
    setStatus(e.message, false);
  }
}

async function brainAutoBlend(userText, history) {
  readSettings();
  const combo = getProjectEngineCombo();
  const payload = {
    prompt: userText,
    history: history.map(m => ({ role: m.role, content: m.text })),
    engineCombo: combo.id,
    auto: state.settings?.brainAuto !== false,
    connMode: state.settings.connMode,
    apiBase: state.settings.apiBase,
    apiKey: state.settings.apiKey,
    ollamaUrl: state.settings.ollamaUrl,
    ollamaModel: state.settings.ollamaModel,
    syncedAgents: state.noahubai?.agents || [],
    codingQuality: state.brain?.config?.codingQuality || 50,
    textLength: state.brain?.config?.textLength || 50
  };
  const data = await bridgeFetch('/api/brain/auto', { method: 'POST', body: JSON.stringify(payload) });
  if (!data.ok) throw new Error(data.error || 'Brain auto-blend failed');
  state.brain = state.brain || {};
  state.brain.lastBlend = { route: data.route, models: data.models, ts: Date.now() };
  saveState();
  return data;
}

function shouldUseBrainAuto() {
  if (state.settings?.brainAuto === false) return false;
  const combo = getProjectEngineCombo();
  return (combo.providers && combo.providers.length >= 2) || combo.id === 'multi';
}

async function refreshBridgeStatus() {
  const box = $('bridgeStatusBox');
  const badge = $('bridgeBadge');
  if (!box) return false;
  try {
    const st = await bridgeFetch('/api/bridge/status');
    window._bridgeStatus = st;
    box.innerHTML =
      '<h3>Bridge online</h3><p>Cursor transcripts on this PC. Use workspace links below and session list.</p>';
    paintBridgeWorkspaceLinks(st);
    await syncNoahubaiAgents();
    if (badge) {
      badge.textContent = 'BRIDGE ON';
      badge.style.borderColor = 'rgba(0,255,238,.4)';
    }
    return true;
  } catch (e) {
    window._bridgeStatus = null;
    paintBridgeWorkspaceLinks(null);
    box.innerHTML =
      '<h3>Bridge offline</h3><p>Run <strong>RUN-AI-HUB.bat</strong> (uses bridge_server.py). Plain file open cannot read Cursor on Windows.<br>' +
      esc(e.message) +
      '</p>';
    if (badge) badge.textContent = 'OFFLINE';
    return false;
  }
}

async function loadOutboxPreview() {
  if (!$('outboxPreview')) return;
  try {
    const data = await bridgeFetch('/api/bridge/outbox');
    $('outboxPreview').value = data.content || '';
  } catch (_) {
    $('outboxPreview').value = '';
  }
}

function sessionListToolbar() {
  return (
    '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">' +
    '<button type="button" class="btn btn-ghost" data-bridge-act="refresh-sessions">This folder</button>' +
    '<button type="button" class="btn" data-bridge-act="scan-all">Other folders</button></div>'
  );
}

function paintCursorSessions(sessions) {
  const list = $('cursorSessionList');
  if (!list) return;
  if (!sessions.length) {
    list.innerHTML =
      sessionListToolbar() +
      '<p class="empty">No Cursor Agent transcripts found. Use Agent in Cursor, then Scan all.</p>';
    return;
  }
  const sorted = [...sessions].sort((a, b) => {
    const ah = a.isThisWorkspace !== false ? 1 : 0;
    const bh = b.isThisWorkspace !== false ? 1 : 0;
    if (ah !== bh) return bh - ah;
    return String(b.modified || '').localeCompare(String(a.modified || ''));
  });
  let html = sessionListToolbar();
  sorted.forEach(s => {
    const linked = state.bridge?.linkedSessionId === s.sessionId;
    const here = s.isThisWorkspace !== false;
    const paths = [];
    if (s.projectPath) paths.push('<a href="#" data-open-path="' + esc(s.projectPath) + '">workspace</a>');
    if (s.jsonlPath) paths.push('<a href="#" data-open-path="' + esc(s.jsonlPath) + '">transcript</a>');
    html +=
      '<div class="bridge-session' +
      (here ? '' : ' other-folder') +
      '" data-sid="' +
      esc(s.sessionId) +
      '"><h4>' +
      esc(s.preview || s.sessionId.slice(0, 8)) +
      (linked ? ' · linked' : '') +
      '<span class="folder-tag' +
      (here ? '' : ' warn') +
      '">' +
      (here ? 'this folder' : 'other folder') +
      '</span></h4><p>' +
      esc(s.projectSlug) +
      ' · ' +
      s.messageCount +
      ' msgs</p>' +
      (paths.length ? '<p class="bridge-paths">' + paths.join(' · ') + '</p>' : '') +
      '<div class="actions">' +
      '<button type="button" class="btn" data-act="link">Link</button>' +
      '<button type="button" class="btn primary" data-act="import">Import</button>' +
      '<button type="button" class="btn" data-act="sync">Sync</button></div></div>';
  });
  list.innerHTML = html;
}

function onCursorSessionClick(ev) {
  const btn = ev.target.closest('button[data-act]');
  if (!btn) return;
  const row = btn.closest('.bridge-session');
  if (!row) return;
  const sid = row.dataset.sid;
  const act = btn.dataset.act;
  ev.stopPropagation();
  if (act === 'link') {
    ensureBridgeState();
    state.bridge.linkedSessionId = sid;
    saveState();
    paintCursorSessions(cursorSessionsCache || []);
    setStatus('Linked Cursor session ' + sid.slice(0, 8), true);
  } else if (act === 'import') importCursorSession(sid, true);
  else if (act === 'sync') importCursorSession(sid, false);
}

async function renderCursorSessions(force, scanAll) {
  const list = $('cursorSessionList');
  if (!list) return;
  if (!force && !scanAll && cursorSessionsCache) {
    paintCursorSessions(cursorSessionsCache);
    return;
  }
  list.innerHTML = sessionListToolbar() + '<p class="empty">Loading…</p>';
  try {
    const q = (force ? '&refresh=1' : '') + (scanAll ? '&all=1' : '');
    const data = await bridgeFetch('/api/bridge/cursor/sessions?limit=40' + q);
    cursorSessionsCache = data.sessions || [];
    paintCursorSessions(cursorSessionsCache);
    if (isLibraryNav(state.activeNav) && state.ui.libraryTab === 'folders') renderLibraryView();
  } catch (e) {
    list.innerHTML = sessionListToolbar() + '<p class="empty">' + esc(e.message) + '</p>';
  }
}

function onBridgePanelClick(ev) {
  const openBtn = ev.target.closest('[data-open-path]');
  if (openBtn) {
    ev.preventDefault();
    openLocalPath(openBtn.dataset.openPath);
    return;
  }
  const act = ev.target.closest('[data-bridge-act]');
  if (act?.dataset.bridgeAct === 'scan-all') {
    ev.preventDefault();
    renderCursorSessions(true, true);
    return;
  }
  if (act?.dataset.bridgeAct === 'refresh-sessions') {
    ev.preventDefault();
    renderCursorSessions(true, false);
  }
}

function appendBridgeMessages(msgs, replace) {
  const project = getActiveProject();
  if (!project) return 0;
  chatRenderKey = '';
  timelineRenderKey = '';
  let n = 0;
  const seen = new Set();
  if (!replace) {
    (project.messages || []).forEach(m => seen.add(messageFingerprint(m)));
  }
  msgs.forEach(m => {
    const text = (m.text || '').trim();
    if (!text) return;
    const role = m.role === 'user' ? 'user' : m.role === 'assistant' ? 'assistant' : 'system';
    const draft = makeMessage(role, text, { agent: 'cursor-import', source: 'cursor', imported: true });
    if (!replace && seen.has(messageFingerprint(draft))) return;
    seen.add(messageFingerprint(draft));
    project.messages.push(draft);
    n++;
  });
  if (n) saveState();
  return n;
}

async function importCursorSession(sessionId, full) {
  try {
    const data = await bridgeFetch('/api/bridge/cursor/sessions/' + sessionId + '/import', { method: 'POST', body: {} });
    const msgs = data.messages || [];
    if (full) {
      const project = getActiveProject();
      if (project) project.messages = [];
    }
    const n = appendBridgeMessages(msgs, full);
    if (getStartMode() === 'whole') enterWorkspace();
    setChatView('thread');
    setStatus('Imported ' + n + ' messages from Cursor Agent', true);
  } catch (e) {
    setStatus(e.message, false);
  }
}

async function bridgeSyncNow() {
  try {
    const data = await bridgeFetch('/api/bridge/cursor/poll');
    let total = 0;
    (data.newBatches || []).forEach(batch => {
      if (state.bridge?.linkedSessionId && batch.sessionId !== state.bridge.linkedSessionId) return;
      total += appendBridgeMessages(batch.messages || [], false);
    });
    await loadOutboxPreview();
    setStatus(total ? 'Synced ' + total + ' new Cursor lines' : 'Cursor already up to date', true);
    if (total) renderChatHub();
  } catch (e) {
    setStatus(e.message, false);
  }
}

async function relayToCursor(text) {
  const project = getActiveProject();
  await bridgeFetch('/api/bridge/outbox', {
    method: 'POST',
    body: JSON.stringify({ text, project: project?.name || 'AI Hub' })
  });
  await loadOutboxPreview();
}

function startBridgePoll() {
  if (bridgePollTimer) clearInterval(bridgePollTimer);
  bridgePollTimer = setInterval(() => {
    if (!perf.visible()) return;
    if (!state.bridge?.autoSync) return;
    if (state.activeNav !== 'bridge') return;
    bridgeSyncNow().catch(() => {});
  }, BRIDGE_POLL_MS);
}

async function initBridgePanel(force) {
  const now = Date.now();
  if (!force && now - bridgePanelAt < 12000 && cursorSessionsCache) {
    applyBridgeUI();
    return;
  }
  bridgePanelAt = now;
  applyBridgeUI();
  const ok = await refreshBridgeStatus();
  if (ok) {
    await renderCursorSessions(true, false);
    await loadOutboxPreview();
    const here = (cursorSessionsCache || []).filter(s => s.isThisWorkspace !== false).length;
    setStatus('Bridge ready · ' + here + ' session(s) for this folder', true);
  }
}

function getStartMode() {
  const m = state.settings?.startMode;
  return m === 'odd' ? 'odd' : 'whole';
}

function applyStartMode() {
  const mode = getStartMode();
  document.body.classList.remove('mode-whole', 'mode-odd', 'workspace-open');
  document.body.classList.add(mode === 'odd' ? 'mode-odd' : 'mode-whole');
  if (mode === 'odd') {
    state.workspaceOpen = true;
    document.body.classList.add('workspace-open');
  } else if (state.workspaceOpen) {
    document.body.classList.add('workspace-open');
  }
  syncModeSwitches();
  renderProjects();
}

function setStartMode(mode) {
  state.settings.startMode = mode === 'odd' ? 'odd' : 'whole';
  if (mode === 'odd') {
    state.workspaceOpen = true;
  } else {
    state.workspaceOpen = false;
  }
  saveState();
  applyStartMode();
}

function syncModeSwitches() {
  const mode = getStartMode();
  document.querySelectorAll('.mode-switch').forEach(sw => {
    sw.querySelectorAll('button[data-mode]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.mode === mode);
    });
  });
}

function initModeSwitches() {
  document.querySelectorAll('.mode-switch button[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => setStartMode(btn.dataset.mode));
  });
}

function enterWorkspace() {
  state.workspaceOpen = true;
  document.body.classList.add('workspace-open');
  saveState();
  switchNav('chats');
  renderProjects();
}

function exitToStart() {
  if (getStartMode() !== 'whole') return;
  state.workspaceOpen = false;
  document.body.classList.remove('workspace-open');
  $('chatSection').classList.remove('open');
  saveState();
  renderProjects();
}

function openSettings() {
  if (getStartMode() === 'whole' && !state.workspaceOpen) enterWorkspace();
  switchNav('agents');
  renderAgentColorUI();
  $('settingsPanel').scrollIntoView({ behavior: 'smooth' });
}

function saveStateNow() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (_) {}
}

function saveState() {
  clearTimeout(saveStateTimer);
  saveStateTimer = setTimeout(saveStateNow, 350);
}

function saveWorkspaceNow() {
  readBridgeUI();
  const conn = $('connMode');
  if (conn) {
    state.settings.connMode = conn.value;
    state.settings.ollamaUrl = $('ollamaUrl')?.value || state.settings.ollamaUrl;
    state.settings.ollamaModel = $('ollamaModel')?.value || state.settings.ollamaModel;
    state.settings.apiBase = $('apiBase')?.value || state.settings.apiBase;
    state.settings.apiKey = $('apiKey')?.value || state.settings.apiKey;
    state.settings.apiModel = $('apiModel')?.value || state.settings.apiModel;
  }
  saveStateNow();
  const p = getActiveProject();
  setStatus('Saved · ' + (p?.name || 'workspace') + ' stored in this browser', true);
  const btn = $('btnSave');
  if (btn) {
    btn.classList.add('saved');
    setTimeout(() => btn.classList.remove('saved'), 1400);
  }
}

function $(id) {
  return document.getElementById(id);
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}

function setStatus(text, ok) {
  const dot = ok === true ? 'ok' : 'warn';
  $('statusText').innerHTML = `<span class="dot ${dot}"></span>${text}`;
}

function enabledCount() {
  return PROVIDERS.filter(p => state.providers[p]).length;
}

function getActiveProject() {
  return state.projects.find(p => p.id === state.activeProjectId) || state.projects[0];
}

function getProjectEngineCombo(project) {
  const p = project || getActiveProject();
  if (!p) return ENGINE_COMBOS[0];
  if (p.engineCombo) {
    const byId = ENGINE_COMBOS.find(c => c.id === p.engineCombo);
    if (byId) return byId;
  }
  return ENGINE_COMBOS.find(c => c.meta === p.meta) || ENGINE_COMBOS[0];
}

function applyEngineCombo(comboId) {
  const combo = ENGINE_COMBOS.find(c => c.id === comboId);
  const project = getActiveProject();
  if (!combo || !project) return;
  project.meta = combo.meta;
  project.engineCombo = combo.id;
  combo.providers.forEach(prov => {
    if (PROVIDERS.includes(prov)) state.providers[prov] = true;
  });
  saveState();
  renderProviderUI();
  renderProjects();
  renderEngineComboPicker();
  setStatus('Engine combo: ' + combo.name + ' (' + combo.meta + ')', true);
}

function pickProvider() {
  const enabled = PROVIDERS.filter(p => state.providers[p]);
  const combo = getProjectEngineCombo();
  const order = AGENT_ROUTES[combo.route] || AGENT_ROUTES.coding;
  for (const p of order) if (enabled.includes(p)) return p;
  if (combo.meta === 'Ollama' && state.settings?.connMode === 'ollama') return 'ollama';
  return enabled[0] || 'gpt';
}

function renderEngineComboPicker() {
  const host = $('engineComboPicker');
  if (!host) return;
  const active = getProjectEngineCombo();
  host.innerHTML = ENGINE_COMBOS.map(c => {
    const multi = c.providers.length >= 2;
    const grad = multi ? buildRainbowGradient(getCombinedRainbowStops(null)) : '';
    return (
      '<button type="button" class="combo-chip' +
      (c.id === active.id ? ' active' : '') +
      (multi ? ' combo-rainbow' : '') +
      '" data-combo="' +
      esc(c.id) +
      '" title="' +
      esc(c.meta) +
      '"><strong>' +
      esc(c.name) +
      '</strong><span' +
      (multi ? ' class="combo-rainbow-meta" style="background:' + esc(grad) + ';-webkit-background-clip:text;background-clip:text;color:transparent"' : '') +
      '>' +
      esc(c.meta) +
      '</span></button>'
    );
  }).join('');
}

function initNav() {
  const sb = $('sidebar');
  if (!navInitialized) {
    sb.innerHTML = '<div class="logo">O</div>';
    NAV.forEach(n => {
      const b = document.createElement('button');
      b.type = 'button';
    b.className = 'sidebtn' + (n.id === 'bridge' ? ' bridge-nav' : '');
    b.dataset.nav = n.id;
      b.innerHTML = `<span>${n.icon}</span>${n.label}`;
      b.addEventListener('click', () => switchNav(n.id));
      sb.appendChild(b);
    });
    navInitialized = true;
  }
  updateNavActive();
}

function updateNavActive() {
  document.querySelectorAll('.sidebtn').forEach(el => {
    el.classList.toggle('active', el.dataset.nav === state.activeNav);
  });
}

function switchNav(id) {
  if (id === 'groups') id = 'agents';
  const prevNav = state.activeNav;
  state.activeNav = id;
  saveState();
  updateNavActive();
  ensureUi();
  if (isLibraryNav(id)) {
    if (id === 'files') state.ui.libraryTab = 'folders';
    else if (prevNav !== 'agents' && prevNav !== 'files') state.ui.libraryTab = state.ui.libraryTab || 'agents';
    if (state.ui.libraryTab === 'groups' && !isLibraryNav(prevNav)) state.ui.navBeforeGroups = prevNav;
  }

  const isChats = id === 'chats';
  const isBridge = id === 'bridge';
  const isBrain = id === 'brain';
  const isLibrary = isLibraryNav(id);
  const isCodes = id === 'codes';
  const isPictures = id === 'pictures';
  if ($('view-code-stage')) $('view-code-stage').classList.toggle('active', isCodes);
  $('view-chats').classList.toggle('active', isChats);
  if ($('view-bridge')) $('view-bridge').classList.toggle('active', isBridge);
  if ($('view-brain')) $('view-brain').classList.toggle('active', isBrain);
  if ($('view-library')) $('view-library').classList.toggle('active', isLibrary);
  if ($('view-pictures')) $('view-pictures').classList.toggle('active', isPictures);
  $('view-alt').classList.toggle('active', !isChats && !isBridge && !isBrain && !isLibrary && !isCodes && !isPictures);
  const contentEl = document.querySelector('.content');
  if (contentEl) {
    contentEl.classList.toggle('bridge-focus', isBridge);
    contentEl.classList.toggle('codes-focus', isCodes);
    contentEl.classList.toggle('pictures-focus', isPictures);
  }
  if (isBridge && getStartMode() === 'whole') enterWorkspace();

  const showAgents = id !== 'codes' && !isBridge && !isBrain && !isPictures;
  $('view-right-main').classList.toggle('active', showAgents);
  $('view-codes').classList.toggle('active', id === 'codes');

  if (isChats) {
    renderProjects();
    renderChatHub();
  } else if (isLibrary) {
    if (id === 'files' && state.ui.libraryTab !== 'folders') state.ui.libraryTab = 'folders';
    renderLibraryView();
    if (state.ui.libraryTab === 'folders') renderCursorSessions(false, false);
  } else if (id === 'codes') {
    renderCodes();
    renderCodeStage();
    loadPinsFromFolder().catch(() => {});
  } else if (id === 'pictures') {
    renderPicturesView();
  } else if (id === 'brain') {
    loadBrainConfig().catch(() => renderBrainView());
  } else if (ALT_COPY[id]) {
    $('altTitle').textContent = ALT_COPY[id][0];
    $('altBody').textContent = ALT_COPY[id][1];
    if (id === 'pins') renderPinsList();
  }

  const p = getActiveProject();
  $('subtitle').textContent = p
    ? `${NAV.find(n => n.id === id)?.label || 'Workspace'} · ${p.name}`
    : 'OverDOn — unified multi-provider workspace';
}

function renderPinsList() {
  const pinned = getMainProjects().filter(p => p.pinned);
  $('altBody').innerHTML = pinned.length
    ? pinned.map(p => `<div class="agent"><h3>${esc(p.name)}</h3><p>${esc(p.desc)}</p></div>`).join('')
    : '<p class="empty">No pinned projects. Double-click a project card to pin it.</p>';
}

function ensurePicturesState(s) {
  const root = s || state;
  if (!root.pictures || typeof root.pictures !== 'object') {
    root.pictures = { prompt: '', activeId: 'pollinations', history: [] };
  }
  if (!root.pictures.activeId) root.pictures.activeId = 'pollinations';
  if (!Array.isArray(root.pictures.history)) root.pictures.history = [];
  if (root.pictures.prompt === undefined) root.pictures.prompt = '';
  return root.pictures;
}

function getPictureGenerator(id) {
  return PICTURE_GENERATORS.find(g => g.id === id) || PICTURE_GENERATORS[0];
}

function setActivePictureGenerator(id) {
  ensurePicturesState();
  state.pictures.activeId = id;
  saveState();
  renderPicturesView();
}

function readPicturesPrompt() {
  const el = $('picturesPrompt');
  if (el) state.pictures.prompt = el.value;
  return (state.pictures.prompt || '').trim();
}

function pushPictureHistory(entry) {
  ensurePicturesState();
  state.pictures.history.unshift(entry);
  if (state.pictures.history.length > PICTURES_HISTORY_MAX) {
    state.pictures.history.length = PICTURES_HISTORY_MAX;
  }
  saveState();
}

async function generateOpenAIImage(prompt) {
  readSettings();
  if (!state.settings.apiKey) {
    throw new Error('No API key — open Settings and add your OpenAI key, or use Pollinations (free).');
  }
  const base = (state.settings.apiBase || 'https://api.openai.com/v1').replace(/\/$/, '');
  const r = await fetch(base + '/images/generations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer ' + state.settings.apiKey
    },
    body: JSON.stringify({
      model: 'dall-e-3',
      prompt,
      n: 1,
      size: '1024x1024',
      response_format: 'url'
    }),
    signal: AbortSignal.timeout(120000)
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error('DALL·E ' + r.status + (t ? ': ' + t.slice(0, 120) : ''));
  }
  const data = await r.json();
  const url = data.data?.[0]?.url;
  if (!url) throw new Error('No image URL in API response');
  return url;
}

async function generatePicture() {
  const prompt = readPicturesPrompt();
  if (!prompt) {
    setStatus('Enter a picture prompt first.', false);
    return;
  }
  ensurePicturesState();
  const gen = getPictureGenerator(state.pictures.activeId);
  const btn = $('btnPicturesGenerate');
  if (btn) btn.disabled = true;
  setStatus('Generating with ' + gen.name + '…', null);
  const preview = $('picturesPreview');
  const meta = $('picturesPreviewMeta');
  if (preview) {
    preview.hidden = true;
    preview.removeAttribute('src');
  }
  if (meta) meta.textContent = 'Working…';
  try {
    let imageUrl = '';
    if (gen.api === 'openai') {
      imageUrl = await generateOpenAIImage(prompt);
    } else if (gen.buildUrl) {
      imageUrl = gen.buildUrl(prompt);
    } else {
      throw new Error('Select Pollinations or DALL·E 3 to generate here, or use Open on a web/local tool.');
    }
    const entry = {
      id: 'pic-' + Date.now(),
      prompt,
      url: imageUrl,
      generatorId: gen.id,
      generatorName: gen.name,
      ts: Date.now()
    };
    pushPictureHistory(entry);
    if (preview) {
      preview.hidden = false;
      preview.src = imageUrl;
      preview.alt = prompt.slice(0, 120);
    }
    if (meta) meta.textContent = gen.name + ' · ' + formatTimeLabel(entry.ts);
    const badge = $('picturesBadge');
    if (badge) badge.textContent = state.pictures.history.length + ' SAVED';
    renderPicturesGallery();
    setStatus('Image ready — ' + gen.name, true);
  } catch (e) {
    if (meta) meta.textContent = 'Failed';
    setStatus(e.message, false);
  } finally {
    if (btn) btn.disabled = false;
  }
}

function openActivePictureGenerator() {
  const gen = getPictureGenerator(state.pictures.activeId);
  const url = gen.openUrl || (gen.buildUrl && readPicturesPrompt() ? gen.buildUrl(readPicturesPrompt()) : null);
  if (!url) {
    setStatus(gen.name + ' generates inside AI Hub — click Generate.', null);
    return;
  }
  window.open(url, '_blank', 'noopener,noreferrer');
}

function renderPicturesGallery() {
  const host = $('picturesGallery');
  if (!host) return;
  ensurePicturesState();
  const hist = state.pictures.history;
  if (!hist.length) {
    host.innerHTML = '<p class="empty">Generated images appear here.</p>';
    return;
  }
  host.innerHTML = hist
    .map(
      h =>
        '<button type="button" class="pictures-thumb" data-pic-id="' +
        esc(h.id) +
        '" title="' +
        esc(h.prompt) +
        '"><img src="' +
        esc(h.url) +
        '" alt="" loading="lazy"><span class="pictures-thumb-label">' +
        esc(h.generatorName || '') +
        '</span></button>'
    )
    .join('');
}

function showPictureFromHistory(id) {
  ensurePicturesState();
  const h = state.pictures.history.find(x => x.id === id);
  if (!h) return;
  const preview = $('picturesPreview');
  const meta = $('picturesPreviewMeta');
  if (preview) {
    preview.hidden = false;
    preview.src = h.url;
    preview.alt = h.prompt;
  }
  if (meta) meta.textContent = (h.generatorName || '') + ' · ' + formatTimeLabel(h.ts);
  const el = $('picturesPrompt');
  if (el) {
    el.value = h.prompt;
    state.pictures.prompt = h.prompt;
  }
  state.pictures.activeId = h.generatorId || state.pictures.activeId;
  renderPicturesGenGrid();
}

function renderPicturesGenGrid() {
  const host = $('picturesGenGrid');
  if (!host) return;
  ensurePicturesState();
  const active = state.pictures.activeId;
  host.innerHTML = PICTURE_GENERATORS.map(g => {
    const canGen = !!(g.buildUrl || g.api === 'openai');
    return (
      '<button type="button" class="gen-card' +
      (g.id === active ? ' active' : '') +
      '" data-gen="' +
      esc(g.id) +
      '">' +
      '<span class="gen-card-badge">' +
      esc(g.badge) +
      '</span>' +
      '<strong>' +
      esc(g.name) +
      '</strong>' +
      '<p>' +
      esc(g.desc) +
      '</p>' +
      (canGen ? '<span class="gen-card-tag">In Hub</span>' : '<span class="gen-card-tag gen-card-tag-web">Open external</span>') +
      '</button>'
    );
  }).join('');
}

function renderPicturesView() {
  ensurePicturesState();
  const el = $('picturesPrompt');
  if (el && el.value !== state.pictures.prompt) el.value = state.pictures.prompt || '';
  renderPicturesGenGrid();
  renderPicturesGallery();
  const badge = $('picturesBadge');
  if (badge) {
    const n = state.pictures.history.length;
    badge.textContent = n ? n + ' SAVED' : PICTURE_GENERATORS.length + ' TOOLS';
  }
  const gen = getPictureGenerator(state.pictures.activeId);
  const hint = $('picturesGenHint');
  if (hint) {
    hint.textContent =
      gen.api === 'openai'
        ? 'DALL·E 3 uses your OpenAI API key from Settings → Providers.'
        : gen.buildUrl
          ? 'Generate runs instantly via ' + gen.name + ' (no key).'
          : 'Open launches ' + gen.name + ' in your browser — run local tools first if needed.';
  }
}

function initPicturesPanel() {
  const view = $('view-pictures');
  if (!view || view.dataset.bound) return;
  view.dataset.bound = '1';
  $('btnPicturesGenerate')?.addEventListener('click', generatePicture);
  $('btnPicturesOpen')?.addEventListener('click', openActivePictureGenerator);
  $('picturesPrompt')?.addEventListener('input', () => {
    ensurePicturesState();
    state.pictures.prompt = $('picturesPrompt').value;
  });
  $('picturesGenGrid')?.addEventListener('click', e => {
    const card = e.target.closest('[data-gen]');
    if (!card?.dataset.gen) return;
    setActivePictureGenerator(card.dataset.gen);
  });
  $('picturesGallery')?.addEventListener('click', e => {
    const thumb = e.target.closest('[data-pic-id]');
    if (!thumb?.dataset.picId) return;
    showPictureFromHistory(thumb.dataset.picId);
  });
  $('btnPicturesOpenResult')?.addEventListener('click', () => {
    const src = $('picturesPreview')?.src;
    if (src) window.open(src, '_blank', 'noopener,noreferrer');
  });
}

function getProjectsByGroup() {
  const map = new Map();
  getMainProjects().forEach(p => {
    const g = (p.meta || 'Other').trim();
    if (!map.has(g)) map.set(g, []);
    map.get(g).push(p);
  });
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

function groupsGoBack() {
  ensureUi();
  if (state.ui.groupsSelected) {
    state.ui.groupsSelected = null;
    saveState();
    renderLibraryView();
    setStatus('Groups · all themes', true);
    return;
  }
  if (isLibraryNav(state.activeNav) && state.ui.libraryTab === 'groups') {
    switchNav(state.ui.navBeforeGroups || 'chats');
    return;
  }
  switchNav(state.ui.navBeforeGroups || 'chats');
}

function renderGroupsView() {
  ensureUi();
  const body = $('altBody');
  if (!body) return;
  $('altTitle').textContent = 'Groups';
  const selected = state.ui.groupsSelected;
  const hint =
    '<p class="groups-kbd-hint"><kbd>Esc</kbd> · <kbd>Backspace</kbd> — ' +
    (selected ? 'back to all groups' : 'leave Groups') +
    '</p>';

  if (selected) {
    const projects = getMainProjects().filter(p => (p.meta || 'Other').trim() === selected);
    let html =
      hint +
      '<button type="button" class="btn btn-ghost groups-back-btn">← All groups</button>' +
      '<h3 class="groups-detail-title">' +
      esc(selected) +
      '</h3>';
    if (!projects.length) {
      html += '<p class="empty">No projects in this group.</p>';
    } else {
      html += projects
        .map(
          p =>
            '<button type="button" class="groups-project-chip" data-group-project="' +
            esc(p.id) +
            '"><strong>' +
            esc(p.name) +
            '</strong><span>' +
            esc(p.desc) +
            '</span></button>'
        )
        .join('');
    }
    body.innerHTML = html;
    return;
  }

  const groups = getProjectsByGroup();
  if (!groups.length) {
    body.innerHTML = hint + '<p class="empty">No projects yet. Create one with + Project.</p>';
    return;
  }
  body.innerHTML =
    hint +
    groups
      .map(
        ([key, list]) =>
          '<button type="button" class="group-row" data-group-key="' +
          esc(key) +
          '"><div><h4>' +
          esc(key) +
          '</h4><p>' +
          list.length +
          ' project' +
          (list.length === 1 ? '' : 's') +
          '</p></div><span class="count">' +
          list.length +
          '</span></button>'
      )
      .join('');
}

function initGlobalKeyboard() {
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      saveWorkspaceNow();
      return;
    }
    if ($('chatSummaryModal')?.classList.contains('open') && e.key === 'Escape') {
      closeChatSummaryModal();
      return;
    }
    const modal = $('codePreviewModal');
    if (modal?.classList.contains('open') && e.key === 'Escape') {
      closeCodePreview();
      return;
    }
    if (state.activeNav === 'codes' && state.codes?.activeKey && e.key === 'Escape') {
      const el = document.activeElement;
      const editing =
        el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
      if (!editing) {
        e.preventDefault();
        closeCodeWorkspace();
        return;
      }
    }
    if (!isLibraryNav(state.activeNav) || state.ui.libraryTab !== 'groups') return;
    if (e.key !== 'Escape' && e.key !== 'Backspace') return;
    const el = document.activeElement;
    const editing =
      el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
    if (e.key === 'Backspace' && editing) return;
    e.preventDefault();
    groupsGoBack();
  });
}

function getSearchQuery() {
  const main = $('search');
  const start = $('searchStart');
  if (main && start) {
    if (document.activeElement === start) main.value = start.value;
    else if (document.activeElement === main) start.value = main.value;
  }
  return ((main && main.value) || (start && start.value) || '').toLowerCase().trim();
}

function fillProjectGrid(grid, list) {
  if (!grid) return;
  grid.innerHTML = '';
  if (!list.length) {
    grid.innerHTML = '<p class="empty">No projects match.</p>';
    return;
  }
  const frag = document.createDocumentFragment();
  list.forEach(p => {
    const el = document.createElement('article');
    el.className = 'project' + (p.id === state.activeProjectId ? ' selected' : '');
    el.dataset.pid = p.id;
    if (p.pinned) el.style.borderColor = '#7367ff';
    const n = countSummarizableMessages(p);
    el.innerHTML =
      projectCardBadges(p) +
      '<h3>' +
      esc(p.name) +
      '</h3><p>' +
      esc(p.desc) +
      '</p><div class="meta">' +
      esc(p.meta) +
      (p.isRemix ? ' · remix' : '') +
      '</div><div class="project-card-actions"><button type="button" class="btn btn-ghost btn-mini btn-summarize-chat" data-pid="' +
      esc(p.id) +
      '"' +
      (n ? '' : ' disabled') +
      '>SUMMARIZE CHAT</button></div>';
    frag.appendChild(el);
  });
  grid.appendChild(frag);
}

function renderProjects() {
  const q = getSearchQuery();
  const list = getMainProjects().filter(
    p => !q || p.name.toLowerCase().includes(q) || (p.desc || '').toLowerCase().includes(q)
  );
  const whole = getStartMode() === 'whole';
  const open = document.body.classList.contains('workspace-open');
  if (whole && !open) fillProjectGrid($('projectGridStart'), list);
  else fillProjectGrid($('projectGrid'), list);
  renderProjectStrip();
  if (open || getStartMode() === 'odd') renderChatHub();
  updateShowOriginalsButton();
}

function setChatView(mode) {
  ensureUi();
  state.ui.chatView = mode === 'thread' ? 'thread' : 'timeline';
  saveState();
  renderChatHub();
}

/** Open a project thread (from timeline, strip, or grid). */
function openProjectChat(projectId, msgTs) {
  const p = state.projects.find(x => x.id === projectId);
  if (!p) return;
  if (state.activeNav !== 'chats') switchNav('chats');
  if (getStartMode() === 'whole' && !document.body.classList.contains('workspace-open')) enterWorkspace();
  state.activeProjectId = projectId;
  state.ui.chatView = 'thread';
  chatRenderKey = '';
  timelineRenderKey = '';
  saveState();
  renderProjects();
  renderChatHub();
  renderEngineComboPicker();
  $('subtitle').textContent = 'Chat · ' + p.name;
  setStatus('Opened chat: ' + p.name, true);
  if (msgTs != null) {
    requestAnimationFrame(() =>
      requestAnimationFrame(() => scrollThreadToMessage(msgTs))
    );
  }
}

function scrollThreadToMessage(ts) {
  const box = $('messages');
  if (!box || ts == null) return;
  const card = box.querySelector('.thread-card[data-ts="' + String(ts) + '"]');
  if (card) {
    card.classList.add('thread-focus');
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    window.setTimeout(() => card.classList.remove('thread-focus'), 2400);
  } else {
    box.scrollTop = box.scrollHeight;
  }
}

function setAgentFilter(agentId) {
  ensureUi();
  const id = agentId || 'all';
  state.ui.filterAgent = id;
  timelineRenderKey = '';
  saveState();
  const sel = $('filterAgent');
  if (sel) sel.value = id;
  renderAgentFilterChips();
  updateChatViewHint();
  if ((state.ui.chatView || 'timeline') === 'timeline') renderTimeline();
  setStatus(id === 'all' ? 'Showing all agents' : 'Filter: ' + agentLabel(id), true);
}

function renderChatFilters() {
  const agentSel = $('filterAgent');
  const projSel = $('filterProject');
  const srcSel = $('filterSource');
  if (!projSel) return;
  const agents = new Set();
  state.projects.forEach(p =>
    (p.messages || []).forEach(m => {
      normalizeMessage(m, 0, p.id);
      agents.add(resolveAgentId(m, p.id));
    })
  );
  const curA = state.ui.filterAgent || 'all';
  if (agentSel) {
    agentSel.innerHTML = '<option value="all">All agents</option>';
    [...agents].sort().forEach(id => {
      const o = document.createElement('option');
      o.value = id;
      o.textContent = agentLabel(id);
      if (id === curA) o.selected = true;
      agentSel.appendChild(o);
    });
  }
  renderAgentFilterChips();
  const curP = state.ui.filterProject || 'all';
  projSel.innerHTML = '<option value="all">All projects</option>';
  getMainProjects().forEach(p => {
    const o = document.createElement('option');
    o.value = p.id;
    o.textContent = p.name + (p.isRemix ? ' (remix)' : '');
    if (p.id === curP) o.selected = true;
    projSel.appendChild(o);
  });
  if (srcSel) {
    const curS = state.ui.filterSource || 'all';
    srcSel.value = curS;
  }
}

function renderProjectStrip() {
  const strip = $('projectStrip');
  if (!strip) return;
  const active = state.activeProjectId;
  strip.innerHTML = '';
  getMainProjects().forEach(p => {
    const wrap = document.createElement('div');
    wrap.className = 'project-chip-wrap' + (p.id === active ? ' active' : '');
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'project-chip';
    b.title = p.isRemix ? 'Remix · open thread' : 'Open thread';
    b.dataset.pid = p.id;
    b.textContent = p.isRemix ? p.name + ' ·' : p.name;
    const sum = document.createElement('button');
    sum.type = 'button';
    sum.className = 'btn btn-ghost btn-mini chip-summarize btn-summarize-chat';
    sum.dataset.pid = p.id;
    sum.textContent = '∑';
    sum.title = summarizeTitleForProject(p);
    sum.disabled = summarizing || sending || !countSummarizableMessages(p);
    wrap.appendChild(b);
    wrap.appendChild(sum);
    strip.appendChild(wrap);
  });
}

function renderTimeline() {
  const box = $('timelineView');
  if (!box) return;
  const items = collectFeedItems();
  const key =
    items.length +
    ':' +
    (items[0]?.ts || 0) +
    ':' +
    state.ui.filterAgent +
    ':' +
    state.ui.filterProject +
    ':' +
    state.ui.filterSource +
    ':' +
    agentColorsRevision();
  if (key === timelineRenderKey && box.childElementCount > 0) return;
  timelineRenderKey = key;
  const badge = $('chatHubBadge');
  if (badge) badge.textContent = items.length ? items.length + ' EVENTS' : 'TIMELINE';
  if (!items.length) {
    box.innerHTML = '<p class="empty">No messages yet. Send in a project thread, import from Bridge, or sync Cursor Agent.</p>';
    return;
  }
  const slice = items.slice(0, TIMELINE_RENDER_LIMIT);
  const frag = document.createDocumentFragment();
  let lastDay = '';
  slice.forEach(it => {
    const day = formatDayLabel(it.ts);
    if (day !== lastDay) {
      lastDay = day;
      const h = document.createElement('div');
      h.className = 'timeline-day';
      h.textContent = day;
      frag.appendChild(h);
    }
    const imported = isCursorImportedMessage(it.msg);
    const agent = resolveAgentId(it.msg, it.projectId);
    const card = document.createElement('article');
    card.className =
      'feed-item role-' +
      (it.msg.role || 'assistant') +
      (it.msg.error ? ' error' : '') +
      (imported ? ' source-cursor' : '');
    card.dataset.pid = it.projectId;
    card.dataset.ts = String(it.ts);
    card.title = 'Open project chat';
    card.setAttribute('role', 'button');
    card.tabIndex = 0;
    const abs = new Date(it.ts).toLocaleString();
    const metaHtml =
      '<div class="feed-meta">' +
      '<span class="pill agent-pill' +
      (agent === 'combined' ? ' agent-pill-rainbow' : '') +
      '" style="' +
      esc(agentPillStyle(agent, it.projectId)) +
      '">' +
      esc(displayAgentLabel(it.msg, it.projectId)) +
      '</span>' +
      (imported ? '<span class="pill imported">Imported</span>' : '<span class="pill pill-live">Live</span>') +
      '<span class="pill proj">' +
      esc(it.projectName) +
      '</span>' +
      '<button type="button" class="pill pill-summarize btn-summarize-chat" data-pid="' +
      esc(it.projectId) +
      '" title="' +
      esc(summarizeTitleForProject(state.projects.find(x => x.id === it.projectId))) +
      '">Summary</button>' +
      '<time datetime="' +
      esc(abs) +
      '" title="' +
      esc(abs) +
      '">' +
      esc(formatTimeLabel(it.ts)) +
      '</time></div>';
    const bodyHtml = '<div class="feed-body">' + esc(messageDisplayText(it.msg)) + '</div>';
    card.innerHTML = buildChatFrameHtml(metaHtml, bodyHtml);
    applyAgentChatClasses(card, it.msg, it.projectId);
    frag.appendChild(card);
  });
  if (items.length > TIMELINE_RENDER_LIMIT) {
    const note = document.createElement('p');
    note.className = 'empty';
    note.textContent = 'Showing newest ' + TIMELINE_RENDER_LIMIT + ' of ' + items.length + ' events.';
    frag.appendChild(note);
  }
  box.innerHTML = '';
  box.appendChild(frag);
  updateSummarizeButton();
}

function renderChatHub() {
  ensureUi();
  renderChatFilters();
  renderChatLegend();
  updateChatViewHint();
  renderProjectStrip();
  renderAgentsLive();
  if (isLibraryNav(state.activeNav)) renderLibraryView();
  const mode = state.ui.chatView || 'timeline';
  const timeline = $('timelineView');
  const thread = $('chatSection');
  const strip = $('projectStrip');
  document.querySelectorAll('#chatTabs button').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.chatView === mode);
  });
  if (timeline) timeline.classList.toggle('hidden', mode !== 'timeline');
  if (strip) strip.style.display = 'flex';
  if (thread) {
    if (mode === 'thread') {
      thread.classList.add('open');
      renderChat();
    } else {
      thread.classList.remove('open');
    }
  }
  if (mode === 'timeline') renderTimeline();
  updateThreadPanelHead();
  updateChatWrapTheme();
  updateSummarizeButton();
}

function renderAgentsLive() {
  const host = $('agentLiveList');
  if (!host) return;
  const stats = collectAgentStats();
  if (!stats.length) {
    host.innerHTML = '<p class="empty">No agent activity yet.</p>';
    return;
  }
  host.innerHTML = stats
    .map(s => {
      const st = agentMeta(s.id);
      const col = st.border || st.color;
      return (
        '<button type="button" class="agent-row agent-' +
        agentSlug(s.id) +
        '" data-agent="' +
        esc(s.id) +
        '" style="border-left-color:' +
        esc(col) +
        '">' +
        '<span class="dot" style="background:' +
        esc(col) +
        '"></span>' +
        '<span class="info"><h4>' +
        esc(agentLabel(s.id)) +
        '</h4><p>' +
        esc(s.lastText || '—') +
        '</p></span>' +
        '<span class="stat">' +
        s.count +
        '<br>' +
        esc(formatTimeLabel(s.lastTs)) +
        '</span></button>'
      );
    })
    .join('');
}

function renderAgentsView() {
  renderLibraryView();
}

function onSummarizeClick(ev) {
  const btn = ev.target.closest('.btn-summarize-chat');
  if (!btn || btn.disabled) return false;
  const pid = btn.dataset.pid || state.activeProjectId;
  if (!pid) return false;
  ev.preventDefault();
  ev.stopPropagation();
  summarizeChat(pid);
  return true;
}

function onTimelineClick(ev) {
  if (onSummarizeClick(ev)) return;
  const card = ev.target.closest('.feed-item');
  if (!card?.dataset.pid) return;
  ev.preventDefault();
  openProjectChat(card.dataset.pid, card.dataset.ts ? Number(card.dataset.ts) : null);
}

function onTimelineKeydown(ev) {
  if (ev.key !== 'Enter' && ev.key !== ' ') return;
  const card = ev.target.closest('.feed-item');
  if (!card?.dataset.pid) return;
  ev.preventDefault();
  openProjectChat(card.dataset.pid, card.dataset.ts ? Number(card.dataset.ts) : null);
}

function onAgentRowClick(ev) {
  const row = ev.target.closest('[data-agent]');
  if (!row) return;
  const id = row.dataset.agent;
  if (!id) return;
  ensureUi();
  setAgentFilter(id);
  switchNav('chats');
  setChatView('timeline');
}

function onProjectGridClick(ev, grid) {
  if (onSummarizeClick(ev)) return;
  const card = ev.target.closest('.project');
  if (!card || !grid.contains(card)) return;
  const id = card.dataset.pid;
  const p = state.projects.find(x => x.id === id);
  if (!p) return;
  if (ev.type === 'dblclick') {
    ev.preventDefault();
    p.pinned = !p.pinned;
    saveState();
    renderProjects();
    if (state.activeNav === 'pins') renderPinsList();
    return;
  }
  if (state.activeNav === 'chats') openProjectChat(id);
  else selectProject(id);
}

function selectProject(id) {
  state.activeProjectId = id;
  chatRenderKey = '';
  timelineRenderKey = '';
  saveState();
  if (getStartMode() === 'whole') enterWorkspace();
  renderProjects();
  renderChatHub();
  renderEngineComboPicker();
  const p = getActiveProject();
  $('subtitle').textContent = `Chat · ${p.name}`;
}

function renderChat() {
  const p = getActiveProject();
  if (!p) return;
  const box = $('messages');
  if (!box) return;
  const key = p.id + ':' + p.messages.length + ':' + (p.messages[p.messages.length - 1]?.ts || 0) + ':' + agentColorsRevision();
  if (key === chatRenderKey && box.childElementCount > 0) return;
  chatRenderKey = key;
  const slice = p.messages.length > CHAT_RENDER_LIMIT ? p.messages.slice(-CHAT_RENDER_LIMIT) : p.messages;
  if (!slice.length) {
    box.innerHTML = '<p class="empty">No messages in this project. Send below or import from Bridge.</p>';
  } else {
    const frag = document.createDocumentFragment();
    if (p.messages.length > CHAT_RENDER_LIMIT) {
      const note = document.createElement('p');
      note.className = 'empty';
      note.textContent = 'Showing last ' + CHAT_RENDER_LIMIT + ' messages.';
      frag.appendChild(note);
    }
    slice.forEach((m, idx) => {
      normalizeMessage(m, Date.now() - idx, p.id);
      const d = document.createElement('article');
      const imported = isCursorImportedMessage(m);
      const agent = resolveAgentId(m, p.id);
      d.className =
        'thread-card ' + (m.role || 'assistant') + (m.error ? ' error' : '') + (imported ? ' source-cursor' : '');
      d.dataset.ts = String(m.ts);
      const metaHtml =
        '<div class="thread-head"><span class="thread-agent-label">' +
        esc(imported ? 'Imported · ' + displayAgentLabel(m, p.id) : displayAgentLabel(m, p.id)) +
        '</span><time>' +
        esc(formatTimeLabel(m.ts)) +
        '</time></div>';
      const bodyHtml = '<div class="thread-body">' + esc(messageDisplayText(m)) + '</div>';
      d.innerHTML = buildChatFrameHtml(metaHtml, bodyHtml);
      applyAgentChatClasses(d, m, p.id);
      if (m.role === 'user') d.classList.add('from-user');
      else d.classList.add('from-agent');
      if (m.kind === 'summary') d.classList.add('thread-summary');
      frag.appendChild(d);
    });
    box.innerHTML = '';
    box.appendChild(frag);
    box.scrollTop = box.scrollHeight;
  }
  const badge = $('activeProviderBadge');
  if (badge) {
    const n = collectFeedItems().length;
    badge.textContent = n ? n + ' events' : enabledCount() + ' on';
  }
}

function renderProviderUI() {
  const checks = $('providerChecks');
  checks.innerHTML = '';
  PROVIDERS.forEach(p => {
    const lab = document.createElement('label');
    lab.className = 'prov-check agent-' + agentSlug(p);
    const col = agentColor(p);
    lab.innerHTML =
      '<input type="checkbox" data-prov="' +
      p +
      '" ' +
      (state.providers[p] ? 'checked' : '') +
      '> <span class="prov-dot" style="background:' +
      esc(col) +
      '"></span> ' +
      esc(agentLabel(p) || p.charAt(0).toUpperCase() + p.slice(1));
    checks.appendChild(lab);
  });
  checks.querySelectorAll('input').forEach(inp => {
    inp.addEventListener('change', () => {
      state.providers[inp.dataset.prov] = inp.checked;
      saveState();
      timelineRenderKey = '';
      renderChatHub();
    });
  });
  const s = state.settings;
  $('connMode').value = s.connMode || 'ollama';
  $('ollamaUrl').value = s.ollamaUrl || 'http://127.0.0.1:11434';
  $('ollamaModel').value = s.ollamaModel || 'llama3.2';
  $('apiBase').value = s.apiBase || 'https://api.openai.com/v1';
  $('apiKey').value = s.apiKey || '';
  $('apiModel').value = s.apiModel || 'gpt-4o-mini';
  if ($('settingsBrainAuto')) $('settingsBrainAuto').checked = s.brainAuto !== false;
  toggleConnFields();
  renderEngineComboPicker();
  renderCombinedRainbowUI();
}

function saveCombinedRainbowStops(stops) {
  ensureAgentColors();
  state.settings.combinedRainbowStops = stops.map(parseHexColor).filter(Boolean);
  if (state.settings.combinedRainbowStops.length < 2) {
    state.settings.combinedRainbowStops = [...DEFAULT_RAINBOW_STOPS];
  }
  state.settings.agentColors.combined = {
    ...(state.settings.agentColors.combined || {}),
    stops: [...state.settings.combinedRainbowStops]
  };
  timelineRenderKey = '';
  chatRenderKey = '';
  saveState();
}

function renderCombinedRainbowUI() {
  const host = $('combinedRainbowPanel');
  if (!host) return;
  ensureAgentColors();
  const stops = getCombinedRainbowStops(null);
  const grad = buildRainbowGradient(stops);
  const toggle = $('combinedRainbowToggle');
  if (toggle) toggle.checked = state.settings.combinedRainbow !== false;
  const preview = $('combinedRainbowPreview');
  if (preview) preview.style.background = grad;
  const grid = $('combinedRainbowStops');
  if (!grid) return;
  grid.innerHTML = '';
  stops.forEach((hex, i) => {
    const row = document.createElement('label');
    row.className = 'rainbow-stop-row';
    row.innerHTML =
      '<span>Stop ' +
      (i + 1) +
      '</span><input type="color" data-rainbow-idx="' +
      i +
      '" value="' +
      esc(hex) +
      '">';
    grid.appendChild(row);
  });
  grid.querySelectorAll('input[type="color"]').forEach(inp => {
    inp.addEventListener('input', () => {
      const next = [...getCombinedRainbowStops(null)];
      next[+inp.dataset.rainbowIdx] = inp.value;
      saveCombinedRainbowStops(next);
      renderCombinedRainbowUI();
      renderChatLegend();
      renderAgentFilterChips();
      renderEngineComboPicker();
      renderChatHub();
    });
  });
}

function renderAgentColorUI() {
  const host = $('agentColorPicker');
  if (!host) return;
  ensureAgentColors();
  host.innerHTML = '';
  COLORABLE_AGENTS.filter(id => id !== 'combined').forEach(id => {
    const row = document.createElement('div');
    row.className = 'agent-color-row agent-' + agentSlug(id);
    const custom = state.settings.agentColors[id];
    const hex = custom?.color ? parseHexColor(custom.color) : defaultAgentHex(id);
    const label = document.createElement('span');
    label.className = 'agent-color-label';
    label.textContent = agentLabel(id);
    const swatch = document.createElement('span');
    swatch.className = 'agent-color-swatch';
    swatch.style.background = hex || defaultAgentHex(id);
    const inp = document.createElement('input');
    inp.type = 'color';
    inp.dataset.agent = id;
    inp.value = hex || defaultAgentHex(id);
    inp.title = 'Custom color for ' + agentLabel(id);
    const reset = document.createElement('button');
    reset.type = 'button';
    reset.className = 'btn btn-ghost btn-mini';
    reset.dataset.resetAgent = id;
    reset.textContent = 'Reset';
    reset.disabled = !custom;
    row.append(label, swatch, inp, reset);
    host.appendChild(row);
  });
  host.querySelectorAll('input[type="color"]').forEach(inp => {
    inp.addEventListener('input', () => {
      const id = inp.dataset.agent;
      setAgentCustomColor(id, inp.value);
      const row = inp.closest('.agent-color-row');
      row?.querySelector('.agent-color-swatch')?.style.setProperty('background', inp.value);
      row?.querySelector('[data-reset-agent]')?.removeAttribute('disabled');
      refreshProviderColorDots();
      renderChatHub();
    });
  });
  host.querySelectorAll('[data-reset-agent]').forEach(btn => {
    btn.addEventListener('click', () => {
      resetAgentCustomColor(btn.dataset.resetAgent);
      renderAgentColorUI();
      refreshProviderColorDots();
      renderChatHub();
    });
  });
}

function refreshProviderColorDots() {
  $('providerChecks')?.querySelectorAll('.prov-check').forEach(lab => {
    const inp = lab.querySelector('input[data-prov]');
    if (!inp) return;
    const dot = lab.querySelector('.prov-dot');
    if (dot) dot.style.background = agentColor(inp.dataset.prov);
  });
}

function toggleConnFields() {
  const mode = $('connMode').value;
  $('ollamaFields').style.display = mode === 'ollama' ? 'block' : 'none';
  $('openaiFields').style.display = mode === 'openai' ? 'block' : 'none';
}

function readSettings() {
  state.settings.connMode = $('connMode').value;
  state.settings.ollamaUrl = $('ollamaUrl').value.replace(/\/$/, '');
  state.settings.ollamaModel = $('ollamaModel').value.trim();
  state.settings.apiBase = $('apiBase').value.replace(/\/$/, '');
  state.settings.apiKey = $('apiKey').value;
  state.settings.apiModel = $('apiModel').value.trim();
  if ($('settingsBrainAuto')) state.settings.brainAuto = $('settingsBrainAuto').checked;
  saveState();
}

async function testConnection() {
  readSettings();
  setStatus('Testing connection…', null);
  try {
    if (state.settings.connMode === 'ollama') {
      const r = await fetch(state.settings.ollamaUrl + '/api/tags', { signal: AbortSignal.timeout(8000) });
      if (!r.ok) throw new Error('Ollama HTTP ' + r.status);
      const data = await r.json();
      const names = (data.models || []).map(m => m.name).slice(0, 4).join(', ') || '(none — run: ollama pull llama3.2)';
      setStatus('Ollama OK · ' + names, true);
    } else {
      if (!state.settings.apiKey) throw new Error('Add an API key.');
      const r = await fetch(state.settings.apiBase + '/models', {
        headers: { Authorization: 'Bearer ' + state.settings.apiKey },
        signal: AbortSignal.timeout(10000)
      });
      if (!r.ok) throw new Error('API HTTP ' + r.status + ' (CORS may block browser — use Ollama or a local proxy)');
      setStatus('API OK · ready to chat', true);
    }
  } catch (e) {
    setStatus(e.message + ' · Use RUN-AI-HUB.bat and install Ollama for easiest setup.', false);
  }
}

async function sendMessage() {
  if (sending) return;
  const text = $('chatInput').value.trim();
  if (!text) return;
  const project = getActiveProject();
  if (!project) return;
  readBridgeUI();
  const b = state.bridge;
  $('chatInput').value = '';
  sending = true;
  $('btnSend').disabled = true;
  updateSummarizeButton();
  const parts = [];

  if (b.relayHub !== false) {
    project.messages.push(makeMessage('user', text, { agent: 'you' }));
    timelineRenderKey = '';
    renderChatHub();
  }

  if (b.relayCursor) {
    try {
      await relayToCursor(text);
      parts.push('Cursor outbox');
    } catch (e) {
      parts.push('Cursor failed');
    }
  }

  const runAi = b.relayHub !== false || b.relayOllama;
  let route = 'assistant';
  if (runAi) {
    setStatus('Thinking…', null);
    route = pickProvider();
    try {
      const hist =
        b.relayHub !== false
          ? project.messages.filter(m => m.role === 'user' || m.role === 'assistant').slice(0, -1)
          : [];
      let reply;
      let agentBrand = replyAgentId(route);
      if (shouldUseBrainAuto()) {
        setStatus('Brain auto-blending Blockbuster models…', null);
        const brain = await brainAutoBlend(text, hist);
        reply = brain.blended;
        route = 'combined';
        agentBrand = 'combined';
        parts.push('BRAIN AUTO (' + (brain.models || []).length + ' models)');
      } else {
        reply = await callAI(text, hist, route);
        parts.push(route.toUpperCase());
      }
      if (b.relayHub !== false) {
        project.messages.push(
          makeMessage('assistant', reply, { agent: agentBrand, provider: route, source: 'hub' })
        );
      }
    } catch (e) {
      if (b.relayHub !== false) {
        project.messages.push(
          makeMessage('assistant', 'Error: ' + e.message, { agent: replyAgentId(route), provider: route, error: true })
        );
      }
      setStatus(e.message, false);
      sending = false;
      $('btnSend').disabled = false;
      updateSummarizeButton();
      saveState();
      timelineRenderKey = '';
      renderChatHub();
      return;
    }
  }

  setStatus(parts.length ? parts.join(' · ') : 'Nothing relayed — enable targets in Bridge', true);
  sending = false;
  $('btnSend').disabled = false;
  updateSummarizeButton();
  saveState();
  timelineRenderKey = '';
  renderChatHub();
}

async function callChatMessages(messages) {
  readSettings();
  if (state.settings.connMode === 'ollama') {
    const r = await fetch(state.settings.ollamaUrl + '/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: state.settings.ollamaModel,
        messages,
        stream: false
      }),
      signal: AbortSignal.timeout(180000)
    });
    if (!r.ok) {
      const err = await r.text();
      throw new Error(
        'Ollama failed (' + r.status + '). Start Ollama app, then: ollama pull ' + state.settings.ollamaModel + (err ? ' — ' + err.slice(0, 80) : '')
      );
    }
    const data = await r.json();
    return data.message?.content || '(empty response)';
  }

  if (!state.settings.apiKey) throw new Error('No API key — open Providers or switch to Ollama.');
  const r = await fetch(state.settings.apiBase + '/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer ' + state.settings.apiKey
    },
    body: JSON.stringify({ model: state.settings.apiModel, messages }),
    signal: AbortSignal.timeout(180000)
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error('API ' + r.status + (t ? ': ' + t.slice(0, 120) : ''));
  }
  const data = await r.json();
  return data.choices?.[0]?.message?.content || '(empty)';
}

async function callAITask(systemContent, userContent) {
  return callChatMessages([
    { role: 'system', content: systemContent },
    { role: 'user', content: userContent }
  ]);
}

async function callAI(userText, history, providerLabel) {
  const sys = `You are AI Hub (OverDOn). Routed provider label: ${providerLabel}. Be helpful and concise.`;
  const messages = [
    { role: 'system', content: sys },
    ...history
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.text })),
    { role: 'user', content: userText }
  ];
  return callChatMessages(messages);
}

function buildProjectTranscript(project) {
  const msgs = (project?.messages || []).filter(m => m.role === 'user' || m.role === 'assistant');
  if (!msgs.length) return '';
  let slice = msgs;
  if (msgs.length > SUMMARIZE_MAX_MESSAGES) {
    slice = msgs.slice(0, 24).concat(msgs.slice(-(SUMMARIZE_MAX_MESSAGES - 24)));
  }
  const combo = getProjectEngineCombo(project);
  const lines = ['Project: ' + (project.name || 'Untitled'), 'Engine combo: ' + (combo.meta || '—'), 'Messages: ' + msgs.length, '---'];
  let total = lines.join('\n').length;
  let truncated = false;
  for (const m of slice) {
    normalizeMessage(m, m.ts, project.id);
    const who = m.role === 'user' ? 'User' : displayAgentLabel(m, project.id);
    let body = messageDisplayText(m).trim();
    if (m.kind === 'summary') body = '[prior summary]\n' + body;
    if (body.length > SUMMARIZE_MSG_CHARS) body = body.slice(0, SUMMARIZE_MSG_CHARS) + '…';
    const line = '[' + formatTimeLabel(m.ts) + '] ' + who + ': ' + body;
    if (total + line.length > SUMMARIZE_TOTAL_CHARS) {
      truncated = true;
      break;
    }
    lines.push(line);
    total += line.length + 1;
  }
  if (msgs.length > slice.length || truncated) {
    lines.push('(Transcript trimmed — ' + slice.length + ' of ' + msgs.length + ' messages shown.)');
  }
  return lines.join('\n');
}

function openChatSummaryModal(opts) {
  const modal = $('chatSummaryModal');
  const body = $('chatSummaryBody');
  const title = $('chatSummaryTitle');
  const sub = $('chatSummarySubtitle');
  const addBtn = $('chatSummaryAddToThread');
  const copyBtn = $('chatSummaryCopy');
  if (!modal || !body) return;
  const o = opts || {};
  if (title) title.textContent = o.loading ? 'Summarizing…' : 'Chat summary';
  if (sub) {
    sub.textContent = o.projectName
      ? o.projectName + (o.loading ? ' · AI is reading your thread' : o.error ? ' · failed' : '')
      : '';
  }
  if (o.loading) {
    body.textContent = 'Reading project messages and building a summary of what you and the AIs worked on…';
    body.classList.add('chat-summary-loading');
  } else if (o.error) {
    body.textContent = 'Could not summarize:\n\n' + o.error;
    body.classList.remove('chat-summary-loading');
  } else {
    body.textContent = o.text || '(empty)';
    body.classList.remove('chat-summary-loading');
  }
  if (addBtn) addBtn.disabled = !!(o.loading || o.error || !o.text);
  if (copyBtn) copyBtn.disabled = !!(o.loading || o.error || !o.text);
  modal.hidden = false;
  modal.classList.add('open');
}

function closeChatSummaryModal() {
  const modal = $('chatSummaryModal');
  if (!modal) return;
  modal.classList.remove('open');
  modal.hidden = true;
}

async function summarizeChat(projectId) {
  if (summarizing || sending) return;
  const project = projectId
    ? state.projects.find(x => x.id === projectId)
    : getActiveProject();
  if (!project) return;
  summaryTargetProjectId = project.id;
  const transcript = buildProjectTranscript(project);
  if (!transcript) {
    setStatus('No messages to summarize in this project.', false);
    return;
  }
  summarizing = true;
  updateSummarizeButton();
  openChatSummaryModal({ loading: true, projectName: project.name });
  setStatus('Summarizing chat…', null);
  try {
    const summary = await callAITask(
      SUMMARIZE_SYSTEM_PROMPT,
      'Summarize the following project chat transcript.\n\n' + transcript
    );
    project.chatSummary = {
      text: summary,
      ts: Date.now(),
      messageCount: countSummarizableMessages(project)
    };
    saveState();
    openChatSummaryModal({ loading: false, text: summary, projectName: project.name });
    setStatus('Chat summary ready', true);
  } catch (e) {
    openChatSummaryModal({ loading: false, error: e.message, projectName: project.name });
    setStatus(e.message, false);
  } finally {
    summarizing = false;
    updateSummarizeButton();
  }
}

function addChatSummaryToThread() {
  const p =
    state.projects.find(x => x.id === (summaryTargetProjectId || state.activeProjectId)) || getActiveProject();
  const text = p?.chatSummary?.text;
  if (!p || !text) return;
  const route = pickProvider();
  const brand = replyAgentId(route);
  p.messages.push(
    makeMessage('assistant', '**Chat summary** (' + new Date().toLocaleString() + ')\n\n' + text, {
      agent: brand,
      provider: route,
      source: 'hub',
      kind: 'summary'
    })
  );
  chatRenderKey = '';
  timelineRenderKey = '';
  saveState();
  renderChatHub();
  closeChatSummaryModal();
  setStatus('Summary added to thread', true);
}

async function copyChatSummary() {
  const p =
    state.projects.find(x => x.id === (summaryTargetProjectId || state.activeProjectId)) || getActiveProject();
  const text = p?.chatSummary?.text || $('chatSummaryBody')?.textContent || '';
  if (!text || text.startsWith('Reading project') || text.startsWith('Could not summarize')) return;
  try {
    await navigator.clipboard.writeText(text);
    setStatus('Summary copied', true);
  } catch (_) {
    setStatus('Copy failed — select text in the modal', false);
  }
}

function copyCodeSnippet(key, btn) {
  const text = getCodeText(key);
  if (!text) return Promise.reject(new Error('Unknown snippet'));
  const entry = getCodeEntry(key);
  const label = entry?.tag || key;
  return navigator.clipboard.writeText(text).then(() => {
    if (btn) {
      btn.classList.add('copied');
      setTimeout(() => btn.classList.remove('copied'), 1400);
    }
    setStatus('Copied ' + label, true);
  });
}

function openCodePreview(key) {
  const entry = getCodeEntry(key);
  const text = getCodeText(key);
  if (!text) return;
  codePreviewKey = key;
  const modal = $('codePreviewModal');
  $('codePreviewTitle').textContent = entry?.tag || key;
  $('codePreviewSubtitle').textContent = entry?.title || CODE_META[key] || 'Code snippet';
  $('codePreviewBody').textContent = text;
  modal.hidden = false;
  modal.classList.add('open');
  $('codePreviewCopy').classList.remove('copied');
  $('codePreviewCopy').focus();
}

function closeCodePreview() {
  const modal = $('codePreviewModal');
  if (!modal) return;
  modal.classList.remove('open');
  modal.hidden = true;
  codePreviewKey = null;
}

function initCodePreview() {
  const modal = $('codePreviewModal');
  if (!modal) return;
  $('codePreviewClose')?.addEventListener('click', closeCodePreview);
  $('codePreviewBackdrop')?.addEventListener('click', closeCodePreview);
  $('codePreviewCopy')?.addEventListener('click', () => {
    if (!codePreviewKey) return;
    copyCodeSnippet(codePreviewKey, $('codePreviewCopy')).catch(() => setStatus('Copy failed', false));
  });
}

function appendCodeBubble(list, card) {
  const isPinned = isCodePinned(card);
  const previewId = card.builtin ? card.tag : card.id;
  const stageActive = state.codes?.activeKey === previewId;
  const bubble = document.createElement('article');
  bubble.className = 'code-bubble' + (isPinned ? ' pinned' : '') + (stageActive ? ' stage-active' : '');
  bubble.dataset.codeKey = previewId;

  const head = document.createElement('div');
  head.className = 'code-bubble-head';
  head.innerHTML =
    '<div><div class="code-bubble-tag">' +
    esc(card.tag) +
    '</div><div class="code-bubble-title">' +
    esc(card.title || '') +
    (card.file ? ' · ' + esc(card.file) : '') +
    '</div></div>';

  const preview = document.createElement('div');
  preview.className = 'code-bubble-preview';
  preview.textContent = card.text;

  const actions = document.createElement('div');
  actions.className = 'code-bubble-actions';
  const btnPinOpen = document.createElement('button');
  btnPinOpen.type = 'button';
  btnPinOpen.className = 'btn-pin-open' + (isPinned ? ' pinned-active' : '');
  btnPinOpen.textContent = isPinned ? 'Open' : 'Pin & open';
  btnPinOpen.title = isPinned
    ? 'Open in workspace (left). Shift+click to unpin.'
    : 'Pin and open HTML / software preview in workspace — one click';
  btnPinOpen.addEventListener('click', e => {
    e.stopPropagation();
    if (e.shiftKey && isPinned) {
      togglePinCode(card.id, card.tag, card.text, card.title, card.builtin);
      return;
    }
    pinAndOpenCode(previewId, card);
  });

  const btnPreview = document.createElement('button');
  btnPreview.type = 'button';
  btnPreview.className = 'btn-preview';
  btnPreview.textContent = 'Quick view';
  btnPreview.title = 'Small modal preview (code text)';
  btnPreview.addEventListener('click', e => {
    e.stopPropagation();
    pinAndOpenCode(previewId, card);
  });

  const btnCopy = document.createElement('button');
  btnCopy.type = 'button';
  btnCopy.className = 'icon-btn';
  btnCopy.title = 'Copy code';
  btnCopy.innerHTML = ICON_COPY;
  btnCopy.addEventListener('click', e => {
    e.stopPropagation();
    copyCodeSnippet(previewId, btnCopy).catch(() => setStatus('Copy failed', false));
  });

  const btnPin = document.createElement('button');
  btnPin.type = 'button';
  btnPin.className = 'icon-btn' + (isPinned ? ' pinned-active' : '');
  btnPin.title = isPinned ? 'Pin & open workspace (Shift+click unpin)' : 'Pin & open workspace';
  btnPin.textContent = '📌';
  btnPin.addEventListener('click', e => {
    e.stopPropagation();
    if (e.shiftKey && isPinned) {
      togglePinCode(card.id, card.tag, card.text, card.title, card.builtin);
      return;
    }
    pinAndOpenCode(previewId, card);
  });

  actions.appendChild(btnPinOpen);
  actions.appendChild(btnPreview);
  actions.appendChild(btnPin);
  actions.appendChild(btnCopy);
  bubble.addEventListener('click', e => {
    if (e.target.closest('button')) return;
    pinAndOpenCode(previewId, card);
  });
  bubble.appendChild(head);
  bubble.appendChild(preview);
  bubble.appendChild(actions);
  list.appendChild(bubble);
}

function renderCodes() {
  const host = $('codeBubblesHost');
  if (!host) return;
  ensureCodesState();
  updateCodesLocationField();
  const { pinned, builtins } = listCodeCards();
  const badge = $('codesBadge');
  if (badge) badge.textContent = pinned.length ? pinned.length + ' PINNED' : 'BUBBLES';

  host.innerHTML = '';
  const wrap = document.createDocumentFragment();

  if (pinned.length) {
    const h = document.createElement('p');
    h.className = 'codes-section-label pinned';
    h.textContent = 'Pinned — use Save pins to folder';
    wrap.appendChild(h);
    const list = document.createElement('div');
    list.className = 'code-bubbles';
    pinned.forEach(c => appendCodeBubble(list, c));
    wrap.appendChild(list);
  }

  const h2 = document.createElement('p');
  h2.className = 'codes-section-label';
  h2.textContent = pinned.length ? 'Library' : 'All snippets';
  wrap.appendChild(h2);
  const list2 = document.createElement('div');
  list2.className = 'code-bubbles';
  builtins.forEach(c => appendCodeBubble(list2, c));
  wrap.appendChild(list2);
  host.appendChild(wrap);
}

function newProject() {
  const name = prompt('Project name?');
  if (!name?.trim()) return;
  const lines = ENGINE_COMBOS.map((c, i) => i + 1 + '. ' + c.name + ' — ' + c.meta).join('\n');
  const pick = prompt('Engine combo (number, or leave blank for General):\n\n' + lines);
  let combo = ENGINE_COMBOS[0];
  const n = parseInt(pick, 10);
  if (n >= 1 && n <= ENGINE_COMBOS.length) combo = ENGINE_COMBOS[n - 1];
  const id = 'p-' + Date.now();
  state.projects.unshift({
    id,
    name: name.trim(),
    desc: combo.name + ' workspace',
    meta: combo.meta,
    engineCombo: combo.id,
    messages: [],
    pinned: false
  });
  combo.providers.forEach(prov => {
    if (PROVIDERS.includes(prov)) state.providers[prov] = true;
  });
  state.activeProjectId = id;
  saveState();
  switchNav('chats');
  selectProject(id);
  renderEngineComboPicker();
}

function initParticles() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const canvas = $('bg');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w = 0;
  let h = 0;
  let running = true;
  const particles = [];
  const COUNT = 48;
  const bgGrad = ctx.createLinearGradient(0, 0, 1, 1);
  bgGrad.addColorStop(0, '#050505');
  bgGrad.addColorStop(1, '#0b0b14');

  function resize() {
    w = canvas.width = innerWidth;
    h = canvas.height = innerHeight;
  }

  const resizeThrottled = perf.throttle(resize, 200);
  addEventListener('resize', resizeThrottled);
  resize();

  for (let i = 0; i < COUNT; i++) {
    particles.push({
      x: Math.random() * w,
      y: Math.random() * h,
      r: Math.random() * 1.8 + 0.8,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.2
    });
  }

  document.addEventListener('visibilitychange', () => {
    running = !document.hidden;
    if (running) requestAnimationFrame(loop);
  });

  let last = 0;
  function loop(ts) {
    if (!running) return;
    if (ts - last < 33) {
      requestAnimationFrame(loop);
      return;
    }
    last = ts;
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = 'rgba(0,255,238,.35)';
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
}

async function boot() {
  if (!state.settings.startMode) state.settings.startMode = 'whole';
  if (state.workspaceOpen === undefined) state.workspaceOpen = getStartMode() === 'odd';
  ensurePicturesState();

  initNav();
  initModeSwitches();
  renderProviderUI();
  renderAgentColorUI();
  renderCombinedRainbowUI();
  renderCodes();
  initCodePreview();
  initCodeStage();
  initCodesPanel();
  initCombinedRainbowSettings();
  initPicturesPanel();
  initGlobalKeyboard();
  if (!state.activeProjectId && state.projects[0]) state.activeProjectId = state.projects[0].id;

  applyStartMode();
  timelineRenderKey = '';
  chatRenderKey = '';
  renderChatHub();
  updateShowOriginalsButton();

  let bridgeOnline = false;
  try {
    bridgeOnline = await refreshBridgeStatus();
  } catch (_) {
    bridgeOnline = false;
  }

  if (bridgeOnline) {
    if (getStartMode() === 'whole') {
      state.workspaceOpen = true;
      document.body.classList.add('workspace-open');
      saveState();
    }
    switchNav('bridge');
    await initBridgePanel(true);
  } else if (getStartMode() === 'odd') {
    selectProject(state.activeProjectId);
    switchNav(state.activeNav || 'chats');
  } else {
    switchNav(state.activeNav || 'bridge');
    renderProjects();
    const box = $('bridgeStatusBox');
    if (box) {
      box.innerHTML =
        '<h3>Bridge offline</h3><p>Run <strong>RUN-AI-HUB.bat</strong> from your ai hub folder (do not open the HTML file directly).</p>';
    }
    setStatus('Bridge offline — use RUN-AI-HUB.bat', false);
  }

  if (location.hash === '#bridge') goToBridge();

  const onSearch = perf.debounce(() => {
    const main = $('search');
    const start = $('searchStart');
    if (main && start) {
      if (document.activeElement === start) main.value = start.value;
      else start.value = main.value;
    }
    renderProjects();
    renderChatHub();
  }, 160);
  $('search')?.addEventListener('input', onSearch);
  $('searchStart')?.addEventListener('input', onSearch);
  $('projectGrid')?.addEventListener('click', e => onProjectGridClick(e, $('projectGrid')));
  $('projectGrid')?.addEventListener('dblclick', e => onProjectGridClick(e, $('projectGrid')));
  $('projectGridStart')?.addEventListener('click', e => onProjectGridClick(e, $('projectGridStart')));
  $('projectGridStart')?.addEventListener('dblclick', e => onProjectGridClick(e, $('projectGridStart')));
  $('view-bridge')?.addEventListener('click', e => {
    onBridgePanelClick(e);
    onCursorSessionClick(e);
  });
  if ($('btnBridge')) $('btnBridge').addEventListener('click', goToBridge);
  if ($('btnStartBridge')) $('btnStartBridge').addEventListener('click', goToBridge);
  $('chatTabs')?.addEventListener('click', e => {
    const btn = e.target.closest('button[data-chat-view]');
    if (btn) setChatView(btn.dataset.chatView);
  });
  $('filterAgent')?.addEventListener('change', e => setAgentFilter(e.target.value));
  $('agentFilterChips')?.addEventListener('click', e => {
    const chip = e.target.closest('.agent-chip');
    if (!chip?.dataset.agent) return;
    setAgentFilter(chip.dataset.agent);
  });
  $('filterProject')?.addEventListener('change', e => {
    ensureUi();
    state.ui.filterProject = e.target.value;
    timelineRenderKey = '';
    saveState();
    renderChatHub();
  });
  $('filterSource')?.addEventListener('change', e => {
    ensureUi();
    state.ui.filterSource = e.target.value;
    timelineRenderKey = '';
    saveState();
    renderChatHub();
  });
  $('timelineView')?.addEventListener('click', onTimelineClick);
  $('timelineView')?.addEventListener('keydown', onTimelineKeydown);
  $('projectStrip')?.addEventListener('click', e => {
    if (onSummarizeClick(e)) return;
    const chip = e.target.closest('.project-chip');
    if (chip?.dataset.pid) openProjectChat(chip.dataset.pid);
  });
  $('agentLiveList')?.addEventListener('click', onAgentRowClick);
  initLibraryPanel();
  $('engineComboPicker')?.addEventListener('click', e => {
    const chip = e.target.closest('[data-combo]');
    if (chip?.dataset.combo) applyEngineCombo(chip.dataset.combo);
  });
  $('btnSend').addEventListener('click', sendMessage);
  $('view-chats')?.addEventListener('click', e => {
    onSummarizeClick(e);
  });
  $('chatSummaryClose')?.addEventListener('click', closeChatSummaryModal);
  $('chatSummaryBackdrop')?.addEventListener('click', closeChatSummaryModal);
  $('chatSummaryAddToThread')?.addEventListener('click', addChatSummaryToThread);
  $('chatSummaryCopy')?.addEventListener('click', copyChatSummary);
  $('chatInput').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  $('connMode').addEventListener('change', toggleConnFields);
  $('btnSaveSettings').addEventListener('click', testConnection);
  $('btnNewProject').addEventListener('click', newProject);
  if ($('btnSave')) $('btnSave').addEventListener('click', saveWorkspaceNow);
  if ($('btnSaveAs')) $('btnSaveAs').addEventListener('click', saveProjectAsCopy);
  if ($('btnRemix')) $('btnRemix').addEventListener('click', remixActiveProject);
  if ($('btnShowOriginals')) $('btnShowOriginals').addEventListener('click', toggleShowOriginalsInMain);
  $('btnSettings').addEventListener('click', openSettings);
  if ($('btnStartSettings')) $('btnStartSettings').addEventListener('click', openSettings);
  if ($('btnBackStart')) $('btnBackStart').addEventListener('click', exitToStart);

  ['relayHub', 'relayCursor', 'relayOllama', 'bridgeAutoSync'].forEach(id => {
    const el = $(id);
    if (el) el.addEventListener('change', readBridgeUI);
  });
  if ($('btnBridgeRefresh')) {
    $('btnBridgeRefresh').addEventListener('click', () => renderCursorSessions(true, false));
  }
  if ($('btnClearCursorImports')) {
    $('btnClearCursorImports').addEventListener('click', () => {
      const n = clearCursorImportsForProject();
      setStatus(n ? 'Removed ' + n + ' imported Cursor message(s)' : 'No Cursor imports in this project', !!n);
    });
  }
  if ($('btnBridgeSync')) $('btnBridgeSync').addEventListener('click', bridgeSyncNow);
  if ($('btnCopyOutbox')) {
    $('btnCopyOutbox').addEventListener('click', async () => {
      await loadOutboxPreview();
      const t = $('outboxPreview').value;
      try {
        await navigator.clipboard.writeText(t);
        setStatus('Copied outbox for Cursor', true);
      } catch (_) {
        $('outboxPreview').select();
        setStatus('Select outbox text and copy (Ctrl+C)', null);
      }
    });
  }

  ensureBridgeState();
  startBridgePoll();
  startAgentsSyncPoll();
  loadBrainConfig().catch(() => {});

  if ($('brainAutoToggle')) {
    $('brainAutoToggle').addEventListener('change', () => {
      state.settings.brainAuto = $('brainAutoToggle').checked;
      saveState();
      renderBrainView();
    });
  }
  if ($('btnBrainSyncDevices')) $('btnBrainSyncDevices').addEventListener('click', () => uploadSyncedDevicesToBrain());
  if ($('btnBrainRefresh')) $('btnBrainRefresh').addEventListener('click', () => loadBrainConfig());
  if ($('btnSaveBuiltAgent')) $('btnSaveBuiltAgent').addEventListener('click', () => saveBuiltAgent());
  if ($('btnBrainTest')) {
    $('btnBrainTest').addEventListener('click', async () => {
      try {
        const r = await brainAutoBlend('Say hello in one sentence.', []);
        setStatus('Brain test OK · route: ' + (r.route || 'auto'), true);
      } catch (e) {
        setStatus(e.message, false);
      }
    });
  }
  if ($('btnOpenBrain')) $('btnOpenBrain').addEventListener('click', () => switchNav('brain'));
  if ($('settingsBrainAuto')) {
    $('settingsBrainAuto').addEventListener('change', () => {
      state.settings.brainAuto = $('settingsBrainAuto').checked;
      if ($('brainAutoToggle')) $('brainAutoToggle').checked = state.settings.brainAuto;
      saveState();
      renderBrainView();
    });
  }

  testConnection();
  initParticles();
}

boot();
