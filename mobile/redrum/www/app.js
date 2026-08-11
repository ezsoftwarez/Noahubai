/* REDRUM — Noahubai AI Hub mobile control app
 * Vanilla JS, no bundler required. Uses the Capacitor native bridge
 * (window.Capacitor.Plugins) when running inside the Android shell,
 * and falls back to localStorage/fetch when previewed in a browser.
 */
(function () {
  'use strict';

  const REFRESH_MS = 8000;
  const STORAGE_KEY = 'redrum.serverUrl';

  const cap = window.Capacitor;
  const isNative = !!(cap && cap.isNativePlatform && cap.isNativePlatform());
  const Preferences = cap && cap.Plugins && cap.Plugins.Preferences;

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  let serverUrl = '';
  let pollTimer = null;
  let connected = false;

  // ---------- storage ----------
  async function getStoredUrl() {
    if (Preferences) {
      const { value } = await Preferences.get({ key: STORAGE_KEY });
      return value || '';
    }
    return localStorage.getItem(STORAGE_KEY) || '';
  }

  async function setStoredUrl(url) {
    if (Preferences) {
      await Preferences.set({ key: STORAGE_KEY, value: url });
    } else {
      localStorage.setItem(STORAGE_KEY, url);
    }
  }

  async function clearStoredUrl() {
    if (Preferences) {
      await Preferences.remove({ key: STORAGE_KEY });
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  function normalizeUrl(raw) {
    let url = (raw || '').trim();
    if (!url) return '';
    if (!/^https?:\/\//i.test(url)) url = 'https://' + url;
    return url.replace(/\/+$/, '');
  }

  // ---------- networking ----------
  async function api(path, opts) {
    const res = await fetch(serverUrl + path, Object.assign({
      headers: { 'Content-Type': 'application/json' },
    }, opts));
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  }

  async function testConnection(url) {
    const res = await fetch(url + '/api/health', { method: 'GET' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
  }

  // ---------- toast ----------
  let toastTimer = null;
  function toast(msg) {
    const el = $('#toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 2600);
  }

  // ---------- status dot ----------
  function setConnDot(state) {
    const dot = $('#topStatusDot');
    dot.classList.remove('online', 'offline', 'checking');
    dot.classList.add(state);
  }

  function setDashPill(state, label) {
    const pill = $('#dashConnPill');
    pill.classList.remove('ok', 'warn', 'err', 'neutral');
    pill.classList.add(state);
    pill.textContent = label;
  }

  // ---------- tabs ----------
  function showView(name) {
    $$('.view').forEach((v) => v.classList.toggle('active', v.id === 'view-' + name));
    $$('.tab').forEach((t) => t.classList.toggle('active', t.dataset.view === name));
  }

  $$('.tab').forEach((tab) => {
    tab.addEventListener('click', () => showView(tab.dataset.view));
  });

  // ---------- rendering ----------
  function severityPillClass(sev) {
    sev = (sev || '').toLowerCase();
    if (sev === 'critical' || sev === 'high') return 'err';
    if (sev === 'medium' || sev === 'warning') return 'warn';
    return 'neutral';
  }

  function healthPillClass(healthy) {
    return healthy ? 'ok' : 'err';
  }

  function agentIcon(name) {
    const n = (name || '').toLowerCase();
    if (n.includes('memory')) return '\u{1F9E0}';
    if (n.includes('issue')) return '\u{1F50D}';
    if (n.includes('fix')) return '\u{1F527}';
    return '⚙️';
  }

  function renderStats(statusData, healthData) {
    const stats = (statusData && statusData.statistics) || {};
    const agents = (statusData && statusData.agents) || [];
    const health = (healthData && healthData.system) || {};

    const cards = $$('#dashStats .stat-card .val');
    cards[0].textContent = health.healthy_agents != null
      ? `${health.healthy_agents}/${health.total_agents ?? agents.length}`
      : String(agents.length || 0);
    cards[1].textContent = stats.open_issues ?? stats.total_issues ?? '0';
    cards[2].textContent = stats.total_patterns ?? stats.patterns_learned ?? '0';
    cards[3].textContent = (statusData && statusData.status) ? statusData.status : '—';
  }

  function renderDashAgents(agents, healthMap) {
    const box = $('#dashAgentList');
    if (!agents || !agents.length) {
      box.innerHTML = '<div class="empty"><div class="icon">●</div><div class="msg">Nincs regisztrált ügynök.</div></div>';
      return;
    }
    box.innerHTML = agents.map((a) => {
      const name = a.name || a.id || a;
      const h = (healthMap && healthMap[name]) || {};
      const healthy = h.healthy !== false;
      return `
        <div class="row">
          <div class="row-icon">${agentIcon(name)}</div>
          <div class="row-body">
            <div class="row-title">${escapeHtml(name)}</div>
            <div class="row-sub">${escapeHtml(a.role || a.status || 'aktív')}</div>
          </div>
          <span class="pill ${healthPillClass(healthy)}">${healthy ? 'OK' : 'HIBA'}</span>
        </div>`;
    }).join('');
  }

  function renderAgentsList(agents, healthMap) {
    const box = $('#agentsList');
    if (!agents || !agents.length) {
      box.innerHTML = '<div class="empty"><div class="icon">⚙️</div><div class="msg">Nincs regisztrált ügynök.</div></div>';
      return;
    }
    box.innerHTML = agents.map((a) => {
      const name = a.name || a.id || a;
      const h = (healthMap && healthMap[name]) || {};
      const healthy = h.healthy !== false;
      return `
        <div class="row" data-agent="${escapeHtml(name)}">
          <div class="row-icon">${agentIcon(name)}</div>
          <div class="row-body">
            <div class="row-title">${escapeHtml(name)}</div>
            <div class="row-sub">${escapeHtml(a.bio || a.role || '')}</div>
          </div>
          <button class="btn small restart-btn" data-agent="${escapeHtml(name)}">Restart</button>
        </div>`;
    }).join('');

    $$('.restart-btn').forEach((btn) => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const name = btn.dataset.agent;
        btn.disabled = true;
        btn.textContent = '…';
        try {
          await api(`/api/agents/${encodeURIComponent(name)}/restart`, { method: 'POST' });
          toast(`${name} újraindítva`);
        } catch (err) {
          toast(`Nem sikerült újraindítani: ${name}`);
        } finally {
          btn.disabled = false;
          btn.textContent = 'Restart';
        }
      });
    });
  }

  function renderIssues(issues) {
    const box = $('#issuesList');
    const list = Array.isArray(issues) ? issues : (issues && issues.issues) || [];
    if (!list.length) {
      box.innerHTML = '<div class="empty"><div class="icon">✅</div><div class="msg">Nincs nyitott hiba.</div></div>';
      return;
    }
    box.innerHTML = list.map((iss) => `
      <div class="row">
        <div class="row-icon">⚠️</div>
        <div class="row-body">
          <div class="row-title">${escapeHtml(iss.title || iss.description || iss.id || 'Ismeretlen hiba')}</div>
          <div class="row-sub">${escapeHtml(iss.status || '')}${iss.status && iss.severity ? ' · ' : ''}${escapeHtml(iss.severity || '')}</div>
        </div>
        <span class="pill ${severityPillClass(iss.severity)}">${escapeHtml((iss.severity || iss.status || '—').toString())}</span>
      </div>`).join('');
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    })[c]);
  }

  function fmtTime() {
    const d = new Date();
    return d.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  // ---------- data refresh ----------
  async function refreshAll() {
    if (!serverUrl) return;
    try {
      const [status, health, agentsRes, issuesRes] = await Promise.all([
        api('/api/status'),
        api('/api/health'),
        api('/api/agents'),
        api('/api/issues').catch(() => ({ issues: [] })),
      ]);

      connected = true;
      setConnDot('online');
      setDashPill('ok', 'online');
      $('#dashTs').textContent = fmtTime();

      const agents = agentsRes.agents || [];
      const healthMap = (health && health.agents) || {};

      renderStats(status, health);
      renderDashAgents(agents, healthMap);
      renderAgentsList(agents, healthMap);
      renderIssues(issuesRes);
    } catch (err) {
      connected = false;
      setConnDot('offline');
      setDashPill('err', 'kapcsolat sikertelen');
    }
  }

  function startPolling() {
    stopPolling();
    refreshAll();
    pollTimer = setInterval(refreshAll, REFRESH_MS);
  }

  function stopPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = null;
  }

  // ---------- connect flow ----------
  async function connectTo(rawUrl, statusEl) {
    const url = normalizeUrl(rawUrl);
    if (!url) {
      if (statusEl) statusEl.textContent = 'Adj meg egy érvényes szerver címet.';
      return false;
    }
    if (statusEl) {
      statusEl.innerHTML = '<span class="spinner"></span> Kapcsolódás…';
    }
    try {
      await testConnection(url);
      serverUrl = url;
      await setStoredUrl(url);
      if (statusEl) statusEl.textContent = '';
      showApp();
      startPolling();
      return true;
    } catch (err) {
      if (statusEl) statusEl.textContent = 'Nem sikerült elérni a szervert. Ellenőrizd a címet és a hálózatot.';
      return false;
    }
  }

  function showOnboard() {
    $('#onboard').classList.remove('hidden');
  }
  function showApp() {
    $('#onboard').classList.add('hidden');
  }

  // ---------- init ----------
  async function init() {
    const stored = await getStoredUrl();
    $('#settingsUrl').value = stored || '';

    if (stored) {
      serverUrl = stored;
      showApp();
      setConnDot('checking');
      startPolling();
    } else {
      showOnboard();
    }

    $('#onboardConnect').addEventListener('click', () => {
      connectTo($('#serverUrl').value, $('#onboardStatus'));
    });
    $('#serverUrl').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') connectTo($('#serverUrl').value, $('#onboardStatus'));
    });

    $('#settingsSave').addEventListener('click', async () => {
      const ok = await connectTo($('#settingsUrl').value, $('#settingsStatus'));
      if (ok) toast('Csatlakozva');
    });

    $('#settingsDisconnect').addEventListener('click', async () => {
      stopPolling();
      await clearStoredUrl();
      serverUrl = '';
      $('#settingsUrl').value = '';
      $('#serverUrl').value = '';
      setConnDot('offline');
      showOnboard();
      showView('dashboard');
    });

    // pull-to-refresh-ish: tap the connection pill to force refresh
    $('#dashConnPill').addEventListener('click', refreshAll);

    if (isNative && cap.Plugins.StatusBar) {
      try { await cap.Plugins.StatusBar.setStyle({ style: 'DARK' }); } catch (e) {}
    }
    if (isNative && cap.Plugins.SplashScreen) {
      try { await cap.Plugins.SplashScreen.hide(); } catch (e) {}
    }

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stopPolling();
      else if (serverUrl) startPolling();
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
