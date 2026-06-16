# Noahubai

Unified local AI workspace with:

- AI Hub main menu UI
- Cursor transcript bridge
- Noahubai core agents: Memory, Issue, Fixer

## Single file to run

```bash
python3 main.py
```

That starts the AI Hub main menu on:

- `http://127.0.0.1:8765/index.html`

If FastAPI dependencies are installed, it also starts the Noahubai API on:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## Modes

```bash
python3 main.py --mode all
python3 main.py --mode ui
python3 main.py --mode backend
```

## Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Open-source oriented pieces

- Local/standard-library bridge server in `AI HUB oVerk1LL/bridge_server.py`
- Python agent core under `core/` and `agents/`
- Open-source-friendly image tools already surfaced in the UI