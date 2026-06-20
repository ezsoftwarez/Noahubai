AI Hub v1 — Setup folder
========================

**Primary Noahubai product surface.** Install and run this daily.

Setup.exe     First-time install / refresh files to B:\AI HUB oVerk1LL
AI HUB.exe    Start Bridge server + open browser (standalone, no Python needed)

Also available: ..\RUN-AI-HUB.bat (if Python is installed)

After extracting AI HUB v1.zip, run Setup.exe once, then use AI HUB.exe daily.

Plans (Free / Pro / Team)
-------------------------
- Free: local chat, Cursor bridge, BYOK — no license needed
- Pro: advanced memory, automation, analytics — activate via Noahubai backend
- Team: shared workspaces, managed sync

See repo docs/PRICING.md for full tier details.

License activation (connects to Noahubai backend on port 8000):
  POST /api/entitlements/activate  { "license_key": "NHUB-pro-..." }

Experiments (job board, freelance demos) are separate — not part of AI Hub pricing.
See docs/experiments/README.md in the repo root.
