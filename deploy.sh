#!/bin/bash
set -e
echo "🚀 KORE Deploy startet..."
if [ ! -d "/var/www/kore-agent" ]; then
    git clone https://github.com/thomassiepmann/Kore-Context-Engineering-Agent.git /var/www/kore-agent
fi
cd /var/www/kore-agent
pip install -r requirements.txt --break-system-packages -q
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Bitte CHUTES_API_KEY in /var/www/kore-agent/.env eintragen!"
fi
cp kore.service /etc/systemd/system/kore.service
systemctl daemon-reload
systemctl enable kore
systemctl start kore
(crontab -l 2>/dev/null | grep -v kore; echo "0 3 * * * cd /var/www/kore-agent && /usr/bin/python3 learner.py >> /var/log/kore-learner.log 2>&1") | crontab -
echo "✅ KORE läuft auf Port 9000"
echo "🌐 http://89.167.83.224:9000/widget"
