from flask import Flask
import requests
import os

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

URL = "https://kktix.com/events/akiba1/registrations/new"

def send_discord(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def check_ticket():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    text = res.text
    return ("自行選位" in text or "電腦配位" in text)

@app.route("/")
def run_check():
    if check_ticket():
        send_discord("🔥 KKTIX 有票了！")
        return "有票了"
    else:
        return "還沒票"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)