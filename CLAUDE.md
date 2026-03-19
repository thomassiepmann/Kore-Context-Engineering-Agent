# KORE Agent — Claude Code Context

## Stack
- Python, SQLite, Chutes API (Qwen3-235B-A22B)
- Arbos Framework (Jacob Stevens, Bittensor)
- Hetzner Server 89.167.83.224, Port 9000
- Targon Pod: ssh rentals-cwgqpzptji9bxvpj@ssh.deployments.targon.com
- GitHub: thomassiepmann/Kore-Context-Engineering-Agent
- Telegram Bot Control

## Projekt-Regeln
# Python: always use venv
# No hardcoded API keys — use .env
# SQLite DB: kore.db
# Cronjobs: ArXiv/docs daily 03:00, memory updates Sunday 03:30
# Prompt evolution (RL) is active — don't break scoring logic

## Aktive Features
- Prompt Evolution (Reinforcement Learning)
- Kistengenerator Recommender
- ArXiv Crawler (tägliche Briefings)
- Telegram Bot Interface

## Arbos Integration (arbos-trading)
- Repo: github.com/thomassiepmann/arbos-trading
- Targon Pod: ~/Arbos/
- APIs: Chutes (Kimi-K2.5), OpenRouter
- Ziele: Numinous SN6 + Hyperliquid Trading, MetaNova SN68 Mining

## Befehle
# Local: python main.py
# Check port 9000: curl http://localhost:9000/health
# DB inspect: sqlite3 kore.db ".tables"
# Deploy to Hetzner: scp -r . ubuntu@89.167.83.224:/var/www/kore/
# SSH Targon: ssh rentals-cwgqpzptji9bxvpj@ssh.deployments.targon.com

## Kontext-Regeln
- NIEMALS Bittensor/KORE mit Client-Projekten mischen
- Sicherheit: API-Keys nur in .env, nie in Code
- RL-Scoring-Logik ist sensibel — vor Änderungen dokumentieren
