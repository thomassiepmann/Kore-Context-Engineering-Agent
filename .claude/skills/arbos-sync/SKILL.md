# arbos-sync
description: Sync local changes to Targon Pod and check Arbos status

## Live Context (auto-injected)
- Local git status: !`git status --short`
- Files changed vs last push: !`git diff origin/main --name-only 2>/dev/null | head -20`
- Local Arbos structure: !`find . -name "*.py" | grep -v __pycache__ | head -20`
- Local Python version: !`python3 --version`

## Instructions
1. Check what changed locally
2. Sync to Targon Pod: `rsync -avz --exclude '__pycache__' --exclude '.git' . rentals-cwgqpzptji9bxvpj@ssh.deployments.targon.com:~/Arbos/`
3. Optionally restart the agent on Targon
4. Verify changes are live

Sync reason / what changed: [BESCHREIBUNG]
