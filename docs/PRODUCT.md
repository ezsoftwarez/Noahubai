# Noahubai Product Definition

## One-line pitch

**Local AI workspace for Cursor and multi-model power users.**

## Primary product: AI Hub (Cursor Bridge)

The sellable product surface is **AI Hub** in [`AI HUB oVerk1LL/`](../AI%20HUB%20oVerk1LL/). It is the daily-use app for Windows power users who work with Cursor, local models (Ollama), and cloud APIs in one place.

| Surface | Role |
|---------|------|
| **AI Hub** | Primary product — install, run, and pay for workflow features |
| **Noahubai backend** | Engine — memory, issue tracking, auto-fix agents behind the hub |
| **Steamish Browser** | Optional component — browsing inside the stack |
| **Codeer / Bloxxbuster** | Legacy standalone clients — not the main offer |

### Why AI Hub is primary

- Packaged Windows installer: [`AI HUB oVerk1LL/Setup/README.txt`](../AI%20HUB%20oVerk1LL/Setup/README.txt)
- Daily-run executable (`AI HUB.exe`) with no Python required
- Cursor bridge, project chats, transcript import, multi-model routing
- Clear audience: indie devs and Cursor power users on Windows

### Official install / run

1. Extract AI Hub v1 bundle
2. Run `Setup.exe` once (installs to `B:\AI HUB oVerk1LL` or chosen path)
3. Use `AI HUB.exe` daily (starts bridge + opens browser)

Alternative with Python: [`AI HUB oVerk1LL/RUN-AI-HUB.bat`](../AI%20HUB%20oVerk1LL/RUN-AI-HUB.bat)

## Engine: Noahubai backend

The FastAPI backend in [`backend/server.py`](../backend/server.py) powers agents (Memory, Issue, Fixer). It runs locally on port 8000 and is **not** the billing surface — entitlements are checked here but sold through AI Hub workflow value.

## Experiments (not the main product)

Side-income and prototype tools live under [`docs/experiments/`](experiments/README.md). They are **optional** and not part of the core monetization story:

- Job-board demo (`moneymaer demo.html`)
- Freelance lead finder (`AGENT WORK.html`)

Do not lead marketing or pricing with these demos.

## Audience

| Segment | Need |
|---------|------|
| **Indie developers** | One workspace for Cursor + local/cloud models |
| **Power users** | Project memory, automation, packaged local AI stack |
| **Small teams** (later) | Shared workspaces, audit, managed sync |

## Open-core model

- **Free:** local core, BYOK, single-user workflows — see [`PRICING.md`](PRICING.md)
- **Paid:** time-saving workflow features, sync, team tools — not raw token markup
- **Services:** setup, custom agent packs, consulting while the product matures

## Related docs

- [Pricing tiers](PRICING.md)
- [Experiments folder](experiments/README.md)
- [Architecture plan](../ARCHITECTURE_PLAN.md)
