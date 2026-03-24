import requests
from datetime import datetime

TOKEN = "8540573483:AAHnPkPT0a4DE4NgtmUXmDuatZVL7isCPJ4"
CHAT_ID = "1087337645"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def get_tao_price():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bittensor&vs_currencies=usd,eur", timeout=10)
        d = r.json()["bittensor"]
        return f"${d['usd']} USD / €{d['eur']} EUR"
    except:
        return "Nicht verfügbar"

def get_taostats():
    try:
        r = requests.get("https://taostats.io/api/v1/price", timeout=10)
        return r.json()
    except:
        return None

def run():
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    preis = get_tao_price()

    send(f"""🧠 <b>Bittensor Briefing</b>
🕐 {now}

💰 <b>TAO Preis:</b> {preis}

<b>Deine Subnetze:</b>
⚡ SN6  Numinous    — Trading Signals
🔬 SN50 Synth       — Tide-Chart Predictions
🧬 SN68 MetaNova    — Drug Discovery Mining
🤖 SN22 Desearch    — Web Search

<b>Arbos Status:</b>
→ Targon Pod: ssh rentals-cwgqpzptji9bxvpj@...
→ Schreib /status für Server-Übersicht

<b>Heute zu tun:</b>
- Arbos Telegram Control aktivieren
- Synth SN50 → gTrade Loop testen""")

if __name__ == "__main__":
    run()
