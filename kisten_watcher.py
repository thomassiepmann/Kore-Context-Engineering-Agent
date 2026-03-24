import requests
from datetime import datetime

TOKEN = "8540573483:AAHnPkPT0a4DE4NgtmUXmDuatZVL7isCPJ4"
CHAT_ID = "1087337645"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def check():
    fehler = []

    # Backend erreichbar?
    try:
        r = requests.get("http://localhost:8001/api/kistenpreise", timeout=5)
        if r.status_code != 200:
            fehler.append(f"❌ Backend antwortet mit Status {r.status_code}")
        else:
            # Preise prüfen
            kisten = r.json()
            if isinstance(kisten, list):
                ohne_preis = []
                for k in kisten:
                    if isinstance(k, dict):
                        preis = k.get("preis") or k.get("festpreis") or k.get("price") or 0
                        if not preis or float(preis) <= 0:
                            ohne_preis.append(k.get("name", k.get("id", "?")))
                if ohne_preis:
                    fehler.append(f"⚠️ Kisten ohne Preis: {', '.join(str(x) for x in ohne_preis)}")
            else:
                fehler.append(f"⚠️ Unerwartetes Format: {type(kisten)}")
    except Exception as e:
        fehler.append(f"❌ Backend nicht erreichbar: {e}")

    if fehler:
        now = datetime.now().strftime("%d.%m %H:%M")
        send(f"🔧 <b>Kistengenerator Alert {now}</b>\n\n" + "\n".join(fehler))
    else:
        print("✅ Kistengenerator OK")

if __name__ == "__main__":
    check()
