from flask import Flask, request
import requests
import os
import datetime

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

URL = "https://kktix.com/events/akiba1/registrations/new"

def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def check_ticket():
    res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    return ("自行選位" in res.text or "電腦配位" in res.text)

@app.route("/")
def run():
    mode = request.args.get("mode", "check")

    from datetime import datetime, timezone, timedelta

    tw = timezone(timedelta(hours=8))
    now = datetime.now(tw).strftime("%H:%M:%S")

    # 🟡 每小時狀態回報
    if mode == "status":
        send(f"🟡 系統正常運作中（台灣時間{now}）")
        return "status ok"

    # 🔥 查票模式
    if check_ticket():
        send(f"🔥 KKTIX 有票了！（{now}）")
        return "有票"
    else:
        return "沒票"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)