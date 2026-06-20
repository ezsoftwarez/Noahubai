# Noahubai

**Local AI workspace for Cursor and multi-model power users.**

Noahubai is an open-core stack: **AI Hub** is the primary product you install and run daily; the **Noahubai backend** powers memory, issue tracking, and auto-fix agents behind it.

## Quick start

### AI Hub (recommended — primary product)

Windows packaged install:

1. Open [`AI HUB oVerk1LL/Setup/`](AI%20HUB%20oVerk1LL/Setup/)
2. Run `Setup.exe` once
3. Launch `AI HUB.exe` daily

With Python: [`AI HUB oVerk1LL/RUN-AI-HUB.bat`](AI%20HUB%20oVerk1LL/RUN-AI-HUB.bat)

### Noahubai backend (engine)

```bash
pip install -r requirements.txt
python main.py
```

- Web UI: http://localhost:8000  
- API docs: http://localhost:8000/docs  
- Entitlements: http://localhost:8000/api/entitlements  

## What you get

| Component | Role |
|-----------|------|
| **AI Hub** | Cursor bridge, project chats, BYOK providers, transcript import |
| **Noahubai backend** | Memory, Issue, and Fixer agents (FastAPI on port 8000) |
| **Steamish Browser** | Optional Qt browser module |
| **Experiments** | Job/freelance demos — not the core product ([docs/experiments/](docs/experiments/)) |

## Pricing (open-core)

| Plan | For |
|------|-----|
| **Free** | Local core, BYOK, single-user workflows |
| **Pro** | Advanced memory, automation, analytics, audit trail |
| **Team** | Shared workspaces, team knowledge, managed sync |

Details: [docs/PRICING.md](docs/PRICING.md)  
Product definition: [docs/PRODUCT.md](docs/PRODUCT.md)

### Activate a license (Pro / Team)

```bash
curl -X POST http://localhost:8000/api/entitlements/activate \
  -H "Content-Type: application/json" \
  -d '{"license_key": "NHUB-pro-your-id-xxxxxxxx"}'
```

Dev key generation (local only):

```bash
curl "http://localhost:8000/api/entitlements/dev-key?tier=pro"
```

Environment variables:

| Variable | Purpose |
|----------|---------|
| `NOAHUBAI_LICENSE_KEY` | License key |
| `NOAHUBAI_PLAN` | Override plan (`free`, `pro`, `team`) |
| `NOAHUBAI_ENTITLEMENTS_STRICT` | Block premium routes without entitlement |

## Documentation

- [Product definition](docs/PRODUCT.md)
- [Pricing tiers](docs/PRICING.md)
- [System summary](SYSTEM_SUMMARY.md)
- [Complete documentation](COMPLETE_DOCUMENTATION.md)
- [Architecture plan](ARCHITECTURE_PLAN.md)

## Repository layout

```
Noahubai/
├── AI HUB oVerk1LL/     # Primary product (install & run)
├── backend/             # FastAPI + entitlements
├── agents/              # Memory, Issue, Fixer agents
├── core/                # Event bus, registry, state
├── docs/                # Product & pricing docs
├── steamish_browser/    # Optional browser module
└── main.py              # Backend entry point
```

## License model

- **Open-source core** — free for local single-user use  
- **Paid tiers** — workflow features (not token markup); users BYOK  
- **Services** — setup, custom agent packs, Cursor workflow consulting  

## Support

- GitHub: https://github.com/ezsoftwarez/Noahubai  
- Issues: report bugs on GitHub  
