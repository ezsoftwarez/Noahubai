# DEMOCORE OS / brOS

Web-alapú asztali OS — ablakkezelő, taskbar, **DEMOCORE DAW**, **NOAHUBAI**, **AI Hub** szinkron.

## Windows telepítés

Másold a teljes mappát ide:

`C:\Users\krake\OneDrive\Asztali gép\DEMOCORE DAW`

A repo gyökérben maradjanak a Noahubai és AI Hub fájlok (`main.py`, `AI HUB oVerk1LL\`, stb.).

## Indítás (egy kattintás)

Dupla katt: **`START-DEMOCORE.bat`**

Ez elindítja:
1. **NOAHUBAI** — `http://127.0.0.1:8000`
2. **AI Hub Bridge** — `http://127.0.0.1:8765`
3. **DEMOCORE OS** — `http://127.0.0.1:5173`

Csak a web shell: **`dev.cmd`**

## Mit tud a shell?

- Boot → asztal, ablakok, Start menü
- **DEMOCORE DAW** — digitális audio munkaállomás
- **NOAHUBAI** — memory / issue / fixer agentek (beágyazott UI)
- **AI Hub** — Cursor bridge + több AI provider
- **Agents Manager** — egyesített agent szinkron dashboard
- **Agent Builder** — custom agentek AI Hub Brain-be
- **AI Hub Brain** — Auto mode Blockbuster model blend

## Szolgáltatások

| Szolgáltatás | Port | Indítás |
|-------------|------|---------|
| DEMOCORE OS | 5173 | `dev.cmd` vagy `npm dev` |
| NOAHUBAI | 8000 | `python main.py` (repo gyökér) |
| AI Hub | 8765 | `AI HUB oVerk1LL\RUN-AI-HUB.bat` |

## Agent szinkron + Brain

- AI Hub **Brain** tab — fő orchestrator, **Auto** kapcsoló
- Blockbuster free modellek párhuzamos blend: `deepseek`, `llama`, `gemma`, `mistral`
- Agents Manager → **Upload to AI Hub Brain** (szinkronizált eszközök)
- Agent Builder → mentés `/api/brain/agents` végpontra
- Bridge: `GET /api/brain/config`, `POST /api/brain/auto`, `POST /api/brain/devices/upload`

## Stack

Vite · React 19 · TypeScript · Noahubai (FastAPI) · AI Hub bridge (Python)
