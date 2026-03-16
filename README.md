# KORE Agent
**Context-Orchestration-Research-Engine**

KI-Gedächtnis für alle Paradieschen-Projekte. Baut automatisch optimierte Claude-Prompts aus Projekt-Kontext.

## Projekte
- `paradieschen` — Kistengenerator, biotaste, AI Workspace
- `meeratmen` — Atemtechnik-App
- `tafill` — Baumpflege Website
- `arbos` — Bittensor Agenten-Framework
- `workspace` — Paradieschen AI Workspace

## Start
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```
API Docs: http://localhost:9000/docs

## Endpoints
| Method | Endpoint | Beschreibung |
|--------|----------|-------------|
| GET | `/projects` | Alle Projekte |
| POST | `/prompt` | Optimierten Prompt generieren |
| POST | `/feedback` | Qualitäts-Feedback 1-5 |
| POST | `/learn` | Lernzyklus manuell starten |
| GET | `/widget` | HTML Widget für Workspace |

## Deploy (Hetzner)
```bash
bash deploy.sh
```
