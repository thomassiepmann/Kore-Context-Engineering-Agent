import os, requests, subprocess, time
from datetime import datetime

TOKEN = "8540573483:AAHnPkPT0a4DE4NgtmUXmDuatZVL7isCPJ4"
CHAT_ID = "1087337645"
BASE = f"https://api.telegram.org/bot{TOKEN}"

def send(text):
    requests.post(f"{BASE}/sendMessage", data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def check_port(port):
    try:
        requests.get(f"http://localhost:{port}", timeout=3)
        return "✅"
    except:
        return "❌"

def cmd_status():
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    send(f"""🤖 <b>KORE Server Status</b>
🕐 {now}

{check_port(9000)}  KORE Agent       :9000
{check_port(8080)}  Kistengenerator  :8080
{check_port(8001)}  Kisten-Backend   :8001
{check_port(8090)}  Biotools         :8090
{check_port(3000)}  Tafill Website   :3000

🖥 Server: 89.167.83.224""")

def cmd_health():
    disk = subprocess.run(["df","-h","/"], capture_output=True, text=True).stdout.split("\n")[1].split()
    mem  = subprocess.run(["free","-h"], capture_output=True, text=True).stdout.split("\n")[1].split()
    load = open("/proc/loadavg").read().split()[:3]
    send(f"""💻 <b>Server Health</b>

💾 Disk: {disk[2]} / {disk[1]} ({disk[4]})
🧠 RAM:  {mem[2]} / {mem[1]}
⚡ Load: {' '.join(load)}""")

def cmd_briefing():
    now = datetime.now().strftime("%d.%m.%Y")
    send(f"""📋 <b>Tages-Briefing {now}</b>

<b>Projekte:</b>
{check_port(9000)}  KORE Agent
{check_port(8080)}  Kistengenerator
{check_port(8090)}  Biotools Workspace
{check_port(3000)}  Tafill Website

<b>Offene TODOs:</b>
- Kistengenerator: KistenFestpreis Bug fixen
- Tafill: SSL + DNS einrichten
- MeerAtmen: Entwicklung starten
- Arbos: Trading Loop aktivieren

<b>KORE Cronjobs aktiv:</b>
- tägl. 03:00 ArXiv Crawler
- So. 03:30 Memory Update""")

def cmd_deploy(projekt):
    pfade = {
        "tafill":          "/var/www/tafill-baumpflege",
        "kore":            "/var/www/kore-agent",
        "kistengenerator": "/var/www/kistengenerator-v2",
        "biotools":        "/var/www/biotools",
    }
    if projekt not in pfade:
        send(f"❓ Unbekannt: {projekt}\nVerfügbar: {', '.join(pfade.keys())}")
        return
    send(f"🚀 Deploy {projekt} gestartet...")
    r = subprocess.run(["git","-C",pfade[projekt],"pull"], capture_output=True, text=True)
    if r.returncode == 0:
        send(f"✅ {projekt} aktualisiert!\n{r.stdout[:300]}")
    else:
        send(f"❌ Fehler:\n{r.stderr[:300]}")

def cmd_logs(dienst):
    r = subprocess.run(["journalctl","-u",dienst,"--no-pager","-n","20"], capture_output=True, text=True)
    send(f"📜 <b>Logs {dienst}:</b>\n<pre>{r.stdout[-1000:]}</pre>")

def process(update):
    try:
        text = update.get("message",{}).get("text","").strip()
        if not text.startswith("/"): return
        parts = text.split()
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if   cmd == "/status":   cmd_status()
        elif cmd == "/health":   cmd_health()
        elif cmd == "/briefing": cmd_briefing()
        elif cmd == "/deploy":   cmd_deploy(arg)
        elif cmd == "/logs":     cmd_logs(arg or "kore")
        elif cmd == "/start":
            send("👋 <b>KORE Bot aktiv!</b>\n\n/status — alle Projekte\n/health — Server\n/briefing — Tagesübersicht\n/deploy [projekt] — Git Pull\n/logs [dienst] — Logs")
        else:
            send(f"❓ Unbekannt: {cmd}\n\n/status /health /briefing /deploy /logs")
    except Exception as e:
        send(f"❌ Fehler: {e}")

def run():
    send("🤖 <b>KORE Telegram Bot gestartet!</b>\n\nSchreib /status um alle Projekte zu sehen.")
    offset = 0
    while True:
        try:
            r = requests.get(f"{BASE}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=35)
            for u in r.json().get("result", []):
                offset = u["update_id"] + 1
                process(u)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    run()
