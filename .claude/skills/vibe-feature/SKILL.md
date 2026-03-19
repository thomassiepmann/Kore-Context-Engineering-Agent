# vibe-feature
description: Extend KORE Agent or Arbos with a new capability

## Live Context (auto-injected)
- Agent files: !`find . -name "*.py" -not -path "*/__pycache__/*" -not -path "*/.git/*" | head -30`
- Structure: !`tree -L 3 -I "__pycache__|.git|venv|node_modules"`
- Git status: !`git status --short`
- Recent commits: !`git log --oneline -5`
- DB schema: !`sqlite3 kore.db ".schema" 2>/dev/null | head -60 || echo "DB not found locally"`
- DB tables overview: !`sqlite3 kore.db "SELECT name FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "No DB"`
- KORE health: !`curl -s http://localhost:9000/health 2>/dev/null || echo "Port 9000 offline"`
- Active cronjobs: !`crontab -l 2>/dev/null || echo "No crontab"`
- Env vars (safe): !`printenv | grep -E 'CHUTES|OPENROUTER|TELEGRAM|BITTENSOR' | sed 's/=.*/=***/'`

## Instructions
Extend the KORE Agent or Arbos framework with this capability.
- Python, clean code with docstrings
- No hardcoded keys — use os.getenv()
- If it's a new module: add it to the main loop
- If it's RL-related: preserve existing scoring logic
- Telegram integration if it needs user control

Feature: [DEIN VIBE-TEXT]
